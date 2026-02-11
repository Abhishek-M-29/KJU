"""
Feature engineering for sepsis prediction.
Converts time-series clinical data to statistical features.
"""

import numpy as np
from scipy import stats

# Base clinical variables
FEATURE_NAMES = [
    "heartrate", "sysbp", "diasbp", "meanbp", "resprate",
    "tempc", "spo2", "glucose", "age", "gender"
]


def construct_features_simple(seqs):
    """
    Simple feature engineering - mean only (10 features).
    Recommended for small datasets to avoid overfitting.
    
    Args:
        seqs: List of observation sequences. Each sequence is a 2D array
              where rows are time steps and columns are features.
    
    Returns:
        List of feature vectors (one per patient)
    """
    X = []
    for i in range(len(seqs)):
        arr = np.array(seqs[i], dtype=np.float64)
        data_mean = np.nanmean(arr, axis=0)
        data_mean = np.nan_to_num(data_mean, nan=0.0)
        X.append(data_mean.tolist())
    return X


def construct_features_enhanced(seqs):
    """
    Enhanced feature engineering (110 features).
    Use only with large datasets (>1000 samples).
    
    Features per variable:
    - mean, std, min, max, median
    - range, IQR
    - trend (last - first)
    - rate of change (mean of differences)
    - last value
    - skewness
    
    Args:
        seqs: List of observation sequences
    
    Returns:
        List of feature vectors (one per patient)
    """
    X = []
    for i in range(len(seqs)):
        arr = np.array(seqs[i], dtype=np.float64)
        features = []
        
        # Basic statistics
        features.extend(np.nanmean(arr, axis=0))
        features.extend(np.nanstd(arr, axis=0))
        features.extend(np.nanmin(arr, axis=0))
        features.extend(np.nanmax(arr, axis=0))
        features.extend(np.nanmedian(arr, axis=0))
        
        # Range and IQR
        features.extend(np.nanmax(arr, axis=0) - np.nanmin(arr, axis=0))
        q75 = np.nanpercentile(arr, 75, axis=0)
        q25 = np.nanpercentile(arr, 25, axis=0)
        features.extend(q75 - q25)
        
        # Trend features
        if len(arr) > 1:
            features.extend(arr[-1] - arr[0])
            features.extend(np.nanmean(np.diff(arr, axis=0), axis=0))
        else:
            features.extend(np.zeros(arr.shape[1]))
            features.extend(np.zeros(arr.shape[1]))
        
        # Last value
        features.extend(arr[-1])
        
        # Skewness
        if len(arr) > 2:
            for j in range(arr.shape[1]):
                try:
                    sk = stats.skew(arr[:, j], nan_policy='omit')
                    features.append(sk if np.isfinite(sk) else 0.0)
                except:
                    features.append(0.0)
        else:
            features.extend(np.zeros(arr.shape[1]))
        
        # Clean up NaN/Inf
        features = [0.0 if not np.isfinite(f) else f for f in features]
        X.append(features)
    
    return X


def observation_to_features(observations: list) -> np.ndarray:
    """
    Convert API observations to feature vector.
    
    Args:
        observations: List of dicts with clinical variables
    
    Returns:
        Feature array of shape (1, n_features)
    """
    arr = np.array([
        [obs["heartrate"], obs["sysbp"], obs["diasbp"], obs["meanbp"], 
         obs["resprate"], obs["tempc"], obs["spo2"], obs["glucose"], 
         obs["age"], obs["gender"]]
        for obs in observations
    ], dtype=np.float64)
    
    return np.nanmean(arr, axis=0).reshape(1, -1)
