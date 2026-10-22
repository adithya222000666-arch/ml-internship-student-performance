"""
Student Performance Prediction System - Flask Web Application and Prediction API
Week 4 Final Capstone Project
"""

import os
import json
import logging
from pathlib import Path
from typing import Any, Dict, Tuple

import joblib
import numpy as np
import pandas as pd
from flask import Flask, jsonify, render_template, request

# -----------------------------------------------------------------------------
# Configuration and Logging
# -----------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("student_performance_app")

BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"
MODEL_PATH = MODELS_DIR / "student_performance_pipeline.joblib"
METADATA_PATH = MODELS_DIR / "model_metadata.json"

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static")
)

# Global model and metadata state
PIPELINE = None
METADATA: Dict[str, Any] = {}


def load_artifacts() -> bool:
    """Load serialized ML pipeline and schema metadata."""
    global PIPELINE, METADATA
    try:
        if not MODEL_PATH.exists():
            logger.error(f"Model artifact not found at {MODEL_PATH}")
            return False

        PIPELINE = joblib.load(MODEL_PATH)
        logger.info(f"Loaded trained pipeline from {MODEL_PATH}")

        if METADATA_PATH.exists():
            with open(METADATA_PATH, "r", encoding="utf-8") as f:
                METADATA = json.load(f)
            logger.info("Loaded model metadata successfully")
        else:
            logger.warning(f"Metadata file not found at {METADATA_PATH}. Using fallback schema.")
            METADATA = {}

        return True
    except Exception as e:
        logger.error(f"Failed to load model artifacts: {e}", exc_info=True)
        return False


# Attempt eager loading
load_artifacts()


# -----------------------------------------------------------------------------
# Academic Performance Categorization
# -----------------------------------------------------------------------------
def categorize_grade(grade: float) -> Tuple[str, str, str]:
    """
    Categorize Portuguese 0-20 scale final grade (G3).
    Returns (Category Name, Description, CSS Classification Badge).
    """
    if grade >= 16.0:
        return "Excellent", "Distinction (Very Strong Academic Standing)", "badge-excellent"
    elif grade >= 14.0:
        return "Good", "Above Average Academic Performance", "badge-good"
    elif grade >= 12.0:
        return "Satisfactory", "Solid Passing Standing", "badge-satisfactory"
    elif grade >= 10.0:
        return "Sufficient", "Passing Grade (Borderline)", "badge-sufficient"
    else:
        return "Academic Support Recommended", "Below Passing Standard (G3 < 10)", "badge-at-risk"


