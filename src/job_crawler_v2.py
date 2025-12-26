"""
Enhanced Job Crawler with Mock Data Fallback
Web scrapers can break when sites change HTML. This version includes mock data for testing.
"""

import re
import time
from typing import List, Dict, Optional
from urllib.parse import urlencode
import requests
from bs4 import BeautifulSoup


class JobPosting:
    """Represents a single job posting"""

    def __init__(
        self,
        title: str,
        company: str,
        location: str,
        description: str,
        url: str,
        source: str,
        required_skills: List[str] = None,
        preferred_skills: List[str] = None,
        experience_years: Optional[int] = None,
        tech_stack: List[str] = None,
        remote_type: Optional[str] = None
    ):
        self.title = title
        self.company = company
        self.location = location
        self.description = description
        self.url = url
        self.source = source
        self.required_skills = required_skills or []
        self.preferred_skills = preferred_skills or []
        self.experience_years = experience_years
        self.tech_stack = tech_stack or []
        self.remote_type = remote_type

    def to_dict(self) -> Dict:
        """Convert job posting to dictionary"""
        return {
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'description': self.description,
            'url': self.url,
            'source': self.source,
            'required_skills': self.required_skills,
            'preferred_skills': self.preferred_skills,
            'experience_years': self.experience_years,
            'tech_stack': self.tech_stack,
            'remote_type': self.remote_type
        }


