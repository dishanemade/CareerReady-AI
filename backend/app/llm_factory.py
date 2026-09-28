"""
Returns a LangChain chat model based on the LLM_PROVIDER env var.
This keeps every chain provider-agnostic -- switch providers in one place.
"""

import os
from dotenv import load_dotenv

load_dotenv()


def get_llm(temperature: float = 0.2):
    provider = os.getenv("LLM_PROVIDER", "openai").lower()

    if provider == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=temperature,
            api_key=os.getenv("OPENAI_API_KEY"),
        )

    elif provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(
            model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6"),
            temperature=temperature,
            api_key=os.getenv("ANTHROPIC_API_KEY"),
        )

    else:
        raise ValueError(
            f"Unknown LLM_PROVIDER '{provider}'. Use 'openai' or 'anthropic' in your .env file."
        )
