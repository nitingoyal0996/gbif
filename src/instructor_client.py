from dotenv import load_dotenv
import instructor
from groq import Groq, AsyncGroq
import os

load_dotenv()

default_provider = "openai"
default_model = "gpt-4.1"
default_temperature = 0.0


async def get_client(
    model: str = default_model,
    provider: str = default_provider,
    temperature: float = default_temperature,
    async_client: bool = True,
):
    if provider == "openai":
        return instructor.from_provider(
            model=provider + "/" + model,
            async_client=async_client,
            temperature=temperature,
        )
    elif provider == "groq":
        api_key = os.getenv("GROQ_API_KEY")
        if async_client:
            client = AsyncGroq(api_key=api_key)
        else:
            client = Groq(api_key=api_key)
        return instructor.from_groq(
            client,
            model="openai/",
            temperature=temperature,
        )
    else:
        raise ValueError(f"Invalid provider: {provider}")
