import os
import sys
from pathlib import Path
base_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(base_dir))


import logging
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from agents.state import State
from langchain_core.messages import SystemMessage, AIMessage


load_dotenv()
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)

def email_node(state: State):
    system_prompt = """
    Write a complete, short, high-converting marketing email.
    The email must include:

    1. Subject line – highly clickable, curiosity-driven or benefit-driven.
    2. Preheader – one short sentence encouraging the open.
    3. Email body – dynamic, concise, easy to read, based on:
    - AIDA
    - PAS
    - benefit-driven language
    - emotions, specifics, curiosity
    - no fluff, no jargon

    MOST IMPORTANT USE DATA PROVIDED TO MAKE THE EMAIL AS RELEVANT AS POSSIBLE.
    YOU MUST USE SOME OF THE KEY INSIGHTS GATHERED FROM THE SCRAPED PROFILES

    Requirements:
    - The email must be light, brief, conversion-oriented, and skimmable.
    - Adapt the tone and style to my target audience.
    - Avoid long paragraphs (max 2–3 sentences each).
    - The entire message should increase the likelihood of clicking by building curiosity, emotion, or gentle urgency (light FOMO without aggression).

    Input data:
    Product/service: Selling protein supplements.
    Primary customer problem: Finding effective and affordable protein supplements to support muscle growth and recovery.
    Campaign goal: Drive sales through a limited-time discount offer.
    Additional context: Link to shop is https://exampleshop.com/proteins, 20% off with code MUSCLE20.

    Using these inputs, generate the final, ready-to-send marketing email.
    """

    transcript_messages = state["messages"][-1]
    print(transcript_messages)

    # Build LLM input: system prompt + transcript
    llm_messages = [SystemMessage(content=system_prompt)] + [transcript_messages]

    # Call LLM
    email_draft = llm.invoke(llm_messages)

    # Save generated email text into the state for later use (optional)
    state["email_draft"] = email_draft.content

    # Print for debugging
    print("\n===== EMAIL AGENT OUTPUT =====\n")
    print(email_draft)
    print(email_draft.content)
    print("\n================================\n")

    # Return the email back into the graph as the assistant message
    return {
        "messages": [AIMessage(content=email_draft.content)]
    }


if __name__ == "__main__":
    email_node()