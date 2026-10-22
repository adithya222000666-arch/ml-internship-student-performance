"""
Week 4: End-to-End Machine Learning Pipeline
Student Performance Prediction System

Trains and evaluates regression models to predict student final grade (G3),
evaluating Linear Regression and Random Forest Regression (and Ridge Regression),
handling numerical and categorical preprocessing via ColumnTransformer,
and serializing the complete fitted pipeline and metadata.
"""

from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

from sklearn.model_selection import train_test_split, cross_validate, KFold
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# -----------------------------------------------------------------------------
# 1. Directory and Path Configuration
# -----------------------------------------------------------------------------
WEEK4_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = WEEK4_DIR.parent
DATA_PATH = PROJECT_ROOT / "week1" / "data" / "student-mat.csv"
MODELS_DIR = WEEK4_DIR / "models"
OUTPUTS_DIR = WEEK4_DIR / "outputs"

MODELS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_STATE = 42
TARGET_COLUMN = "G3"
EXCLUDED_FEATURES = ["G1", "G2", "G3"]


def load_and_validate_data(csv_path: Path) -> pd.DataFrame:
    """Load and validate the student-mat.csv dataset."""
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Dataset not found at expected path: {csv_path}\n"
            "Please ensure week1/data/student-mat.csv exists."
        )

    df = pd.read_csv(csv_path, sep=";")
    print(f"[DATA] Loaded dataset shape: {df.shape}")

    # Validate essential target and structure
    if TARGET_COLUMN not in df.columns:
        raise ValueError(f"Target column '{TARGET_COLUMN}' not found in dataset columns: {df.columns.tolist()}")

    for col in ["G1", "G2"]:
        if col not in df.columns:
            print(f"[DATA WARNING] Earlier grade column '{col}' not found.")

    return df


def build_preprocessor(numerical_cols: list[str], categorical_cols: list[str]) -> ColumnTransformer:
    """
    Construct scikit-learn ColumnTransformer for numerical and categorical features.
    Numerical: Median imputation + StandardScaler
    Categorical: Most-frequent imputation + OneHotEncoder(handle_unknown='ignore')
    """
    numeric_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    categorical_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numerical_cols),
            ("cat", categorical_transformer, categorical_cols)
        ],
        remainder="drop"
    )
    return preprocessor


