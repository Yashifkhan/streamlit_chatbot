# from langchain_groq import ChatGroq
# from langgraph.graph import StateGraph, START, END
# from typing import TypedDict, Literal,Annotated
# from langchain_core.messages import HumanMessage, SystemMessage,BaseMessage
# from langgraph.graph.message import add_messages
# from langgraph.checkpoint.sqlite import SqliteSaver
# from pydantic import BaseModel, Field
# from langgraph.prebuilt import ToolNode, tools_condition
# # from langchain_community.tools import DuckDuckGoSearchRun
# from langchain_community.tools import DuckDuckGoSearchRun
# from dotenv import load_dotenv
# import sqlite3
# import os
# from langchain_core.tools import tool 
# load_dotenv()

# conn=sqlite3.connect(database="chatbot.db",check_same_thread=False)

# GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# model = ChatGroq(
#     model="openai/gpt-oss-120b",
#     api_key=GROQ_API_KEY,
#     temperature=1,
#     max_tokens=1024,
# )

# class chatState(TypedDict):
#     messages:Annotated[list[BaseMessage],add_messages]
#     question:str
#     answer:str

# check_pointer=SqliteSaver(conn=conn)
# graph=StateGraph(chatState)




# # tools 
# search_tool=DuckDuckGoSearchRun(region="us-en")

# # callculater tool 
# @tool
# def calculator(
#     first_num: float,
#     second_num: float,
#     operation: str
# ) -> float:
#     """
#     Perform a basic arithmetic operation on two numbers.

#     Supported operations:
#     add, sub, mul, div
#     """

#     if operation == "add":
#         return first_num + second_num

#     elif operation == "sub":
#         return first_num - second_num

#     elif operation == "mul":
#         return first_num * second_num

#     elif operation == "div":
#         if second_num == 0:
#             raise ValueError("Division by zero is not allowed")

#         return first_num / second_num

#     else:
#         raise ValueError(
#             f"Unsupported operation: {operation}"
#         )

# # get stock price tool 

# @tool
# def get_stock_price(symbol: str) -> str:
#     """
#     Fetch the latest stock price for a given stock symbol.
#     Example: AAPL, TSLA
#     """
#     return f"Stock price data for {symbol}"

# # make tool list 
# tool_list=[get_stock_price,search_tool,calculator]
# # tool bind with llm 
# llm_with_tool=model.bind_tools(tool_list)


# # def chat_llm(state:chatState):
# #     # prompt=f"you are a helpfull assistant,give the answer of user qustion {state['question']} "
# #     messages=state['messages']
# #     result=model.invoke(messages)
# #     return {'messages':[result]}

# def chat_llm(state: chatState):
#     messages = state["messages"]
#     result = llm_with_tool.invoke(messages)
#     return {"messages": [result]}
    
# tool_node=ToolNode(tool_list)
# graph.add_node('chat_llm',chat_llm)

# graph.add_edge(START,'chat_llm')
# graph.add_node("tool_node", tool_node)
# graph.add_edge('chat_llm',END)

# workflow=graph.compile(checkpointer=check_pointer)
# # inital_state={'question':"what is ai/ml and how to learn the ml"}
# inital_state={
#     'messages':[HumanMessage(content="what is the capitl of india")]
# }


# if __name__ == "__main__":
#     thread_id = "1"
#     while True:
#         user_message = input("type here ..")
#         if user_message.strip().lower() in ["exit", "quit", "bye"]:
#             break

#         config = {"configurable": {"thread_id": thread_id}}
#         response = workflow.invoke(
#             {"messages": [HumanMessage(content=user_message)]},
#             config=config,
#         )
#         print("chat bot result", response["messages"][-1].content)
# # print("chat boat result ",result)


from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import HumanMessage, BaseMessage
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
from dotenv import load_dotenv
import sqlite3
import os

load_dotenv()

conn = sqlite3.connect(database="chatbot.db", check_same_thread=False)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

model = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=GROQ_API_KEY,
    temperature=0.2,          # FIX: lowered from 1 -> more reliable tool-calling
    max_tokens=1024,
)


class chatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    question: str
    answer: str


check_pointer = SqliteSaver(conn=conn)
graph = StateGraph(chatState)


# ---------- tools ----------
search_tool = DuckDuckGoSearchRun(region="us-en")


@tool
def calculator(first_num: float, second_num: float, operation: str) -> float:
    """
    Perform a basic arithmetic operation on two numbers.
    Supported operations: add, sub, mul, div
    """
    if operation == "add":
        return first_num + second_num
    elif operation == "sub":
        return first_num - second_num
    elif operation == "mul":
        return first_num * second_num
    elif operation == "div":
        if second_num == 0:
            raise ValueError("Division by zero is not allowed")
        return first_num / second_num
    else:
        raise ValueError(f"Unsupported operation: {operation}")


@tool
def get_stock_price(symbol: str) -> str:
    """
    Fetch the latest stock price for a given stock symbol.
    Example: AAPL, TSLA
    """
    return f"Stock price data for {symbol}"


tool_list = [get_stock_price, search_tool, calculator]

# tool bind with llm
llm_with_tool = model.bind_tools(tool_list)


def chat_llm(state: chatState):
    messages = state["messages"]
    result = llm_with_tool.invoke(messages)
    return {"messages": [result]}


tool_node = ToolNode(tool_list)

# ---------- graph wiring (THE ACTUAL FIX) ----------
graph.add_node("chat_llm", chat_llm)
graph.add_node("tool_node", tool_node)

graph.add_edge(START, "chat_llm")

# conditional edge: agar tool_calls hain -> tool_node, warna -> END
graph.add_conditional_edges(
    "chat_llm",
    tools_condition,
    {
        "tools": "tool_node",
        "__end__": END,
    },
)

# tool run hone ke baad result wapas LLM ko bhejo
graph.add_edge("tool_node", "chat_llm")

workflow = graph.compile(checkpointer=check_pointer)


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