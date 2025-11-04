import gradio as gr
from agents.workflow import compiled_graph
from typing import List
from langchain_core.messages import HumanMessage, AIMessage

config = {"configurable": {"thread_id": "1"}}

def respond(user_input: str, history):
    #history.append({"role": "user", "content": user_input})
    result = compiled_graph.invoke({
        "messages": [HumanMessage(content=user_input)] 
    }, config=config)

    return result["messages"][-1].content
    # history.append({"role": "assistant", "content": assistant_msg.content})
    # return history, history


demo = gr.ChatInterface(fn=respond)

if __name__ == "__main__":
    demo.launch()