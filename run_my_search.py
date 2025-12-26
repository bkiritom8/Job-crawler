#!/usr/bin/env python3
"""
Personalized job search for Bhargav Pamidighantam
Focuses on MLOps, DevOps, and Cloud Engineering roles
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.job_matching_agent import JobMatchingAgent


def main():
    """Run personalized job search"""

    print("🚀 Starting job search for Bhargav Pamidighantam")
    print("Target roles: MLOps Engineer, DevOps Engineer, Cloud Engineer, ML Engineer, AI Engineer")
    print("-" * 70)

    # Initialize agent
    agent = JobMatchingAgent(config_path="config/config.json")

    # Target roles - prioritizing MLOps and DevOps
    target_roles = [
        "MLOps Engineer",
        "DevOps Engineer",
        "Cloud Engineer",
        "Machine Learning Engineer",
        "AI Engineer",
        "ML Infrastructure Engineer",
        "Platform Engineer"
    ]

    # Run matching
    matches = agent.run(
        resume_path="my_resume.txt",
        target_roles=target_roles,
        location="Remote",  # Change to specific location if needed
        remote=True,        # Set to False if you want on-site/hybrid
        max_jobs=70,        # Collect more jobs for better matches
        min_score=65,       # Show jobs with 65+ match score
        top_n=20            # Display top 20 matches
    )

    # Display results
    print("\n")
    agent.display_results(matches, output_format="console")

    # Save to file
    output_file = "my_job_matches.json"
    agent.save_results(matches, output_file)

    # Print summary
    print("\n" + "=" * 70)
    print("📊 SEARCH SUMMARY")
    print("=" * 70)
    print(f"Total matches found: {len(matches)}")

    # Category breakdown
    excellent = [m for m in matches if m['final_score'] >= 90]
    strong = [m for m in matches if 75 <= m['final_score'] < 90]
    partial = [m for m in matches if 65 <= m['final_score'] < 75]

    print(f"\nExcellent fits (90+): {len(excellent)}")
    print(f"Strong fits (75-89): {len(strong)}")
    print(f"Partial fits (65-74): {len(partial)}")

    # Skill gap analysis
    print("\n📈 SKILL GAP ANALYSIS")
    print("-" * 70)

    all_missing_skills = []
    for match in matches[:15]:  # Top 15 jobs
        all_missing_skills.extend(match['missing_skills'])

    from collections import Counter
    skill_gaps = Counter(all_missing_skills).most_common(10)

    if skill_gaps:
        print("\nTop skills to develop (appearing in multiple job postings):")
        for skill, count in skill_gaps:
            print(f"  • {skill} (mentioned in {count} jobs)")

    # Top companies
    print("\n🏢 TOP COMPANIES")
    print("-" * 70)

    companies = {}
    for match in matches[:10]:
        company = match['job']['company']
        score = match['final_score']
        if company not in companies or score > companies[company]:
            companies[company] = score

    print("\nTop matching companies:")
    for company, score in sorted(companies.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  • {company} (best match: {score})")

    print(f"\n✅ Results saved to: {output_file}")
    print("\n🎯 Next steps:")
    print("  1. Review the top matches above")
    print("  2. Update resume with any missing skills you already have")
    print("  3. Start learning the skills identified in gap analysis")
    print("  4. Apply to jobs with 85+ match score first")
    print("  5. Customize your cover letter based on matching/missing skills")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
