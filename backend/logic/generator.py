"""
Vertex AI REST API Client.
Uses direct HTTP calls with API key authentication.
"""
import logging
import json
from typing import Optional, Dict, Any
import requests

import config.settings as settings
from models.content_models import ContentModel

logger = logging.getLogger(__name__)

class VertexAIClient:
    """Wrapper for Vertex AI REST API with API Key authentication."""
    
    def __init__(self):
        self.settings = settings.get_settings()
        self.model_name = self.settings.vertex_ai_model
        self.api_key = self.settings.gemini_api_key
        self.project_id = self.settings.gcp_project_id
        self.location = self.settings.gcp_region
        
        # Vertex AI REST API endpoint (global endpoint for publisher models)
        self.base_url = "https://aiplatform.googleapis.com/v1/publishers/google/models"
        
        self._initialized = False

    def _initialize(self):
        """Lazy initialization of AI client."""
        if self._initialized:
            return

        try:
            if not self.api_key:
                raise ValueError("GEMINI_API_KEY is missing in settings")
                
            masked_key = self.api_key[:10] + "..." + self.api_key[-4:]
            logger.info(f"Initialized Vertex AI REST client with API Key ({masked_key}) for model: {self.model_name}")
            self._initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize AI client: {e}")
            raise

    def generate_content(
        self,
        prompt: str,
        schema: Optional[Dict[str, Any]] = None,
        temperature: Optional[float] = None,
        max_output_tokens: Optional[int] = None
    ) -> str:
        """
        Generate content using Vertex AI REST API.
        
        Args:
            prompt: The user prompt
            schema: Response schema (optional, not used with REST API to avoid complexity)
            temperature: Generation temperature
            max_output_tokens: Max tokens to generate
            
        Returns:
            Generated text response
        """
        self._initialize()
        
        # Build generation config
        generation_config = {}
        if temperature is not None:
            generation_config["temperature"] = temperature
        if max_output_tokens is not None:
            generation_config["maxOutputTokens"] = max_output_tokens
        
        # Add response format hint for JSON
        generation_config["responseMimeType"] = "application/json"
        
        # Build request payload
        payload = {
            "contents": [{
                "role": "user",
                "parts": [{"text": prompt}]
            }]
        }
        
        if generation_config:
            payload["generationConfig"] = generation_config
        
        # Make API request
        url = f"{self.base_url}/{self.model_name}:generateContent"
        params = {"key": self.api_key}
        
        try:
            logger.info(f"Calling Vertex AI API: {self.model_name}")
            response = requests.post(
                url,
                params=params,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Extract text from response
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    text = candidate["content"]["parts"][0].get("text", "")
                    return text
            
            raise ValueError(f"Unexpected response format: {result}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Vertex AI API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"AI generation failed: {e}")
            raise
