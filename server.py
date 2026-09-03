from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal,Annotated
from langchain_core.messages import HumanMessage, SystemMessage,BaseMessage
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

model = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=GROQ_API_KEY,
    temperature=1,
    max_tokens=1024,
)

class chatState(TypedDict):
    messages:Annotated[list[BaseMessage],add_messages]
    question:str
    answer:str

check_pointer=MemorySaver()
graph=StateGraph(chatState)

def chat_llm(state:chatState):
    # prompt=f"you are a helpfull assistant,give the answer of user qustion {state['question']} "
    messages=state['messages']
    result=model.invoke(messages)
    return {'messages':[result]}

graph.add_node('chat_llm',chat_llm)

graph.add_edge(START,'chat_llm')
graph.add_edge('chat_llm',END)

workflow=graph.compile(checkpointer=check_pointer)
# inital_state={'question':"what is ai/ml and how to learn the ml"}
inital_state={
    'messages':[HumanMessage(content="what is the capitl of india")]
}


if __name__ == "__main__":
    thread_id = "1"
    while True:
        user_message = input("type here ..")
        if user_message.strip().lower() in ["exit", "quit", "bye"]:
            break

        config = {"configurable": {"thread_id": thread_id}}
        response = workflow.invoke(
            {"messages": [HumanMessage(content=user_message)]},
            config=config,
        )
        print("chat bot result", response["messages"][-1].content)
# print("chat boat result ",result)