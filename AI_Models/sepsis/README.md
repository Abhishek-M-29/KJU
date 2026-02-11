# 🩺 Sepsis Prediction Model

A machine learning-based sepsis risk prediction system using Random Forest classifier.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the API
```bash
cd src
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Access the API
- **Swagger UI**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/
- **Model Info**: http://localhost:8000/model/info

---

## 📁 Project Structure

```
sepsis/
├── README.md              # This file
├── requirements.txt       # Python dependencies
├── models/               # Pre-trained models
│   ├── MyRF.pkl          # Random Forest (recommended)
│   ├── MyMLP.pkl         # Neural Network
│   ├── MyXGB.pkl         # XGBoost
│   └── scaler.pkl        # Feature scaler for MLP
├── src/                  # Source code
│   ├── api.py            # FastAPI server
│   ├── train.py          # Training script
│   ├── models.py         # Model definitions
│   └── features.py       # Feature engineering
├── data/                 # Data directory (add your data here)
└── docs/                 # Documentation
    └── MODEL_SPEC.md     # Model specification
```

---

## 📊 Model Performance

| Model | ROC-AUC | Recall | Precision | F1 |
|-------|---------|--------|-----------|-----|
| **MyRF** | **0.7518** | **0.7182** | 0.6870 | 0.7022 |
| MyMLP | 0.7558 | 0.6364 | 0.6931 | 0.6635 |
| MyXGB | 0.7449 | 0.6455 | 0.6574 | 0.6514 |

**Note**: MyRF is recommended due to highest recall - critical for clinical sepsis screening.

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/model/info` | Model metadata |
| POST | `/predict` | Single prediction |
| POST | `/predict/batch` | Batch predictions |

### Example Request
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "P001",
    "observations": [
      {
        "heartrate": 95,
        "sysbp": 110,
        "diasbp": 70,
        "meanbp": 83,
        "resprate": 24,
        "tempc": 38.5,
        "spo2": 94,
        "glucose": 140,
        "age": 72,
        "gender": 1
      }
    ]
  }'
```

### Example Response
```json
{
  "patient_id": "P001",
  "prediction": 1,
  "probability": 0.73,
  "risk_level": "HIGH",
  "interpretation": "High risk of sepsis. Immediate clinical evaluation recommended."
}
```

---

## 🏋️ Training

To retrain the model with your own data:

```bash
cd src
python train.py --data ../data/your_data.pkl
```

See [docs/MODEL_SPEC.md](docs/MODEL_SPEC.md) for data format requirements.

---

## ⚠️ Disclaimer

This model is a **screening aid only**, not a diagnostic tool. Always use clinical judgment. The model has known overfitting (train-CV gap: 0.26) - use with caution on new populations.

---

## 📄 License

For research and educational purposes only.
