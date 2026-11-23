"""Streamlit chat for the Notion MCP agent."""

import json
import streamlit as st
from Autogen.autogen_projects.notion_mcp_streamlit.agent import run_agent


st.set_page_config(page_title="Notion assistant", page_icon="📓")
st.title("Notion assistant")
st.caption("Ask a question or describe a task for your Notion workspace.")


def show_activity(activity: list[dict[str, object]]) -> None:
    for item in activity:
        tool = item.get("tool", "Notion MCP tool")
        if item.get("kind") == "request":
            label = f"Request · {tool}"
            payload = item.get("arguments", {})
        else:
            label = f"Response · {tool}"
            payload = item.get("result", "(empty response)")

        with st.expander(label):
            if isinstance(payload, (dict, list)):
                st.json(payload)
            elif isinstance(payload, str):
                try:
                    st.json(json.loads(payload))
                except json.JSONDecodeError:
                    st.write(payload)
            else:
                st.write(payload)


with st.sidebar:
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("activity"):
            activity = message["activity"]
            with st.expander(f"MCP activity · {len(activity)} events"):
                show_activity(activity)

prompt = st.chat_input("Ask Notion something…")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Working with Notion…"):
                answer, activity = run_agent(prompt)
        except Exception as error:
            answer, activity = f"I couldn't complete that request.\n\n{error}", []

        st.markdown(answer)
        if activity:
            with st.expander(f"MCP activity · {len(activity)} events", expanded=True):
                show_activity(activity)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer, "activity": activity}
    )
