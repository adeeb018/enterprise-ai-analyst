from openai import OpenAI
from src.config.settings import settings


class CloudLLMClient:

    def __init__(self):
        print(f"DEBUG: Loaded API Key -> {settings.llm_api_key[:5]}... (Length: {len(settings.llm_api_key)})")
        # OpenRouter uses the OpenAI client structure with a custom base_url
        self.client = OpenAI(
            base_url=settings.llm_api_base,
            api_key=settings.llm_api_key,
        )
        self.model = settings.llm_model

    def generate(
        self,
        prompt: str,
        format: str = None,  # Can map to response_format if needed
        options: dict = None,
    ) -> str:
        
        temperature = 0
        if options and "temperature" in options:
            temperature = options["temperature"]

        # Base payload for OpenAI-compatible clients
        kwargs = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "temperature": temperature,
        }

        # If JSON mode is requested (OpenRouter supports response_format)
        if format == "json":
            kwargs["response_format"] = {"type": "json_object"}

        response = self.client.chat.completions.create(**kwargs)

        content = response.choices[0].message.content
        if content is None:
            return ""  # Or handle the empty case gracefully
        return content.strip()