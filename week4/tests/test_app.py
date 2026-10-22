"""
Automated Pytest Test Suite for Student Performance Prediction System
Week 4 Capstone QA Verification
"""

import sys
from pathlib import Path
import pytest
import numpy as np

# Ensure week4 is in sys.path
WEEK4_DIR = Path(__file__).resolve().parent.parent
if str(WEEK4_DIR) not in sys.path:
    sys.path.insert(0, str(WEEK4_DIR))

import app as flask_app_module
from app import app, PIPELINE, METADATA, load_artifacts


@pytest.fixture(scope="module")
def client():
    """Create Flask test client."""
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        with app.app_context():
            load_artifacts()
            yield test_client


@pytest.fixture
def valid_payload():
    """Return a complete, valid student attribute payload."""
    return {
        "school": "GP",
        "sex": "F",
        "age": 17,
        "address": "U",
        "famsize": "GT3",
        "Pstatus": "T",
        "Medu": 3,
        "Fedu": 3,
        "Mjob": "other",
        "Fjob": "other",
        "reason": "course",
        "guardian": "mother",
        "traveltime": 1,
        "studytime": 2,
        "failures": 0,
        "schoolsup": "no",
        "famsup": "yes",
        "paid": "no",
        "activities": "yes",
        "nursery": "yes",
        "higher": "yes",
        "internet": "yes",
        "romantic": "no",
        "famrel": 4,
        "freetime": 3,
        "goout": 3,
        "Dalc": 1,
        "Walc": 1,
        "health": 4,
        "absences": 4
    }


# -----------------------------------------------------------------------------
# 1. Startup & Model Artifact Tests
# -----------------------------------------------------------------------------
def test_model_artifact_loading():
    """Test that model pipeline and metadata are successfully loaded."""
    model_path = WEEK4_DIR / "models" / "student_performance_pipeline.joblib"
    metadata_path = WEEK4_DIR / "models" / "model_metadata.json"

    assert model_path.exists(), f"Model artifact not found at {model_path}"
    assert metadata_path.exists(), f"Metadata not found at {metadata_path}"

    assert flask_app_module.PIPELINE is not None, "Pipeline was not initialized in app module"
    assert hasattr(flask_app_module.PIPELINE, "predict"), "Loaded pipeline must provide a predict method"
    assert len(flask_app_module.METADATA.get("feature_names", [])) == 30


