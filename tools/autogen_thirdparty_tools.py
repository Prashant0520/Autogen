import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.tools import FunctionTool
import os
from dotenv import load_dotenv
from autogen_ext.tools.http import HttpTool
import requests

load_dotenv()

api_key = os.environ.get("AICREDITS_API_KEY")
base_url = os.environ.get("BASE_URL")
serper_api_key = os.environ.get("SERPER_API_KEY")

if not api_key:
    raise ValueError("Please set the OpenAI_API_KEY")


def search_web(query: str) -> str:
    """Search recent news for the given query and return titles, snippets and links."""
    try:
        resp = requests.post(
            "https://google.serper.dev/news",
            headers={"X-API-KEY": serper_api_key, "Content-Type": "application/json"},
            json={"q": query, "gl": "in", "num": 10, "tbs": "qdr:d"},  # qdr:d = past day
            timeout=15,
        )
        resp.raise_for_status()
        items = resp.json().get("news", [])
        if not items:
            return "No results found"
        return "\n\n".join(
            f"{i['title']} ({i.get('source', '')}, {i.get('date', '')})\n"
            f"{i.get('snippet', '')}\n{i['link']}"
            for i in items
        )
    except Exception as e:
        print(f"Error occurred while searching the web: {e}")
        return "No results found"

model_client = OpenAIChatCompletionClient(model="gpt-5-nano", api_key=api_key, base_url=base_url)

search_agent = AssistantAgent(
    name="SearchAgent",
    model_client=model_client,
    tools=[search_web],
    description="An agent that can search the web for information",
    system_message="You are a helpful assistant that can search the web for information using the `search_web` tool.",
    reflect_on_tool_use=True,
)

async def run_serper_search():
    """Run the search agent with a sample query."""
    query = "Latest News of India Express on 24-09-2026 about ECI?"
    print(f"Querying: {query}")

    result = await search_agent.run(task=query)

    print(result.messages[-1].content)

if (__name__=="__main__"):
    asyncio.run(run_serper_search())