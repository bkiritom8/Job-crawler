"""
Advanced example showing more control over the matching process
"""

import sys
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.resume_parser import ResumeParser
from src.job_crawler import JobCrawler
from src.skill_normalizer import SkillNormalizer
from src.matching_engine import MatchingEngine


def main():
    """Advanced usage with manual control"""

    # Load configurations
    with open("config/config.json") as f:
        config = json.load(f)

    with open("config/skill_taxonomy.json") as f:
        taxonomy = json.load(f)

    # Initialize components individually
    resume_parser = ResumeParser(skill_taxonomy=taxonomy)
    job_crawler = JobCrawler(config=config)
    skill_normalizer = SkillNormalizer(taxonomy=taxonomy)
    matching_engine = MatchingEngine(
        model_name="all-MiniLM-L6-v2",
        config=config['matching']
    )

    # Parse resume
    print("Parsing resume...")
    resume_data = resume_parser.parse("examples/sample_resume.txt")

    print("\nExtracted Skills:")
    for skill in resume_data['skills'][:10]:
        print(f"  - {skill}")

    # Crawl jobs with custom parameters
    print("\nCrawling job postings...")
    jobs = job_crawler.search(
        query="Senior Machine Learning Engineer",
        location="Remote",
        remote=True,
        max_results_per_source=20,
        sources=['indeed']  # Only use Indeed
    )

    print(f"Found {len(jobs)} jobs")

    # Custom matching with detailed analysis
    print("\nMatching jobs to resume...")

    job_dicts = [job.to_dict() for job in jobs]
    matches = matching_engine.batch_match(
        resume_data=resume_data,
        job_postings=job_dicts,
        skill_normalizer=skill_normalizer
    )

    # Custom filtering and analysis
    excellent_matches = [m for m in matches if m['final_score'] >= 90]
    strong_matches = [m for m in matches if 75 <= m['final_score'] < 90]

    print(f"\nResults:")
    print(f"  Excellent matches (90+): {len(excellent_matches)}")
    print(f"  Strong matches (75-89): {len(strong_matches)}")

    # Detailed analysis of top match
    if matches:
        top_match = matches[0]
        print(f"\nTop Match:")
        print(f"  Title: {top_match['job']['title']}")
        print(f"  Company: {top_match['job']['company']}")
        print(f"  Score: {top_match['final_score']}")
        print(f"  Component Scores:")
        for component, score in top_match['component_scores'].items():
            print(f"    - {component}: {score}")

    # Skill gap analysis
    all_missing_skills = set()
    for match in matches[:10]:
        all_missing_skills.update(match['missing_skills'])

    print(f"\nCommon missing skills (skill gap analysis):")
    for skill in list(all_missing_skills)[:10]:
        print(f"  - {skill}")


if __name__ == "__main__":
    main()
