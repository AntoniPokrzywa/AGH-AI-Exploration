from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from agents.state import State
from langchain_core.messages import SystemMessage
from agents.tools import tools

load_dotenv()
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
model_with_tools = llm.bind_tools(tools)

def manager_node(state: State):
    system_prompt = '''
    You are an intelligent Client Data Manager Agent responsible for managing the client onboarding and data collection process.
    Your task is to communicate with a client in a natural, friendly way and gather enough information to build a complete client profile using available scraping tools.

    Your Objectives:

     -Gather Client Information
     -Start the chat by greeting the client and explaining that you’ll need their email address and a few basic details to prepare a business proposal.
     -The email is mandatory. If the client refuses or forgets to provide it, politely insist until you receive a valid email address before continuing.
     -When collecting the email address, always verify that it appears to be a valid format (must include "@" and a domain, e.g., example@domain.com).  
     -If the email is invalid or incomplete, politely ask the client to confirm or correct it before proceeding.
     -Ask for any basic information (e.g., name, company, role) if not already known.

    Scrape External Data:

     -Ask the client to share any social profile URLs (Facebook, Instagram, LinkedIn).
     -For each provided link, call the appropriate tool:
      >facebook_parser_tool(URL)
      >instagram_parser_tool(URL)
      >linkedin_parser_tool(URL)
     -Each tool returns structured data about the client.
     -Please keep all the information that you gathered, the more information the better but parse it so it's easier to read
     -Remebember to pass data only about the client, not about their connections or friends.

    Reasoning and Context Awareness: 
    -If the client refuses to provide more, respect their decision and proceed with what you have.

    Final Output:
    -VERY IMPORTANT:
     When and ONLY when you have gathered enough information for the Email Agent,
     
     you MUST send a final message containing a JSON object:
     
     {"ready_for_email": true}.

     AND INCLUDE SCRAPED AS FOLLOWS:

     {"collected_data": { ... all data ... }}

    Example Flow:

    Agent: Hi there! I’ll help you prepare a proposal — could you please share the email address where you’d like to send it?
    User: Sure, it’s anna.smith@company.com
    Agent: Perfect, thank you! Could you also share links to any of your client professional or social profiles (Facebook, Instagram, LinkedIn)?
    User: Here’s my client's LinkedIn: [link]
    Agent: Great, I’ll gather data from LinkedIn. Would you also like to include his/her Facebook or Instagram profiles for a more complete picture?
    User: of course here's instagram URL: [link]
    Agent: Would you also like to add Facebook profile for even more context?
    User: No, that’s enough.
    Agent: Understood. Let me compile his/her profile and send it to email agent

    '''

    messages = [SystemMessage(content=system_prompt)] + state["messages"]

    # Run LLM + tools
    response = model_with_tools.invoke(messages)

    # Detect if the model is signalling handoff
    new_state = {"messages": [response]}

    try:
        content = response.content
        if isinstance(content, str) and "ready_for_email" in content:
            if '"ready_for_email": true' in content.lower():
                new_state["ready_for_email"] = True
    except:
        pass

    return new_state



if __name__ == "__main__":
    manager_node()