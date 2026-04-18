import sys
import os
from unittest.mock import MagicMock

# Mocking external dependencies for import test
sys.modules['boto3'] = MagicMock()
sys.modules['langfuse'] = MagicMock()
sys.modules['langfuse.langchain'] = MagicMock()
sys.modules['langchain_aws'] = MagicMock()
sys.modules['langchain_community.tools'] = MagicMock()
sys.modules['langchain_core.tools'] = MagicMock()
sys.modules['langgraph'] = MagicMock()
sys.modules['langgraph.prebuilt'] = MagicMock()

try:
    print("Testing imports in src/app.py...")
    # Add src to path
    sys.path.append(os.path.join(os.getcwd(), 'src'))
    import app
    print("SUCCESS: src/app.py imported successfully (with mocks).")
except Exception as e:
    print(f"FAILURE: src/app.py import failed: {e}")
    sys.exit(1)
