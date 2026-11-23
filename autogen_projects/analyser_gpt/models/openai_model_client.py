from autogen_ext.models.openai import OpenAIChatCompletionClient
from Autogen.autogen_projects.analyser_gpt.config.constants import MODEL_OPENAI
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("OPENAI_API_KEY")
base_url = os.environ.get("BASE_URL")

if not api_key:
    raise ValueError("Please set the OpenAI_API_KEY")
if not base_url:
    raise ValueError("Please set the BASE_URL")



def get_model_client():
    model = MODEL_OPENAI

    kwargs = {
        "model": model,
        "api_key": api_key,
        "base_url": base_url,
    }

    if model.startswith("anthropic/claude-"):
        kwargs["model_info"] = {
            "vision": False,
            "function_calling": True,
            "json_output": False,
            "family": "unknown",
        }

    return OpenAIChatCompletionClient(**kwargs)
