from openai import OpenAI
from src.config.settings import settings


class GeminiLLMClient:

    def __init__(self):
        print(f"DEBUG: Loaded API Key -> {settings.llm_api_key[:5]}... (Length: {len(settings.llm_api_key)})")
        
        # Swapped to Google AI Studio's OpenAI-compatible base URL
        self.client = OpenAI(
            base_url=settings.gemini_llm_api_base,
            api_key=settings.gemini_llm_api_key, # This will now be your Google AI Studio API key
        )
        
        # Change your model name to a valid Gemini model ID supported by Google's API
        self.model = settings.gemini_llm_model

    def generate(
        self,
        prompt: str,
        format: str = None,  
        options: dict = None,
    ) -> str:
        
        temperature = 0
        if options and "temperature" in options:
            temperature = options["temperature"]

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

        # Google's OpenAI-compatible endpoint supports JSON mode format
        if format == "json":
            kwargs["response_format"] = {"type": "json_object"}

        response = self.client.chat.completions.create(**kwargs)

        return response.choices[0].message.content.strip()