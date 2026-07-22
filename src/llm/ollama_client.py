from ollama import Client

from src.config.settings import settings


class OllamaClient:

    def __init__(self):

        self.client = Client(
            host=settings.ollama_base_url
        )

        self.model = settings.ollama_model

    def generate(
        self,
        prompt: str,
        format: str = None,
        options: dict = None,
    ) -> str:
        
        # Default options baseline
        merged_options = {
            "temperature": 0
        }
        
        # Merge any custom options if passed
        if options:
            merged_options.update(options)
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "options": merged_options,
        }

        # Only include format if explicitly requested
        if format:
            payload["format"] = format

        response = self.client.chat(**payload)

        return response["message"]["content"].strip()