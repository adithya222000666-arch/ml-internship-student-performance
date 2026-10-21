
import os
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    silhouette_score,
    davies_bouldin_score,
    calinski_harabasz_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.cluster import KMeans, AgglomerativeClustering

warnings.filterwarnings("ignore")

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(
    BASE_DIR, "..", "week1", "data", "student-mat.csv"
)
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

RANDOM_STATE = 42


def main():
    print("=" * 60)
    print("WEEK 3: UNSUPERVISED LEARNING")
    print("=" * 60)

    # 1. Load dataset
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(
            f"Dataset not found: {DATA_PATH}\n"
            "Check that week1/data/student-mat.csv exists."
        )

    df = pd.read_csv(DATA_PATH, sep=";")
    print(f"\nDataset shape: {df.shape}")
    print("Dataset loaded successfully.")

    # 2. Prepare features
    # Exclude grades G1, G2 and G3 from clustering.
    # This lets clusters reflect student characteristics
    # rather than being driven directly by grade columns.
    features = df.drop(columns=["G1", "G2", "G3"], errors="ignore")

    numerical_columns = features.select_dtypes(
        include=np.number
    ).columns.tolist()
    categorical_columns = features.select_dtypes(
        exclude=np.number
    ).columns.tolist()

    numerical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])

    categorical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore")),
    ])

    preprocessor = ColumnTransformer([
        ("num", numerical_pipeline, numerical_columns),
        ("cat", categorical_pipeline, categorical_columns),
    ])

    X = preprocessor.fit_transform(features)
    if hasattr(X, "toarray"):
        X = X.toarray()

    print(f"Features used: {features.shape[1]}")
    print(f"Numerical features: {len(numerical_columns)}")
    print(f"Categorical features: {len(categorical_columns)}")
    print(f"Processed feature matrix: {X.shape}")

    # 3. PCA for dimensionality reduction
    pca = PCA(n_components=2, random_state=RANDOM_STATE)
    X_pca = pca.fit_transform(X)

    explained = pca.explained_variance_ratio_.sum()
    print(f"\nPCA variance explained by 2 components: {explained:.3f}")

    pca_df = pd.DataFrame({
        "PC1": X_pca[:, 0],
        "PC2": X_pca[:, 1],
    })
    pca_df.to_csv(
        os.path.join(OUTPUT_DIR, "pca_coordinates.csv"),
        index=False,
    )

    # 4. Compare clustering algorithms
    results = []
    cluster_labels = {}

    for k in [2, 3, 4, 5, 6]:
        kmeans = KMeans(
            n_clusters=k,
            random_state=RANDOM_STATE,
            n_init=10,
        )
        labels_kmeans = kmeans.fit_predict(X)
        cluster_labels[("K-Means", k)] = labels_kmeans

        results.append({
            "Algorithm": "K-Means",
            "Clusters": k,
            "Silhouette Score": silhouette_score(X, labels_kmeans),
            "Davies-Bouldin Score": davies_bouldin_score(X, labels_kmeans),
            "Calinski-Harabasz Score": calinski_harabasz_score(X, labels_kmeans),
            "Inertia": kmeans.inertia_,
        })

        hierarchical = AgglomerativeClustering(
            n_clusters=k,
            linkage="ward",
        )
        labels_hierarchical = hierarchical.fit_predict(X)
        cluster_labels[("Hierarchical", k)] = labels_hierarchical

        results.append({
            "Algorithm": "Hierarchical",
            "Clusters": k,
            "Silhouette Score": silhouette_score(X, labels_hierarchical),
            "Davies-Bouldin Score": davies_bouldin_score(X, labels_hierarchical),
            "Calinski-Harabasz Score": calinski_harabasz_score(X, labels_hierarchical),
            "Inertia": np.nan,
        })

        print(f"Evaluated K-Means and Hierarchical clustering for k={k}")

    results_df = pd.DataFrame(results)
    results_df.to_csv(
        os.path.join(OUTPUT_DIR, "clustering_comparison.csv"),
        index=False,
    )

    # 5. Select the best configuration by silhouette score
    best_row = results_df.loc[
        results_df["Silhouette Score"].idxmax()
    ]
    best_algorithm = best_row["Algorithm"]
    best_k = int(best_row["Clusters"])
    best_labels = cluster_labels[(best_algorithm, best_k)]

    print("\nBest configuration by silhouette score:")
    print(f"Algorithm: {best_algorithm}")
    print(f"Number of clusters: {best_k}")
    print(f"Silhouette score: {best_row['Silhouette Score']:.4f}")

    # 6. Save cluster assignments
    clustered_df = df.copy()
    clustered_df["Cluster"] = best_labels
    clustered_df.to_csv(
        os.path.join(OUTPUT_DIR, "student_cluster_assignments.csv"),
        index=False,
    )

    # 7. Visualize the selected clusters in PCA space
    plot_df = pca_df.copy()
    plot_df["Cluster"] = best_labels.astype(str)

    plt.figure(figsize=(10, 6))
    sns.scatterplot(
        data=plot_df,
        x="PC1",
        y="PC2",
        hue="Cluster",
        palette="tab10",
        s=65,
        alpha=0.8,
    )
    plt.title(f"{best_algorithm} Clusters Visualized Using PCA")
    plt.xlabel("Principal Component 1")
    plt.ylabel("Principal Component 2")
    plt.tight_layout()
    plt.savefig(
        os.path.join(OUTPUT_DIR, "cluster_visualization.png"),
        dpi=300,
    )
    plt.close()

    # 8. Plot silhouette score comparison
    plt.figure(figsize=(11, 6))
    sns.lineplot(
        data=results_df,
        x="Clusters",
        y="Silhouette Score",
        hue="Algorithm",
        marker="o",
    )
    plt.title("Clustering Algorithm Comparison")
    plt.xlabel("Number of Clusters")
    plt.ylabel("Silhouette Score (higher is generally better)")
    plt.xticks([2, 3, 4, 5, 6])
    plt.tight_layout()
    plt.savefig(
        os.path.join(OUTPUT_DIR, "silhouette_comparison.png"),
        dpi=300,
    )
    plt.close()

    # 9. Record PCA information
    pca_summary = pd.DataFrame({
        "Component": ["PC1", "PC2"],
        "Explained Variance Ratio": pca.explained_variance_ratio_,
    })
    pca_summary.to_csv(
        os.path.join(OUTPUT_DIR, "pca_explained_variance.csv"),
        index=False,
    )

    print("\nFiles saved in:", OUTPUT_DIR)
    for filename in sorted(os.listdir(OUTPUT_DIR)):
        print(" -", filename)

    print("\nWeek 3 clustering task completed successfully.")


if __name__ == "__main__":
    main()
