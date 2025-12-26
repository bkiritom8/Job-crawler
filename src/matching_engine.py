"""Matching Engine - Semantic matching between resumes and job postings"""

import re
from typing import Dict, List, Tuple, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


class MatchingEngine:
    """
    Semantic matching engine for comparing resumes to job postings
    Uses transformer-based embeddings for semantic similarity
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", config: Dict = None):
        """
        Initialize matching engine

        Args:
            model_name: Name of sentence transformer model
            config: Configuration dictionary with weights and penalties
        """
        print(f"Loading semantic model: {model_name}...")
        self.model = SentenceTransformer(model_name)

        # Default configuration
        self.config = config or {
            'weights': {
                'skill_overlap': 0.40,
                'tool_alignment': 0.25,
                'experience_fit': 0.20,
                'role_alignment': 0.15
            },
            'penalties': {
                'missing_core_requirement': 15,
                'seniority_mismatch': 10
            }
        }

    def match(
        self,
        resume_data: Dict,
        job_posting: Dict,
        skill_normalizer=None
    ) -> Dict:
        """
        Match a resume against a job posting

        Args:
            resume_data: Parsed resume data
            job_posting: Job posting dictionary
            skill_normalizer: Optional skill normalizer for better matching

        Returns:
            Dictionary with match results and score
        """
        # Calculate individual component scores
        skill_score = self._calculate_skill_overlap(
            resume_data, job_posting, skill_normalizer
        )

        tool_score = self._calculate_tool_alignment(
            resume_data, job_posting, skill_normalizer
        )

        experience_score = self._calculate_experience_fit(
            resume_data, job_posting
        )

        role_score = self._calculate_role_alignment(
            resume_data, job_posting
        )

        semantic_score = self._calculate_semantic_similarity(
            resume_data, job_posting
        )

        # Weighted combination
        weights = self.config['weights']
        base_score = (
            skill_score * weights['skill_overlap'] +
            tool_score * weights['tool_alignment'] +
            experience_score * weights['experience_fit'] +
            role_score * weights['role_alignment']
        )

        # Blend with semantic similarity (20% weight)
        combined_score = base_score * 0.8 + semantic_score * 0.2

        # Apply penalties
        penalties = self._calculate_penalties(resume_data, job_posting)
        final_score = max(0, combined_score - penalties)

        # Extract matching and missing skills
        matching_skills, missing_skills = self._analyze_skills(
            resume_data, job_posting, skill_normalizer
        )

        return {
            'final_score': round(final_score, 2),
            'component_scores': {
                'skill_overlap': round(skill_score, 2),
                'tool_alignment': round(tool_score, 2),
                'experience_fit': round(experience_score, 2),
                'role_alignment': round(role_score, 2),
                'semantic_similarity': round(semantic_score, 2)
            },
            'penalties_applied': round(penalties, 2),
            'matching_skills': matching_skills,
            'missing_skills': missing_skills,
            'recommendation': self._get_recommendation(final_score)
        }

    def _calculate_skill_overlap(
        self,
        resume_data: Dict,
        job_posting: Dict,
        skill_normalizer
    ) -> float:
        """Calculate skill overlap score (0-100)"""
        resume_skills = set(resume_data.get('skills', []))
        job_description = job_posting.get('description', '')

        # Extract skills from job description
        if skill_normalizer:
            job_skills = set(skill_normalizer.extract_from_text(job_description))
        else:
            job_skills = set(self._extract_skills_simple(job_description))

        if not job_skills:
            return 50.0  # Neutral if no skills identified

        # Calculate overlap
        common_skills = resume_skills & job_skills
        overlap_ratio = len(common_skills) / len(job_skills)

        return min(100.0, overlap_ratio * 100)

    def _calculate_tool_alignment(
        self,
        resume_data: Dict,
        job_posting: Dict,
        skill_normalizer
    ) -> float:
        """Calculate tool/technology alignment score (0-100)"""
        resume_tools = set(
            resume_data.get('tools', []) +
            resume_data.get('frameworks', []) +
            resume_data.get('programming_languages', [])
        )

        job_description = job_posting.get('description', '').lower()

        # Count how many resume tools are mentioned in job
        matches = 0
        for tool in resume_tools:
            if tool.lower() in job_description:
                matches += 1

        if not resume_tools:
            return 50.0

        alignment_ratio = matches / len(resume_tools)
        return min(100.0, alignment_ratio * 120)  # Allow bonus for high alignment

    def _calculate_experience_fit(
        self,
        resume_data: Dict,
        job_posting: Dict
    ) -> float:
        """Calculate experience level fit (0-100)"""
        resume_years = resume_data.get('experience_years')
        job_description = job_posting.get('description', '')

        # Extract required experience from job
        required_years = self._extract_required_experience(job_description)

        if resume_years is None or required_years is None:
            return 70.0  # Neutral if experience unclear

        # Calculate fit
        if resume_years >= required_years:
            # Check for over-qualification (> 2x required)
            if resume_years > required_years * 2:
                return 75.0  # Slightly penalize over-qualification
            else:
                return 100.0  # Perfect fit
        else:
            # Under-qualified
            gap = required_years - resume_years
            if gap <= 1:
                return 80.0  # Close enough
            elif gap <= 2:
                return 60.0  # Moderate gap
            else:
                return 40.0  # Significant gap

    def _calculate_role_alignment(
        self,
        resume_data: Dict,
        job_posting: Dict
    ) -> float:
        """Calculate role/title alignment (0-100)"""
        resume_titles = resume_data.get('job_titles', [])
        job_title = job_posting.get('title', '')

        if not resume_titles or not job_title:
            return 60.0  # Neutral

        # Extract key role terms
        job_terms = self._extract_role_terms(job_title)
        resume_terms = set()
        for title in resume_titles:
            resume_terms.update(self._extract_role_terms(title))

        # Calculate overlap
        common_terms = job_terms & resume_terms
        if not job_terms:
            return 60.0

        overlap_ratio = len(common_terms) / len(job_terms)
        return overlap_ratio * 100

    def _calculate_semantic_similarity(
        self,
        resume_data: Dict,
        job_posting: Dict
    ) -> float:
        """Calculate semantic similarity using transformer embeddings (0-100)"""
        # Combine resume text
        resume_text = resume_data.get('raw_text', '')
        if not resume_text:
            resume_text = ' '.join(
                resume_data.get('skills', []) +
                resume_data.get('tools', []) +
                [str(t) for t in resume_data.get('job_titles', [])]
            )

        # Job description
        job_text = job_posting.get('description', '')

        if not resume_text or not job_text:
            return 50.0

        # Limit text length for efficiency
        resume_text = resume_text[:2000]
        job_text = job_text[:2000]

        try:
            # Generate embeddings
            embeddings = self.model.encode([resume_text, job_text])

            # Calculate cosine similarity
            similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]

            # Convert to 0-100 scale
            return float((similarity + 1) * 50)  # Cosine similarity is -1 to 1

        except Exception as e:
            print(f"Semantic similarity error: {e}")
            return 50.0

    def _calculate_penalties(
        self,
        resume_data: Dict,
        job_posting: Dict
    ) -> float:
        """Calculate penalties for missing requirements or mismatches"""
        penalties = 0

        # Check for "required" keywords in job description
        job_description = job_posting.get('description', '').lower()

        # Look for hard requirements
        required_section = re.search(
            r'(?:required|must have|requirements?):(.+?)(?:preferred|nice to have|$)',
            job_description,
            re.IGNORECASE | re.DOTALL
        )

        if required_section:
            required_text = required_section.group(1)
            resume_text = resume_data.get('raw_text', '').lower()

            # Check for critical missing skills
            critical_terms = ['required', 'must', 'essential']
            for term in critical_terms:
                if term in required_text and term not in resume_text:
                    penalties += self.config['penalties']['missing_core_requirement']
                    break  # Only penalize once

        # Seniority mismatch
        resume_seniority = resume_data.get('seniority_level', '').lower()
        job_title = job_posting.get('title', '').lower()

        seniority_mismatch = False
        if 'senior' in job_title and 'junior' in resume_seniority:
            seniority_mismatch = True
        elif 'junior' in job_title and 'senior' in resume_seniority:
            seniority_mismatch = True

        if seniority_mismatch:
            penalties += self.config['penalties']['seniority_mismatch']

        return penalties

    def _analyze_skills(
        self,
        resume_data: Dict,
        job_posting: Dict,
        skill_normalizer
    ) -> Tuple[List[str], List[str]]:
        """Analyze matching and missing skills"""
        resume_skills = set(resume_data.get('skills', []))
        job_description = job_posting.get('description', '')

        # Extract skills from job
        if skill_normalizer:
            job_skills = set(skill_normalizer.extract_from_text(job_description))
        else:
            job_skills = set(self._extract_skills_simple(job_description))

        matching = list(resume_skills & job_skills)
        missing = list(job_skills - resume_skills)

        return matching[:10], missing[:10]  # Top 10 each

    def _extract_skills_simple(self, text: str) -> List[str]:
        """Simple skill extraction without normalizer"""
        # Common tech terms
        common_skills = [
            'Python', 'Java', 'JavaScript', 'SQL', 'AWS', 'Docker',
            'Kubernetes', 'React', 'Node.js', 'Machine Learning',
            'TensorFlow', 'PyTorch', 'Git', 'CI/CD', 'Agile'
        ]

        found = []
        text_lower = text.lower()

        for skill in common_skills:
            if skill.lower() in text_lower:
                found.append(skill)

        return found

    def _extract_required_experience(self, text: str) -> Optional[int]:
        """Extract required years of experience from job description"""
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

    def _extract_role_terms(self, title: str) -> set:
        """Extract key role terms from job title"""
        # Remove common words
        stopwords = {'the', 'a', 'an', 'and', 'or', 'for', 'in', 'at', 'to'}

        words = re.findall(r'\b\w+\b', title.lower())
        terms = {w for w in words if w not in stopwords and len(w) > 2}

        return terms

    def _get_recommendation(self, score: float) -> str:
        """Get recommendation based on score"""
        if score >= 90:
            return "Excellent Fit"
        elif score >= 75:
            return "Strong Fit"
        elif score >= 60:
            return "Partial Fit"
        else:
            return "Weak Fit"

    def batch_match(
        self,
        resume_data: Dict,
        job_postings: List[Dict],
        skill_normalizer=None
    ) -> List[Dict]:
        """
        Match a resume against multiple job postings

        Args:
            resume_data: Parsed resume data
            job_postings: List of job posting dictionaries
            skill_normalizer: Optional skill normalizer

        Returns:
            List of match results with scores
        """
        results = []

        for job in job_postings:
            match_result = self.match(resume_data, job, skill_normalizer)
            match_result['job'] = job
            results.append(match_result)

        # Sort by score (descending)
        results.sort(key=lambda x: x['final_score'], reverse=True)

        return results