class MockJobGenerator:
    """Generate realistic mock job postings for testing"""

    def __init__(self):
        self.mlops_jobs = [
            {
                'title': 'MLOps Engineer',
                'company': 'DataRobot',
                'location': 'Remote',
                'description': '''We are seeking an experienced MLOps Engineer to build and maintain our ML infrastructure.

Required Skills:
- Python, PyTorch, TensorFlow
- Docker, Kubernetes
- CI/CD pipelines (GitHub Actions, Jenkins)
- AWS (SageMaker, EC2, S3)
- MLflow or similar experiment tracking
- 2+ years experience with ML systems

Preferred:
- Terraform, Ansible
- Prometheus, Grafana
- Model serving (Seldon, TorchServe)

You will work on deploying ML models at scale, building automated training pipelines, and monitoring model performance in production.''',
                'url': 'https://www.example.com/jobs/mlops-engineer-1'
            },
            {
                'title': 'Senior MLOps Engineer',
                'company': 'Databricks',
                'location': 'San Francisco, CA (Hybrid)',
                'description': '''Join our ML Platform team to build infrastructure for ML at scale.

Requirements:
- 3+ years MLOps/DevOps experience
- Strong Python programming
- Kubernetes, Docker expertise
- Experience with Spark, Airflow
- ML frameworks: PyTorch, TensorFlow, scikit-learn
- Cloud platforms (AWS, Azure, or GCP)

Nice to have:
- Distributed computing (Ray, Dask)
- Feature stores
- LLM deployment experience

Build tools that data scientists love to use!''',
                'url': 'https://www.example.com/jobs/senior-mlops-1'
            },
            {
                'title': 'Machine Learning Engineer - Infrastructure',
                'company': 'Scale AI',
                'location': 'Remote',
                'description': '''ML Infrastructure Engineer to work on our ML platform.

Must have:
- Python, Java, or Go
- Docker, Kubernetes
- CI/CD automation
- AWS or GCP
- 2+ years ML systems experience

Responsibilities:
- Build ML training pipelines
- Deploy models to production
- Monitor model performance
- Optimize inference latency

Tech stack: Python, Kubernetes, AWS, PyTorch, FastAPI''',
                'url': 'https://www.example.com/jobs/ml-infra-1'
            },
            {
                'title': 'MLOps Platform Engineer',
                'company': 'Weights & Biases',
                'location': 'Remote',
                'description': '''Help build the next generation of MLOps tools.

Requirements:
- Strong Python skills
- Experience with ML frameworks (PyTorch, TensorFlow, Hugging Face)
- Kubernetes, Docker
- Building developer tools
- 2-5 years experience

You'll work on:
- Experiment tracking systems
- Model registry
- Dataset versioning
- Integration with ML frameworks

Ideal for someone passionate about ML infrastructure and developer experience.''',
                'url': 'https://www.example.com/jobs/mlops-platform-1'
            },
            {
                'title': 'DevOps Engineer - ML Team',
                'company': 'OpenAI',
                'location': 'San Francisco, CA',
                'description': '''DevOps Engineer supporting our ML research and deployment.

Requirements:
- 3+ years DevOps experience
- Kubernetes, Docker, Terraform
- CI/CD (GitHub Actions, CircleCI)
- AWS, GCP
- Python scripting
- Experience with ML workloads (GPU clusters)

Bonus:
- LLM deployment
- High-performance computing
- Networking optimization

Work with cutting-edge AI systems!''',
                'url': 'https://www.example.com/jobs/devops-ml-1'
            }
        ]

        self.devops_jobs = [
            {
                'title': 'DevOps Engineer',
                'company': 'HashiCorp',
                'location': 'Remote',
                'description': '''DevOps Engineer to build and maintain cloud infrastructure.

Skills needed:
- Terraform, Ansible
- Kubernetes, Docker
- AWS or GCP
- CI/CD pipelines
- Python or Go
- 2+ years DevOps experience

Build infrastructure as code, automate deployments, ensure reliability.''',
                'url': 'https://www.example.com/jobs/devops-1'
            },
            {
                'title': 'Platform Engineer',
                'company': 'Stripe',
                'location': 'Remote',
                'description': '''Platform Engineer to build internal developer tools.

Must have:
- Kubernetes, Docker
- Terraform, infrastructure as code
- CI/CD automation
- Python, Go, or Java
- AWS or GCP

Build platforms that enable developers to ship faster!''',
                'url': 'https://www.example.com/jobs/platform-1'
            },
            {
                'title': 'Cloud Engineer',
                'company': 'Snowflake',
                'location': 'San Mateo, CA (Hybrid)',
                'description': '''Cloud Infrastructure Engineer for our data platform.

Requirements:
- AWS, Azure, or GCP expertise
- Kubernetes, Docker
- Terraform, CloudFormation
- Python, Bash scripting
- 2+ years cloud experience

Work on multi-cloud infrastructure at scale.''',
                'url': 'https://www.example.com/jobs/cloud-eng-1'
            }
        ]

        self.ml_engineer_jobs = [
            {
                'title': 'Machine Learning Engineer',
                'company': 'Hugging Face',
                'location': 'Remote',
                'description': '''ML Engineer to work on NLP and LLMs.

Requirements:
- Python, PyTorch or TensorFlow
- NLP, transformers, Hugging Face library
- Model training and fine-tuning
- 2+ years ML experience

Build state-of-the-art NLP models!''',
                'url': 'https://www.example.com/jobs/ml-engineer-1'
            },
            {
                'title': 'Applied ML Engineer',
                'company': 'Anthropic',
                'location': 'San Francisco, CA',
                'description': '''Applied ML Engineer working on LLM applications.

Must have:
- Strong Python skills
- PyTorch, transformers
- LLM experience (fine-tuning, prompting)
- Model evaluation
- 2+ years ML experience

Work on cutting-edge AI safety research!''',
                'url': 'https://www.example.com/jobs/applied-ml-1'
            },
            {
                'title': 'AI/ML Engineer',
                'company': 'Cohere',
                'location': 'Remote',
                'description': '''AI Engineer to build and deploy LLMs.

Requirements:
- Python, PyTorch
- NLP, transformers, Hugging Face
- Model optimization
- API development (FastAPI, Flask)
- AWS or GCP

Build language models that power applications!''',
                'url': 'https://www.example.com/jobs/ai-ml-1'
            }
        ]

    def generate_jobs(self, role_type: str, count: int = 10) -> List[JobPosting]:
        """Generate mock jobs for a given role type"""

        role_map = {
            'mlops': self.mlops_jobs,
            'devops': self.devops_jobs,
            'ml': self.ml_engineer_jobs,
        }

        # Determine which job pool to use
        role_lower = role_type.lower()
        if 'mlops' in role_lower or 'ml ops' in role_lower:
            job_pool = self.mlops_jobs
        elif 'devops' in role_lower or 'platform' in role_lower:
            job_pool = self.devops_jobs
        elif 'machine learning' in role_lower or 'ml engineer' in role_lower or 'ai engineer' in role_lower:
            job_pool = self.ml_engineer_jobs
        elif 'cloud' in role_lower:
            job_pool = self.devops_jobs
        else:
            # Mix of all
            job_pool = self.mlops_jobs + self.devops_jobs + self.ml_engineer_jobs

        # Create JobPosting objects
        jobs = []
        for i, job_data in enumerate(job_pool[:count]):
            job = JobPosting(
                title=job_data['title'],
                company=job_data['company'],
                location=job_data['location'],
                description=job_data['description'],
                url=job_data['url'],
                source='MockData'
            )
            jobs.append(job)

        return jobs


