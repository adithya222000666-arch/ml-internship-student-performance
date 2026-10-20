
from pathlib import Path
import json

import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# --------------------------------------------------
# 1. Set up project paths
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
DATA_PATH = PROJECT_DIR / "week1" / "data" / "student-mat.csv"
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_STATE = 42


# --------------------------------------------------
# 2. Load the original dataset
# --------------------------------------------------
if not DATA_PATH.exists():
    raise FileNotFoundError(
        f"Dataset not found at: {DATA_PATH}\n"
        "Check that week1/data/student-mat.csv exists."
    )

df = pd.read_csv(DATA_PATH, sep=";")

print("=" * 60)
print("WEEK 2: SUPERVISED MACHINE LEARNING")
print("=" * 60)
print(f"Dataset shape: {df.shape}")


# --------------------------------------------------
# 3. Define target and input features
# --------------------------------------------------
TARGET = "G3"

# Exclude G1 and G2 because they are earlier grades.
X = df.drop(columns=[TARGET, "G1", "G2"])
y = df[TARGET]

# Drop rows with a missing target, if any.
valid_rows = y.notna()
X = X.loc[valid_rows].copy()
y = y.loc[valid_rows].copy()

categorical_features = X.select_dtypes(
    include=["object", "category"]
).columns.tolist()

numerical_features = X.select_dtypes(
    include=["number"]
).columns.tolist()

print(f"Input features: {X.shape[1]}")
print(f"Numerical features: {len(numerical_features)}")
print(f"Categorical features: {len(categorical_features)}")
print(f"Target: {TARGET} (final grade, 0-20)")


# --------------------------------------------------
# 4. Split into training and testing sets
# --------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=RANDOM_STATE
)

print(f"Training samples: {len(X_train)}")
print(f"Testing samples: {len(X_test)}")


# --------------------------------------------------
# 5. Preprocess features without data leakage
# --------------------------------------------------
numeric_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler())
])

categorical_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("encoder", OneHotEncoder(handle_unknown="ignore"))
])

preprocessor = ColumnTransformer([
    ("numeric", numeric_pipeline, numerical_features),
    ("categorical", categorical_pipeline, categorical_features)
])


# --------------------------------------------------
# 6. Define the two regression models
# --------------------------------------------------
models = {
    "Linear Regression": LinearRegression(),
    "Random Forest": RandomForestRegressor(
        n_estimators=200,
        random_state=RANDOM_STATE,
        min_samples_leaf=2
    )
}

results = []
predictions = pd.DataFrame({
    "Actual_G3": y_test.reset_index(drop=True)
})


# --------------------------------------------------
# 7. Train and evaluate each model
# --------------------------------------------------
for model_name, estimator in models.items():
    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("model", estimator)
    ])

    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)
    rmse = mean_squared_error(y_test, y_pred) ** 0.5
    r2 = r2_score(y_test, y_pred)

    results.append({
        "Model": model_name,
        "MAE": mae,
        "RMSE": rmse,
        "R2": r2
    })

    predictions[model_name] = y_pred

    print(f"\n{model_name}")
    print(f"  MAE:  {mae:.3f}")
    print(f"  RMSE: {rmse:.3f}")
    print(f"  R²:   {r2:.3f}")


# --------------------------------------------------
# 8. Save evaluation results and predictions
# --------------------------------------------------
results_df = pd.DataFrame(results)
results_df.to_csv(OUTPUT_DIR / "model_comparison.csv", index=False)
predictions.to_csv(OUTPUT_DIR / "test_predictions.csv", index=False)

with open(OUTPUT_DIR / "evaluation_summary.json", "w") as file:
    json.dump(results, file, indent=4)

print("\nModel comparison:")
print(results_df.to_string(index=False))


# --------------------------------------------------
# 9. Plot model comparison
# --------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

axes[0].bar(results_df["Model"], results_df["MAE"])
axes[0].set_title("Mean Absolute Error (lower is better)")
axes[0].set_ylabel("MAE")
axes[0].tick_params(axis="x", rotation=15)

axes[1].bar(results_df["Model"], results_df["R2"])
axes[1].set_title("R² Score (higher is generally better)")
axes[1].set_ylabel("R²")
axes[1].tick_params(axis="x", rotation=15)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "model_comparison.png", dpi=300)
plt.close()

print("\nSaved files:")
for path in sorted(OUTPUT_DIR.iterdir()):
    print(f"  {path.name}")

print("\nWeek 2 model training completed.")
