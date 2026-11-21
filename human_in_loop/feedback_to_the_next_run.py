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
    raise ValueError("Please set the AICREDITS_API_KEY environment variable.")

model_client = OpenAIChatCompletionClient(model="gpt-5-nano", api_key=api_key, base_url=base_url)

assistant = AssistantAgent(
    name="Writer",
    description="You are a great writer",
    model_client=model_client,
    system_message="You are a really helpful assistant who writes in less than 30 words."
)
assistant_2 = AssistantAgent(
    name="Reviewer",
    description="You are a great reviewer",
    model_client=model_client,
    system_message="You are a really helpful assistant who reviewer in less than 30 words."
)
assistant_3 = AssistantAgent(
    name="Editor",
    description="You are a great editor",
    model_client=model_client,
    system_message="You are a really helpful assistant who writes in less than 30 words."
)

team = RoundRobinGroupChat(
    participants=[assistant,assistant_2,assistant_3],
    max_turns=3
)

async def main():
    task = "write 3 line poem about the sky."

    while True:
        stream = team.run_stream(task=task)

        await Console(stream)

        feedback_from_user_application = input("Please provide feedback to the team: ")

        if(feedback_from_user_application.lower().strip()=='exit'):
            break

        task = feedback_from_user_application

if (__name__=='__main__'):
    asyncio.run(main())