class JobCrawler:
    """
    Main job crawler with fallback to mock data

    NOTE: Web scraping Indeed/LinkedIn is difficult because:
    1. They frequently change HTML structure
    2. They block scrapers with CAPTCHAs
    3. They rate-limit aggressively

    For production, use official APIs:
    - Indeed API: https://opensource.indeedeng.io/api-documentation/
    - LinkedIn API: Requires partnership
    - Alternative: Use job aggregator APIs (Adzuna, The Muse, etc.)
    """

    def __init__(self, config: Dict = None, use_mock: bool = True):
        self.config = config or {}
        self.use_mock = use_mock
        self.mock_generator = MockJobGenerator()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def search(
        self,
        query: str,
        location: str = "",
        remote: bool = False,
        max_results_per_source: int = 25,
        sources: List[str] = None
    ) -> List[JobPosting]:
        """
        Search for jobs across sources

        Args:
            query: Job search query
            location: Location filter
            remote: Remote jobs filter
            max_results_per_source: Max jobs per source
            sources: List of sources (ignored in mock mode)

        Returns:
            List of JobPosting objects
        """

        if self.use_mock:
            print(f"ℹ️  Using mock data (web scraping is unreliable)")
            print(f"   For production, integrate with job APIs (see docs)")
            return self.mock_generator.generate_jobs(query, max_results_per_source)

        # Try real scraping (likely to fail)
        jobs = []
        print("⚠️  Attempting web scraping (may not work)...")

        try:
            # Attempt Indeed scraping
            indeed_jobs = self._scrape_indeed(query, location, remote, max_results_per_source)
            jobs.extend(indeed_jobs)
        except Exception as e:
            print(f"⚠️  Indeed scraping failed: {e}")
            print(f"   Falling back to mock data...")
            jobs.extend(self.mock_generator.generate_jobs(query, max_results_per_source // 2))

        return jobs

    def search_multiple_roles(
        self,
        roles: List[str],
        location: str = "",
        remote: bool = False,
        max_results_per_role: int = 20
    ) -> List[JobPosting]:
        """Search for multiple job roles"""

        all_jobs = []

        for role in roles:
            print(f"\n{'='*60}")
            print(f"Searching for: {role}")
            print('='*60)

            jobs = self.search(
                query=role,
                location=location,
                remote=remote,
                max_results_per_source=max_results_per_role
            )

            all_jobs.extend(jobs)
            print(f"Found {len(jobs)} jobs for {role}")

        # Remove duplicates based on URL
        unique_jobs = {}
        for job in all_jobs:
            if job.url and job.url not in unique_jobs:
                unique_jobs[job.url] = job

        print(f"\n📊 Total unique jobs: {len(unique_jobs)}")
        return list(unique_jobs.values())

    def _scrape_indeed(self, query: str, location: str, remote: bool, max_results: int) -> List[JobPosting]:
        """
        Attempt to scrape Indeed (likely to fail due to anti-scraping measures)
        """
        jobs = []

        try:
            params = {
                'q': query,
                'l': location if not remote else 'Remote',
            }

            url = f"https://www.indeed.com/jobs?{urlencode(params)}"
            response = self.session.get(url, timeout=10)

            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}")

            soup = BeautifulSoup(response.content, 'html.parser')

            # Indeed's structure changes frequently - these selectors may not work
            job_cards = soup.find_all('div', class_=re.compile('job|result'))

            if not job_cards:
                raise Exception("No job cards found - HTML structure may have changed")

            for card in job_cards[:max_results]:
                # Parse job card (this is fragile and will likely break)
                title_elem = card.find('h2') or card.find('a', class_=re.compile('title'))
                if not title_elem:
                    continue

                job = JobPosting(
                    title=title_elem.get_text(strip=True),
                    company="Company",
                    location=location or "Remote",
                    description="Description not available",
                    url="https://www.indeed.com",
                    source="Indeed"
                )
                jobs.append(job)

        except Exception as e:
            print(f"   Indeed scraping error: {e}")
            raise

        return jobs
