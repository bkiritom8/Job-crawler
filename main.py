#!/usr/bin/env python3
"""
Job Matching Agent - Command Line Interface

This is the main entry point for the job matching agent.
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.job_matching_agent import JobMatchingAgent


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Job Matching Agent - Find jobs that match your resume",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python main.py --interactive

  # Search for specific roles
  python main.py --resume resume.pdf --roles "Machine Learning Engineer,Data Scientist"

  # Search for remote jobs
  python main.py --resume resume.pdf --roles "Software Engineer" --remote

  # Search in specific location
  python main.py --resume resume.pdf --roles "Backend Developer" --location "San Francisco"

  # Save results to file
  python main.py --resume resume.pdf --roles "Data Engineer" --output results.json
        """
    )

    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Run in interactive mode'
    )

    parser.add_argument(
        '--resume', '-r',
        type=str,
        help='Path to resume file (PDF or TXT)'
    )

    parser.add_argument(
        '--roles',
        type=str,
        help='Target job roles (comma-separated)'
    )

    parser.add_argument(
        '--location', '-l',
        type=str,
        default="",
        help='Location filter (e.g., "San Francisco, CA")'
    )

    parser.add_argument(
        '--remote',
        action='store_true',
        help='Filter for remote jobs only'
    )

    parser.add_argument(
        '--max-jobs',
        type=int,
        default=50,
        help='Maximum number of jobs to collect (default: 50)'
    )

    parser.add_argument(
        '--min-score',
        type=int,
        default=60,
        help='Minimum match score threshold (default: 60)'
    )

    parser.add_argument(
        '--top-n',
        type=int,
        default=15,
        help='Number of top results to display (default: 15)'
    )

    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output file path (JSON format)'
    )

    parser.add_argument(
        '--config', '-c',
        type=str,
        default='config/config.json',
        help='Path to configuration file (default: config/config.json)'
    )

    parser.add_argument(
        '--format', '-f',
        type=str,
        choices=['console', 'json'],
        default='console',
        help='Output format (default: console)'
    )

    args = parser.parse_args()

    # Initialize agent
    try:
        agent = JobMatchingAgent(config_path=args.config)
    except Exception as e:
        print(f"Error initializing agent: {e}")
        sys.exit(1)

    # Interactive mode
    if args.interactive:
        agent.interactive_mode()
        return

    # Non-interactive mode - validate required arguments
    if not args.resume:
        parser.error("--resume is required in non-interactive mode")

    if not args.roles:
        parser.error("--roles is required in non-interactive mode")

    # Parse roles
    target_roles = [r.strip() for r in args.roles.split(',')]

    # Run matching
    try:
        matches = agent.run(
            resume_path=args.resume,
            target_roles=target_roles,
            location=args.location,
            remote=args.remote,
            max_jobs=args.max_jobs,
            min_score=args.min_score,
            top_n=args.top_n
        )

        # Display results
        agent.display_results(matches, output_format=args.format)

        # Save to file if specified
        if args.output:
            agent.save_results(matches, args.output)

    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error during job matching: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
