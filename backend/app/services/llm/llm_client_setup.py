"""
OpenAI client initialization and setup.
"""
import os
from openai import AsyncOpenAI
import logging

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError(
        "OPENAI_API_KEY not found in environment variables. "
        "Please set it in a .env file in the project root or as an environment variable. and rebuild the docker container."
    )

client = AsyncOpenAI(api_key=api_key)

# Configure logger to output to stdout (appears in Docker logs)
logger = logging.getLogger("llm_client")

