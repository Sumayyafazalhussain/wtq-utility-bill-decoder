"""Gemini LLM client with retry logic."""
import json
import logging
from pathlib import Path
from typing import Optional

from google import genai
from google.genai import types
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from config import API_KEY, MODEL_NAME

logger = logging.getLogger(__name__)


class LLMClient:
    """Wrapper around Gemini API for bill extraction and Q&A."""

    def __init__(self, api_key: str = None, model_name: str = None):
        self.api_key = api_key or API_KEY
        self.model_name = model_name or MODEL_NAME
        self.client = genai.Client(api_key=self.api_key)
        logger.info(f"LLM Client initialized: {self.model_name}")

    def _image_to_part(self, image_path: Path) -> types.Part:
        """Convert image file to Gemini Part object."""
        with open(image_path, "rb") as f:
            image_bytes = f.read()

        suffix = image_path.suffix.lower()
        mime_map = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
        }
        mime_type = mime_map.get(suffix, "image/png")

        return types.Part.from_bytes(data=image_bytes, mime_type=mime_type)

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=2, min=15, max=120),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    )
    def generate(self, prompt: str, image_path: Optional[Path] = None) -> str:
        """Generate response from Gemini, optionally with an image."""
        contents = []

        if image_path:
            contents.append(self._image_to_part(image_path))

        contents.append(prompt)

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
            )
            return response.text
        except Exception as e:
            logger.warning(f"API call failed: {e}. Retrying...")
            raise

    def generate_json(self, prompt: str, image_path: Optional[Path] = None) -> dict:
        """Generate and parse JSON response."""
        raw = self.generate(prompt, image_path)
        cleaned = raw.strip()

        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            lines = lines[1:]
            if lines and lines[-1].strip().startswith("```"):
                lines = lines[:-1]
            cleaned = "\n".join(lines)

        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1:
            cleaned = cleaned[start : end + 1]

        return json.loads(cleaned)