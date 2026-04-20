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
    print("Testing imports in src/main.py...")
    # Add src to path
    sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
    import main
    print("SUCCESS: src/main.py imported successfully (with mocks).")
    print(f"  - chatbot function exists: {hasattr(main, 'chatbot')}")
    print(f"  - lambda_handler function exists: {hasattr(main, 'lambda_handler')}")
    print(f"  - get_client import exists: {hasattr(main, 'get_client')}")
except Exception as e:
    print(f"FAILURE: src/main.py import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
