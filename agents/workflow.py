from langgraph.graph import StateGraph, END, START
import sys
from pathlib import Path
base_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(base_dir))

from agents.nodes.manager import manager_node
from agents.nodes.facebook import facebook_node, facebook_tool_node
from agents.state import State, ScraperState
from langgraph.checkpoint.memory import MemorySaver
#from agents.tools import tool_node
from typing import Literal, Any
from dotenv import load_dotenv
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode

load_dotenv()



def should_continue(state) -> Any:
    """Decide if we should continue the loop or stop based upon whether the LLM made a tool call"""

    messages = state["messages"]
    last_message = messages[-1]

    # If the LLM makes a tool call, then perform an action
    if last_message.tool_calls:
        return "tool_node"

    # Otherwise, we stop (reply to the user)
    return END

# FB Scraper subgraph workflow

@tool
def facebook_parser_tool(url: str):
    """Parses a Facebook profile and returns structured information about the user."""
    fb_graph_builder = StateGraph(ScraperState)
    fb_graph_builder.add_node("facebook_node", facebook_node)
    fb_graph_builder.add_node("tool_node", facebook_tool_node)
    fb_graph_builder.add_conditional_edges(
        "facebook_node",
        should_continue,
        ["tool_node", END]
    )
    fb_graph_builder.add_edge("tool_node", "facebook_node")
    fb_graph_builder.set_entry_point("facebook_node")
    fb_compiled_graph = fb_graph_builder.compile()
    result = fb_compiled_graph.invoke({"url": url})
    return result["messages"]

tool_node = ToolNode([facebook_parser_tool])

# Main graph workflow
memory = MemorySaver()
graph_builder = StateGraph(State)

graph_builder.add_node("manager_node", manager_node)
graph_builder.add_node("tool_node", tool_node)




graph_builder.add_edge(START, "manager_node")
graph_builder.add_conditional_edges(
    "manager_node",
    should_continue,
    ["tool_node", END]
)
graph_builder.add_edge("tool_node", "manager_node")
compiled_graph = graph_builder.compile(checkpointer=memory)


png_bytes = compiled_graph.get_graph(xray=True).draw_mermaid_png()
with open("workflow_graph.png", "wb") as f:
    f.write(png_bytes)
