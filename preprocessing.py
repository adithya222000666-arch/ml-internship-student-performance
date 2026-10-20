
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler

# ==================================================
# 1. PROJECT CONFIGURATION
# ==================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "student-mat.csv"
OUTPUT_DIR = BASE_DIR / "outputs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
sns.set_theme(style="whitegrid")


# ==================================================
# 2. LOAD THE DATASET
# ==================================================

if not DATA_PATH.exists():
    raise FileNotFoundError(
        f"Dataset not found: {DATA_PATH}\n"
        "Place student-mat.csv inside the data folder."
    )

df = pd.read_csv(DATA_PATH, sep=";")

print("\n========== DATASET OVERVIEW ==========")
print("Dataset shape:", df.shape)
print("\nFirst five rows:")
print(df.head())
print("\nDataset information:")
df.info()

print("\nStatistical summary:")
print(df.describe())


# ==================================================
# 3. DATA QUALITY CHECKS
# ==================================================

print("\n========== DATA QUALITY CHECKS ==========")

print("\nMissing values before cleaning:")
print(df.isnull().sum())

print("\nDuplicate rows:", df.duplicated().sum())

# Remove duplicate records.
df = df.drop_duplicates().copy()

# Replace infinite numerical values with missing values.
df = df.replace([np.inf, -np.inf], np.nan)

# Identify numerical and categorical columns.
numeric_cols = df.select_dtypes(
    include=np.number
).columns

categorical_cols = df.select_dtypes(
    include=["object", "category", "string"]
).columns

# Handle missing numerical values using the median.
for col in numeric_cols:
    if df[col].isnull().any():
        df[col] = df[col].fillna(df[col].median())

# Handle missing categorical values using the mode.
for col in categorical_cols:
    if df[col].isnull().any():
        mode_values = df[col].mode()

        if not mode_values.empty:
            df[col] = df[col].fillna(mode_values.iloc[0])
        else:
            df[col] = df[col].fillna("Unknown")

print("\nMissing values after cleaning:")
print(df.isnull().sum())

print("\nCleaned dataset shape:", df.shape)

df.to_csv(
    OUTPUT_DIR / "cleaned_student_data.csv",
    index=False
)


# ==================================================
# 4. EXPLORATORY DATA ANALYSIS (EDA)
# ==================================================

print("\n========== EXPLORATORY DATA ANALYSIS ==========")

# Final grade distribution.
plt.figure(figsize=(8, 5))
sns.histplot(data=df, x="G3", bins=11, kde=True)
plt.title("Distribution of Final Student Grades")
plt.xlabel("Final Grade (G3)")
plt.ylabel("Number of Students")
plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "grade_distribution.png",
    dpi=150
)
plt.close()

# Study time versus final grade.
plt.figure(figsize=(8, 5))
sns.boxplot(data=df, x="studytime", y="G3")
plt.title("Study Time vs Final Grade")
plt.xlabel("Weekly Study Time Category")
plt.ylabel("Final Grade (G3)")
plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "study_time_vs_grade.png",
    dpi=150
)
plt.close()

# Correlation heatmap.
numeric_df = df.select_dtypes(include=np.number)
correlation = numeric_df.corr()

plt.figure(figsize=(12, 9))
sns.heatmap(
    correlation,
    cmap="coolwarm",
    center=0
)
plt.title("Correlation Heatmap of Numerical Features")
plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "correlation_heatmap.png",
    dpi=150
)
plt.close()

print("EDA graphs saved successfully.")

print("\nFinal grade statistics:")
print("Mean:", round(df["G3"].mean(), 2))
print("Median:", df["G3"].median())
print("Minimum:", df["G3"].min())
print("Maximum:", df["G3"].max())


# ==================================================
# 5. FEATURE SELECTION
# ==================================================

print("\n========== FEATURE SELECTION ==========")

# Select relevant numerical columns for future analysis.
# G3 is retained here for analysis, but will be the
# prediction target rather than an input in Week 2.

selected_features = [
    "age",
    "studytime",
    "failures",
    "absences",
    "G1",
    "G2",
    "G3"
]

selected_df = df[selected_features].copy()

selected_df.to_csv(
    OUTPUT_DIR / "selected_features.csv",
    index=False
)

print("Selected columns:")
print(selected_df.columns.tolist())

print("\nSelected data preview:")
print(selected_df.head())


# ==================================================
# 6. CATEGORICAL ENCODING
# ==================================================

print("\n========== CATEGORICAL ENCODING ==========")

categorical_cols = df.select_dtypes(
    include=["object", "category", "string"]
).columns.tolist()

df_encoded = pd.get_dummies(
    df,
    columns=categorical_cols,
    dtype=int
)

df_encoded.to_csv(
    OUTPUT_DIR / "encoded_student_data.csv",
    index=False
)

print("Columns before encoding:", len(df.columns))
print("Columns after encoding:", len(df_encoded.columns))
print("Encoded dataset saved successfully.")


# ==================================================
# 7. NUMERICAL NORMALIZATION
# ==================================================

print("\n========== NUMERICAL NORMALIZATION ==========")

# Demonstration only: fit on the full dataset.
# In Week 2, fit the scaler on training data only
# to prevent data leakage.

scaler = StandardScaler()

numeric_cols = df_encoded.select_dtypes(
    include=np.number
).columns

df_scaled = df_encoded.copy()

df_scaled[numeric_cols] = scaler.fit_transform(
    df_encoded[numeric_cols]
)

df_scaled.to_csv(
    OUTPUT_DIR / "processed_student_data.csv",
    index=False
)

print("Numerical features standardized successfully.")
print("\nScaled dataset preview:")
print(df_scaled.head())


# ==================================================
# 8. FINAL VERIFICATION
# ==================================================

print("\n========== FINAL VERIFICATION ==========")

print("Final cleaned rows:", len(df))
print("Original columns:", len(df.columns))
print("Encoded columns:", len(df_encoded.columns))

print(
    "Missing values in cleaned dataset:",
    int(df.isnull().sum().sum())
)

print(
    "Missing values in encoded dataset:",
    int(df_encoded.isnull().sum().sum())
)

expected_files = [
    "cleaned_student_data.csv",
    "selected_features.csv",
    "encoded_student_data.csv",
    "processed_student_data.csv",
    "grade_distribution.png",
    "study_time_vs_grade.png",
    "correlation_heatmap.png"
]

print("\nOutput file verification:")

for filename in expected_files:
    output_path = OUTPUT_DIR / filename

    status = (
        "CREATED"
        if output_path.exists() and output_path.stat().st_size > 0
        else "MISSING"
    )

    print(f"{filename}: {status}")
