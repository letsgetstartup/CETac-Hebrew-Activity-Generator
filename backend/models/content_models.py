"""Content models for generated Hebrew learning activities."""
from enum import Enum
from typing import List
from pydantic import BaseModel, Field, field_validator
import re


class BloomLevel(str, Enum):
    """Bloom's Taxonomy cognitive levels."""
    REMEMBERING = "Remembering"
    UNDERSTANDING = "Understanding"
    APPLYING = "Applying"
    ANALYZING = "Analyzing"
    EVALUATING = "Evaluating"
    CREATING = "Creating"


class VocabularyItem(BaseModel):
    """A single vocabulary word with translation."""
    hebrew: str = Field(..., description="Hebrew word with niqqud", min_length=1)
    english: str = Field(..., description="English translation", min_length=1)
    
    @field_validator("hebrew")
    @classmethod
    def validate_hebrew(cls, v: str) -> str:
        """Ensure Hebrew text contains at least some Hebrew characters."""
        if not any('\u0590' <= c <= '\u05FF' for c in v):
            raise ValueError("Hebrew field must contain Hebrew characters")
        return v.strip()


class Question(BaseModel):
    """A comprehension question with multiple choice answers."""
    id: int = Field(..., description="Unique question ID", ge=1)
    stem_hebrew: str = Field(
        ...,
        description="Question text in Hebrew (should be niqqud for A1-A2)",
        min_length=5
    )
    options: List[str] = Field(
        ...,
        description="4 answer options in Hebrew",
        min_length=4,
        max_length=4
    )
    correct_answer_index: int = Field(
        ...,
        description="Index of correct answer (0-3)",
        ge=0,
        le=3
    )
    explanation: str = Field(
        ...,
        description="Pedagogical explanation in Hebrew of why answer is correct",
        min_length=10
    )
    cognitive_level: BloomLevel = Field(
        ...,
        description="Bloom's Taxonomy level of this question"
    )
    
    @field_validator("options")
    @classmethod
    def validate_options_unique(cls, v: List[str]) -> List[str]:
        """Ensure all options are unique."""
        if len(v) != len(set(v)):
            raise ValueError("All answer options must be unique")
        return v


class ContentModel(BaseModel):
    """Complete learning activity model."""
    title_hebrew: str = Field(
        ...,
        description="Activity title in Hebrew",
        min_length=3,
        max_length=100
    )
    cefr_level: str = Field(
        ...,
        description="CEFR level (A1, A2, B1, B2, C1)",
        pattern=r"^[ABC][12]$"
    )
    text_content: str = Field(
        ...,
        description="Main reading text in Hebrew with appropriate niqqud",
        min_length=50,
        max_length=1000
    )
    vocabulary_list: List[VocabularyItem] = Field(
        ...,
        description="Key vocabulary from the text",
        min_length=3,
        max_length=15
    )
    questions: List[Question] = Field(
        ...,
        description="Comprehension questions",
        min_length=3,
        max_length=10
    )
    
    @field_validator("text_content")
    @classmethod
    def validate_hebrew_content(cls, v: str, info) -> str:
        """Validate Hebrew text and niqqud requirements."""
        # Check for Hebrew characters
        if not any('\u0590' <= c <= '\u05FF' for c in v):
            raise ValueError("text_content must contain Hebrew characters")
        
        # For A1 and A2, require niqqud (vowel marks)
        if info.data.get("cefr_level") in ["A1", "A2"]:
            niqqud_chars = re.findall(r'[\u0591-\u05C7]', v)
            if len(niqqud_chars) < 10:
                raise ValueError(
                    f"Level {info.data.get('cefr_level')} requires extensive niqqud. "
                    f"Found only {len(niqqud_chars)} niqqud marks."
                )
        
        return v.strip()
    
    @field_validator("questions")
    @classmethod
    def validate_bloom_distribution(cls, v: List[Question]) -> List[Question]:
        """Ensure variety in cognitive levels (not all Remembering)."""
        levels = [q.cognitive_level for q in v]
        if len(set(levels)) == 1 and len(levels) > 2:
            raise ValueError(
                "Questions should vary in Bloom levels. "
                "Don't use only one cognitive level for all questions."
            )
        return v
    
    def model_post_init(self, __context) -> None:
        """Additional validation after model creation."""
        # Ensure question IDs are sequential
        expected_ids = list(range(1, len(self.questions) + 1))
        actual_ids = sorted([q.id for q in self.questions])
        if actual_ids != expected_ids:
            raise ValueError(
                f"Question IDs must be sequential 1-{len(self.questions)}. "
                f"Got: {actual_ids}"
            )
