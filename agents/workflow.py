from langgraph.graph import StateGraph, END, START
import sys
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(base_dir))

from agents.nodes.manager import manager_node
from agents.nodes.facebook import facebook_node, facebook_tool_node
from agents.nodes.instagram import instagram_node, instagram_tool_node
from agents.nodes.email import email_node
from agents.state import State, ScraperState
from langgraph.checkpoint.memory import MemorySaver

# from agents.tools import tool_node
from typing import Literal, Any
from dotenv import load_dotenv
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode

load_dotenv()


def should_continue(state) -> Any:
    messages = state["messages"]
    last_message = messages[-1]

    # 1. Manager wants to call a tool → go to tool_node
    if last_message.tool_calls:
        return "tool_node"

    # 2. Manager finished scraping → go to email agent
    if state.get("ready_for_email") is True:
        return "email_node"

    # 3. Otherwise just answer to user normally
    return END


# FB Scraper subgraph workflow


@tool
def facebook_parser_tool(url: str):
    """Parses a Facebook profile and returns structured information about the user."""
    fb_graph_builder = StateGraph(ScraperState)
    fb_graph_builder.add_node("facebook_node", facebook_node)
    fb_graph_builder.add_node("tool_node", facebook_tool_node)
    fb_graph_builder.add_conditional_edges(
        "facebook_node", should_continue, ["tool_node", END]
    )
    fb_graph_builder.add_edge("tool_node", "facebook_node")
    fb_graph_builder.set_entry_point("facebook_node")
    fb_compiled_graph = fb_graph_builder.compile()
    result = fb_compiled_graph.invoke({"url": url})
    return result["messages"]


@tool
def instagram_parser_tool(url: str):
    """Parses an Instagram profile and returns structured information about the user."""
    ig_graph_builder = StateGraph(ScraperState)
    ig_graph_builder.add_node("instagram_node", instagram_node)
    ig_graph_builder.add_node("tool_node", instagram_tool_node)
    ig_graph_builder.add_conditional_edges(
        "instagram_node", should_continue, ["tool_node", END]
    )
    ig_graph_builder.add_edge("tool_node", "instagram_node")
    ig_graph_builder.set_entry_point("instagram_node")
    ig_compiled_graph = ig_graph_builder.compile()
    result = ig_compiled_graph.invoke({"url": url})
    return result["messages"]


tool_node = ToolNode([facebook_parser_tool, instagram_parser_tool])


# Main graph workflow
memory = MemorySaver()
graph_builder = StateGraph(State)

graph_builder.add_node("manager_node", manager_node)
graph_builder.add_node("tool_node", tool_node)
graph_builder.add_node("email_node", email_node)


graph_builder.add_edge(START, "manager_node")
graph_builder.add_conditional_edges(
    "manager_node",
    should_continue,
    ["tool_node", "email_node", END]
)

graph_builder.add_edge("tool_node", "manager_node")
graph_builder.add_edge("email_node", END)
compiled_graph = graph_builder.compile(checkpointer=memory)


png_bytes = compiled_graph.get_graph(xray=True).draw_mermaid_png()
with open("workflow_graph.png", "wb") as f:
    f.write(png_bytes)
