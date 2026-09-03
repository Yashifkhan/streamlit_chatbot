import uuid

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage

from server import workflow


st.set_page_config(page_title="Chatbot", page_icon="💬")

st.title("Chatbot")
st.caption("Ask a question and get an answer from your LangGraph assistant.")


if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())


# Display previous messages
for message in st.session_state.messages:

    role = "user" if isinstance(message, HumanMessage) else "assistant"

    with st.chat_message(role):
        st.markdown(message.content)


user_message = st.chat_input("Type your message...")


if user_message:

    human_message = HumanMessage(content=user_message)

    st.session_state.messages.append(human_message)

    # Display user message
    with st.chat_message("user"):
        st.markdown(user_message)

    # Display assistant response
    with st.chat_message("assistant"):

        try:

            config = {
                "configurable": {
                    "thread_id": st.session_state.thread_id
                }
            }

            response = workflow.stream(
                {"messages": [human_message]},
                config=config,
                stream_mode="messages"
            )

            # Placeholder for streaming text
            message_placeholder = st.empty()

            full_response = ""

            for message_chunk, metadata in response:

                # Only process AI messages
                if isinstance(message_chunk, AIMessage):

                    content = message_chunk.content

                    if content:
                        full_response += content

                        message_placeholder.markdown(full_response)

            # Save final response to session state
            if full_response:
                st.session_state.messages.append(
                    AIMessage(content=full_response)
                )

        except Exception as error:

            st.error(f"Unable to get a response: {error}")