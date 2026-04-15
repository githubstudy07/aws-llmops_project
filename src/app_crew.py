import json
import os
import sys
import sqlite3

def lambda_handler(event, context):
    diagnostics = {}
    
    # numpy 診断
    try:
        import numpy
        diagnostics["numpy"] = f"OK (v{numpy.__version__})"
    except Exception as e:
        diagnostics["numpy"] = f"FAILED: {str(e)}"
        
    # crewai 診断
    try:
        import crewai
        diagnostics["crewai"] = "OK"
    except Exception as e:
        diagnostics["crewai"] = f"FAILED: {str(e)}"

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({
            "status": "diagnostic_mode",
            "python_version": sys.version,
            "sqlite_version": sqlite3.sqlite_version,
            "diagnostics": diagnostics,
            "path": sys.path
        })
    }
