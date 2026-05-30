#!/usr/bin/env python3
"""
Synthea Healthcare Data Pipeline
================================
Complete pipeline to generate synthetic patient data, load into MariaDB,
and translate to Neo4j knowledge graph.

This script orchestrates:
1. Generate synthetic patients using Synthea
2. Load Synthea CSV data into MariaDB
3. Translate MariaDB data to Neo4j Knowledge Graph

Usage:
    python synthea_pipeline.py --patients 50 --state Massachusetts
    python synthea_pipeline.py --skip-generate  # Use existing Synthea data
    python synthea_pipeline.py --clear-all      # Clear all data first
"""

import os
import sys
import subprocess
import argparse
from datetime import datetime

# Script directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SYNTHEA_JAR = os.path.join(SCRIPT_DIR, 'synthea-with-dependencies.jar')
DEFAULT_OUTPUT_DIR = os.path.join(SCRIPT_DIR, 'synthea_output')


def run_synthea(num_patients=50, state='Massachusetts', city=None, output_dir=None):
    """Run Synthea to generate synthetic patient data"""
    
    output_dir = output_dir or DEFAULT_OUTPUT_DIR
    
    print("\n" + "=" * 70)
    print("🏥 Step 1: Generating Synthetic Patient Data with Synthea")
    print("=" * 70)
    print(f"\n   Patients: {num_patients}")
    print(f"   Location: {state}" + (f", {city}" if city else ""))
    print(f"   Output: {output_dir}")
    
    # Build Synthea command
    cmd = [
        'java', '-jar', SYNTHEA_JAR,
        '-p', str(num_patients),
        '--exporter.csv.export=true',
        f'--exporter.baseDirectory={output_dir}',
        state
    ]
    
    if city:
        cmd.append(city)
    
    print(f"\n   Running: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, cwd=SCRIPT_DIR, capture_output=False, text=True)
        
        if result.returncode == 0:
            print("\n✅ Synthea completed successfully!")
            return True
        else:
            print(f"\n⚠️  Synthea completed with warnings (exit code: {result.returncode})")
            # Synthea often returns non-zero even on success
            # Check if CSV files were created
            csv_dir = os.path.join(output_dir, 'csv')
            if os.path.exists(csv_dir) and os.listdir(csv_dir):
                print("   CSV files were generated, continuing...")
                return True
            return False
            
    except FileNotFoundError:
        print("❌ Error: Java not found. Please install Java to run Synthea.")
        return False
    except Exception as e:
        print(f"❌ Error running Synthea: {e}")
        return False


def run_mariadb_loader(synthea_dir=None, clear=False):
    """Run the MariaDB loader script"""
    
    print("\n" + "=" * 70)
    print("🗄️  Step 2: Loading Synthea Data into MariaDB")
    print("=" * 70)
    
    synthea_dir = synthea_dir or os.path.join(DEFAULT_OUTPUT_DIR, 'csv')
    
    # Build command
    cmd = [sys.executable, os.path.join(SCRIPT_DIR, 'synthea_to_mariadb.py'),
           '--synthea-dir', synthea_dir]
    
    if clear:
        cmd.append('--clear')
    
    print(f"\n   Running: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, cwd=SCRIPT_DIR)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error loading data into MariaDB: {e}")
        return False


def run_neo4j_translator(clear=False, skip_observations=False):
    """Run the Neo4j translator script"""
    
    print("\n" + "=" * 70)
    print("🔗 Step 3: Translating to Neo4j Knowledge Graph")
    print("=" * 70)
    
    # Build command
    cmd = [sys.executable, os.path.join(SCRIPT_DIR, 'synthea_to_neo4j.py')]
    
    if clear:
        cmd.append('--clear')
    
    if skip_observations:
        cmd.append('--skip-observations')
    
    print(f"\n   Running: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, cwd=SCRIPT_DIR)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error translating to Neo4j: {e}")
        return False


def check_prerequisites():
    """Check if all prerequisites are met"""
    issues = []
    
    # Check for Java
    try:
        result = subprocess.run(['java', '-version'], capture_output=True, text=True)
        if result.returncode != 0:
            issues.append("Java is not working properly")
    except FileNotFoundError:
        issues.append("Java is not installed (required for Synthea)")
    
    # Check for Synthea JAR
    if not os.path.exists(SYNTHEA_JAR):
        issues.append(f"Synthea JAR not found: {SYNTHEA_JAR}")
    
    # Check for .env file
    env_file = os.path.join(SCRIPT_DIR, '.env')
    if not os.path.exists(env_file):
        issues.append(".env file not found (required for database connections)")
    
    # Check for required Python packages
    required_packages = ['mariadb', 'neo4j', 'python-dotenv']
    for pkg in required_packages:
        try:
            __import__(pkg.replace('-', '_'))
        except ImportError:
            issues.append(f"Python package '{pkg}' not installed")
    
    return issues


def main():
    parser = argparse.ArgumentParser(
        description='Synthea Healthcare Data Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python synthea_pipeline.py --patients 50
  python synthea_pipeline.py --patients 100 --state California --city "Los Angeles"
  python synthea_pipeline.py --skip-generate --clear-all
  python synthea_pipeline.py --skip-observations
        """
    )
    
    # Synthea options
    parser.add_argument('-p', '--patients', type=int, default=50,
                        help='Number of patients to generate (default: 50)')
    parser.add_argument('-s', '--state', default='Massachusetts',
                        help='US state for patient generation (default: Massachusetts)')
    parser.add_argument('-c', '--city', default=None,
                        help='City for patient generation (optional)')
    parser.add_argument('--output-dir', default=None,
                        help='Synthea output directory')
    
    # Pipeline options
    parser.add_argument('--skip-generate', action='store_true',
                        help='Skip Synthea generation (use existing data)')
    parser.add_argument('--skip-mariadb', action='store_true',
                        help='Skip MariaDB loading')
    parser.add_argument('--skip-neo4j', action='store_true',
                        help='Skip Neo4j translation')
    parser.add_argument('--skip-observations', action='store_true',
                        help='Skip syncing observations to Neo4j (faster)')
    
    # Data management
    parser.add_argument('--clear-all', action='store_true',
                        help='Clear all existing data before loading')
    parser.add_argument('--clear-mariadb', action='store_true',
                        help='Clear MariaDB data before loading')
    parser.add_argument('--clear-neo4j', action='store_true',
                        help='Clear Neo4j data before loading')
    
    args = parser.parse_args()
    
    # Header
    print("\n" + "=" * 70)
    print("       🏥 SYNTHEA HEALTHCARE DATA PIPELINE 🏥")
    print("=" * 70)
    print(f"\n   Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check prerequisites
    print("\n📋 Checking prerequisites...")
    issues = check_prerequisites()
    
    if issues:
        print("\n⚠️  Prerequisites issues found:")
        for issue in issues:
            print(f"   - {issue}")
        
        if 'Java' in str(issues) and not args.skip_generate:
            print("\n💡 Tip: Use --skip-generate to skip Synthea if you have existing data")
            return 1
    else:
        print("   ✓ All prerequisites met")
    
    # Track success
    success = True
    
    # Step 1: Generate Synthea data
    if not args.skip_generate:
        if not run_synthea(
            num_patients=args.patients,
            state=args.state,
            city=args.city,
            output_dir=args.output_dir
        ):
            print("\n❌ Synthea generation failed")
            success = False
    else:
        print("\n⏭️  Skipping Synthea generation (--skip-generate)")
    
    # Step 2: Load into MariaDB
    if success and not args.skip_mariadb:
        synthea_csv_dir = os.path.join(args.output_dir or DEFAULT_OUTPUT_DIR, 'csv')
        
        if not run_mariadb_loader(
            synthea_dir=synthea_csv_dir,
            clear=args.clear_all or args.clear_mariadb
        ):
            print("\n❌ MariaDB loading failed")
            success = False
    else:
        if args.skip_mariadb:
            print("\n⏭️  Skipping MariaDB loading (--skip-mariadb)")
    
    # Step 3: Translate to Neo4j
    if success and not args.skip_neo4j:
        if not run_neo4j_translator(
            clear=args.clear_all or args.clear_neo4j,
            skip_observations=args.skip_observations
        ):
            print("\n❌ Neo4j translation failed")
            success = False
    else:
        if args.skip_neo4j:
            print("\n⏭️  Skipping Neo4j translation (--skip-neo4j)")
    
    # Summary
    print("\n" + "=" * 70)
    if success:
        print("✅ PIPELINE COMPLETED SUCCESSFULLY!")
    else:
        print("⚠️  PIPELINE COMPLETED WITH ERRORS")
    print("=" * 70)
    print(f"\n   Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if success:
        print("\n📊 Your healthcare knowledge graph is ready!")
        print("\n   MariaDB Tables:")
        print("   - Synthea_Patient, Synthea_Condition, Synthea_Medication, etc.")
        print("   - Patient_AI_Features (for ML models)")
        print("   - Patient_Vitals_Summary (aggregated vitals)")
        print("\n   Neo4j Node Types:")
        print("   - Patient, Condition, Medication, Encounter, Observation, etc.")
        print("   - AIFeatureSet (ML model inputs)")
        print("   - RiskFactor (health risk indicators)")
        print("\n   AI Model Integration:")
        print("   - Cardiovascular risk features: age, gender, height, weight, bp, cholesterol, glucose, lifestyle")
        print("   - Diabetes risk features: age, gender, bmi, hba1c, glucose, hypertension, heart_disease")
        print("\n   Sample Cypher Queries:")
        print("   - MATCH (p:Patient) RETURN p.name, p.age LIMIT 10")
        print("   - MATCH (p:Patient)-[:HAS_CONDITION]->(c) RETURN p.name, c.description")
        print("   - MATCH (p:Patient)-[:HAS_AI_FEATURES]->(ai) RETURN p.name, ai.bmi, ai.bp_systolic")
        print("   - MATCH (p:Patient)-[:HAS_RISK_FACTOR]->(rf) RETURN p.name, rf.name")
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
