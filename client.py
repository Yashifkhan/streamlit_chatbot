# import uuid

# import streamlit as st
# from langchain_core.messages import AIMessage, HumanMessage
# import uuid
# # from server import workow
# from main import workflow

# def generate_uuid():
#     thread_id=uuid.uuid4()
#     return thread_id

# def reset_chat():
#     thread_id=generate_uuid()
#     st.session_state.thread_id=thread_id
#     add_thread(st.session_state.thread_id)
#     st.session_state.messages=[]
    
    
# def add_thread(thread_id):
#     if thread_id not in st.session_state.chat_threads:
#         st.session_state.chat_threads.append(thread_id)
    
# def load_conversion(thread_id):
#     print("thread_id",thread_id)
#     state = workflow.get_state(config={'configurable': {'thread_id': thread_id}})
#     result = state.values.get("messages", [])
#     print("result --->>",result)
#     return result

# def get_chat_title(thread_id):
#     messages = load_conversion(thread_id)

#     for message in messages:
#         if isinstance(message, HumanMessage):
#             text = message.content.strip()

#             # Show first 10–15 words
#             words = text.split()

#             if len(words) > 15:
#                 return " ".join(words[:15]) + "..."

#             return text

#     return "New conversation"

# st.set_page_config(page_title="Chatbot", page_icon="💬")

# st.title("Chatbot")
# st.caption("Ask a question and get an answer from your LangGraph assistant.")


# if "messages" not in st.session_state:
#     st.session_state.messages = []

# if "thread_id" not in st.session_state:
#     st.session_state.thread_id = generate_uuid()

# if 'chat_threads' not in st.session_state:
#     st.session_state.chat_threads=[]
# add_thread(st.session_state.thread_id)

# st.sidebar.title("Emo v2 ")

# if st.sidebar.button('New chat'):
#     reset_chat()
    

# st.sidebar.header('MY conversations')

# # for thread_id in st.session_state.chat_threads[::-1]:
# #     if st.sidebar.button(str(thread_id)):
# #         st.session_state.thread_id=thread_id
# #         messages=load_conversion(thread_id)
# #         print("messages",messages)
# #         temp_messages=[]
# #         for msg in messages:
# #             print("msg",msg)
# #             if isinstance(msg,HumanMessage):
# #                 role ="user "
# #             else :
# #                 role = "assistent"
# #             temp_messages.append({'role':role,'content':msg.content})
# #         st.session_state.messages = messages

# for thread_id in st.session_state.chat_threads[::-1]:
#     chat_title = get_chat_title(thread_id)          # <-- naya
#     if st.sidebar.button(chat_title, key=str(thread_id)):   # <-- label change + unique key zaroori
#         st.session_state.thread_id = thread_id
#         messages = load_conversion(thread_id)
#         print("messages", messages)
#         temp_messages = []
#         for msg in messages:
#             print("msg", msg)
#             if isinstance(msg, HumanMessage):
#                 role = "user "
#             else:
#                 role = "assistent"
#             temp_messages.append({'role': role, 'content': msg.content})
#         st.session_state.messages = messages

# # Display previous messages
# for message in st.session_state.messages:

#     role = "user" if isinstance(message, HumanMessage) else "assistant"

#     with st.chat_message(role):
#         st.markdown(message.content)


# user_message = st.chat_input("Type your message...")



# if user_message:

#     human_message = HumanMessage(content=user_message)

#     st.session_state.messages.append(human_message)

#     # Display user message
#     with st.chat_message("user"):
#         st.markdown(user_message)

#     # Display assistant response
#     with st.chat_message("assistant"):
#         try:
#             config = {
#                 "configurable": {
#                     "thread_id": st.session_state.thread_id
#                 },
#                 "metadata": {
#                     "thread_id": st.session_state["thread_id"]
#                 },
#                 "run_name": "emo_chats"
#             }

#             response = workflow.stream(
#                 {"messages": [human_message]},
#                 config=config,
#                 stream_mode="messages"
#             )

#             message_placeholder = st.empty()
#             full_response = ""

