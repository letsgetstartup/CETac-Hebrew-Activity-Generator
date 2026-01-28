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

            # Ensure minimum tokens for Pro/Reasoning models to avoid truncation
            if max_tokens and max_tokens < 4096:
                logger.warning(f"Increasing max_tokens from {max_tokens} to 4096 for safety")
                max_tokens = 4096

            raw_response = self.ai_client.generate_content(
                prompt=system_prompt,
                schema=None,
                temperature=temperature,
                max_output_tokens=max_tokens
            )

            # 4. Validate Response
            # Hyper-robust JSON extraction using stack-based bracket counting
            def extract_json(res_text: str) -> str:
                res_text = res_text.strip()
                start_idx = res_text.find('{')
                if start_idx == -1:
                    return res_text
                
                stack = []
                for i in range(start_idx, len(res_text)):
                    if res_text[i] == '{':
                        stack.append('{')
                    elif res_text[i] == '}':
                        if stack:
                            stack.pop()
                            if not stack:
                                return res_text[start_idx:i+1]
                return res_text[start_idx:]

            clean_json = extract_json(raw_response)

            try:
                content_data = json.loads(clean_json)
                validated_content = ContentModel(**content_data)
            except json.JSONDecodeError as e:
                logger.error(f"JSON Decode Error: {e}, Raw: {raw_response}")
                raise ValueError("The AI model returned an unexpected format. Please try again.")
            except ValidationError as e:
                logger.error(f"Content Validation Failed: {e}")
                raise ValueError("The generated content did not pass pedagogical validation. Please try again.")

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
