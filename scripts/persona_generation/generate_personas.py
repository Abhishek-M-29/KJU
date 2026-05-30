#!/usr/bin/env python
"""
Generate Synthea-Level Patient Personas

Main script for generating randomized patient personas using the persona_generator package.
Uses a base class system with condition/medication templates and random selection
to create realistic, varied patient data.

Usage:
    python generate_personas.py --count 10 --profile random
    python generate_personas.py --count 5 --profile diabetic_controlled
    python generate_personas.py --diverse 20
    python generate_personas.py --list-profiles

Examples:
    # Generate 10 random personas from random profiles
    python generate_personas.py --count 10
    
    # Generate 5 heart failure patients
    python generate_personas.py --count 5 --profile heart_failure
    
    # Generate diverse set (cycles through all profiles)
    python generate_personas.py --diverse 30
    
    # Preview only (no database insertion)
    python generate_personas.py --count 5 --preview
"""

import argparse
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from persona_generator import PersonaGenerator, DatabaseManager


def list_profiles():
    """List all available persona profiles"""
    generator = PersonaGenerator()
    profiles = generator.get_available_profiles()
    
    print("\n" + "=" * 60)
    print("📋 AVAILABLE PERSONA PROFILES")
    print("=" * 60)
    
    for profile in sorted(profiles):
        desc = generator.get_profile_description(profile)
        print(f"\n  • {profile}")
        print(f"    └─ {desc}")
    
    print("\n" + "=" * 60)
    print(f"Total: {len(profiles)} profiles available")
    print("=" * 60 + "\n")


def preview_personas(personas):
    """Preview generated personas without inserting"""
    print("\n" + "=" * 80)
    print("📋 PERSONA PREVIEW")
    print("=" * 80)
    
    for i, persona in enumerate(personas, 1):
        print(f"\n{'─' * 80}")
        print(f"PERSONA {i}: {persona.demographics.full_name}")
        print(f"{'─' * 80}")
        
        # Demographics
        d = persona.demographics
        print(f"  Age: {d.age} | Gender: {d.gender.value} | Race: {d.race.value}")
        print(f"  Location: {d.city}, {d.state}")
        print(f"  Marital: {d.marital_status.value} | Income: ${d.income:,}")
        
        # Conditions
        print(f"\n  Active Conditions ({len(persona.active_conditions)}):")
        for c in persona.active_conditions[:5]:
            print(f"    • [{c.code}] {c.description}")
        if len(persona.active_conditions) > 5:
            print(f"    ... and {len(persona.active_conditions) - 5} more")
        
        # Medications
        print(f"\n  Active Medications ({len(persona.active_medications)}):")
        for m in persona.active_medications[:5]:
            print(f"    • {m.description} ({m.frequency})")
        if len(persona.active_medications) > 5:
            print(f"    ... and {len(persona.active_medications) - 5} more")
        
        # Allergies
        if persona.allergies:
            print(f"\n  Allergies ({len(persona.allergies)}):")
            for a in persona.allergies:
                print(f"    • {a.description} ({a.severity})")
        
        # Latest Vitals
        if persona.latest_vitals:
            v = persona.latest_vitals
            print(f"\n  Latest Vitals:")
            print(f"    BP: {v.systolic_bp}/{v.diastolic_bp} mmHg | HR: {v.heart_rate} bpm")
            print(f"    BMI: {v.bmi} | SpO2: {v.oxygen_saturation}%")
        
        # AI Risk Scores
        if persona.ai_features:
            af = persona.ai_features
            print(f"\n  Risk Scores:")
            print(f"    Diabetes: {af.diabetes_risk_score}/10 | CVD: {af.cardiovascular_risk_score}/10")
            print(f"    Sepsis: {af.sepsis_risk_score}/10 | Readmission: {af.readmission_risk_score}/10")
        
        # Social History
        if persona.social_history:
            sh = persona.social_history
            print(f"\n  Social History:")
            print(f"    Smoking: {sh.smoking_status} | Alcohol: {sh.alcohol_use}")
            print(f"    Exercise: {sh.exercise_frequency} | Diet: {sh.diet_quality}")
            print(f"    Occupation: {sh.occupation}")
        
        # Family History
        if persona.family_history:
            print(f"\n  Family History:")
            for fh in persona.family_history[:3]:
                print(f"    • {fh.relation.title()}: {fh.condition}")
        
        # Narrative
        if persona.narrative:
            print(f"\n  Narrative:")
            # Word wrap the narrative
            words = persona.narrative.split()
            line = "    "
            for word in words:
                if len(line) + len(word) > 76:
                    print(line)
                    line = "    " + word
                else:
                    line += " " + word if line.strip() else word
            if line.strip():
                print(line)
    
    print("\n" + "=" * 80)
    print(f"Total: {len(personas)} personas generated")
    print("=" * 80 + "\n")