#             for message_chunk, metadata in response:
#                 print("\n======================")
#                 print("TYPE:", type(message_chunk).__name__)
#                 print("NODE:", metadata.get("langgraph_node"))
#                 print("CONTENT:", message_chunk.content)

#                 if hasattr(message_chunk, "tool_calls"):
#                     print("TOOL CALLS:", message_chunk.tool_calls)

#                 print("======================")

#                 # Only process AI messages
#                 if isinstance(message_chunk, AIMessage):

#                     content = message_chunk.content

#                     if isinstance(content, str) and content:
#                         full_response += content

#                         message_placeholder.markdown(
#                             full_response
#                         )

#             # Save complete assistant response
#             if full_response:
#                 st.session_state.messages.append(
#                     AIMessage(content=full_response)
#                 )

#         except Exception as error:
#             st.error(f"Unable to get a response: {error}")







import uuid
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from main import workflow


def generate_uuid():
    thread_id = uuid.uuid4()
    return thread_id


def reset_chat():
    thread_id = generate_uuid()
    st.session_state.thread_id = thread_id
    add_thread(st.session_state.thread_id)
    st.session_state.messages = []


def add_thread(thread_id):
    if thread_id not in st.session_state.chat_threads:
        st.session_state.chat_threads.append(thread_id)


def load_conversion(thread_id):
    state = workflow.get_state(config={'configurable': {'thread_id': thread_id}})
    result = state.values.get("messages", [])
    return result


def get_chat_title(thread_id):
    messages = load_conversion(thread_id)
    for message in messages:
        if isinstance(message, HumanMessage):
            text = message.content.strip()
            words = text.split()
            if len(words) > 15:
                return " ".join(words[:15]) + "..."
            return text
    return "New conversation"


st.set_page_config(page_title="Chatbot", page_icon="💬")
st.title("Chatbot")
st.caption("Ask a question and get an answer from your LangGraph assistant.")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = generate_uuid()

if 'chat_threads' not in st.session_state:
    st.session_state.chat_threads = []

add_thread(st.session_state.thread_id)

st.sidebar.title("Emo v2")

if st.sidebar.button('New chat'):
    reset_chat()

st.sidebar.header('MY conversations')

for thread_id in st.session_state.chat_threads[::-1]:
    chat_title = get_chat_title(thread_id)
    if st.sidebar.button(chat_title, key=str(thread_id)):
        st.session_state.thread_id = thread_id
        st.session_state.messages = load_conversion(thread_id)

# Display previous messages (skip ToolMessage / non-human, non-ai content)
for message in st.session_state.messages:
    if isinstance(message, HumanMessage):
        role = "user"
    elif isinstance(message, AIMessage):
        role = "assistant"
    else:
        continue  # ToolMessage etc. -> UI mein show nahi karna

    if message.content:
        with st.chat_message(role):
            st.markdown(message.content)

user_message = st.chat_input("Type your message...")

if user_message:
    human_message = HumanMessage(content=user_message)
    st.session_state.messages.append(human_message)

    with st.chat_message("user"):
        st.markdown(user_message)

    with st.chat_message("assistant"):
        try:
            config = {
                "configurable": {"thread_id": st.session_state.thread_id},
                "metadata": {"thread_id": st.session_state["thread_id"]},
                "run_name": "emo_chats"
            }

            response = workflow.stream(
                {"messages": [human_message]},
                config=config,
                stream_mode="messages"
            )

            message_placeholder = st.empty()
            full_response = ""

            for message_chunk, metadata in response:
                # Sirf chat_llm node ke AIMessage chunks UI mein dikhao
                # (tool_node ke ToolMessage chunks ko skip karo)
                if isinstance(message_chunk, AIMessage) and metadata.get("langgraph_node") == "chat_llm":
                    content = message_chunk.content
                    if isinstance(content, str) and content:
                        full_response += content
                        message_placeholder.markdown(full_response)

            if full_response:
                st.session_state.messages.append(AIMessage(content=full_response))
            else:
                st.warning("Model se koi text response nahi aaya (sirf tool call hua ho sakta hai).")

        except Exception as error:
            st.error(f"Unable to get a response: {error}")