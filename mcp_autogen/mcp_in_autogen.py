from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
import asyncio 
import time
from autogen_ext.tools.mcp import McpWorkbench,StdioServerParams
import os
from dotenv import load_dotenv
import warnings
warnings.filterwarnings("ignore")
load_dotenv()

api_key = os.environ.get("AICREDITS_API_KEY")
base_url = os.environ.get("BASE_URL")

if not api_key:
    raise ValueError("Please set the OpenAI_API_KEY")

async def main(main_task ):

    params = StdioServerParams(
    command = 'uvx',
    args=['mcp-server-time','--local-timezone=America/New_York'],
    read_timeout_seconds=60,
    )

    model = OpenAIChatCompletionClient(
        model='gpt-4o',
        api_key=api_key, 
        base_url=base_url
    )

    async with McpWorkbench(server_params=params) as workbench:

        agent = AssistantAgent(
            name='Agent',
            system_message='You are a helpful assistant',
            model_client=model,
            workbench=workbench,
            reflect_on_tool_use=True
        )

        async for message in agent.run_stream(task=main_task):
            print("-"*50)
            print(message)
            print('-'*50)

if(__name__=='__main__'):
    main_task = 'What is the time right now in New Delhi?'
    asyncio.run(main(main_task))