def generate_report(personas):
    """Generate a summary report of generated personas"""
    print("\n" + "=" * 60)
    print("📊 GENERATION SUMMARY REPORT")
    print("=" * 60)
    
    # Demographics summary
    ages = [p.demographics.age for p in personas]
    genders = {"M": 0, "F": 0}
    for p in personas:
        genders[p.demographics.gender.value] += 1
    
    print(f"\n  Total Personas: {len(personas)}")
    print(f"  Age Range: {min(ages)} - {max(ages)} (avg: {sum(ages)/len(ages):.1f})")
    print(f"  Gender: {genders['M']} male, {genders['F']} female")
    
    # Condition frequency
    condition_counts = {}
    for p in personas:
        for c in p.active_conditions:
            desc = c.description.split(",")[0]  # Shorten
            condition_counts[desc] = condition_counts.get(desc, 0) + 1
    
    print("\n  Top Conditions:")
    for cond, count in sorted(condition_counts.items(), key=lambda x: -x[1])[:10]:
        print(f"    • {cond}: {count} patients")
    
    # Risk score distribution
    risk_scores = {
        "diabetes": [p.ai_features.diabetes_risk_score for p in personas if p.ai_features],
        "cardiovascular": [p.ai_features.cardiovascular_risk_score for p in personas if p.ai_features],
        "sepsis": [p.ai_features.sepsis_risk_score for p in personas if p.ai_features],
    }
    
    print("\n  Risk Score Averages:")
    for risk_type, scores in risk_scores.items():
        if scores:
            avg = sum(scores) / len(scores)
            print(f"    • {risk_type.title()}: {avg:.1f}/10")
    
    # Lifestyle factors
    smokers = sum(1 for p in personas if p.social_history and p.social_history.smoking_status == "current")
    obese = sum(1 for p in personas if p.ai_features and p.ai_features.is_obese)
    
    print("\n  Lifestyle Factors:")
    print(f"    • Current Smokers: {smokers} ({100*smokers/len(personas):.1f}%)")
    print(f"    • Obese (BMI ≥ 30): {obese} ({100*obese/len(personas):.1f}%)")
    
    print("\n" + "=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Generate Synthea-level patient personas",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "--count", "-n",
        type=int,
        default=10,
        help="Number of personas to generate (default: 10)"
    )
    
    parser.add_argument(
        "--profile", "-p",
        type=str,
        default=None,
        help="Persona profile to use (use --list-profiles to see options)"
    )
    
    parser.add_argument(
        "--diverse", "-d",
        type=int,
        default=None,
        help="Generate a diverse set cycling through all profiles"
    )
    
    parser.add_argument(
        "--seed", "-s",
        type=int,
        default=None,
        help="Random seed for reproducibility"
    )
    
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Preview personas without inserting into database"
    )
    
    parser.add_argument(
        "--list-profiles",
        action="store_true",
        help="List all available persona profiles"
    )
    
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate summary report after creation"
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Minimal output"
    )
    
    args = parser.parse_args()
    
    # List profiles and exit
    if args.list_profiles:
        list_profiles()
        return 0
    
    # Create generator
    generator = PersonaGenerator(seed=args.seed)
    
    # Generate personas
    if not args.quiet:
        print("\n🏥 Synthea-Level Persona Generator")
        print("=" * 40)
    
    if args.diverse:
        if not args.quiet:
            print(f"📋 Generating {args.diverse} diverse personas...")
        personas = generator.generate_diverse_set(count=args.diverse)
    elif args.profile:
        if args.profile not in generator.get_available_profiles():
            print(f"❌ Unknown profile: {args.profile}")
            print("   Use --list-profiles to see available options")
            return 1
        if not args.quiet:
            print(f"📋 Generating {args.count} '{args.profile}' personas...")
        personas = generator.generate(profile=args.profile, count=args.count)
    else:
        if not args.quiet:
            print(f"📋 Generating {args.count} random personas...")
        personas = generator.generate_random(count=args.count)
    
    if not args.quiet:
        print(f"✅ Generated {len(personas)} personas")
    
    # Preview mode
    if args.preview:
        preview_personas(personas)
        return 0
    
    # Insert into databases
    if not args.quiet:
        print("\n📦 Inserting into databases...")
    
    db = DatabaseManager()
    try:
        success_count = db.insert_personas(personas, verbose=not args.quiet)
        
        if not args.quiet:
            counts = db.get_persona_count()
            print(f"\n📊 Database Totals:")
            print(f"   MariaDB: {counts['mariadb']} patients")
            print(f"   Neo4j: {counts['neo4j']} patients")
    finally:
        db.close()
    
    # Generate report
    if args.report:
        generate_report(personas)
    
    if not args.quiet:
        print("\n✅ Done!\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
