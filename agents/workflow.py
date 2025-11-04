from langgraph.graph import StateGraph, END, START
from agents.nodes.facebook_scrapers import facebook_login_node, facebook_scrape_node
from agents.nodes.manager import manager_node
from agents.state import State
from langgraph.checkpoint.memory import MemorySaver
from agents.tools import tool_node

memory = MemorySaver()
graph_builder = StateGraph(State)


graph_builder.add_node("manager_node", manager_node)
graph_builder.add_node("facebook_login_node", facebook_login_node)
graph_builder.add_node("facebook_scrape_node", facebook_scrape_node)
# Add tool node
graph_builder.add_node("tool_node", tool_node)

def should_continue(state: State) -> str:
    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        # The LLM wants to run a tool
        return "tool_node"
    else:
        # The LLM has given a final answer
        return "end"

graph_builder.add_conditional_edges(
    "manager_node",  # The node to branch FROM
    should_continue, # The function that decides WHERE to go
    {
        # The mapping: "return_value_from_function": "destination_node_name"
        "tool_node": "tool_node",
        "end": END
    }
)
# graph_builder.add_edge("facebook_login_node", "facebook_scrape_node")
graph_builder.add_edge(START, "manager_node")
graph_builder.add_edge("manager_node", END)

compiled_graph = graph_builder.compile(checkpointer=memory)
png_bytes = compiled_graph.get_graph(xray=True).draw_mermaid_png()
with open("workflow_graph.png", "wb") as f:
    f.write(png_bytes)

print("Graph saved as workflow_graph.png")