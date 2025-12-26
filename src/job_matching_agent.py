"""Job Matching Agent - Main orchestrator for job matching system"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from colorama import Fore, Style, init

from .resume_parser import ResumeParser
from .job_crawler import JobCrawler
from .skill_normalizer import SkillNormalizer
from .matching_engine import MatchingEngine

# Initialize colorama for colored terminal output
init(autoreset=True)


class JobMatchingAgent:
    """
    Main agent that orchestrates the job matching process
    """

    def __init__(self, config_path: str = "config/config.json"):
        """
        Initialize the job matching agent

        Args:
            config_path: Path to configuration file
        """
        print(f"{Fore.CYAN}Initializing Job Matching Agent...{Style.RESET_ALL}")

        # Load configuration
        self.config = self._load_config(config_path)

        # Load skill taxonomy
        taxonomy_path = Path(config_path).parent / "skill_taxonomy.json"
        self.skill_taxonomy = self._load_taxonomy(taxonomy_path)

        # Initialize components
        self.resume_parser = ResumeParser(skill_taxonomy=self.skill_taxonomy)
        self.job_crawler = JobCrawler(config=self.config)
        self.skill_normalizer = SkillNormalizer(taxonomy=self.skill_taxonomy)
        self.matching_engine = MatchingEngine(
            model_name=self.config.get('semantic_model', 'all-MiniLM-L6-v2'),
            config=self.config.get('matching', {})
        )

        print(f"{Fore.GREEN}✓ Agent initialized successfully{Style.RESET_ALL}\n")

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"{Fore.YELLOW}Warning: Config not found, using defaults{Style.RESET_ALL}")
            return {}

    def _load_taxonomy(self, taxonomy_path: str) -> Dict:
        """Load skill taxonomy from JSON file"""
        try:
            with open(taxonomy_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"{Fore.YELLOW}Warning: Taxonomy not found, using empty taxonomy{Style.RESET_ALL}")
            return {}

    def run(
        self,
        resume_path: str,
        target_roles: List[str],
        location: str = "",
        remote: bool = False,
        max_jobs: int = 50,
        min_score: int = 60,
        top_n: int = 15
    ) -> List[Dict]:
        """
        Run the complete job matching pipeline

        Args:
            resume_path: Path to resume file (PDF or TXT)
            target_roles: List of target job roles
            location: Location filter
            remote: Filter for remote jobs
            max_jobs: Maximum jobs to collect
            min_score: Minimum match score threshold
            top_n: Number of top results to return

        Returns:
            List of top matching jobs with scores
        """
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Starting Job Matching Pipeline{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")

        # Step 1: Parse Resume
        print(f"{Fore.YELLOW}[1/4] Parsing resume...{Style.RESET_ALL}")
        resume_data = self.resume_parser.parse(resume_path)
        self._print_resume_summary(resume_data)

        # Step 2: Crawl Job Postings
        print(f"\n{Fore.YELLOW}[2/4] Crawling job postings...{Style.RESET_ALL}")
        jobs = self.job_crawler.search_multiple_roles(
            roles=target_roles,
            location=location,
            remote=remote,
            max_results_per_role=max_jobs // len(target_roles)
        )

        print(f"{Fore.GREEN}✓ Collected {len(jobs)} job postings{Style.RESET_ALL}")

        # Step 3: Match Jobs to Resume
        print(f"\n{Fore.YELLOW}[3/4] Matching jobs to resume...{Style.RESET_ALL}")

        job_dicts = [job.to_dict() for job in jobs]
        matches = self.matching_engine.batch_match(
            resume_data=resume_data,
            job_postings=job_dicts,
            skill_normalizer=self.skill_normalizer
        )

        # Step 4: Filter and Rank
        print(f"\n{Fore.YELLOW}[4/4] Ranking results...{Style.RESET_ALL}")

        # Filter by minimum score
        filtered_matches = [m for m in matches if m['final_score'] >= min_score]

        # Take top N
        top_matches = filtered_matches[:top_n]

        print(f"{Fore.GREEN}✓ Found {len(top_matches)} relevant matches (score >= {min_score}){Style.RESET_ALL}\n")

        return top_matches

    def _print_resume_summary(self, resume_data: Dict):
        """Print a summary of parsed resume data"""
        print(f"\n{Fore.CYAN}Resume Summary:{Style.RESET_ALL}")
        print(f"  Skills: {len(resume_data.get('skills', []))}")
        print(f"  Programming Languages: {', '.join(resume_data.get('programming_languages', [])[:5])}")
        print(f"  Frameworks: {', '.join(resume_data.get('frameworks', [])[:5])}")
        print(f"  Experience: {resume_data.get('experience_years', 'N/A')} years")
        print(f"  Seniority: {resume_data.get('seniority_level', 'N/A')}")

    def display_results(self, matches: List[Dict], output_format: str = "console"):
        """
        Display matching results

        Args:
            matches: List of match results
            output_format: Output format ('console' or 'json')
        """
        if output_format == "json":
            return self._display_json(matches)
        else:
            return self._display_console(matches)

    def _display_console(self, matches: List[Dict]):
        """Display results in formatted console output"""
        print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}TOP MATCHING JOBS{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")

        for i, match in enumerate(matches, 1):
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

    def _display_json(self, matches: List[Dict]) -> str:
        """Display results in JSON format"""
        output = []

        for match in matches:
            job = match['job']
            output.append({
                'job_title': job['title'],
                'company': job['company'],
                'location': job['location'],
                'url': job.get('url', ''),
                'source': job['source'],
                'match_score': match['final_score'],
                'recommendation': match['recommendation'],
                'component_scores': match['component_scores'],
                'matching_skills': match['matching_skills'],
                'missing_skills': match['missing_skills']
            })

        json_output = json.dumps(output, indent=2)
        print(json_output)
        return json_output

    def save_results(self, matches: List[Dict], output_path: str):
        """
        Save matching results to file

        Args:
            matches: List of match results
            output_path: Path to output file (JSON)
        """
        output = []

        for match in matches:
            job = match['job']
            output.append({
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
                'description': job['description'][:500]  # Truncate for size
            })

        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2)

        print(f"{Fore.GREEN}✓ Results saved to {output_path}{Style.RESET_ALL}")

    def interactive_mode(self):
        """Run agent in interactive mode"""
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Job Matching Agent - Interactive Mode{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")

        # Get resume path
        resume_path = input(f"{Fore.YELLOW}Enter path to your resume (PDF or TXT): {Style.RESET_ALL}").strip()

        # Get target roles
        print(f"\n{Fore.YELLOW}Enter target job roles (comma-separated):{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Example: Machine Learning Engineer, Data Scientist{Style.RESET_ALL}")
        roles_input = input("> ").strip()
        target_roles = [r.strip() for r in roles_input.split(',')]

        # Get location
        location = input(f"\n{Fore.YELLOW}Enter location (or press Enter for any location): {Style.RESET_ALL}").strip()

        # Remote preference
        remote_input = input(f"{Fore.YELLOW}Remote only? (y/n): {Style.RESET_ALL}").strip().lower()
        remote = remote_input == 'y'

        # Run matching
        matches = self.run(
            resume_path=resume_path,
            target_roles=target_roles,
            location=location,
            remote=remote
        )

        # Display results
        self.display_results(matches)

        # Save option
        save_input = input(f"\n{Fore.YELLOW}Save results to file? (y/n): {Style.RESET_ALL}").strip().lower()
        if save_input == 'y':
            output_path = input(f"{Fore.YELLOW}Enter output path (default: results.json): {Style.RESET_ALL}").strip()
            if not output_path:
                output_path = "results.json"
            self.save_results(matches, output_path)
