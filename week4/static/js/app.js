/**
 * Student Performance Prediction System
 * Frontend Application Logic & Prediction API Client
 */

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("predictionForm");
    const btnPredict = document.getElementById("btnPredict");
    const btnSpinner = document.getElementById("btnSpinner");
    const resultCard = document.getElementById("resultCard");
    const errorCard = document.getElementById("errorCard");
    const errorMessage = document.getElementById("errorMessage");

    const predictedGrade = document.getElementById("predictedGrade");
    const gradeBarFill = document.getElementById("gradeBarFill");
    const resultBadge = document.getElementById("resultBadge");
    const standingTitle = document.getElementById("standingTitle");
    const standingDescription = document.getElementById("standingDescription");
    const modelUsed = document.getElementById("modelUsed");
    const rawGrade = document.getElementById("rawGrade");

    // Preset profile definitions
    const sampleProfiles = {
        high: {
            school: "GP", sex: "F", age: 16, address: "U", famsize: "GT3", Pstatus: "T",
            Medu: 4, Fedu: 4, Mjob: "teacher", Fjob: "health", reason: "reputation",
            guardian: "mother", traveltime: 1, studytime: 4, failures: 0, schoolsup: "no",
            famsup: "yes", paid: "no", activities: "yes", nursery: "yes", higher: "yes",
            internet: "yes", romantic: "no", famrel: 5, freetime: 3, goout: 2, Dalc: 1,
            Walc: 1, health: 5, absences: 2
        },
        avg: {
            school: "GP", sex: "M", age: 17, address: "U", famsize: "GT3", Pstatus: "T",
            Medu: 2, Fedu: 2, Mjob: "other", Fjob: "other", reason: "course",
            guardian: "mother", traveltime: 1, studytime: 2, failures: 0, schoolsup: "no",
            famsup: "yes", paid: "no", activities: "yes", nursery: "yes", higher: "yes",
            internet: "yes", romantic: "no", famrel: 4, freetime: 3, goout: 3, Dalc: 1,
            Walc: 1, health: 4, absences: 4
        },
        risk: {
            school: "MS", sex: "M", age: 19, address: "R", famsize: "GT3", Pstatus: "A",
            Medu: 1, Fedu: 1, Mjob: "other", Fjob: "other", reason: "other",
            guardian: "other", traveltime: 3, studytime: 1, failures: 3, schoolsup: "no",
            famsup: "no", paid: "no", activities: "no", nursery: "no", higher: "no",
            internet: "no", romantic: "yes", famrel: 2, freetime: 5, goout: 5, Dalc: 4,
            Walc: 5, health: 2, absences: 20
        }
    };

    const numericalFields = new Set([
        "age", "Medu", "Fedu", "traveltime", "studytime", "failures",
        "famrel", "freetime", "goout", "Dalc", "Walc", "health", "absences"
    ]);

    // Populate form with profile
    function applyProfile(profile) {
        Object.entries(profile).forEach(([key, val]) => {
            const el = form.elements[key];
            if (el) {
                el.value = val;
            }
        });
        hideMessages();
    }

    // Attach sample buttons
    document.getElementById("btnSampleHigh")?.addEventListener("click", () => applyProfile(sampleProfiles.high));
    document.getElementById("btnSampleAvg")?.addEventListener("click", () => applyProfile(sampleProfiles.avg));
    document.getElementById("btnSampleRisk")?.addEventListener("click", () => applyProfile(sampleProfiles.risk));
    document.getElementById("btnReset")?.addEventListener("click", () => {
        form.reset();
        applyProfile(sampleProfiles.avg);
        hideMessages();
    });

    function hideMessages() {
        if (resultCard) resultCard.style.display = "none";
        if (errorCard) errorCard.style.display = "none";
    }

    function setLoading(isLoading) {
        if (btnPredict) {
            btnPredict.disabled = isLoading;
            const btnText = btnPredict.querySelector(".btn-text");
            if (btnText) {
                btnText.textContent = isLoading ? "Computing Prediction..." : "🚀 Predict Final Grade (G3)";
            }
        }
        if (btnSpinner) {
            btnSpinner.style.display = isLoading ? "inline-block" : "none";
        }
    }

    // Form submission handler
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        hideMessages();

        // Collect all form data into structured object with proper types
        const formData = new FormData(form);
        const payload = {};

        for (const [key, value] of formData.entries()) {
            if (numericalFields.has(key)) {
                const parsed = Number(value);
                if (isNaN(parsed)) {
                    showError(`Field '${key}' must be a valid number.`);
                    return;
                }
                payload[key] = parsed;
            } else {
                payload[key] = value.trim();
            }
        }

        setLoading(true);

        try {
            const response = await fetch("/predict", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (!response.ok || data.status !== "success") {
                const msg = data.message || `Server returned status ${response.status}`;
                showError(msg);
                return;
            }

            renderPrediction(data);
        } catch (err) {
            console.error("Prediction request error:", err);
            showError("Unable to connect to the prediction server. Please verify the application is running.");
        } finally {
            setLoading(false);
        }
    });

    function renderPrediction(data) {
        const grade = Number(data.predicted_g3);
        const raw = Number(data.raw_prediction);

        predictedGrade.textContent = grade.toFixed(2);
        rawGrade.textContent = raw.toFixed(2);
        modelUsed.textContent = data.model_used || "Random Forest Regressor";

        // Progress bar calculation: (grade / 20) * 100%
        const percentage = Math.max(0, Math.min(100, (grade / 20) * 100));
        gradeBarFill.style.width = `${percentage}%`;

        // Update standing & category
        standingTitle.textContent = data.academic_category || "Academic Performance Standing";
        standingDescription.textContent = data.standing_description || "";

        // Badge styling
        resultBadge.className = `badge ${data.badge_class || "badge-good"}`;
        resultBadge.textContent = data.academic_category || "Standard";

        // Reveal card and scroll
        resultCard.style.display = "block";
        resultCard.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    function showError(msg) {
        if (errorMessage) errorMessage.textContent = msg;
        if (errorCard) {
            errorCard.style.display = "block";
            errorCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
        }
    }
});
