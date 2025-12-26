"""Job Crawler Module - Crawls job postings from multiple sources"""

import re
import time
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from urllib.parse import urlencode, quote_plus
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


class BaseCrawler(ABC):
    """Base class for job board crawlers"""

    def __init__(self, delay: float = 2.0):
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    @abstractmethod
    def search(
        self,
        query: str,
        location: str = "",
        remote: bool = False,
        max_results: int = 50
    ) -> List[JobPosting]:
        """Search for jobs matching criteria"""
        pass

    def _rate_limit(self):
        """Apply rate limiting between requests"""
        time.sleep(self.delay)

    def _extract_skills_from_description(self, description: str, skill_list: List[str]) -> List[str]:
        """Extract skills mentioned in job description"""
        found_skills = []
        description_lower = description.lower()

        for skill in skill_list:
            if re.search(r'\b' + re.escape(skill.lower()) + r'\b', description_lower):
                found_skills.append(skill)

        return found_skills

    def _extract_experience_years(self, text: str) -> Optional[int]:
        """Extract required years of experience"""
        patterns = [
            r'(\d+)[\+]?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:experience|exp)',
            r'(\d+)\s*-\s*(\d+)\s*(?:years?|yrs?)'
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) > 1:
                    return int(match.group(2))  # Upper bound
                return int(match.group(1))

        return None