def test_home_page(client):
    """Test GET / serves web interface successfully."""
    response = client.get("/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Student Performance Prediction System" in html
    assert "predictionForm" in html
    assert "btnPredict" in html
    assert "Gabriel Pereira" in html


def test_health_endpoint(client):
    """Test GET /health returns ready status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True
    assert data["feature_count"] == 30
    assert "metrics" in data


def test_api_schema_endpoint(client):
    """Test GET /api/schema returns feature definitions."""
    response = client.get("/api/schema")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert data["feature_count"] == 30
    assert len(data["numerical_features"]) == 13
    assert len(data["categorical_features"]) == 17


# -----------------------------------------------------------------------------
# 2. Prediction API Endpoint Tests
# -----------------------------------------------------------------------------
def test_valid_prediction_request(client, valid_payload):
    """Test POST /predict with a valid complete JSON payload."""
    response = client.post("/predict", json=valid_payload)
    assert response.status_code == 200
    data = response.get_json()

    assert data["status"] == "success"
    assert "predicted_g3" in data
    assert isinstance(data["predicted_g3"], (int, float))
    assert 0.0 <= data["predicted_g3"] <= 20.0
    assert data["scale"] == "0-20"
    assert "academic_category" in data
    assert "badge_class" in data
    assert "disclaimer" in data


def test_prediction_with_form_data(client, valid_payload):
    """Test POST /predict when submitted as form-encoded data."""
    response = client.post("/predict", data=valid_payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert 0.0 <= data["predicted_g3"] <= 20.0


def test_missing_required_fields(client, valid_payload):
    """Test POST /predict rejects payloads missing required fields."""
    incomplete_payload = valid_payload.copy()
    del incomplete_payload["studytime"]
    del incomplete_payload["school"]

    response = client.post("/predict", json=incomplete_payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data["status"] == "error"
    assert "Missing required feature(s)" in data["message"]
    assert "studytime" in data["message"]
    assert "school" in data["message"]


def test_invalid_numeric_type(client, valid_payload):
    """Test POST /predict rejects non-numeric values in numeric fields."""
    bad_payload = valid_payload.copy()
    bad_payload["age"] = "not-a-number"

    response = client.post("/predict", json=bad_payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data["status"] == "error"
    assert "must be a valid numeric value" in data["message"]


def test_invalid_numeric_range(client, valid_payload):
    """Test POST /predict rejects out-of-range numerical values."""
    bad_payload = valid_payload.copy()
    bad_payload["age"] = 99  # Valid range is 15-22

    response = client.post("/predict", json=bad_payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data["status"] == "error"
    assert "outside expected range" in data["message"]


def test_non_finite_numeric(client, valid_payload):
    """Test POST /predict rejects inf or NaN values."""
    bad_payload = valid_payload.copy()
    bad_payload["absences"] = 999999

    response = client.post("/predict", json=bad_payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data["status"] == "error"


def test_invalid_categorical_value(client, valid_payload):
    """Test POST /predict rejects unknown category strings."""
    bad_payload = valid_payload.copy()
    bad_payload["school"] = "OXFORD_UNIVERSITY"

    response = client.post("/predict", json=bad_payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data["status"] == "error"
    assert "invalid category" in data["message"]


def test_malformed_json_content(client):
    """Test POST /predict returns 400 on malformed JSON body."""
    response = client.post(
        "/predict",
        data="{bad-json: [unclosed",
        content_type="application/json"
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["status"] == "error"


def test_empty_request_body(client):
    """Test POST /predict returns 400 when body is empty."""
    response = client.post("/predict", data="", content_type="text/plain")
    assert response.status_code == 400
    data = response.get_json()
    assert data["status"] == "error"


def test_prediction_response_schema(client, valid_payload):
    """Test exact schema consistency of prediction response."""
    response = client.post("/predict", json=valid_payload)
    assert response.status_code == 200
    data = response.get_json()

    expected_keys = {
        "status",
        "predicted_g3",
        "raw_prediction",
        "scale",
        "is_clipped",
        "academic_category",
        "standing_description",
        "badge_class",
        "model_used",
        "disclaimer"
    }
    assert expected_keys.issubset(set(data.keys()))


def test_prediction_output_finite_and_bounded(client, valid_payload):
    """Test that predictions are always finite and within [0, 20]."""
    for _ in range(5):
        response = client.post("/predict", json=valid_payload)
        assert response.status_code == 200
        data = response.get_json()
        val = data["predicted_g3"]
        assert np.isfinite(val)
        assert 0.0 <= val <= 20.0


def test_predict_does_not_retrain_model(client, valid_payload):
    """Verify inference calls do not retrain or mutate model parameters."""
    pipeline_before = flask_app_module.PIPELINE
    model_step_before = pipeline_before.named_steps["model"]

    # Capture state before
    if hasattr(model_step_before, "estimators_"):
        n_estimators_before = len(model_step_before.estimators_)
        tree_sample_before = model_step_before.estimators_[0].tree_.node_count
    else:
        n_estimators_before = None
        tree_sample_before = None

    # Perform multiple predictions
    for _ in range(3):
        res = client.post("/predict", json=valid_payload)
        assert res.status_code == 200

    pipeline_after = flask_app_module.PIPELINE
    model_step_after = pipeline_after.named_steps["model"]

    assert pipeline_before is pipeline_after, "Pipeline instance changed during prediction"
    if n_estimators_before is not None:
        assert len(model_step_after.estimators_) == n_estimators_before
        assert model_step_after.estimators_[0].tree_.node_count == tree_sample_before
