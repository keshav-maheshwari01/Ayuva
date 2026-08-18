# Model Results — Cardiovascular Risk (AYUVA)

## Final Model
- Algorithm: XGBoost (XGBClassifier)
- Hyperparameters: learning_rate=0.3, max_depth=3, n_estimators=100, subsample=0.8
- Selected via GridSearchCV (3-fold CV, scoring='recall')

## Final Feature Set
age_years, ap_hi, ap_lo, cholesterol, gluc, smoke, alco, active, bmi, pulse_pressure, map
(height and weight dropped in favor of derived bmi; pulse_pressure and map derived from ap_hi/ap_lo)

Target: cardio (binary: 0 = no disease, 1 = disease)

## Final Test Set Performance
| Metric    | Score  |
|-----------|--------|
| Accuracy  | 73.36% |
| Precision | 75.12% |
| Recall    | 69.83% |
| F1        | 72.38% |

## Model Development Journey
1. Baseline: Logistic Regression — 73.00% accuracy, 67.73% recall
2. XGBoost, default params, original features — 73.60% accuracy, 68.32% recall
3. XGBoost, tuned (GridSearchCV), original features — 73.85% accuracy, 69.09% recall
4. Feature engineering added (bmi, pulse_pressure, map; height/weight dropped)
5. XGBoost, re-tuned on engineered features — 73.36% accuracy, 69.83% recall (FINAL)

## Interpretation
Performance plateaued around 69-70% recall across multiple hyperparameter 
configurations and feature sets, indicating the dataset's predictive ceiling 
given available features. Further gains would likely require richer clinical 
data (family history, lab values) rather than further tuning.

## Decision Rationale
Recall was prioritized as the primary metric (over raw accuracy) because 
false negatives — missing a real at-risk patient — are the most dangerous 
failure mode for a health-screening tool, per AYUVA's core safety principles.



## Known Limitation: Sparse Coverage for Atypical Age/Feature Combinations

Testing revealed the model has zero training examples for patients under 25 
with cholesterol level 3 (well above normal). Predictions for such 
underrepresented combinations should be treated as low-confidence 
extrapolation, not reliable risk assessment. This reflects a broader dataset 
characteristic — checkup-based data likely skews toward middle-aged and older 
patients, since routine cardiovascular screening is less common in younger 
populations.

Mitigation for future iterations: (1) source a more age-diverse dataset, 
(2) implement an out-of-distribution detection flag at prediction time to 
warn when input falls outside well-represented training regions.