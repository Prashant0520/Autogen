"""Run an AutoGen agent with Notion's local MCP server."""

import asyncio
import os
import warnings
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.tools.mcp import McpWorkbench, StdioServerParams
from dotenv import load_dotenv
warnings.filterwarnings("ignore")
load_dotenv()

async def _run_agent(task: str) -> tuple[str, list[dict[str, object]]]:
    api_key = os.environ.get("AICREDITS_API_KEY")
    base_url = os.environ.get("BASE_URL")
    notion_token = os.environ.get("NOTION_TOKEN")
    if not notion_token:
        raise ValueError("Add NOTION_TOKEN to the project's .env file.")

    model_client = OpenAIChatCompletionClient(
        model=os.environ.get("MODEL"),
        api_key=api_key,
        base_url=base_url,
    )
    server_env = os.environ.copy()
    server_env.pop("BASE_URL", None)
    server_env.pop("AICREDITS_API_KEY", None)
    server_env["NOTION_TOKEN"] = notion_token
    server = StdioServerParams(
        command="cmd.exe",
        args=["/d", "/c", "npx.cmd", "-y", "@notionhq/notion-mcp-server"],
        env=server_env,
        read_timeout_seconds=60,
    )

    activity: list[dict[str, object]] = []
    answer = "The agent finished without a text response."
    try:
        async with McpWorkbench(server_params=server) as workbench:
            agent = AssistantAgent(
                name="notion_agent",
                system_message="""You are a Notion assistant; use MCP tools to search for pages and answer from their content.
Interpret requests by intent: use meaningful titles or keywords; for broad searches.Only create or edit content when explicitly asked, and base answers on tool results.""",
                model_client=model_client,
                workbench=workbench,
                reflect_on_tool_use=True,
                max_tool_iterations=6,
            )
            async for event in agent.run_stream(task=task):
                if type(event).__name__ == "ToolCallRequestEvent":
                    activity.extend(
                        {"kind": "request", "tool": call.name, "arguments": call.arguments}
                        for call in event.content
                    )
                elif type(event).__name__ == "ToolCallExecutionEvent":
                    activity.extend(
                        {
                            "kind": "result",
                            "tool": result.name,
                            "result": result.content,
                            "is_error": result.is_error,
                        }
                        for result in event.content
                    )
                elif isinstance(event, TextMessage) and event.source == "notion_agent":
                    answer = event.content
    finally:
        await model_client.close()

    return answer, activity


def run_agent(task: str) -> tuple[str, list[dict[str, object]]]:
    return asyncio.run(_run_agent(task))
