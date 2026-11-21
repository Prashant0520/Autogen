import asyncio
from codecs import StreamReader
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from dotenv import load_dotenv
from autogen_agentchat.ui import Console
import os
import warnings
warnings.filterwarnings("ignore")
load_dotenv()

api_key = os.environ.get("AICREDITS_API_KEY")
base_url = os.environ.get("BASE_URL")

if not api_key:
    raise ValueError("Please set the OpenAI_API_KEY")


model_client = OpenAIChatCompletionClient(model="gpt-5-nano", api_key=api_key, base_url=base_url)

assistant = AssistantAgent(
    name='MyAssistant',
    description='you are a great assistant',
    model_client=model_client,
    system_message='You are a really helpful assistant who help on the task given.'
)

user_proxy_agent = UserProxyAgent(
    name ='UserProxy',
    description='You are a user proxy agent.',
    input_func=input
)

termination_condition = TextMentionTermination(text='APPROVE')

team = RoundRobinGroupChat(
    participants=[assistant, user_proxy_agent],
    termination_condition=termination_condition,
    max_turns=10
)

stream = team.run_stream(task = 'Write a great poem about soil of india?')

async def main():
    await Console(stream)

if (__name__ == '__main__'):
    asyncio.run(main())