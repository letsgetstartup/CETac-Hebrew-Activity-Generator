"""Configuration models for prompt system."""
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class Tense(str, Enum):
    """Hebrew verb tenses."""
    PRESENT = "PRESENT"
    PAST = "PAST"
    FUTURE = "FUTURE"
    IMPERATIVE = "IMPERATIVE"
    INFINITIVE = "INFINITIVE"


class Binyan(str, Enum):
    """Hebrew verb patterns (binyanim)."""
    PAAL = "PAAL"  # פָּעַל
    NIFAL = "NIFAL"  # נִפְעַל
    PIEL = "PIEL"  # פִּעֵל
    PUAL = "PUAL"  # פֻּעַל
    HIFIL = "HIFIL"  # הִפְעִיל
    HUFAL = "HUFAL"  # הֻפְעַל
    HITPAEL = "HITPAEL"  # הִתְפַּעֵל


class GenderForm(str, Enum):
    """Hebrew gender and number forms."""
    MASCULINE = "MASCULINE"
    FEMININE = "FEMININE"
    PLURAL_MASCULINE = "PLURAL_MASCULINE"
    PLURAL_FEMININE = "PLURAL_FEMININE"


class MorphologicalConstraints(BaseModel):
    """Linguistic constraints for a CEFR level."""
    allowed_tenses: List[Tense] = Field(
        ...,
        description="Permitted verb tenses",
        min_length=1
    )
    allowed_binyanim: List[Binyan] = Field(
        ...,
        description="Permitted verb patterns",
        min_length=1
    )
    max_sentence_length: int = Field(
        ...,
        description="Maximum words per sentence",
        ge=5,
        le=30
    )
    niqqud_required: bool = Field(
        ...,
        description="Whether full vowel marks are required"
    )
    allowed_gender_forms: Optional[List[GenderForm]] = Field(
        default=None,
        description="Permitted gender/number forms"
    )


class BloomTaxonomyRules(BaseModel):
    """Rules for question cognitive level distribution."""
    distribution: Dict[str, float] = Field(
        ...,
        description="Target distribution of Bloom levels (should sum to 1.0)"
    )
    
    @field_validator("distribution")
    @classmethod
    def validate_distribution_sum(cls, v: Dict[str, float]) -> Dict[str, float]:
        """Ensure distribution sums to 1.0."""
        total = sum(v.values())
        if not 0.99 <= total <= 1.01:  # Allow small floating point errors
            raise ValueError(
                f"Bloom taxonomy distribution must sum to 1.0, got {total}"
            )
        return v


class GenerationConfig(BaseModel):
    """Vertex AI generation configuration overrides."""
    temperature: float = Field(default=0.3, ge=0.0, le=2.0)
    max_output_tokens: int = Field(default=2048, ge=100, le=8192)
    top_p: float = Field(default=0.95, ge=0.0, le=1.0)
    top_k: int = Field(default=40, ge=1, le=100)


class ValidationRules(BaseModel):
    """Content validation rules."""
    min_text_length: int = Field(default=50, ge=10)
    max_text_length: int = Field(default=500, ge=50)
    min_questions: int = Field(default=3, ge=1, le=10)
    max_questions: int = Field(default=5, ge=1, le=10)


class FewShotExample(BaseModel):
    """Example activity for few-shot learning."""
    topic: str
    activity: Dict[str, Any] = Field(
        ...,
        description="Activity JSON matching ContentModel schema"
    )


class PromptConfig(BaseModel):
    """Complete prompt configuration for a CEFR level."""
    level: str = Field(..., pattern=r"^[ABC][12]$")
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")
    author: Optional[str] = None
    created_at: Optional[datetime] = None
    description: Optional[str] = None
    
    morphological_constraints: MorphologicalConstraints
    system_prompt_template: str = Field(..., min_length=50)
    vocabulary_whitelist: Optional[List[str]] = None
    few_shot_examples: Optional[List[FewShotExample]] = None
    bloom_taxonomy_rules: Optional[BloomTaxonomyRules] = None
    generation_config: Optional[GenerationConfig] = None
    validation_rules: Optional[ValidationRules] = None
    
    @field_validator("system_prompt_template")
    @classmethod
    def validate_template_has_topic(cls, v: str) -> str:
        """Ensure template includes {{ topic }} placeholder."""
        if "{{ topic }}" not in v and "{{topic}}" not in v:
            raise ValueError(
                "system_prompt_template must include {{ topic }} placeholder"
            )
        return v