# -----------------------------------------------------------------------------
# Input Validation Helper
# -----------------------------------------------------------------------------
def validate_student_payload(payload: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Validate inference payload against the exact feature schema.
    Returns (is_valid, error_message, sanitized_data).
    """
    if not isinstance(payload, dict):
        return False, "Payload must be a valid JSON object.", {}

    feature_schema = METADATA.get("feature_schema", {})
    expected_features = METADATA.get("feature_names", [])

    if not expected_features:
        return False, "Model metadata schema is not initialized.", {}

    sanitized: Dict[str, Any] = {}
    missing_fields = []

    for feat in expected_features:
        if feat not in payload:
            missing_fields.append(feat)

    if missing_fields:
        return False, f"Missing required feature(s): {', '.join(missing_fields)}", {}

    # Validate each feature by type and allowed values/ranges
    for feat in expected_features:
        val = payload[feat]
        schema = feature_schema.get(feat, {})
        feat_type = schema.get("type", "numeric")

        if feat_type == "numeric":
            try:
                num_val = float(val)
            except (ValueError, TypeError):
                return False, f"Feature '{feat}' must be a valid numeric value. Received: {val!r}", {}

            if not np.isfinite(num_val):
                return False, f"Feature '{feat}' must be a finite number. Received: {val!r}", {}

            min_bound = schema.get("min", 0.0)
            max_bound = schema.get("max", 100.0)

            # Reasonable range check
            if num_val < min_bound or num_val > max_bound:
                return (
                    False,
                    f"Feature '{feat}' value {num_val} is outside expected range [{min_bound}, {max_bound}].",
                    {}
                )
            sanitized[feat] = num_val

        elif feat_type == "categorical":
            str_val = str(val).strip()
            allowed = schema.get("allowed_values", [])
            if allowed and str_val not in allowed:
                return (
                    False,
                    f"Feature '{feat}' received invalid category '{str_val}'. Allowed values: {allowed}",
                    {}
                )
            sanitized[feat] = str_val

        else:
            sanitized[feat] = val

    return True, "", sanitized


# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------
@app.route("/", methods=["GET"])
def home():
    """Render web application interface."""
    return render_template(
        "index.html",
        metadata=METADATA,
        model_loaded=(PIPELINE is not None)
    )


@app.route("/health", methods=["GET"])
def health():
    """Health and model readiness endpoint."""
    model_loaded = PIPELINE is not None
    status_code = 200 if model_loaded else 503

    response = {
        "status": "healthy" if model_loaded else "unhealthy",
        "service": "student-performance-prediction",
        "model_loaded": model_loaded,
        "model_name": METADATA.get("model_name", "Random Forest Regressor"),
        "target": METADATA.get("target", "G3"),
        "target_scale": "0-20 scale",
        "feature_count": len(METADATA.get("feature_names", [])),
        "metrics": METADATA.get("champion_metrics", {})
    }
    return jsonify(response), status_code


@app.route("/api/schema", methods=["GET"])
def schema():
    """Returns the input features schema and allowed categorical choices."""
    return jsonify({
        "status": "success",
        "target": METADATA.get("target", "G3"),
        "target_range": METADATA.get("target_range", [0, 20]),
        "feature_count": len(METADATA.get("feature_names", [])),
        "features": METADATA.get("feature_names", []),
        "numerical_features": METADATA.get("numerical_features", []),
        "categorical_features": METADATA.get("categorical_features", []),
        "schema": METADATA.get("feature_schema", {})
    })


@app.route("/predict", methods=["POST"])
def predict():
    """
    Generate student final grade prediction from input attributes.
    Accepts JSON payload. Returns structured prediction response.
    """
    global PIPELINE
    if PIPELINE is None:
        # Attempt reloading once in case artifact was generated after start
        if not load_artifacts():
            return jsonify({
                "status": "error",
                "message": "Prediction model is currently unavailable on this server."
            }), 503

    # Parse input payload
    if request.is_json:
        payload = request.get_json(silent=True)
        if payload is None:
            return jsonify({
                "status": "error",
                "message": "Invalid or malformed JSON payload."
            }), 400
    elif request.form:
        payload = request.form.to_dict()
    else:
        return jsonify({
            "status": "error",
            "message": "Request must have Content-Type 'application/json' or valid form data."
        }), 400

    # Validate against schema
    is_valid, error_msg, sanitized_data = validate_student_payload(payload)
    if not is_valid:
        return jsonify({
            "status": "error",
            "message": error_msg
        }), 400

    try:
        # Construct single-row DataFrame with exact feature order
        ordered_features = METADATA.get("feature_names", list(sanitized_data.keys()))
        input_df = pd.DataFrame([sanitized_data])[ordered_features]

        # Generate prediction via pipeline without retraining
        raw_pred = float(PIPELINE.predict(input_df)[0])

        # Clip bounded prediction to the documented 0-20 academic scale
        bounded_pred = float(np.clip(raw_pred, 0.0, 20.0))
        rounded_pred = round(bounded_pred, 2)

        # Categorize academic standing
        category, category_desc, badge_class = categorize_grade(rounded_pred)

        response = {
            "status": "success",
            "predicted_g3": rounded_pred,
            "raw_prediction": round(raw_pred, 4),
            "scale": "0-20",
            "is_clipped": raw_pred != bounded_pred,
            "academic_category": category,
            "standing_description": category_desc,
            "badge_class": badge_class,
            "model_used": METADATA.get("model_name", "Random Forest Regressor"),
            "disclaimer": (
                "This predicted grade is an automated statistical estimate generated by a machine "
                "learning model based on historical survey attributes. It does not guarantee student "
                "outcomes and should be used solely as a supplementary advisory indicator."
            )
        }
        logger.info(f"Prediction successful: G3={rounded_pred} ({category})")
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Inference error: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": "An error occurred during prediction inference. Please verify inputs."
        }), 500


# -----------------------------------------------------------------------------
# Application Entry Point
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting Student Performance Prediction System on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)
