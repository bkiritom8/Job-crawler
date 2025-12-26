#!/usr/bin/env python3
"""
Quick Test Script - See the system working in 30 seconds!
Uses mock data to demonstrate the matching algorithm
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.job_crawler_v2 import MockJobGenerator, JobPosting
from src.resume_parser import ResumeParser
from src.matching_engine import MatchingEngine
from src.skill_normalizer import SkillNormalizer
import json

print("🚀 Quick Test - Job Matching System\n")
print("="*60)

# Load config
with open("config/skill_taxonomy.json") as f:
    taxonomy = json.load(f)

with open("config/config.json") as f:
    config = json.load(f)

# Parse your resume
print("[1/3] Parsing resume...")
parser = ResumeParser(skill_taxonomy=taxonomy)
resume = parser.parse("my_resume.txt")
print(f"✓ Found {len(resume['skills'])} skills")
print(f"  Languages: {', '.join(resume['programming_languages'][:3])}")
print(f"  Experience: {resume.get('experience_years', 'N/A')} years\n")

# Generate mock jobs
print("[2/3] Generating mock jobs...")
mock_gen = MockJobGenerator()
jobs = mock_gen.generate_jobs("MLOps Engineer", count=5)
print(f"✓ Generated {len(jobs)} MLOps jobs\n")

# Match jobs
print("[3/3] Matching jobs to resume...")
normalizer = SkillNormalizer(taxonomy=taxonomy)
matcher = MatchingEngine(model_name="all-MiniLM-L6-v2", config=config.get('matching', {}))

job_dicts = [j.to_dict() for j in jobs]
matches = matcher.batch_match(resume, job_dicts, normalizer)

print(f"✓ Matched {len(matches)} jobs\n")
print("="*60)
print("TOP 3 MATCHES:\n")

for i, match in enumerate(matches[:3], 1):
    job = match['job']
    score = match['final_score']

    print(f"[{i}] {job['title']} at {job['company']}")
    print(f"    Score: {score}/100 - {match['recommendation']}")
    print(f"    Matching: {', '.join(match['matching_skills'][:3])}")
    print(f"    Missing: {', '.join(match['missing_skills'][:3])}\n")

print("="*60)
print("\n✅ Test complete!")
print("\nNext: Run 'python run_my_search_v2.py' for full analysis")
