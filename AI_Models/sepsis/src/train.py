"""
Training script for sepsis prediction models.

Usage:
    python train.py --data ../data/sepsis_data.pkl
    python train.py --data-dir ../data/processed/
"""

import argparse
import pickle
import sys
from pathlib import Path

from features import construct_features_simple, construct_features_enhanced
from models import train_all_models, evaluate_models


def load_pickle_data(data_dir: Path):
    """Load data from pickle files (original format)."""
    train_seqs = pickle.load(open(data_dir / "sepsis.seqs.train", 'rb'))
    y_train = pickle.load(open(data_dir / "sepsis.labels.train", 'rb'))
    valid_seqs = pickle.load(open(data_dir / "sepsis.seqs.validation", 'rb'))
    y_valid = pickle.load(open(data_dir / "sepsis.labels.validation", 'rb'))
    test_seqs = pickle.load(open(data_dir / "sepsis.seqs.test", 'rb'))
    y_test = pickle.load(open(data_dir / "sepsis.labels.test", 'rb'))
    
    return (train_seqs, y_train), (valid_seqs, y_valid), (test_seqs, y_test)


def main():
    parser = argparse.ArgumentParser(description='Train sepsis prediction models')
    parser.add_argument('--data-dir', type=str, help='Directory with pickle data files')
    parser.add_argument('--enhanced', action='store_true', help='Use enhanced features (110 instead of 10)')
    parser.add_argument('--output', type=str, default='../models', help='Output directory for models')
    args = parser.parse_args()
    
    if not args.data_dir:
        print("❌ Please provide --data-dir with path to data files")
        print("   Expected files: sepsis.seqs.train, sepsis.labels.train, etc.")
        sys.exit(1)
    
    data_dir = Path(args.data_dir)
    output_dir = Path(args.output)
    
    # Load data
    print("===> Loading data...")
    (train_seqs, y_train), (valid_seqs, y_valid), (test_seqs, y_test) = load_pickle_data(data_dir)
    
    print(f"\n📊 Dataset sizes:")
    print(f"   Train: {len(train_seqs)}")
    print(f"   Valid: {len(valid_seqs)}")
    print(f"   Test:  {len(test_seqs)}")
    
    # Feature engineering
    construct_fn = construct_features_enhanced if args.enhanced else construct_features_simple
    feature_type = "enhanced (110)" if args.enhanced else "simple (10)"
    print(f"\n🔧 Using {feature_type} features")
    
    X_train = construct_fn(train_seqs)
    X_valid = construct_fn(valid_seqs)
    X_test = construct_fn(test_seqs)
    
    # Combine train + valid for final training
    X_train_valid = X_train + X_valid
    y_train_valid = y_train + y_valid
    
    n_features = len(X_train_valid[0])
    n_samples = len(X_train_valid)
    ratio = n_samples / n_features
    
    print(f"\n📐 Samples per feature: {ratio:.1f}")
    if ratio < 10:
        print("   ⚠️ WARNING: High overfitting risk!")
    
    # Train models
    print("\n" + "="*60)
    print("🚀 TRAINING MODELS")
    print("="*60)
    
    results = train_all_models(X_train_valid, y_train_valid, output_dir)
    
    # Evaluate
    print("\n" + "="*60)
    print("📊 EVALUATION ON TEST SET")
    print("="*60)
    
    eval_results = evaluate_models(X_train_valid, X_test, y_train_valid, y_test, output_dir)
    
    # Final ranking
    print("\n" + "="*60)
    print("🏆 FINAL RANKING (by ROC-AUC)")
    print("="*60)
    for r in sorted(eval_results, key=lambda x: -x['roc_auc']):
        print(f"{r['name']:12} AUC={r['roc_auc']:.4f} Recall={r['recall']:.4f}")
    
    print(f"\n✅ Models saved to: {output_dir.absolute()}")


if __name__ == "__main__":
    main()