def train_and_evaluate():
    """Main execution function for the ML pipeline."""
    print("=" * 70)
    print("WEEK 4 CAPSTONE: END-TO-END MACHINE LEARNING PIPELINE")
    print("=" * 70)

    # 1. Load data
    df = load_and_validate_data(DATA_PATH)

    # 2. Separate target and features (strictly excluding G1, G2, G3)
    feature_cols = [c for c in df.columns if c not in EXCLUDED_FEATURES]
    X = df[feature_cols].copy()
    y = df[TARGET_COLUMN].copy()

    # Verify no missing target rows
    valid_mask = y.notna()
    X = X.loc[valid_mask].reset_index(drop=True)
    y = y.loc[valid_mask].reset_index(drop=True)

    # Identify numerical and categorical columns
    numerical_cols = X.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols = X.select_dtypes(exclude=["number"]).columns.tolist()

    print(f"[FEATURES] Total input features: {len(feature_cols)}")
    print(f"[FEATURES] Numerical features ({len(numerical_cols)}): {numerical_cols}")
    print(f"[FEATURES] Categorical features ({len(categorical_cols)}): {categorical_cols}")
    print(f"[TARGET] Target column: {TARGET_COLUMN} (Scale: {y.min()} to {y.max()})")

    # Feature statistics for inference validation
    feature_meta = {}
    for col in numerical_cols:
        feature_meta[col] = {
            "type": "numeric",
            "min": float(X[col].min()),
            "max": float(X[col].max()),
            "mean": float(X[col].mean()),
            "median": float(X[col].median()),
            "default": float(X[col].median())
        }
    for col in categorical_cols:
        unique_vals = sorted(X[col].dropna().unique().tolist())
        mode_val = X[col].mode()[0]
        feature_meta[col] = {
            "type": "categorical",
            "allowed_values": unique_vals,
            "mode": mode_val,
            "default": mode_val
        }

    # 3. Train-test split (reproducible 80/20 split matching Week 2)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.20,
        random_state=RANDOM_STATE
    )
    print(f"[SPLIT] Train samples: {len(X_train)} | Test samples: {len(X_test)}")

    # 4. Define candidate models
    candidate_models = {
        "Linear Regression": LinearRegression(),
        "Ridge Regression": Ridge(alpha=1.0, random_state=RANDOM_STATE),
        "Random Forest": RandomForestRegressor(
            n_estimators=200,
            random_state=RANDOM_STATE,
            min_samples_leaf=2
        )
    }

    # 5. Cross-validation and Test Evaluation
    cv_strategy = KFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    model_results = []
    fitted_pipelines = {}
    test_predictions = pd.DataFrame({"Actual_G3": y_test.values})

    for name, estimator in candidate_models.items():
        preprocessor = build_preprocessor(numerical_cols, categorical_cols)
        pipeline = Pipeline([
            ("preprocessor", preprocessor),
            ("model", estimator)
        ])

        # Cross-validation on training data
        cv_scores = cross_validate(
            pipeline,
            X_train,
            y_train,
            cv=cv_strategy,
            scoring={
                "mae": "neg_mean_absolute_error",
                "rmse": "neg_root_mean_squared_error",
                "r2": "r2"
            },
            return_train_score=True
        )

        cv_mae = -cv_scores["test_mae"].mean()
        cv_rmse = -cv_scores["test_rmse"].mean()
        cv_r2 = cv_scores["test_r2"].mean()

        # Fit on entire training set
        pipeline.fit(X_train, y_train)
        fitted_pipelines[name] = pipeline

        # Predictions on train and test
        y_train_pred = pipeline.predict(X_train)
        y_test_pred = pipeline.predict(X_test)

        train_mae = mean_absolute_error(y_train, y_train_pred)
        train_rmse = mean_squared_error(y_train, y_train_pred) ** 0.5
        train_r2 = r2_score(y_train, y_train_pred)

        test_mae = mean_absolute_error(y_test, y_test_pred)
        test_rmse = mean_squared_error(y_test, y_test_pred) ** 0.5
        test_r2 = r2_score(y_test, y_test_pred)

        model_results.append({
            "Model": name,
            "CV_MAE": round(cv_mae, 4),
            "CV_RMSE": round(cv_rmse, 4),
            "CV_R2": round(cv_r2, 4),
            "Train_MAE": round(train_mae, 4),
            "Train_RMSE": round(train_rmse, 4),
            "Train_R2": round(train_r2, 4),
            "Test_MAE": round(test_mae, 4),
            "Test_RMSE": round(test_rmse, 4),
            "Test_R2": round(test_r2, 4),
        })

        test_predictions[name] = y_test_pred

        print(f"\n--- {name} ---")
        print(f"  5-Fold CV  -> MAE: {cv_mae:.4f}, RMSE: {cv_rmse:.4f}, R2: {cv_r2:.4f}")
        print(f"  Train Set  -> MAE: {train_mae:.4f}, RMSE: {train_rmse:.4f}, R2: {train_r2:.4f}")
        print(f"  Test Set   -> MAE: {test_mae:.4f}, RMSE: {test_rmse:.4f}, R2: {test_r2:.4f}")

    results_df = pd.DataFrame(model_results)
    print("\n" + "=" * 70)
    print("MODEL COMPARISON SUMMARY")
    print("=" * 70)
    print(results_df.to_string(index=False))

    # 6. Save model comparison and evaluation summaries
    results_df.to_csv(OUTPUTS_DIR / "model_comparison.csv", index=False)
    test_predictions.to_csv(OUTPUTS_DIR / "test_predictions.csv", index=False)

    with open(OUTPUTS_DIR / "evaluation_summary.json", "w") as f:
        json.dump(model_results, f, indent=4)

    # 7. Select champion model (lowest Test MAE & highest Test R2)
    best_row = results_df.sort_values(by=["Test_MAE", "Test_RMSE"], ascending=[True, True]).iloc[0]
    best_model_name = best_row["Model"]
    champion_pipeline = fitted_pipelines[best_model_name]
    print(f"\n[CHAMPION] Selected Best Model: {best_model_name} (Test MAE: {best_row['Test_MAE']}, Test R2: {best_row['Test_R2']})")

    # 8. Save production artifact and metadata
    model_artifact_path = MODELS_DIR / "student_performance_pipeline.joblib"
    joblib.dump(champion_pipeline, model_artifact_path)
    print(f"[SAVE] Serialized full pipeline to: {model_artifact_path}")

    # Generate metadata file for application inference and documentation
    metadata = {
        "model_name": best_model_name,
        "artifact_file": "student_performance_pipeline.joblib",
        "target": TARGET_COLUMN,
        "target_range": [0, 20],
        "total_training_samples": len(X_train),
        "total_test_samples": len(X_test),
        "feature_count": len(feature_cols),
        "feature_names": feature_cols,
        "numerical_features": numerical_cols,
        "categorical_features": categorical_cols,
        "feature_schema": feature_meta,
        "evaluation_summary": model_results,
        "champion_metrics": {
            "Test_MAE": float(best_row["Test_MAE"]),
            "Test_RMSE": float(best_row["Test_RMSE"]),
            "Test_R2": float(best_row["Test_R2"]),
            "CV_MAE": float(best_row["CV_MAE"]),
            "CV_RMSE": float(best_row["CV_RMSE"]),
            "CV_R2": float(best_row["CV_R2"])
        }
    }

    metadata_path = MODELS_DIR / "model_metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=4)
    print(f"[SAVE] Serialized model metadata to: {metadata_path}")

    # 9. Visualizations
    sns.set_theme(style="whitegrid")

    # A. Model Comparison Bar Chart
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    metrics_to_plot = [("Test_MAE", "MAE (Lower is Better)", "#2b5c8f"),
                       ("Test_RMSE", "RMSE (Lower is Better)", "#d95f02"),
                       ("Test_R2", "R² Score (Higher is Better)", "#2ca02c")]

    for ax, (metric, title, color) in zip(axes, metrics_to_plot):
        bars = ax.bar(results_df["Model"], results_df[metric], color=color, alpha=0.85, edgecolor="black")
        ax.set_title(title, fontsize=12, fontweight="bold")
        ax.set_ylabel(metric)
        ax.tick_params(axis="x", rotation=15)
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f"{height:.3f}",
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3), textcoords="offset points",
                        ha="center", va="bottom", fontsize=10, fontweight="bold")

    plt.suptitle("Supervised Regression Models - Test Set Comparison", fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    chart1_path = OUTPUTS_DIR / "model_comparison_metrics.png"
    plt.savefig(chart1_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[PLOT] Saved: {chart1_path}")

    # B. Actual vs Predicted for Champion Model
    y_test_arr = np.array(y_test)
    y_champ_arr = np.array(test_predictions[best_model_name])
    residuals = y_test_arr - y_champ_arr

    plt.figure(figsize=(7, 6))
    plt.scatter(y_test_arr, y_champ_arr, color="#1f77b4", alpha=0.7, edgecolors="k", s=60, label="Test Predictions")
    min_val = min(y_test_arr.min(), y_champ_arr.min())
    max_val = max(y_test_arr.max(), y_champ_arr.max())
    plt.plot([min_val, max_val], [min_val, max_val], "r--", linewidth=2, label="Ideal (y = x)")
    plt.title(f"Actual vs. Predicted Final Grade (G3)\n{best_model_name}", fontsize=13, fontweight="bold")
    plt.xlabel("Actual G3 Grade (0-20)", fontsize=11)
    plt.ylabel("Predicted G3 Grade (0-20)", fontsize=11)
    plt.legend(frameon=True)
    plt.tight_layout()
    chart2_path = OUTPUTS_DIR / "actual_vs_predicted.png"
    plt.savefig(chart2_path, dpi=300)
    plt.close()
    print(f"[PLOT] Saved: {chart2_path}")

    # C. Residuals Distribution
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    sns.histplot(residuals, kde=True, ax=axes[0], color="#6a3d9a", bins=15)
    axes[0].axvline(0, color="red", linestyle="--", linewidth=1.5)
    axes[0].set_title(f"Residuals Distribution ({best_model_name})", fontsize=12, fontweight="bold")
    axes[0].set_xlabel("Residual (Actual - Predicted)")

    axes[1].scatter(y_champ_arr, residuals, alpha=0.7, color="#33a02c", edgecolors="k")
    axes[1].axhline(0, color="red", linestyle="--", linewidth=1.5)
    axes[1].set_title("Residuals vs. Fitted Values", fontsize=12, fontweight="bold")
    axes[1].set_xlabel("Fitted (Predicted) Grade")
    axes[1].set_ylabel("Residual")

    plt.tight_layout()
    chart3_path = OUTPUTS_DIR / "residuals_distribution.png"
    plt.savefig(chart3_path, dpi=300)
    plt.close()
    print(f"[PLOT] Saved: {chart3_path}")

    # D. Feature Importance (Random Forest)
    rf_pipeline = fitted_pipelines["Random Forest"]
    rf_model = rf_pipeline.named_steps["model"]
    preproc = rf_pipeline.named_steps["preprocessor"]

    # Extract transformed feature names
    cat_encoder = preproc.named_transformers_["cat"].named_steps["encoder"]
    cat_feature_names = cat_encoder.get_feature_names_out(categorical_cols).tolist()
    all_feature_names = numerical_cols + cat_feature_names

    if hasattr(rf_model, "feature_importances_"):
        importances = rf_model.feature_importances_
        fi_df = pd.DataFrame({
            "Feature": all_feature_names,
            "Importance": importances
        }).sort_values(by="Importance", ascending=False).head(15)

        plt.figure(figsize=(10, 6))
        sns.barplot(data=fi_df, x="Importance", y="Feature", hue="Feature", palette="viridis", legend=False)
        plt.title("Top 15 Most Important Features (Random Forest Regressor)", fontsize=13, fontweight="bold")
        plt.xlabel("Gini Feature Importance")
        plt.tight_layout()
        chart4_path = OUTPUTS_DIR / "feature_importance.png"
        plt.savefig(chart4_path, dpi=300)
        plt.close()
        print(f"[PLOT] Saved: {chart4_path}")

    print("\nPipeline execution and artifact generation completed successfully!")
    return metadata


if __name__ == "__main__":
    train_and_evaluate()
