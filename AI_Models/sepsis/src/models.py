"""
Model definitions and training utilities for sepsis prediction.
"""

import numpy as np
import joblib
import warnings
from pathlib import Path
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, 
    f1_score, roc_auc_score, matthews_corrcoef
)

warnings.filterwarnings('ignore')

# Optional GPU libraries
try:
    from xgboost import XGBClassifier
    HAS_XGB = True
except ImportError:
    HAS_XGB = False

try:
    from lightgbm import LGBMClassifier
    HAS_LGBM = True
except ImportError:
    HAS_LGBM = False

RANDOM_STATE = 41
N_JOBS = 14
MODEL_DIR = Path(__file__).parent.parent / "models"


def get_models_and_params(scale_pos_weight: float = 1.0):
    """Get model instances and their hyperparameter grids."""
    
    models = {
        "MyDT": (
            DecisionTreeClassifier(random_state=RANDOM_STATE, class_weight='balanced'),
            {
                'max_depth': [3, 5, 7, 10, 15],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4]
            }
        ),
        "MyRF": (
            RandomForestClassifier(random_state=RANDOM_STATE, n_jobs=N_JOBS, class_weight='balanced'),
            {
                'n_estimators': [100, 200, 300],
                'max_depth': [5, 10, 15, None],
                'min_samples_split': [2, 5],
                'max_features': ['sqrt', 'log2']
            }
        ),
        "MyGBM": (
            GradientBoostingClassifier(random_state=RANDOM_STATE),
            {
                'n_estimators': [100, 200, 300],
                'max_depth': [3, 5, 7],
                'learning_rate': [0.01, 0.05, 0.1],
                'subsample': [0.8, 1.0]
            }
        ),
        "MyMLP": (
            MLPClassifier(max_iter=2000, random_state=RANDOM_STATE, early_stopping=True),
            {
                'hidden_layer_sizes': [(100,), (200,), (100, 50), (100, 100)],
                'alpha': [0.0001, 0.001, 0.01],
                'learning_rate_init': [0.001, 0.01]
            }
        ),
    }
    
    if HAS_XGB:
        models["MyXGB"] = (
            XGBClassifier(
                random_state=RANDOM_STATE,
                tree_method='hist',
                device='cuda',
                n_jobs=N_JOBS,
                verbosity=0,
                scale_pos_weight=scale_pos_weight,
                eval_metric='auc'
            ),
            {
                'n_estimators': [100, 200, 300, 500],
                'max_depth': [3, 5, 7, 9],
                'learning_rate': [0.01, 0.05, 0.1],
                'subsample': [0.8, 1.0],
                'colsample_bytree': [0.8, 1.0]
            }
        )
    
    if HAS_LGBM:
        models["MyLGBM"] = (
            LGBMClassifier(
                random_state=RANDOM_STATE,
                device='gpu',
                n_jobs=N_JOBS,
                verbose=-1,
                is_unbalance=True,
                metric='auc'
            ),
            {
                'n_estimators': [100, 200, 300, 500],
                'max_depth': [3, 5, 7, -1],
                'learning_rate': [0.01, 0.05, 0.1],
                'num_leaves': [31, 50, 100],
                'subsample': [0.8, 1.0]
            }
        )
    
    return models


def train_all_models(X, y, output_dir=None):
    """
    Train all models with GridSearchCV.
    
    Args:
        X: Feature matrix
        y: Labels
        output_dir: Directory to save models (default: ../models)
    
    Returns:
        dict: Results for each model
    """
    output_dir = Path(output_dir) if output_dir else MODEL_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    
    X = np.array(X)
    y = np.array(y)
    
    # Normalize for MLP
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    joblib.dump(scaler, output_dir / "scaler.pkl")
    
    # Class balance
    n_pos = sum(y)
    n_neg = len(y) - n_pos
    scale_pos_weight = n_neg / n_pos if n_pos > 0 else 1
    print(f"📊 Class balance: {n_pos} positive / {n_neg} negative")
    
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    models = get_models_and_params(scale_pos_weight)
    
    results = {}
    
    for name, (estimator, params) in models.items():
        print(f"\n{'='*50}")
        print(f"Training {name}...")
        
        X_use = X_scaled if name == "MyMLP" else X
        cv_jobs = 2 if name in ["MyRF", "MyXGB", "MyLGBM"] else N_JOBS
        
        gsearch = GridSearchCV(
            estimator, param_grid=params, scoring='roc_auc',
            cv=cv, n_jobs=cv_jobs, verbose=1, return_train_score=True
        )
        gsearch.fit(X_use, y)
        
        # Save model
        joblib.dump(gsearch.best_estimator_, output_dir / f"{name}.pkl")
        
        # Overfitting detection
        best_idx = gsearch.best_index_
        train_score = gsearch.cv_results_['mean_train_score'][best_idx]
        cv_score = gsearch.best_score_
        gap = train_score - cv_score
        
        status = "⚠️ OVERFIT" if gap > 0.1 else ("⚡ Caution" if gap > 0.05 else "✅ Good")
        print(f"✅ {name}: Train={train_score:.4f}, CV={cv_score:.4f}, Gap={gap:.4f} {status}")
        
        results[name] = {
            'train_score': train_score,
            'cv_score': cv_score,
            'gap': gap,
            'best_params': gsearch.best_params_
        }
    
    return results


def evaluate_models(X_train, X_test, y_train, y_test, model_dir=None):
    """
    Evaluate all trained models on test set.
    
    Returns:
        list: Evaluation results for each model
    """
    model_dir = Path(model_dir) if model_dir else MODEL_DIR
    
    X_train = np.array(X_train)
    X_test = np.array(X_test)
    y_train = np.array(y_train)
    y_test = np.array(y_test)
    
    # Load scaler
    try:
        scaler = joblib.load(model_dir / "scaler.pkl")
        X_train_scaled = scaler.transform(X_train)
        X_test_scaled = scaler.transform(X_test)
    except:
        X_train_scaled = X_train
        X_test_scaled = X_test
    
    model_names = ["MyDT", "MyRF", "MyGBM", "MyMLP", "MyXGB", "MyLGBM"]
    results = []
    
    print(f"\n{'='*60}")
    print("📊 TEST SET EVALUATION")
    print('='*60)
    
    for name in model_names:
        try:
            clf = joblib.load(model_dir / f"{name}.pkl")
        except FileNotFoundError:
            continue
        
        X_tr = X_train_scaled if name == "MyMLP" else X_train
        X_te = X_test_scaled if name == "MyMLP" else X_test
        
        clf.fit(X_tr, y_train)
        y_pred = clf.predict(X_te)
        y_prob = clf.predict_proba(X_te)[:, 1] if hasattr(clf, 'predict_proba') else y_pred
        
        metrics = {
            'name': name,
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, zero_division=0),
            'recall': recall_score(y_test, y_pred, zero_division=0),
            'f1': f1_score(y_test, y_pred, zero_division=0),
            'roc_auc': roc_auc_score(y_test, y_prob),
            'mcc': matthews_corrcoef(y_test, y_pred)
        }
        results.append(metrics)
        
        print(f"\n🔍 {name}:")
        print(f"   ROC-AUC: {metrics['roc_auc']:.4f}")
        print(f"   Recall:  {metrics['recall']:.4f}")
        print(f"   F1:      {metrics['f1']:.4f}")
    
    return results
