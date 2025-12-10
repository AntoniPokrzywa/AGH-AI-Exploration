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

    Requirements:
    - The email must be light, brief, conversion-oriented, and skimmable.
    - Adapt the tone and style to my target audience.
    - Avoid long paragraphs (max 2–3 sentences each).
    - The entire message should increase the likelihood of clicking by building curiosity, emotion, or gentle urgency (light FOMO without aggression).
    - Try to generate an email that looks like it was written by a friend recommending something useful, not a sales pitch.

    Here you have list of possible products to promote:

    1. Product/service: Selling protein supplements.
    - Primary customer problem: Finding effective and affordable protein supplements to support muscle growth and recovery.
    - Campaign goal: Drive sales through a limited-time discount offer.
    - Additional context: Link to shop is https://exampleshop.com/proteins, 20% off with code MUSCLE20.

    2. Product/service: Electric scooter for daily commuting.
    - Primary customer problem: Wasting time in traffic and relying on crowded public transport.
    - Campaign goal: Encourage customers to switch to fast, eco-friendly urban mobility using a limited-time promo.
    - Additional context: Link to shop is https://exampleshop.com/scooter, 15% off with code RIDE15.

    3. Product/service: High-capacity air fryer for healthy cooking.
    - Primary customer problem: Wanting to cook tasty meals quickly without excess oil or complicated recipes.
    - Campaign goal: Boost sales by highlighting health benefits and time savings.
    - Additional context: Link to shop is https://exampleshop.com/airfryer, 25% off with code CRISPY25.

    4. Product/service: Ergonomic everyday backpack.
    - Primary customer problem: Need for a lightweight, spacious, and comfortable backpack for work, school, or short trips.
    - Campaign goal: Increase sales by highlighting comfort, durability, and versatility.
    - Additional context: Link to shop is https://exampleshop.com/backpack, 15% off with code PACK15.

    5. Product/service: Smartwatch for daily productivity and fitness.
    - Primary customer problem: Lack of motivation for physical activity and difficulty organizing the day without smart notifications.
    - Campaign goal: Encourage smartwatch purchase as a tool for improving health, productivity, and convenience.
    - Additional context: Link to shop is https://exampleshop.com/smartwatch, 20% off with code SMART20.

    6. Product/service: Best-selling self-improvement book.
    - Primary customer problem: Desire to improve habits, motivation, or productivity, but lack of a proven roadmap.
    - Campaign goal: Boost sales by showing concrete change the book brings to the reader's life.
    - Additional context: Link to shop is https://exampleshop.com/book, 10% off with code READ10.

    7. Product/service: Wireless noise-cancelling headphones.
    - Primary customer problem: Difficulty focusing due to noise and poor sound quality from cheap headphones.
    - Campaign goal: Encourage customers to upgrade to better sound and comfort through a limited-time promotion.
    - Additional context: Link to shop is https://exampleshop.com/headphones, 25% off with code SOUND25.

    Please choose the most relevant product/service based on the client's profile and interests.
    Using these inputs, generate the final, ready-to-send marketing email.
    PREFER TO NOT CREATE EMAIL IF USER IS NOT 100% RELEVANT.
    THINGS LIKE CITY ARE NOT RELEVANT.
    IF YOU ARE NOT SURE WHICH PRODUCT TO PROMOTE, DO NOT CREATE EMAIL.
    FOR WRONG PREDICTION YOU WILL BE PENALIZED WITH 50 points.
    """
    transcript_messages = state["messages"][-1]
    print(transcript_messages)
    with open("file.txt", 'a') as f:
        # write only the AIMessage text (fall back to str if no .content)
        text = getattr(transcript_messages, "content", None)
        if text is None:
            text = str(transcript_messages)
        f.write(text.rstrip() + "\n")
    

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