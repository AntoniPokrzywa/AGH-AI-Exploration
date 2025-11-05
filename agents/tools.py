from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode

@tool
def facebook_parser_tool(url: str):
    """Parses a Facebook profile and returns structured information about the user."""
    
    return f"""
    
    Name: Miś Puchatek
    Username: @MiodowyMisKrakow
    Bio: "A bear of very little brain, but a very big appetite. Just looking for 'Małe Co Nieco'. 🍯"
    Location: Stumilowy Las, near Kraków, Poland
    Friends: Prosiaczek, Kłapouchy, Tygrys, Królik, Krzyś A., Sowa Przemądrzała, Kangurzyca, Maleństwo
    Relationship Status: It's complicated (with Honey)
    Sport Clubs (Follows): KS Cracovia (Likes the stripes!)
    Hobbies: Napping, Visiting friends, Tree climbing (for specific reasons), Composing "Mruczanki" (Hums)
    Liked Pages: "Bar Mleczny 'Pod Baryłką'", "Pasieka 'Złoty Ul'", "Krakowskie Błonia (Perfect for Naps)"
    recent posts: {url}
    
    """

@tool
def instagram_parser_tool(url: str):
    """Parses a Instagram profile and returns structured information about the user."""

    return """
    Username: @KubuśPuchatek
    Full Name: Kubuś Puchatek
    Bio: "Just a friendly bear who loves honey and adventures in the Hundred Acre Wood. 🍯🐻"
    Website: www.hundredacrewood.com
    Followers: 1.2M
    Following: 150
    Posts: 345
    Recent Posts:
    1. Photo of a honey pot with the caption "Can't resist the sweet stuff! 🍯 #HoneyLover"
    2. Video of a walk in the woods with friends, captioned "Exploring the Hundred Acre Wood with my pals! 🌳  🐾
    """

@tool
def linkedin_parser_tool(url: str):
    """Parses a LinkedIn profile and returns structured information about the user."""

    return """
    Name: Kubuś Puchatek
    Current Position: Chief Honey Officer at Hundred Acre Wood Enterprises
    Location: Stumilowy Las, Poland
    Summary: Experienced bear with a passion for honey and friendship. Skilled in problem-solving and team collaboration.
    Experience:
    - Chief Honey Officer, Hundred Acre Wood Enterprises (2015-Present)
    - Assistant to the Regional Manager, Hundred Acre Wood Enterprises (2010-2015)
    Education:
    - Bachelor of Arts in Friendship Studies, University of the Hundred Acre Wood (2006-2010)
    Skills: Team Leadership, Problem Solving, Honey Tasting, Friendship Building
    """

# Put all your tools in a list
tools = [facebook_parser_tool, instagram_parser_tool, linkedin_parser_tool]

# Create the single, smart tool node
tool_node = ToolNode(tools)