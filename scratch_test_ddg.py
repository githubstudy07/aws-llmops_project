import importlib.metadata
try:
    version = importlib.metadata.version("langgraph")
    print(f"SUCCESS: langgraph version: {version}")
    import langgraph
    from langgraph.prebuilt import create_react_agent
    print("SUCCESS: create_react_agent imported")
except Exception as e:
    print(f"FAILED: langgraph diagnostic failed: {e}")
