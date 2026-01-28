import sys
import os

print(f"Python executable: {sys.executable}")
print(f"PYTHONPATH: {os.environ.get('PYTHONPATH')}")
print(f"CWD: {os.getcwd()}")

try:
    import pydantic
    print(f"Pydantic version: {pydantic.__version__}")
    
    import vertexai
    print("vertexai imported successfully")
    
    from backend.services.prompt_manager import PromptManager
    print("PromptManager imported successfully")
    
    from backend.services.content_generator import ContentGenerator
    print("ContentGenerator imported successfully")
    
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")
