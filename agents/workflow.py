from langgraph.graph import StateGraph, END, START
from agents.nodes.facebook_scrapers import facebook_login_node, facebook_scrape_node
from agents.nodes.manager import manager_node
from agents.state import State
from langgraph.checkpoint.memory import MemorySaver
from agents.tools import tool_node
from typing import Literal

memory = MemorySaver()
graph_builder = StateGraph(State)


graph_builder.add_node("manager_node", manager_node)
graph_builder.add_node("facebook_login_node", facebook_login_node)
graph_builder.add_node("facebook_scrape_node", facebook_scrape_node)
# Add tool node
graph_builder.add_node("tool_node", tool_node)

def should_continue(state: State) -> Literal["tool_node", END]:
    """Decide if we should continue the loop or stop based upon whether the LLM made a tool call"""

    messages = state["messages"]
    last_message = messages[-1]

    # If the LLM makes a tool call, then perform an action
    if last_message.tool_calls:
        return "tool_node"

    # Otherwise, we stop (reply to the user)
    return END


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

print("Graph saved as workflow_graph.png")