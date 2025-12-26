"""Resume Parser Module - Extracts structured information from resumes"""

import re
from pathlib import Path
from typing import Dict, List, Set, Optional
import PyPDF2
import pdfplumber


class ResumeParser:
    """Parse resumes from PDF or text format and extract structured information"""

    def __init__(self, skill_taxonomy: Dict = None):
        self.skill_taxonomy = skill_taxonomy or {}
        self.experience_patterns = [
            r'(\d+)[\+]?\s*(?:years?|yrs?)',
            r'(\d+)\s*-\s*(\d+)\s*(?:years?|yrs?)'
        ]

    def parse(self, file_path: str) -> Dict:
        """
        Parse a resume file and extract structured information

        Args:
            file_path: Path to resume file (PDF or TXT)

        Returns:
            Dictionary containing parsed resume data
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Resume file not found: {file_path}")

        # Extract text based on file type
        if path.suffix.lower() == '.pdf':
            text = self._extract_pdf_text(file_path)
        else:
            text = self._extract_text_file(file_path)

        # Parse structured information
        return {
            'raw_text': text,
            'skills': self._extract_skills(text),
            'tools': self._extract_tools(text),
            'programming_languages': self._extract_programming_languages(text),
            'frameworks': self._extract_frameworks(text),
            'databases': self._extract_databases(text),
            'cloud_platforms': self._extract_cloud_platforms(text),
            'experience_years': self._extract_experience_years(text),
            'education': self._extract_education(text),
            'certifications': self._extract_certifications(text),
            'keywords': self._extract_keywords(text),
            'job_titles': self._extract_job_titles(text),
            'seniority_level': self._determine_seniority(text)
        }

    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF using multiple methods for robustness"""
        text = ""

        # Try pdfplumber first (better formatting)
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"pdfplumber failed: {e}, trying PyPDF2...")

        # Fallback to PyPDF2
        if not text.strip():
            try:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
            except Exception as e:
                raise ValueError(f"Failed to extract PDF text: {e}")

        return text

    def _extract_text_file(self, file_path: str) -> str:
        """Extract text from plain text file"""
        encodings = ['utf-8', 'latin-1', 'cp1252']

        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    return file.read()
            except UnicodeDecodeError:
                continue

        raise ValueError(f"Could not decode text file with supported encodings")

    def _extract_skills(self, text: str) -> List[str]:
        """Extract all skills from resume text"""
        skills = set()
        text_lower = text.lower()

        # Extract from all taxonomy categories
        for category in self.skill_taxonomy.values():
            for skill, synonyms in category.items():
                for synonym in synonyms:
                    if re.search(r'\b' + re.escape(synonym) + r'\b', text_lower):
                        skills.add(skill)
                        break

        return sorted(list(skills))

    def _extract_programming_languages(self, text: str) -> List[str]:
        """Extract programming languages"""
        return self._extract_from_taxonomy(text, 'programming_languages')

    def _extract_frameworks(self, text: str) -> List[str]:
        """Extract frameworks and libraries"""
        return self._extract_from_taxonomy(text, 'frameworks_libraries')

    def _extract_databases(self, text: str) -> List[str]:
        """Extract database technologies"""
        return self._extract_from_taxonomy(text, 'databases')

    def _extract_cloud_platforms(self, text: str) -> List[str]:
        """Extract cloud platforms"""
        return self._extract_from_taxonomy(text, 'cloud_platforms')

    def _extract_tools(self, text: str) -> List[str]:
        """Extract tools and technologies"""
        return self._extract_from_taxonomy(text, 'tools_technologies')

    def _extract_from_taxonomy(self, text: str, category: str) -> List[str]:
        """Extract skills from a specific taxonomy category"""
        skills = set()
        text_lower = text.lower()

        if category not in self.skill_taxonomy:
            return []

        for skill, synonyms in self.skill_taxonomy[category].items():
            for synonym in synonyms:
                if re.search(r'\b' + re.escape(synonym) + r'\b', text_lower):
                    skills.add(skill)
                    break

        return sorted(list(skills))

    def _extract_experience_years(self, text: str) -> Optional[int]:
        """Extract years of experience from resume"""
        # Look for patterns like "5+ years", "3-5 years", etc.
        for pattern in self.experience_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                if isinstance(matches[0], tuple):
                    # Range like "3-5 years"
                    return int(matches[0][1])  # Take upper bound
                else:
                    # Single number like "5 years"
                    return int(matches[0])

        # Try to infer from job history
        year_pattern = r'\b(19|20)\d{2}\b'
        years = re.findall(year_pattern, text)
        if len(years) >= 2:
            years = [int(y) for y in years]
            return max(years) - min(years)

        return None

    def _extract_education(self, text: str) -> List[Dict[str, str]]:
        """Extract education information"""
        education = []

        degrees = [
            'Ph\.?D', 'Doctorate', 'Doctor of Philosophy',
            'Master', 'M\.?S\.?', 'M\.?A\.?', 'MBA', 'M\.?Eng',
            'Bachelor', 'B\.?S\.?', 'B\.?A\.?', 'B\.?Eng',
            'Associate', 'A\.?S\.?', 'A\.?A\.?'
        ]

        fields = [
            'Computer Science', 'Data Science', 'Engineering',
            'Mathematics', 'Statistics', 'Physics', 'Business',
            'Information Technology', 'Software Engineering',
            'Machine Learning', 'Artificial Intelligence'
        ]

        degree_pattern = '|'.join(degrees)
        field_pattern = '|'.join(fields)

        # Find degree mentions
        pattern = f'({degree_pattern}).*?(?:in|of)?\\s*({field_pattern})?'
        matches = re.findall(pattern, text, re.IGNORECASE)

        for match in matches:
            education.append({
                'degree': match[0].strip(),
                'field': match[1].strip() if match[1] else ''
            })

        return education

    def _extract_certifications(self, text: str) -> List[str]:
        """Extract professional certifications"""
        certifications = []

        cert_patterns = [
            r'AWS Certified',
            r'Google Cloud Certified',
            r'Azure Certified',
            r'PMP',
            r'Scrum Master',
            r'CISSP',
            r'CompTIA',
            r'Certified.*Engineer',
            r'Professional.*Certificate'
        ]

        for pattern in cert_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            certifications.extend(matches)

        return list(set(certifications))

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords (nouns and technical terms)"""
        # Simple keyword extraction - can be enhanced with NLP
        words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)

        # Filter common words
        stopwords = {'The', 'This', 'That', 'With', 'From', 'Have', 'Been', 'Were', 'Was', 'Are', 'Your', 'Their'}
        keywords = [w for w in words if w not in stopwords]

        # Get word frequency
        from collections import Counter
        word_freq = Counter(keywords)

        # Return top keywords
        return [word for word, _ in word_freq.most_common(30)]

    def _extract_job_titles(self, text: str) -> List[str]:
        """Extract job titles from resume"""
        titles = []

        common_titles = [
            'Engineer', 'Developer', 'Scientist', 'Analyst', 'Manager',
            'Director', 'Architect', 'Consultant', 'Specialist', 'Lead',
            'Senior', 'Junior', 'Principal', 'Staff', 'VP', 'CTO', 'CEO'
        ]

        # Look for lines with job titles
        for line in text.split('\n'):
            line = line.strip()
            if any(title in line for title in common_titles):
                if len(line) < 100:  # Likely a title, not a description
                    titles.append(line)

        return titles[:5]  # Return top 5

    def _determine_seniority(self, text: str) -> str:
        """Determine seniority level from resume"""
        text_lower = text.lower()

        # Check for explicit seniority markers
        if any(word in text_lower for word in ['principal', 'staff engineer', 'distinguished']):
            return 'Principal/Staff'
        elif any(word in text_lower for word in ['senior', 'lead', 'sr.']):
            return 'Senior'
        elif any(word in text_lower for word in ['junior', 'jr.', 'associate']):
            return 'Junior'

        # Infer from experience
        years = self._extract_experience_years(text)
        if years:
            if years >= 10:
                return 'Senior/Lead'
            elif years >= 5:
                return 'Mid-level'
            elif years >= 2:
                return 'Junior/Mid-level'
            else:
                return 'Entry-level'

        return 'Mid-level'  # Default