class IndeedCrawler(BaseCrawler):
    """Crawler for Indeed job postings"""

    def __init__(self, delay: float = 2.0):
        super().__init__(delay)
        self.base_url = "https://www.indeed.com"

    def search(
        self,
        query: str,
        location: str = "",
        remote: bool = False,
        max_results: int = 50
    ) -> List[JobPosting]:
        """Search Indeed for job postings"""
        jobs = []

        try:
            params = {
                'q': query,
                'l': location if not remote else 'Remote',
                'start': 0
            }

            # Indeed shows ~15 jobs per page
            pages = min((max_results // 15) + 1, 5)  # Limit to 5 pages

            for page in range(pages):
                params['start'] = page * 10

                url = f"{self.base_url}/jobs?{urlencode(params)}"
                response = self.session.get(url, timeout=10)

                if response.status_code != 200:
                    print(f"Indeed request failed with status {response.status_code}")
                    break

                soup = BeautifulSoup(response.content, 'html.parser')

                # Find job cards (Indeed's structure may change)
                job_cards = soup.find_all('div', class_=re.compile('job_seen_beacon|jobsearch-ResultsList'))

                if not job_cards:
                    job_cards = soup.find_all('td', class_='resultContent')

                for card in job_cards:
                    try:
                        job = self._parse_job_card(card)
                        if job:
                            jobs.append(job)

                        if len(jobs) >= max_results:
                            break
                    except Exception as e:
                        print(f"Error parsing job card: {e}")
                        continue

                if len(jobs) >= max_results:
                    break

                self._rate_limit()

        except Exception as e:
            print(f"Indeed search error: {e}")

        return jobs[:max_results]

    def _parse_job_card(self, card) -> Optional[JobPosting]:
        """Parse individual job card from Indeed"""
        try:
            # Title and URL
            title_elem = card.find('h2', class_=re.compile('jobTitle'))
            if not title_elem:
                title_elem = card.find('a', class_=re.compile('jcs-JobTitle'))

            if not title_elem:
                return None

            title = title_elem.get_text(strip=True)
            job_link = title_elem.find('a')
            url = self.base_url + job_link['href'] if job_link and 'href' in job_link.attrs else ""

            # Company
            company_elem = card.find('span', class_=re.compile('companyName'))
            company = company_elem.get_text(strip=True) if company_elem else "Unknown"

            # Location
            location_elem = card.find('div', class_=re.compile('companyLocation'))
            location = location_elem.get_text(strip=True) if location_elem else "Not specified"

            # Description snippet
            desc_elem = card.find('div', class_=re.compile('job-snippet'))
            description = desc_elem.get_text(strip=True) if desc_elem else ""

            return JobPosting(
                title=title,
                company=company,
                location=location,
                description=description,
                url=url,
                source='Indeed'
            )

        except Exception as e:
            print(f"Error parsing Indeed job card: {e}")
            return None


class LinkedInCrawler(BaseCrawler):
    """Crawler for LinkedIn job postings"""

    def __init__(self, delay: float = 2.0):
        super().__init__(delay)
        self.base_url = "https://www.linkedin.com"

    def search(
        self,
        query: str,
        location: str = "",
        remote: bool = False,
        max_results: int = 50
    ) -> List[JobPosting]:
        """Search LinkedIn for job postings"""
        jobs = []

        try:
            params = {
                'keywords': query,
                'location': location,
                'f_WT': '2' if remote else '',  # Remote filter
                'start': 0
            }

            # LinkedIn shows 25 jobs per page
            pages = min((max_results // 25) + 1, 3)  # Limit to 3 pages

            for page in range(pages):
                params['start'] = page * 25

                url = f"{self.base_url}/jobs/search/?{urlencode(params)}"
                response = self.session.get(url, timeout=10)

                if response.status_code != 200:
                    print(f"LinkedIn request failed with status {response.status_code}")
                    break

                soup = BeautifulSoup(response.content, 'html.parser')

                # Find job cards
                job_cards = soup.find_all('div', class_=re.compile('base-card'))

                if not job_cards:
                    job_cards = soup.find_all('li', class_=re.compile('jobs-search-results__list-item'))

                for card in job_cards:
                    try:
                        job = self._parse_job_card(card)
                        if job:
                            jobs.append(job)

                        if len(jobs) >= max_results:
                            break
                    except Exception as e:
                        print(f"Error parsing LinkedIn job card: {e}")
                        continue

                if len(jobs) >= max_results:
                    break

                self._rate_limit()

        except Exception as e:
            print(f"LinkedIn search error: {e}")

        return jobs[:max_results]

    def _parse_job_card(self, card) -> Optional[JobPosting]:
        """Parse individual job card from LinkedIn"""
        try:
            # Title
            title_elem = card.find('h3', class_=re.compile('base-search-card__title'))
            if not title_elem:
                title_elem = card.find('a', class_=re.compile('job-card-list__title'))

            if not title_elem:
                return None

            title = title_elem.get_text(strip=True)

            # URL
            link_elem = card.find('a', class_=re.compile('base-card__full-link'))
            url = link_elem['href'] if link_elem and 'href' in link_elem.attrs else ""

            # Company
            company_elem = card.find('h4', class_=re.compile('base-search-card__subtitle'))
            if not company_elem:
                company_elem = card.find('a', class_=re.compile('job-card-container__company-name'))
            company = company_elem.get_text(strip=True) if company_elem else "Unknown"

            # Location
            location_elem = card.find('span', class_=re.compile('job-search-card__location'))
            location = location_elem.get_text(strip=True) if location_elem else "Not specified"

            return JobPosting(
                title=title,
                company=company,
                location=location,
                description="",  # LinkedIn requires additional request for full description
                url=url,
                source='LinkedIn'
            )

        except Exception as e:
            print(f"Error parsing LinkedIn job card: {e}")
            return None


class JobCrawler:
    """Main job crawler that aggregates results from multiple sources"""

    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.crawlers = {
            'indeed': IndeedCrawler(),
            'linkedin': LinkedInCrawler(),
        }

    def search(
        self,
        query: str,
        location: str = "",
        remote: bool = False,
        max_results_per_source: int = 25,
        sources: List[str] = None
    ) -> List[JobPosting]:
        """
        Search for jobs across multiple sources

        Args:
            query: Job search query (e.g., "Machine Learning Engineer")
            location: Location filter
            remote: Filter for remote jobs
            max_results_per_source: Maximum jobs per source
            sources: List of sources to use (defaults to all)

        Returns:
            List of JobPosting objects
        """
        all_jobs = []

        if sources is None:
            sources = list(self.crawlers.keys())

        for source in sources:
            if source not in self.crawlers:
                print(f"Unknown source: {source}")
                continue

            print(f"Searching {source}...")

            try:
                crawler = self.crawlers[source]
                jobs = crawler.search(
                    query=query,
                    location=location,
                    remote=remote,
                    max_results=max_results_per_source
                )
                all_jobs.extend(jobs)
                print(f"Found {len(jobs)} jobs from {source}")

            except Exception as e:
                print(f"Error searching {source}: {e}")

        print(f"\nTotal jobs collected: {len(all_jobs)}")
        return all_jobs

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

        # Remove duplicates based on URL
        unique_jobs = {}
        for job in all_jobs:
            if job.url and job.url not in unique_jobs:
                unique_jobs[job.url] = job

        return list(unique_jobs.values())
