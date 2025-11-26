from typing import TypedDict, Annotated, NotRequired
from langchain_core.messages import AnyMessage
import operator


# Shared State type used by nodes and the workflow
class State(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    ready_for_email: NotRequired[bool]
    email_draft: NotRequired[str]
    
class ScraperState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    url: str
    status: str | None
