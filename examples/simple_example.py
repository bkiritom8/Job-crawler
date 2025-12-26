"""
Simple example of using the Job Matching Agent programmatically
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.job_matching_agent import JobMatchingAgent


def main():
    """Simple example usage"""

    # Initialize the agent
    agent = JobMatchingAgent(config_path="config/config.json")

    # Define job search parameters
    resume_path = "examples/sample_resume.txt"  # Change to your resume
    target_roles = [
        "Machine Learning Engineer",
        "Data Scientist",
        "AI Engineer"
    ]

    # Run the matching pipeline
    matches = agent.run(
        resume_path=resume_path,
        target_roles=target_roles,
        location="San Francisco",
        remote=False,
        max_jobs=30,
        min_score=60,
        top_n=10
    )

    # Display results in console
    agent.display_results(matches, output_format="console")

    # Save results to file
    agent.save_results(matches, "examples/output/job_matches.json")


if __name__ == "__main__":
    main()
