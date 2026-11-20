from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from autogen_core.tools import FunctionTool
import os
import asyncio
from dotenv import load_dotenv
import warnings
warnings.filterwarnings("ignore")
load_dotenv()

api_key = os.environ.get("AICREDITS_API_KEY")
base_url = os.environ.get("BASE_URL")

if not api_key:
    raise ValueError("Please set the OpenAI_API_KEY")


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

def reverse_string(text: str) -> str:
    '''
    Reverse the given text
    input:str
    output:str
    The reverse string is returned.
    '''
    return text[::-1]

reverse_tool = FunctionTool(reverse_string, description='A tool to reverse a string')

agent = AssistantAgent(
    name="ReverseStringAgent",
    model_client= model_client,
    system_message='You are a helpful assistant that can reverse string using `reverse_string` tool. Give the result with summary',
    tools=[reverse_tool],
    reflect_on_tool_use=True # Important
)

async def main(): 
    result = await agent.run(task = '"Hello, World!"')

    print(result.messages[-1].content)

if (__name__=="__main__"):
    asyncio.run(main())
