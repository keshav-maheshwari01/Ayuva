# EDA Notes — Cardiovascular Risk Dataset

## Dataset
- Source: [Kaggle link/citation you found earlier]
- Original size: 70,000 rows, 13 columns
- After cleaning: [your df_clean row count] rows

## Cleaning Decisions
### Blood Pressure (ap_hi, ap_lo)
- Issue found: [what you saw — negative values, values in thousands]
- Fix applied: [your valid_bp filter — what thresholds you used]
- Rows removed: [count/percentage]

### Weight / Height
- Checked for outliers (up to 200kg weight found)
- Decision: kept as-is, no capping/removal
- Reason: [your reasoning — physically plausible, no error pattern found, XGBoost robust to outliers]

## Feature Encoding
- Gender: 1=female, 2=male (confirmed via avg height comparison)
- Cholesterol/Glucose: 1=normal, 2=above normal, 3=well above normal (ordinal)

## Key EDA Findings
- Age, ap_hi, ap_lo: all higher in cardio=1 group — [your actual numbers]
- Cholesterol: strong signal, disease rate rises from 43.6% → 76.3% across levels 1→3
- Glucose: similar but weaker signal
- Gender: no meaningful direct effect on disease rate — dropped
- Smoke/Alcohol: showed a *misleading* result — lower disease rate in smokers/drinkers, 
  traced to a confound with gender (men smoke/drink far more, gender itself has near-zero
  effect on disease) — kept in feature set despite this, since the raw signal alone was misleading

## Final Feature Set
Features: age_years, height, weight, ap_hi, ap_lo, cholesterol, gluc, smoke, alco, active
Target: cardio
Dropped: id, gender, raw age (days)

## Train/Test Split
80/20 split, stratified on target, random_state=42
Train: [shape], Test: [shape]




## Phase 5 — Baseline Model: Logistic Regression

### Setup
- Model: scikit-learn LogisticRegression, default parameters
- Features scaled using StandardScaler (fit on train only, applied to test — avoids data leakage)
- Trained on x_train_scaled, y_train (54,993 rows)
- Evaluated on x_test_scaled (13,749 rows), never seen during training

### Results
| Metric     | Score  |
|------------|--------|
| Accuracy   | 0.7300 |
| Precision  | 0.7523 |
| Recall     | 0.6773 |
| F1 Score   | 0.7129 |

Confusion Matrix:
|                  | Predicted 0 | Predicted 1 |
|------------------|-------------|-------------|
| Actual 0 (no CVD)| 5429 (TN)   | 1517 (FP)   |
| Actual 1 (CVD)   | 2195 (FN)   | 4608 (TP)   |

### Interpretation (FACT)
- The model correctly classifies 73% of cases overall.
- Recall (sensitivity) is 67.7% — meaning the model misses roughly 1 in 3 
  actual disease cases (2195 false negatives out of 6803 real positive cases).

### Inference
- For a health-screening context, this recall level is not sufficient on its own.
  False negatives (missed real disease cases) are the most dangerous failure mode
  for AYUVA, per the project's own risk principles (section 8, section 17).

### Recommendation
- This model serves as the baseline for comparison. XGBoost (Phase 6) must be
  evaluated against this baseline, with particular attention to whether it
  improves recall — not just overall accuracy — to justify its added complexity
  over this simpler, more interpretable model.

### Limitation
- Default classification threshold (0.5) was used. Recall could likely be 
  improved by lowering this threshold (accepting more false positives to catch 
  more true positives) — worth exploring in later phases (Phase 7: ML evaluation) 
  once XGBoost is also built, so both models can be tuned and compared fairly.