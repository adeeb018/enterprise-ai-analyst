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
    ) -> str:

        response = self.client.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            options={
                "temperature": 0
            },
        )

        return response["message"]["content"].strip()