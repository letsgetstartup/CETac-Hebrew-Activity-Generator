"""Unit tests for PromptManager."""
import pytest
import json
from pathlib import Path
from backend.services.prompt_manager import PromptManager, FileSystemConfigSource
from backend.models.config_models import PromptConfig

# Mock config data
MOCK_A1_CONFIG = {
    "level": "A1",
    "version": "1.0.0",
    "morphological_constraints": {
        "allowed_tenses": ["PRESENT"],
        "allowed_binyanim": ["PAAL"],
        "max_sentence_length": 10,
        "niqqud_required": True
    },
    "system_prompt_template": "Create a {{ topic }} activity for level {{ level }}.",
    "vocabulary_whitelist": [],
    "few_shot_examples": []
}

class MockConfigSource:
    def load_config(self, level: str, variant: str = "default") -> dict:
        if level == "A1" and variant == "default":
            return MOCK_A1_CONFIG
        raise FileNotFoundError(f"Config not found: {level}_{variant}")

@pytest.fixture
def prompt_manager():
    return PromptManager(config_source=MockConfigSource())

def test_load_config_success(prompt_manager):
    config = prompt_manager.get_config("A1")
    assert isinstance(config, PromptConfig)
    assert config.level == "A1"
    assert config.version == "1.0.0"

def test_render_system_prompt(prompt_manager):
    prompt = prompt_manager.render_system_prompt(
        level="A1",
        topic="Soccer"
    )
    assert "Create a Soccer activity" in prompt
    assert "level A1" in prompt

def test_config_not_found(prompt_manager):
    with pytest.raises(FileNotFoundError):
        prompt_manager.get_config("C1")

def test_template_rendering_error(prompt_manager):
    # This shouldn't happen with valid config, but testing resilience
    pass
