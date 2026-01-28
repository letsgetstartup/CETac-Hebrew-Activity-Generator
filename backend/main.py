"""
Main entry point for Firebase Cloud Functions (Gen 2).
Exposes the API endpoints.
"""
import logging
from firebase_functions import https_fn, options
from firebase_admin import initialize_app
import json
from pydantic import ValidationError

from config import get_settings
from models.request_models import GenerateActivityRequest
from models.response_models import ErrorResponse, ValidationErrorResponse
from services.content_generator import ContentGenerator
from models.adaptation import AdaptContentRequest

# Initialize Firebase Admin
initialize_app()

settings = get_settings()

# Configure Logging
logging.basicConfig(level=getattr(logging, settings.log_level.upper()))
logger = logging.getLogger(__name__)

# Initialize Service Singleton
# (In serverless, this might re-init per cold start, which is fine)
content_generator = ContentGenerator()

@https_fn.on_request(
    memory=options.MemoryOption.GB_1,
    timeout_sec=120,
    region=options.SupportedRegion.US_CENTRAL1,
    min_instances=1 if settings.is_production else 0,
    max_instances=100,
    concurrency=80,
    secrets=[] # Add secrets to access if needed e.g. ["VERTEX_AI_API_KEY"] if not using ADC
)
def generate_activity(req: https_fn.Request) -> https_fn.Response:
    """
    API Endpoint: Generate a Hebrew Learning Activity.
    Method: POST
    Body: {"topic": "...", "level": "A1", ...}
    """
    
    # 1. CORS Headers
    cors_headers = {
        "Access-Control-Allow-Origin": "*", # Lock down in production
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
    }

    if req.method == "OPTIONS":
        return https_fn.Response("", status=204, headers=cors_headers)

    if req.method != "POST":
        return https_fn.Response(
            json.dumps(ErrorResponse(
                success=False, 
                error="METHOD_NOT_ALLOWED", 
                message="Only POST allowed"
            ).model_dump()),
            status=405, 
            headers=cors_headers,
            mimetype="application/json"
        )

    try:
        # 2. Parse & Validate Request
        try:
            req_json = req.get_json(silent=True)
            if not req_json:
                raise ValueError("Missing JSON body")
            
            request_model = GenerateActivityRequest(**req_json)
        except (ValueError, ValidationError) as e:
            logger.warning(f"Bad Request: {e}")
            error_resp = ValidationErrorResponse(
                success=False,
                error="BAD_REQUEST",
                message="Invalid request format",
                validation_errors=e.errors() if isinstance(e, ValidationError) else [{"msg": str(e)}]
            )
            return https_fn.Response(
                json.dumps(error_resp.model_dump()),
                status=400,
                headers=cors_headers,
                mimetype="application/json"
            )

        # 3. Generate Content
        response_model = content_generator.generate_activity(request_model)
        
        # 4. Return Success
        return https_fn.Response(
            json.dumps(response_model.model_dump()),
            status=200,
            headers=cors_headers,
            mimetype="application/json"
        )

    except Exception as e:
        import traceback
        logger.error(f"Internal Server Error: {e}", exc_info=True)
        return https_fn.Response(
            json.dumps(ErrorResponse(
                success=False, 
                error="INTERNAL_ERROR", 
                message=f"An unexpected error occurred: {str(e)}",
                details={"traceback": traceback.format_exc()}
            ).model_dump()),
            status=500,
            headers=cors_headers,
            mimetype="application/json"
        )

@https_fn.on_request(
    memory=options.MemoryOption.GB_1,
    timeout_sec=120,
    region=options.SupportedRegion.US_CENTRAL1,
)
def adapt_activity(req: https_fn.Request) -> https_fn.Response:
    """
    API Endpoint: Adapt content for special needs.
    Method: POST
    """
    # 1. CORS Headers
    cors_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }

    if req.method == "OPTIONS":
        return https_fn.Response("", status=204, headers=cors_headers)

    if req.method != "POST":
        return https_fn.Response(
            json.dumps({"error": "METHOD_NOT_ALLOWED", "message": "Only POST allowed"}),
            status=405, 
            headers=cors_headers,
            mimetype="application/json"
        )

    try:
        # 2. Parse Request
        try:
            req_json = req.get_json(silent=True)
            if not req_json:
                raise ValueError("Missing JSON body")
            request_model = AdaptContentRequest(**req_json)
        except (ValueError, ValidationError) as e:
            return https_fn.Response(
                json.dumps({"error": "BAD_REQUEST", "details": e.errors() if isinstance(e, ValidationError) else str(e)}),
                status=400,
                headers=cors_headers,
                mimetype="application/json"
            )

        # 3. Call Service
        result = content_generator.adapt_content(request_model)

        # 4. Return Success
        return https_fn.Response(
            json.dumps(result.model_dump()),
            status=200,
            headers=cors_headers,
            mimetype="application/json"
        )

    except Exception as e:
        logger.error(f"Adaptation Error: {e}")
        return https_fn.Response(
            json.dumps({"error": "INTERNAL_ERROR", "message": str(e)}),
            status=500,
            headers=cors_headers,
            mimetype="application/json"
        )
