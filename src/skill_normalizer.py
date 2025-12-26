"""Skill Normalizer - Normalizes skill names and handles synonyms"""

from typing import Dict, List, Set
import re


class SkillNormalizer:
    """Normalizes skills and handles synonym mapping"""

    def __init__(self, taxonomy: Dict):
        """
        Initialize with skill taxonomy

        Args:
            taxonomy: Dictionary mapping canonical skills to synonyms
        """
        self.taxonomy = taxonomy
        self.synonym_map = self._build_synonym_map()

    def _build_synonym_map(self) -> Dict[str, str]:
        """Build reverse mapping from synonyms to canonical names"""
        synonym_map = {}

        for category in self.taxonomy.values():
            for canonical_name, synonyms in category.items():
                # Map canonical name to itself
                synonym_map[canonical_name.lower()] = canonical_name

                # Map all synonyms to canonical name
                for synonym in synonyms:
                    synonym_map[synonym.lower()] = canonical_name

        return synonym_map

    def normalize(self, skill: str) -> str:
        """
        Normalize a skill to its canonical form

        Args:
            skill: Skill name to normalize

        Returns:
            Canonical skill name, or original if not found
        """
        skill_lower = skill.lower().strip()

        # Direct lookup
        if skill_lower in self.synonym_map:
            return self.synonym_map[skill_lower]

        # Try fuzzy matching for common variations
        for synonym, canonical in self.synonym_map.items():
            if skill_lower == synonym or skill_lower.replace('-', ' ') == synonym:
                return canonical

        # Return original if no match found
        return skill

    def normalize_list(self, skills: List[str]) -> List[str]:
        """
        Normalize a list of skills

        Args:
            skills: List of skill names

        Returns:
            List of normalized skill names (unique)
        """
        normalized = set()

        for skill in skills:
            normalized.add(self.normalize(skill))

        return sorted(list(normalized))

    def extract_from_text(self, text: str) -> List[str]:
        """
        Extract and normalize skills from free text

        Args:
            text: Text to extract skills from

        Returns:
            List of normalized skills found in text
        """
        found_skills = set()
        text_lower = text.lower()

        for synonym, canonical in self.synonym_map.items():
            # Use word boundary matching for better accuracy
            pattern = r'\b' + re.escape(synonym) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.add(canonical)

        return sorted(list(found_skills))

    def get_skill_category(self, skill: str) -> str:
        """
        Get the category a skill belongs to

        Args:
            skill: Skill name

        Returns:
            Category name, or 'unknown' if not found
        """
        normalized = self.normalize(skill)

        for category_name, skills in self.taxonomy.items():
            if normalized in skills:
                return category_name

        return 'unknown'

    def calculate_overlap(self, skills1: List[str], skills2: List[str]) -> Dict:
        """
        Calculate overlap between two skill sets

        Args:
            skills1: First skill list
            skills2: Second skill list

        Returns:
            Dictionary with overlap metrics
        """
        # Normalize both lists
        norm1 = set(self.normalize_list(skills1))
        norm2 = set(self.normalize_list(skills2))

        # Calculate metrics
        common = norm1 & norm2
        only_in_1 = norm1 - norm2
        only_in_2 = norm2 - norm1

        overlap_percentage = len(common) / max(len(norm1), 1) * 100

        return {
            'common_skills': sorted(list(common)),
            'common_count': len(common),
            'skills_only_in_first': sorted(list(only_in_1)),
            'skills_only_in_second': sorted(list(only_in_2)),
            'overlap_percentage': overlap_percentage,
            'total_unique_skills': len(norm1 | norm2)
        }

    def categorize_skills(self, skills: List[str]) -> Dict[str, List[str]]:
        """
        Categorize a list of skills by taxonomy category

        Args:
            skills: List of skills

        Returns:
            Dictionary mapping category names to skills
        """
        categorized = {}

        for skill in skills:
            category = self.get_skill_category(skill)
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(skill)

        return categorized

    def find_related_skills(self, skill: str, max_related: int = 5) -> List[str]:
        """
        Find skills related to a given skill (same category)

        Args:
            skill: Skill to find related skills for
            max_related: Maximum number of related skills to return

        Returns:
            List of related skills
        """
        category = self.get_skill_category(skill)

        if category == 'unknown' or category not in self.taxonomy:
            return []

        # Get all skills in same category
        related = list(self.taxonomy[category].keys())

        # Remove the input skill
        normalized = self.normalize(skill)
        if normalized in related:
            related.remove(normalized)

        return related[:max_related]
