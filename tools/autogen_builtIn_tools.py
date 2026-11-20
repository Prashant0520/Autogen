import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
import os
from dotenv import load_dotenv

from autogen_ext.tools.http import HttpTool

# Load environment variables
load_dotenv()
api_key = os.environ.get("AICREDITS_API_KEY")
base_url = os.environ.get("BASE_URL")

if not api_key:
    raise ValueError("Please set the OPENAI_API_KEY environment variable.")

model_client = OpenAIChatCompletionClient(
    model="gemini-2.5-flash", 
    api_key=api_key, 
    base_url=base_url, 
    model_info=
    {
        "vision": False,
        "function_calling": True,
        "json_output": False,
        "family": "gemini",
        "structured_output": True,
    },
)


schema = {
        "type": "object",
        "properties": {
            "fact": {
                "type": "string",
                "description": "A random cat fact"
            },
            "length": {
                "type": "integer",
                "description": "Length of the cat fact"
            }
        },
        "required": ["fact", "length"],
    }


http_tool = HttpTool(
    name="cat_facts_api",
    description="get a cool cat fact",
    scheme="https",
    host="catfact.ninja",
    port=443,
    path="/fact",
    method="GET",
    return_type="json",
    json_schema= schema
)

agent = AssistantAgent(
    name="CatFactsAgent",
    model_client=model_client,
    system_message='You are a helpful assistant that can provide cat facts using the `cat_facts_api` tool. Give the result with summary',
    tools=[http_tool],
    reflect_on_tool_use=True # Important
)


async def main(): 
    result = await agent.run(task = 'Give me a random cat fact')

    print(result.messages)
    print("#################")
    print(result.messages[-1].content)

if (__name__ == "__main__"):
    asyncio.run(main())