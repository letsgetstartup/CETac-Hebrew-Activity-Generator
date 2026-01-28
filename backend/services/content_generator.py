"""
Content Generator Service.
Orchestrates the generation flow: Prompt Loading -> Vertex AI -> Validation.
"""
import logging
import json
import time
from typing import Optional, Dict

from services.prompt_manager import PromptManager
from logic.generator import VertexAIClient
from models.content_models import ContentModel
from models.request_models import GenerateActivityRequest
from models.response_models import ActivityResponse, ErrorResponse, ValidationErrorResponse
from pydantic import ValidationError

logger = logging.getLogger(__name__)

class ContentGenerator:
    """Service to generate educational content."""

    def __init__(self, prompt_manager: Optional[PromptManager] = None, ai_client: Optional[VertexAIClient] = None):
        self.prompt_manager = prompt_manager or PromptManager()
        self.ai_client = ai_client or VertexAIClient()

    def generate_activity(self, request: GenerateActivityRequest) -> ActivityResponse:
        """
        Generates a full learning activity based on the request.
        
        Orchestration steps:
        1. Load Prompt Config (via PromptManager)
        2. Render System Prompt (via PromptManager)
        3. Call Vertex AI (via VertexAIClient)
        4. Validate Response (via Pydantic)
        5. Return structured response
        """
        start_time = time.time()
        logger.info(f"Starting generation for topic='{request.topic}' level='{request.level}'")

        try:
            # 1 & 2. Load and Render Prompt
            # We fetch the config first to get generation settings (temp, tokens) if overridden
            config = self.prompt_manager.get_config(request.level, request.variant)
            
            system_prompt = self.prompt_manager.render_system_prompt(
                level=request.level,
                topic=request.topic,
                variant=request.variant
            )

            # 3. Call Vertex AI
            # Use config generation settings if present, else defaults
            gen_config = config.generation_config
            temperature = gen_config.temperature if gen_config else None
            max_tokens = gen_config.max_output_tokens if gen_config else None

            # Get schema from Pydantic model
            # response_schema = ContentModel.model_json_schema()
            # Note: Disabled schema enforcement to avoid $defs compatibility issues with GenAI SDK. 
            # We rely on response_mime_type="application/json" and manual validation.

            raw_response = self.ai_client.generate_content(
                prompt=system_prompt,
                schema=None,
                temperature=temperature,
                max_output_tokens=max_tokens
            )

            # 4. Validate Response
            # Clean up potential markdown code blocks if the model behaves unexpectedly (though response_mime_type should fix this)
            clean_json = raw_response.strip()
            if clean_json.startswith("```json"):
                clean_json = clean_json[7:-3].strip()
            elif clean_json.startswith("```"):
                clean_json = clean_json[3:-3].strip()

            try:
                content_data = json.loads(clean_json)
                validated_content = ContentModel(**content_data)
                
                # Retrieve vocabulary list from prompt config for additional validation/enrichment if needed
                # (Logic can be added here to warn if generated vocab isn't in allowlist)

            except json.JSONDecodeError as e:
                logger.error(f"JSON Decode Error: {e}, Raw: {raw_response[:100]}...")
                raise ValueError("Model returned invalid JSON")
            except ValidationError as e:
                logger.error(f"Content Validation Failed: {e}")
                # In a production system, we might retry here with a correction prompt
                raise e

            # 5. Return Response
            duration_ms = int((time.time() - start_time) * 1000)
            logger.info(f"Generation successful in {duration_ms}ms")
            
            return ActivityResponse(
                success=True,
                data=validated_content,
                generation_time_ms=duration_ms,
                metadata={
                    "level": request.level,
                    "variant": request.variant,
                    "version": config.version
                }
            )

        except ValidationError as ve:
            raise ve # Re-raise for outer handler or handle specially
        except Exception as e:
            logger.exception("Unexpected error during generation")
            raise e
