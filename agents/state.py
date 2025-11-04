from typing import TypedDict, Annotated
from langchain.messages import AnyMessage
import operator


# Shared State type used by nodes and the workflow
class State(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
