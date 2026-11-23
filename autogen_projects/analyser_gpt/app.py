import streamlit as st
import asyncio
import os

from Autogen.autogen_projects.analyser_gpt.teams.analyzer_gpt import getDataAnalyzerTeam
from Autogen.autogen_projects.analyser_gpt.models.openai_model_client import get_model_client
from Autogen.autogen_projects.analyser_gpt.config.docker_util import getDockerCommandLineExecutor,start_docker_container,stop_docker_container
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.base import TaskResult


st.title('Analyser GPT- Digital Data Analyzer') 

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])


if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'autogen_team_state' not in st.session_state:
    st.session_state.autogen_team_state = None
if('images_shown') not in st.session_state:
    st.session_state.images_shown=[]

task = st.chat_input("Enter your task here...")


async def run_analyser_gpt(task):
    docker = getDockerCommandLineExecutor()
    openai_model_client = get_model_client()

    try:
        await start_docker_container(docker)
        team = getDataAnalyzerTeam(docker, openai_model_client)

        if st.session_state.autogen_team_state is not None:
            await team.load_state(st.session_state.autogen_team_state)

        async for message in team.run_stream(task=task):
            if isinstance(message, TextMessage):
                if message.source.startswith("user"):
                    with st.chat_message("user", avatar="👤"):
                        st.markdown(message.content)

                elif message.source.startswith("Data_Analyzer_agent"):
                    with st.chat_message("Data Analyzer", avatar="🤖"):
                        st.markdown(message.content)

                elif message.source.startswith("Python_Code_Executor"):
                    with st.chat_message("Python Code Executor", avatar="👨‍💻"):
                        st.markdown(message.content)

                st.session_state.messages.append(message.content)

            elif isinstance(message, TaskResult):
                st.markdown(f"Stop Reason: {message.stop_reason}")
                st.session_state.messages.append(
                    f"Stop Reason: {message.stop_reason}"
                )

        st.session_state.autogen_team_state = await team.save_state()
        return None

    except Exception as e:
        st.exception(e)
        return e

    finally:
        await stop_docker_container(docker)



async def do_something_big():
    await asyncio.sleep(1)

if st.session_state.messages:
    for msg in st.session_state.messages:
        st.markdown(msg)


if task:
    if uploaded_file is not None:

        os.makedirs("temp", exist_ok=True)

        with open("temp/data.csv", "wb") as f:
            f.write(uploaded_file.getbuffer())

        task_with_file = f"""
The uploaded CSV file is available as data.csv in your working directory.
Inspect the actual column names before performing analysis.
Use data.csv for this task: {task}
"""

        error = asyncio.run(run_analyser_gpt(task_with_file))

        if error is None and os.path.exists("temp/output.png"):
            st.image("temp/output.png")
        elif error:
            st.error(f"An error occurred: {error}")

    else:
        st.warning("Please upload the file and provide the task")

else:
    st.warning("Please provide the task")
