"""Response models for API endpoints."""
from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from .content_models import ContentModel


class ActivityResponse(BaseModel):
    """Successful activity generation response."""
    success: bool = Field(default=True)
    data: ContentModel = Field(..., description="Generated activity content")
    generation_time_ms: Optional[int] = Field(
        None,
        description="Time taken to generate activity in milliseconds"
    )
    cached: bool = Field(
        default=False,
        description="Whether this result was served from cache"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata (version, model used, etc.)"
    )


class ErrorResponse(BaseModel):
    """Error response model."""
    success: bool = Field(default=False)
    error: str = Field(..., description="Error type/code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional error details for debugging"
    )
    request_id: Optional[str] = Field(
        default=None,
        description="Request ID for tracking and support"
    )


class ValidationErrorResponse(ErrorResponse):
    """Specific error for validation failures."""
    error: str = Field(default="VALIDATION_ERROR")
    validation_errors: list = Field(
        default_factory=list,
        description="List of specific validation errors"
    )
