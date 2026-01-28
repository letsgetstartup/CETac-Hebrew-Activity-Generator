"""Prompt Manager - Loads and manages prompt configurations."""
import json
import logging
from pathlib import Path
from typing import Dict, Optional
from jinja2 import Template, TemplateError
from pydantic import ValidationError

from models.config_models import PromptConfig

logger = logging.getLogger(__name__)


class PromptConfigSource:
    """Base class for prompt configuration sources."""
    def load_config(self, level: str, variant: str = "default") -> dict:
        raise NotImplementedError


class FileSystemConfigSource(PromptConfigSource):
    """Load configs from local file system."""
    def __init__(self, base_path: Optional[Path] = None):
        if base_path is None:
            # Default to config/prompts directory
            base_path = Path(__file__).parent.parent / "config" / "prompts"
        self.base_path = Path(base_path)
        logger.info(f"FileSystemConfigSource initialized at {self.base_path}")
    
    def load_config(self, level: str, variant: str = "default") -> dict:
        """Load configuration JSON file."""
        config_path = self.base_path / level.lower() / f"{variant}.json"
        
        if not config_path.exists():
            raise FileNotFoundError(
                f"Prompt config not found: {config_path}"
            )
        
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {config_path}: {e}")


class FirestoreConfigSource(PromptConfigSource):
    """Load configs from Firestore (for production)."""
    def __init__(self, db_client):
        self.db = db_client
        logger.info("FirestoreConfigSource initialized")
    
    def load_config(self, level: str, variant: str = "default") -> dict:
        """Load configuration from Firestore."""
        doc_ref = self.db.collection("prompt_configs").document(f"{level}_{variant}")
        doc = doc_ref.get()
        
        if not doc.exists:
            raise FileNotFoundError(
                f"Prompt config not found in Firestore: {level}_{variant}"
            )
        
        return doc.to_dict()


class PromptManager:
    """Manages prompt configurations and rendering."""
    
    def __init__(self, config_source: Optional[PromptConfigSource] = None):
        """Initialize with a configuration source."""
        self.config_source = config_source or FileSystemConfigSource()
        self._config_cache: Dict[str, PromptConfig] = {}
        logger.info("PromptManager initialized")
    
    def get_config(
        self,
        level: str,
        variant: str = "default",
        use_cache: bool = True
    ) -> PromptConfig:
        """
        Load and validate prompt configuration.
        
        Args:
            level: CEFR level (A1, A2, B1, etc.)
            variant: Config variant (default, dyslexia_optimized, etc.)
            use_cache: Whether to use cached configs
        
        Returns:
            Validated PromptConfig instance
        """
        cache_key = f"{level}_{variant}"
        
        # Check cache
        if use_cache and cache_key in self._config_cache:
            logger.debug(f"Using cached config: {cache_key}")
            return self._config_cache[cache_key]
        
        # Load from source
        logger.info(f"Loading config: level={level}, variant={variant}")
        try:
            config_dict = self.config_source.load_config(level, variant)
            config = PromptConfig(**config_dict)
            
            # Cache it
            self._config_cache[cache_key] = config
            
            logger.info(
                f"Config loaded successfully: {level} v{config.version}"
            )
            return config
            
        except FileNotFoundError as e:
            logger.error(f"Config not found: {e}")
            raise
        except ValidationError as e:
            logger.error(f"Config validation failed: {e}")
            raise ValueError(f"Invalid prompt configuration: {e}")
    
    def render_system_prompt(
        self,
        level: str,
        topic: str,
        variant: str = "default",
        **extra_context
    ) -> str:
        """
        Render the system prompt template with context.
        
        Args:
            level: CEFR level
            topic: Activity topic
            variant: Config variant
            **extra_context: Additional template variables
        
        Returns:
            Rendered prompt string
        """
        config = self.get_config(level, variant)
        
        # Prepare template context
        context = {
            "topic": topic,
            "level": level,
            **extra_context
        }
        
        try:
            template = Template(config.system_prompt_template)
            rendered = template.render(**context)
            
            logger.debug(f"Rendered prompt for topic='{topic}', level={level}")
            return rendered
            
        except TemplateError as e:
            logger.error(f"Template rendering failed: {e}")
            raise ValueError(f"Failed to render prompt template: {e}")
    
    def get_vocabulary_list(self, level: str, variant: str = "default") -> list:
        """
        Load vocabulary whitelist for a level.
        
        Returns:
            List of approved Hebrew words
        """
        config = self.get_config(level, variant)
        
        if not config.vocabulary_whitelist:
            return []
        
        vocab_words = []
        for vocab_ref in config.vocabulary_whitelist:
            # Handle file:// references
            if vocab_ref.startswith("file://"):
                rel_path = vocab_ref.replace("file://", "")
                vocab_path = (
                    Path(__file__).parent.parent / "config" / "prompts" / rel_path
                )
                
                if vocab_path.exists():
                    with open(vocab_path, "r", encoding="utf-8") as f:
                        # Read lines, skip comments and empty lines
                        words = [
                            line.strip()
                            for line in f
                            if line.strip() and not line.startswith("#")
                        ]
                        vocab_words.extend(words)
                else:
                    logger.warning(f"Vocabulary file not found: {vocab_path}")
        
        logger.info(f"Loaded {len(vocab_words)} vocabulary words for {level}")
        return vocab_words
    
    def clear_cache(self):
        """Clear the configuration cache."""
        self._config_cache.clear()
        logger.info("Config cache cleared")
