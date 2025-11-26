import gradio as gr
from agents.workflow import compiled_graph
from typing import List
from langchain_core.messages import HumanMessage, AIMessage

config = {"configurable": {"thread_id": "1"}}

def respond(user_input: str, history: List[List[str]]):
    # Convert Gradio history → LangChain messages
    messages = []
    for user, assistant in history:
        messages.append(HumanMessage(content=user))
        messages.append(AIMessage(content=assistant))

    # Add the new user message
    messages.append(HumanMessage(content=user_input))

    # Invoke LangGraph with *full* message list
    result = compiled_graph.invoke(
        {"messages": messages},
        config=config
    )

    # Assistant response is last message in the list
    assistant_reply = result["messages"][-1].content

    return assistant_reply


demo = gr.ChatInterface(fn=respond)

if __name__ == "__main__":
    demo.launch()