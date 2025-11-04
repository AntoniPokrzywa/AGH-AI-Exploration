from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os
from agents.state import State
from langchain_core.messages import HumanMessage, AIMessage
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
from agents.tools import tools

model_with_tools = llm.bind_tools(tools)
load_dotenv()

#@tool
def facebook_sraper():
    pass

def manager_node(state: State):
    # Dopytac o maila, naleganie o niego 
    # Powiedziec jakich tooli moze uzywac i kiedy 
    messages = state["messages"] 
    response = model_with_tools.invoke(messages)
    return {"messages": [response]}
    #return state



if __name__ == "__main__":
    manager_node()