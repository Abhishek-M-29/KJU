4. Component Details
4.1 The Orchestrator & Separator
Role: The entry point (API Gateway). It validates input data and sanitizes PII (Personally Identifiable Information).
Logic:
Text Path: Identifies free-text fields (Doctor notes, Radiology summaries, Discharge summaries).
Numeric Path: Extracts structured data (Blood pressure, Lipid profiles, Glucose levels, O2 Saturation) into tensors/vectors.
4.2 Branch A: The ML Swarm (Numeric Analysis)
Instead of one massive model, we deploy a "Swarm" of lightweight, task-specific models.
Architecture: Ensemble Learning (Gradient Boosting / Random Forests).
Why Swarm?
Modularity: We can update the Diabetes Model without retraining the Cardiac Model.
Speed: Inference on tabular data takes milliseconds.
Output: Raw probability scores (e.g., "78% risk of Type 2 Diabetes within 3 years").
4.3 The Explainability Layer (SHAP)
This is the critical trust layer. We apply SHAP (SHapley Additive exPlanations) to the output of the ML Swarm.
Global Interpretability: Which features matter most across the whole population? (e.g., "Age" and "BMI").
Local Interpretability: Why is this specific patient at risk?
Output Example: "Risk Score is elevated (+15%) primarily because Fasting Glucose is 140 mg/dL, despite HDL being normal."
Visuals: Generates Feature Heatmaps (Red = Increases Risk, Blue = Decreases Risk).
4.4 Branch B: MedGamma (Text Analysis)
Model: MedGamma (A specialized Small Language Model, fine-tuned on medical literature).
Task:
NER (Named Entity Recognition): Extract symptoms mentioned in text that are missing in the charts.
Sentiment/History Analysis: Detect family history or lifestyle risks (e.g., "Patient mentions smoking 1 pack/day" buried in notes).
Output: A structured JSON summary of qualitative risk factors.
4.5 The Synthesis Agent (The Narrator)
Role: This is the only General Purpose LLM in the stack, acting as a technical writer, not a diagnostician.
Input:
ML Risk Scores (from Swarm).
SHAP Explanations (Feature contributions).
MedGamma insights (Text summaries).
the output must be in json format of 
{
  "jobId": "diag-job-001",
  "patientId": "3",
  "generatedAt": "2026-02-10T10:06:42Z",
  "status": "draft",
  "executiveSummary": "Based on comprehensive analysis of clinical data, laboratory results, and historical trends, the patient presents with elevated cardiovascular risk requiring immediate clinical attention. The integrated ML swarm analysis identified persistent atrial fibrillation with suboptimal rate control as the primary driver, compounded by progressive heart failure symptoms evidenced by reduced ejection fraction (35%) and new-onset dyspnea. Anticoagulation therapy appears adequate with therapeutic INR levels. However, the confluence of uncontrolled hypertension, elevated fasting glucose, and declining renal function creates a synergistic risk profile warranting aggressive intervention and close monitoring.",
  "riskScore": 85,
  "shapFeatures": [
    {
      "name": "Ejection Fraction (35%)",
      "impact": -22,
      "direction": "negative"
    },
    {
      "name": "Atrial Fibrillation",
      "impact": -18,
      "direction": "negative"
    },
    {
      "name": "Blood Pressure (165/105)",
      "impact": -15,
      "direction": "negative"
    },
    {
      "name": "Fasting Glucose (142)",
      "impact": -8,
      "direction": "negative"
    },
    {
      "name": "Age (71)",
      "impact": -6,
      "direction": "negative"
    },
    {
      "name": "Therapeutic INR",
      "impact": 5,
      "direction": "positive"
    },
    {
      "name": "No Prior MI",
      "impact": 4,
      "direction": "positive"
    }
  ],
  "featureHeatmap": [
    {
      "name": "Cardiac Function",
      "value": 0.92
    },
    {
      "name": "Blood Pressure",
      "value": 0.78
    },
    {
      "name": "Metabolic",
      "value": 0.65
    },
    {
      "name": "Renal Function",
      "value": 0.58
    },
    {
      "name": "Coagulation",
      "value": 0.25
    },
    {
      "name": "Lifestyle",
      "value": 0.45
    }
  ],
  "qualitativeFactors": {
    "riskFactors": [
      "Persistent AF",
      "Heart Failure",
      "Hypertension Stage 2",
      "Pre-diabetic"
    ],
    "protectiveFactors": [
      "Anticoagulated",
      "No smoking history",
      "Compliant with medications"
    ],
    "recommendations": [
      "Urgent cardiology referral",
      "Consider cardioversion",
      "Optimize rate control"
    ]
  }
}

the quantity of shapFeatures , featureHeatmap name and quantity are variable , according to the data recieved from previous models.