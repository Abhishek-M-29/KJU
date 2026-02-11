# Sepsis Prediction Model Specification

## 🏆 Model Selection

**Selected Model: MyRF (Random Forest)**

For sepsis prediction, **recall is the most critical metric** - missing sepsis cases can be fatal. MyRF achieved the **highest recall (71.82%)**.

---

## 📊 Performance Metrics

| Metric | Value |
|--------|-------|
| ROC-AUC | 0.7518 |
| Recall | 0.7182 |
| Precision | 0.6870 |
| F1 Score | 0.7022 |
| Accuracy | 0.7009 |
| MCC | 0.4025 |

### All Models Comparison

| Model | ROC-AUC | Recall | F1 | Train-CV Gap |
|-------|---------|--------|-----|--------------|
| **MyRF** | 0.7518 | 0.7182 | 0.7022 | 0.2636 ⚠️ |
| MyMLP | 0.7558 | 0.6364 | 0.6635 | 0.1081 |
| MyXGB | 0.7449 | 0.6455 | 0.6514 | 0.2530 ⚠️ |
| MyLGBM | 0.7444 | 0.6182 | 0.6296 | 0.2215 ⚠️ |
| MyGBM | 0.7415 | 0.6364 | 0.6481 | 0.2418 ⚠️ |
| MyDT | 0.6925 | 0.5091 | 0.5895 | 0.1135 |

---

## 📋 Input Specification

### Clinical Variables (10 features)

| Variable | Description | Unit | Valid Range |
|----------|-------------|------|-------------|
| `heartrate` | Heart rate | bpm | 0-300 |
| `sysbp` | Systolic blood pressure | mmHg | 0-300 |
| `diasbp` | Diastolic blood pressure | mmHg | 0-200 |
| `meanbp` | Mean arterial pressure | mmHg | 0-250 |
| `resprate` | Respiratory rate | breaths/min | 0-100 |
| `tempc` | Body temperature | °C | 30-45 |
| `spo2` | Oxygen saturation | % | 0-100 |
| `glucose` | Blood glucose | mg/dL | 0-1000 |
| `age` | Patient age | years | 0-150 |
| `gender` | Gender | binary | 0=F, 1=M |

### Data Format

**Training data** (pickle format):
```
sepsis.seqs.train       # List of sequences (N x T x 10)
sepsis.labels.train     # List of labels (0 or 1)
sepsis.seqs.validation  
sepsis.labels.validation
sepsis.seqs.test
sepsis.labels.test
```

**API input** (JSON):
```json
{
  "patient_id": "P001",
  "observations": [
    {
      "heartrate": 95.0,
      "sysbp": 110.0,
      "diasbp": 70.0,
      "meanbp": 83.3,
      "resprate": 24.0,
      "tempc": 38.5,
      "spo2": 94.0,
      "glucose": 140.0,
      "age": 72.0,
      "gender": 1
    }
  ]
}
```

---

## 📤 Output Specification

```json
{
  "patient_id": "P001",
  "prediction": 1,
  "probability": 0.73,
  "risk_level": "HIGH",
  "interpretation": "High risk of sepsis. Immediate clinical evaluation recommended.",
  "timestamp": "2026-02-11T12:00:00",
  "model_used": "MyRF"
}
```

### Risk Levels

| Probability | Level | Action |
|-------------|-------|--------|
| < 0.3 | LOW | Routine monitoring |
| 0.3 - 0.6 | MODERATE | Increased monitoring, consider labs |
| > 0.6 | HIGH | Immediate evaluation |

---

## 🔧 Feature Engineering

### Simple Mode (10 features) - Recommended
- Takes mean of each variable across all observations
- More robust on small datasets
- Lower overfitting risk

### Enhanced Mode (110 features)
- 11 statistics per variable: mean, std, min, max, median, range, IQR, trend, rate of change, last value, skewness
- Only use with >1000 samples
- Higher overfitting risk

---

## ⚠️ Known Limitations

1. **Overfitting**: Train-CV gap of 0.26 indicates overfitting. Model may not generalize well to new populations.

2. **Class Imbalance**: Original data has class imbalance. Model uses `class_weight='balanced'` to compensate.

3. **Missing Data**: Model expects complete data. Missing values should be imputed before prediction.

4. **Population**: Trained on specific ICU population. May not generalize to:
   - Pediatric patients
   - Non-ICU settings
   - Different geographic regions

5. **Not Diagnostic**: This is a **screening tool**, not a diagnostic test. Always use clinical judgment.

---

## 🏗️ Model Architecture

### Random Forest (MyRF)
- **Type**: Ensemble of decision trees
- **n_estimators**: Optimized via GridSearchCV
- **max_depth**: Optimized via GridSearchCV
- **class_weight**: 'balanced'
- **Hyperparameter Tuning**: 5-fold Stratified CV
- **Scoring**: ROC-AUC

---

## 📚 References

- Scikit-learn Random Forest: https://scikit-learn.org/stable/modules/ensemble.html
- Sepsis-3 Definition: Singer et al., JAMA 2016
- MIMIC-III Database: Johnson et al., Scientific Data 2016
