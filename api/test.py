"""
Minimal test function to debug Vercel deployment
"""
import sys
import os
from pathlib import Path

def handler(event, context):
    """Simple test handler"""
    try:
        return {
            "statusCode": 200,
            "body": "Test function works!"
        }
    except Exception as e:
        import traceback
        return {
            "statusCode": 500,
            "body": f"Error: {str(e)}\n{traceback.format_exc()}"
        }
