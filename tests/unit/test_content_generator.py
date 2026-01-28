"""Unit tests for ContentGenerator."""
import pytest
from unittest.mock import MagicMock, patch
from backend.services.content_generator import ContentGenerator
from backend.models.request_models import GenerateActivityRequest
from backend.models.content_models import ContentModel
from backend.models.response_models import ActivityResponse

# Mock successful Gemini response (JSON string)
MOCK_GEMINI_RESPONSE = """
{
    "title_hebrew": "כלב חמוד",
    "cefr_level": "A1",
    "text_content": "זה כלב חמוד מאוד. הכלב אוהב לאכול בשר. הכלב אוהב לישון בבית. יש לכלב זנב ארוך ושחור. אני אוהב את הכלב שלי מאוד.",
    "vocabulary_list": [
        {"hebrew": "כלב", "english": "Dog"},
        {"hebrew": "לאכול", "english": "To eat"},
        {"hebrew": "לישון", "english": "To sleep"},
        {"hebrew": "בית", "english": "House"}
    ],
    "questions": [
        {
            "id": 1,
            "stem_hebrew": "מי זה?",
            "options": ["כלב", "חתול", "סוס", "גמל"],
            "correct_answer_index": 0,
            "explanation": "כתוב שזה כלב.",
            "cognitive_level": "Remembering"
        },
        {
            "id": 2,
            "stem_hebrew": "מה הכלב אוהב?",
            "options": ["לישון", "לרוץ", "לקפוץ", "לשחות"],
            "correct_answer_index": 0,
            "explanation": "הכלב אוהב לישון.",
            "cognitive_level": "Remembering"
        },
        {
            "id": 3,
            "stem_hebrew": "איך הכלב?",
            "options": ["חמוד", "רע", "גדול", "קטן"],
            "correct_answer_index": 0,
            "explanation": "זה כלב חמוד.",
            "cognitive_level": "Understanding"
        }
    ]
}
"""

@pytest.fixture
def mock_ai_client():
    client = MagicMock()
    client.generate_content.return_value = MOCK_GEMINI_RESPONSE
    return client

@pytest.fixture
def mock_prompt_manager():
    pm = MagicMock()
    # Return a dummy config object with generation_config
    config = MagicMock()
    config.generation_config = None
    config.version = "1.0.0"
    pm.get_config.return_value = config
    pm.render_system_prompt.return_value = "System Prompt"
    return pm

def test_generate_activity_success(mock_ai_client, mock_prompt_manager):
    generator = ContentGenerator(
        prompt_manager=mock_prompt_manager,
        ai_client=mock_ai_client
    )
    
    request = GenerateActivityRequest(topic="Dog", level="A1")
    
    # Update regex replacement for the longer text
    valid_hebrew_response = MOCK_GEMINI_RESPONSE.replace(
        "זה כלב חמוד מאוד. הכלב אוהב לאכול בשר. הכלב אוהב לישון בבית. יש לכלב זנב ארוך ושחור. אני אוהב את הכלב שלי מאוד.",
        "זֶה כֶּלֶב חָמוּד מְאוֹד. הַכֶּלֶב אוֹהֵב לֶאֱכוֹל בָּשָׂר. הַכֶּלֶב אוֹהֵב לִישׁוֹן בַּבַּיִת. יֵשׁ לַכֶּלֶב זָנָב אָרוֹךְ וְשָׁחוֹר. אֲנִי אוֹהֵב אֶת הַכֶּלֶב שֶׁלִּי מְאוֹד."
    )
    mock_ai_client.generate_content.return_value = valid_hebrew_response
    
    response = generator.generate_activity(request)
    
    assert isinstance(response, ActivityResponse)
    assert response.success is True
    assert response.data.title_hebrew == "כלב חמוד"
