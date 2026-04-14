import json
import os
import sys
import sqlite3

def lambda_handler(event, context):
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({
            "status": "hello",
            "python_version": sys.version,
            "sqlite_version": sqlite3.sqlite_version,
            "path": sys.path
        })
    }
