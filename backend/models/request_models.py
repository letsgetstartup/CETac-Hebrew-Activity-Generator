"""Request and response models for API endpoints."""
from pydantic import BaseModel, Field, field_validator
from typing import Optional


class GenerateActivityRequest(BaseModel):
    """Request model for activity generation endpoint."""
    topic: str = Field(
        ...,
        description="Topic for the activity (e.g., 'Soccer', 'My Family')",
        min_length=2,
        max_length=100
    )
    level: str = Field(
        ...,
        description="CEFR level: A1, A2, B1, B2, or C1",
        pattern=r"^[ABC][12]$"
    )
    variant: Optional[str] = Field(
        default="default",
        description="Prompt config variant (e.g., 'dyslexia_optimized', 'heritage_learner')"
    )
    user_preferences: Optional[dict] = Field(
        default=None,
        description="Additional user preferences (e.g., preferred topics, difficulty)"
    )
    
    @field_validator("topic")
    @classmethod
    def sanitize_topic(cls, v: str) -> str:
        """Sanitize topic input to prevent prompt injection."""
        # Remove any instruction-like patterns
        dangerous_patterns = [
            "ignore", "system:", "assistant:", "###", "```",
            "forget", "disregard", "instead"
        ]
        v_lower = v.lower()
        for pattern in dangerous_patterns:
            if pattern in v_lower:
                raise ValueError(
                    f"Topic contains potentially unsafe content: '{pattern}'"
                )
        return v.strip()
    
    @field_validator("level")
    @classmethod
    def validate_supported_level(cls, v: str) -> str:
        """Ensure requested level is currently supported."""
        supported = ["A1", "A2", "B1"]  # Expand as configs are added
        if v not in supported:
            raise ValueError(
                f"Level {v} not yet supported. Available: {', '.join(supported)}"
            )
        return v
