#!/usr/bin/env python3
"""
WORKING VERSION - Uses mock data for reliable testing

Why mock data?
- Web scraping Indeed/LinkedIn breaks constantly (HTML changes)
- They block scrapers with CAPTCHAs
- Rate limiting makes it unreliable

This version uses realistic mock jobs so you can:
1. Test the matching system
2. See how scores work
3. Identify your skill gaps
4. Practice before using real job APIs

For production: Integrate with job APIs (Adzuna, The Muse, etc.)
See INTEGRATION_GUIDE.md for details
"""

import sys
from pathlib import Path
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.resume_parser import ResumeParser
from src.skill_normalizer import SkillNormalizer
from src.matching_engine import MatchingEngine
from src.job_crawler_v2 import JobCrawler, MockJobGenerator
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)


def main():
    """Run personalized job search with mock data"""

    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Job Matching System - Bhargav Pamidighantam{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")

    print(f"{Fore.YELLOW}ℹ️  Using mock job data for testing{Style.RESET_ALL}")
    print(f"   Real web scraping is unreliable (sites block scrapers)")
    print(f"   Mock data lets you test the matching algorithm\n")

    # Load configurations
    print("Loading configurations...")
    with open("config/config.json") as f:
        config = json.load(f)

    with open("config/skill_taxonomy.json") as f:
        taxonomy = json.load(f)

    # Initialize components
    print("Initializing components...")
    resume_parser = ResumeParser(skill_taxonomy=taxonomy)
    skill_normalizer = SkillNormalizer(taxonomy=taxonomy)
    matching_engine = MatchingEngine(
        model_name="all-MiniLM-L6-v2",
        config=config.get('matching', {})
    )
    job_crawler = JobCrawler(config=config, use_mock=True)

    # Parse resume
    print(f"\n{Fore.CYAN}[1/4] Parsing your resume...{Style.RESET_ALL}")
    resume_data = resume_parser.parse("my_resume.txt")

    print(f"\n{Fore.GREEN}✓ Resume Summary:{Style.RESET_ALL}")
    print(f"  Skills: {len(resume_data.get('skills', []))}")
    print(f"  Languages: {', '.join(resume_data.get('programming_languages', [])[:5])}")
    print(f"  Frameworks: {', '.join(resume_data.get('frameworks', [])[:5])}")
    print(f"  Experience: {resume_data.get('experience_years', 'N/A')} years")
    print(f"  Seniority: {resume_data.get('seniority_level', 'N/A')}")

    # Target roles - prioritizing MLOps and DevOps
    target_roles = [
        "MLOps Engineer",
        "DevOps Engineer",
        "ML Infrastructure Engineer",
        "Platform Engineer",
        "Cloud Engineer",
        "Machine Learning Engineer",
        "AI Engineer"
    ]

    print(f"\n{Fore.CYAN}[2/4] Collecting job postings...{Style.RESET_ALL}")
    print(f"Target roles: {', '.join(target_roles[:3])}...")

    jobs = job_crawler.search_multiple_roles(
        roles=target_roles,
        location="Remote",
        remote=True,
        max_results_per_role=5  # 5 mock jobs per role
    )

    print(f"\n{Fore.GREEN}✓ Collected {len(jobs)} job postings{Style.RESET_ALL}")

    # Match jobs to resume
    print(f"\n{Fore.CYAN}[3/4] Matching jobs to your resume...{Style.RESET_ALL}")

    job_dicts = [job.to_dict() for job in jobs]
    matches = matching_engine.batch_match(
        resume_data=resume_data,
        job_postings=job_dicts,
        skill_normalizer=skill_normalizer
    )

    # Filter by score
    min_score = 60
    filtered_matches = [m for m in matches if m['final_score'] >= min_score]
    top_matches = filtered_matches[:20]

    print(f"\n{Fore.CYAN}[4/4] Ranking results...{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✓ Found {len(top_matches)} relevant matches (score >= {min_score}){Style.RESET_ALL}\n")

    # Display results
    print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}TOP MATCHING JOBS{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")

    for i, match in enumerate(top_matches, 1):
        job = match['job']
        score = match['final_score']

        # Color code by score
        if score >= 90:
            score_color = Fore.GREEN
        elif score >= 75:
            score_color = Fore.YELLOW
        elif score >= 60:
            score_color = Fore.BLUE
        else:
            score_color = Fore.RED

        print(f"{Fore.WHITE}[{i}] {Style.BRIGHT}{job['title']}{Style.RESET_ALL}")
        print(f"    {Fore.CYAN}Company:{Style.RESET_ALL} {job['company']}")
        print(f"    {Fore.CYAN}Location:{Style.RESET_ALL} {job['location']}")
        print(f"    {Fore.CYAN}Source:{Style.RESET_ALL} {job['source']}")

        if job.get('url'):
            print(f"    {Fore.CYAN}URL:{Style.RESET_ALL} {job['url']}")

        print(f"\n    {score_color}Match Score: {score} / 100{Style.RESET_ALL}")
        print(f"    {Fore.CYAN}Fit Level:{Style.RESET_ALL} {match['recommendation']}")

        # Component scores
        print(f"\n    {Fore.CYAN}Score Breakdown:{Style.RESET_ALL}")
        for component, component_score in match['component_scores'].items():
            print(f"      • {component.replace('_', ' ').title()}: {component_score}")

        # Matching skills
        if match['matching_skills']:
            print(f"\n    {Fore.GREEN}✓ Top Matching Skills:{Style.RESET_ALL}")
            for skill in match['matching_skills'][:5]:
                print(f"      • {skill}")

        # Missing skills
        if match['missing_skills']:
            print(f"\n    {Fore.RED}✗ Missing/Weak Areas:{Style.RESET_ALL}")
            for skill in match['missing_skills'][:5]:
                print(f"      • {skill}")

        print(f"\n{Fore.WHITE}{'-'*70}{Style.RESET_ALL}\n")

    # Save results
    output_file = "my_job_matches.json"
    output_data = []
    for match in top_matches:
        job = match['job']
        output_data.append({
            'job_title': job['title'],
            'company': job['company'],
            'location': job['location'],
            'url': job.get('url', ''),
            'source': job['source'],
            'match_score': match['final_score'],
            'recommendation': match['recommendation'],
            'component_scores': match['component_scores'],
            'matching_skills': match['matching_skills'],
            'missing_skills': match['missing_skills'],
            'description': job['description'][:500]
        })

    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)

    # Summary
    print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}📊 SEARCH SUMMARY{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"Total matches found: {len(top_matches)}")

    # Category breakdown
    excellent = [m for m in top_matches if m['final_score'] >= 90]
    strong = [m for m in top_matches if 75 <= m['final_score'] < 90]
    partial = [m for m in top_matches if 60 <= m['final_score'] < 75]

    print(f"\n{Fore.GREEN}Excellent fits (90+): {len(excellent)}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Strong fits (75-89): {len(strong)}{Style.RESET_ALL}")
    print(f"{Fore.BLUE}Partial fits (60-74): {len(partial)}{Style.RESET_ALL}")

    # Skill gap analysis
    print(f"\n{Fore.CYAN}📈 SKILL GAP ANALYSIS{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'-'*70}{Style.RESET_ALL}")

    all_missing_skills = []
    for match in top_matches[:15]:
        all_missing_skills.extend(match['missing_skills'])

    from collections import Counter
    skill_gaps = Counter(all_missing_skills).most_common(10)

    if skill_gaps:
        print(f"\nTop skills to develop (appearing in multiple job postings):")
        for skill, count in skill_gaps:
            print(f"  {Fore.YELLOW}•{Style.RESET_ALL} {skill} (mentioned in {count} jobs)")

    # Top companies
    print(f"\n{Fore.CYAN}🏢 TOP COMPANIES{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'-'*70}{Style.RESET_ALL}")

    companies = {}
    for match in top_matches[:10]:
        company = match['job']['company']
        score = match['final_score']
        if company not in companies or score > companies[company]:
            companies[company] = score

    print(f"\nTop matching companies:")
    for company, score in sorted(companies.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {Fore.GREEN}•{Style.RESET_ALL} {company} (best match: {score})")

    print(f"\n{Fore.GREEN}✅ Results saved to: {output_file}{Style.RESET_ALL}")

    print(f"\n{Fore.CYAN}🎯 Next Steps:{Style.RESET_ALL}")
    print(f"  1. Review the top matches above")
    print(f"  2. Note the missing skills (Docker, Kubernetes, etc.)")
    print(f"  3. For REAL jobs, integrate with job APIs:")
    print(f"     - Adzuna API (free tier available)")
    print(f"     - The Muse API")
    print(f"     - GitHub Jobs API")
    print(f"     - See INTEGRATION_GUIDE.md")
    print(f"  4. These mock results show you what to expect!")

    print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")


if __name__ == "__main__":
    main()
