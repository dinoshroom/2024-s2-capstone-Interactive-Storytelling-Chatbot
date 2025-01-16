from dotenv import load_dotenv
from openai import OpenAI
import textwrap
from typing import List, Dict, Any
import ast

load_dotenv()
client = OpenAI()

story_messages: List[Dict[str, Any]] = []
char_creation_check_messages: List[Dict[str, Any]] = []
npc_creation_messages: List[Dict[str, Any]] = []


def begin_story() -> None:
    """Begins the story by appending system instructions into the ``story_messages`` array.

    :return: None
    """
    main_story_system_instructions: str = textwrap.dedent("""
        **Remember the following rules:**
        1. The story should feel like a window into an already existing world. 
           a. Make the world feel alive and dynamic by triggering random events or CONFLICTS without being prompted to by the user.
           b. Advance the plot forwards if you feel the Main Character is not doing anything noteworthy.
           c. Make the NPCs ENGAGE with the Main Character through dialogues and actions.
           d. Allow the NPCs to interact and form relationships with other NPCs.
           e. You are allowed to let the NPCs get injured and die.
        2. Present the story in a SECOND-PERSON view. The second-person should refer to the Main Character.
        3. Allow the Main Character's actions/choices to be decided by the user. Avoid providing multiple-choice options; let the user type out their choices freely.
        4. DON'T introduce new characters unless told to in the user message. When you do get told to introduce a new character to the story, remember these:
           a. When introducing new characters, assume they don't know the Main Character yet (it's their first time talking to them).
           b. DON'T use the new character names in the story until they introduce themselves to the Main Character, using a name or alias.
        5. If the user attempts an action that violates established "Rules" in the World JSON dictionary, or is impossible given the current state of the world or characters, explain why it can't be done and ask for a different action.
        6. If the Main Character want to buy something in the story, make the merchant start a discussion with them and give them the prices.
    """)
    story_messages.append(
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": main_story_system_instructions
                }
            ]
        })


def begin_char_creation(main_character: str) -> None:
    """Appends system instructions to both the NPC creation check and NPC creation arrays.
    Also adds the name of the main character to the system instructions to prevent ChatGPT from creating a dictionary for the main character.

    :param main_character: The name of the main character.
    :return: None
    """
    char_creation_check_system_instructions: str = textwrap.dedent(f"""
        **Rules:**
        - A Character JSON dictionary is only created once the ACTUAL NAME of a new character is known. If the Main Character DOESN'T know the new character's name, DON'T create a Character JSON dictionary yet.
            - The new character will introduce themselves to the Main Character by giving them their NAME, so only create a new character when an introduction is made.
        - Don't create a JSON dictionary for the Main Character, "{main_character}".
        
        **Steps:**
        1. You are given a story
        2. Read through the story and determine whether a new character's JSON dictionary needs to be created.
        3. If a JSON dictionary needs to be created, return "True" and a list of the character names that a Character JSON dictionary needs to be created for (e.g. True [“Jane”, “John”]).
        4. If no new character JSON dictionary needs to be created, return "False".
    """)
    char_creation_check_messages.append(
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": char_creation_check_system_instructions
                }
            ]
        }
    )

    npc_creation_system_instructions: str = textwrap.dedent("""
        **Remember the following rules:**
        1. You are given a story.
        2. Read through the story and create NEW Character JSON dictionaries for the characters provided in the list given to you.
        3. When creating new characters, follow the format specified below.
        4. Return NEW character JSON dictionaries ONLY.
        {
            "id": int // Unique ID for the character
            "name": str // Name of the character
            "physical_condition": str // Leave this empty
            "occupation": str // Occupation of the character, give a valid one suiting the genre and story
            "money": float // How much money the character has
            "relationship": Dict[id: str, relationship_type: str] // Leave this empty
            "personality" (3): List[str] // A list of the character's personalities
            "inventory": List[str] // A list of items a character has
            "stats": Dict[stat: str, val: int (1-100)] // Stats determine how much health a character has ("HP")
            "current_location": str // Leave this empty
            "appearance": str // The appearance of the character (including their gender)
        }
    """)
    npc_creation_messages.append(
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": npc_creation_system_instructions
                }
            ]
        }
    )


def get_response(messages: List[Dict[str, Any]]) -> str:
    """Sends a list of messages to the OpenAI API and retrieves the response.

    :param messages: A list of message dictionaries, where each dictionary
                     contains keys like 'role' (e.g., 'system', 'user', 'assistant')
                     and 'content' (the actual message text).
    :return: A string containing the response from the GPT-4o-mini API based on the
             input messages.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=1,
        max_tokens=1400,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={
            "type": "text"
        }
    )
    return response.choices[0].message.content


def append_user_msg(message: str, messages_array: List[Dict[str, Any]]) -> None:
    """Appends a new user message to the messages array.

    :param message: The content of the user's message as a string.
                        This is the text that the user is contributing to the conversation.
    :param messages_array: A list of dictionaries that stores the conversation history.
                               Each dictionary in the list contains information such as
                               the message's role (user or assistant) and the message content.
    :return: None
    """
    messages_array.append(
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": message
                }
            ]
        }
    )


def append_assistant_msg(message: str, messages_array: List[Dict[str, Any]]) -> None:
    """Appends a new assistant message to the messages array.

    :param message: The content of the assistant's message as a string.
                    This is the response generated by the assistant.
    :param messages_array: A list of dictionaries that stores the conversation history.
                           Each dictionary in the list contains the role of the message
                           (e.g., user or assistant) and the message content.
    :return: None
    """
    messages_array.append(
        {
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": message
                }
            ]
        }
    )


def get_story(prompt: str) -> str:
    """Generates a story when given a prompt by interacting with the OpenAI API. Appends the
    resulting story to the story array to keep it going.

    :param prompt: A string containing the initial prompt that the user wants to use to generate the story.
    :return: A string of the generated story. The function uses the prompt to initiate the conversation
            and fetch a response from the API.
    """
    story: str = ""
    append_user_msg(prompt, story_messages)
    response: str = get_response(story_messages)
    story += response
    append_assistant_msg(response, story_messages)
    return story


def npc_creation_check(story: str, current_char_names: list[str]) -> tuple[bool, List[str]]:
    """Passes a story to ChatGPT and determines whether an NPC should be created.
    Also passes a list of character names so ChatGPT won't create characters that have already been created.
    Appends ChatGPT's response to NPC character check array to keep it going.

    :param story: A string of the current story.
    :param current_char_names: A list of character names, used to prevent duplicate characters from being created.
    :return: A tuple, where the first value determines if new character should be created (True), and the second value
            is a list of characters that needs to be created.
    """
    prompt = textwrap.dedent(f"""
        {story}
        - REMEMBER a Character JSON dictionary is only created once the REAL NAME of a new character is known.
        - DO NOT create JSON dictionaries for the characters provided in the list given to you.
        {current_char_names}
    """)

    append_user_msg(prompt, char_creation_check_messages)
    response: str = get_response(char_creation_check_messages)
    append_assistant_msg(response, char_creation_check_messages)

    response_list: list[str] = response.split(" ", 1)
    boolean_val: bool = response_list[0] == "True"

    if len(response_list) == 1:
        character_list = []
    else:
        # ChatGPT sometimes returns values with "“" and "”", so we need to get rid of it if it exists in the string.
        char_list_str: str = response_list[1].replace("“", '"').replace("”", '"')
        character_list = ast.literal_eval(char_list_str)

    return boolean_val, character_list


def create_npc(char_list: List[str], story: str, genre: str, char_id: int) -> str:
    """Generates NPC Character JSON dictionaries for a list of given characters names.

        **Note:** It is recommended to call the ``npc_creation_check`` function before using
        this function to get the name of characters that need a JSON dictionary created.

        :param char_list: A list of character names that needs a JSON dictionary to be created.
        :param story: A string representing the story where these characters first appear.
                      This provides context for the characters and helps generate fitting NPCs.
        :param genre: A string representing the genre of the story (e.g., fantasy, sci-fi, mystery).
                      This helps the system align the characters' attributes with the story's setting.
        :param char_id: An integer representing the starting ID for the characters. Each
                        character will be assigned a unique ID by incrementing this value.
        :return: A string response containing the generated JSON dictionaries for the characters,
                 tailored to the given story and genre.
    """
    char_tuple_list = []
    for char in char_list:
        char_tuple_list.append({"Name": char, "ID": char_id})
        char_id += 1
    prompt: str = textwrap.dedent(f"""
        Create new Character JSON dictionaries for the following characters: {char_tuple_list}. The "{genre}" story where the character first appears is given below:
        {story}
    """)
    append_user_msg(prompt, npc_creation_messages)
    response: str = get_response(npc_creation_messages)
    append_assistant_msg(response, npc_creation_messages)
    return response


def get_rules(prompt: str) -> str:
    """Interacts with GPT-4o-mini to get a set of rules about a world when provided with a prompt.

    :param prompt: A string to be passed into ChatGPT
    :return: A string containing a list of rules.
    """
    system_instructions: str = textwrap.dedent(
        """
        Generate concise and unbreakable rules for a given story genre. The input will be a specific story genre, and the output should consist of 3 to 5 rules that guide the entire storyline within that genre.

        # Steps
        
        1. Identify the core elements and themes common to the specified genre.
        2. Determine the essential structural or thematic rules that stories in this genre typically adhere to.
        3. Formulate concise and clear rules, ensuring they serve as strict guidelines for the story’s development.
        4. Ensure each rule is fundamental to preserving the genre's integrity.
        
        # Output Format
        
        - Provide 3 to 5 rules as a list.
        - Each rule should be a single, complete sentence.
        - Ensure rules are general yet strict enough to guide any storyline in the specified genre.
        
        # Examples
        
        **Input:** Fantasy
        
        **Output:**
        - Magic must be a consistent and integral part of the world.
        - The hero must embark on a quest of great significance.
        - The world should feature mythical creatures and alternate realities.
        - Good and evil forces are clearly delineated.
        - The storyline must conclude with a hero achieving a transformative resolution.
        
        **Input:** Mystery
        
        **Output:**
        - There must be a central, complex puzzle or crime.
        - The detective must be methodical and clever.
        - Clues should be presented logically throughout the story.
        - The final revelation must be both surprising and logical.
        - The story should maintain suspense until the end. 
        
        # Notes
        
        - Ensure rules are applicable to any storyline within the genre.
        - Rules should encourage creativity while providing concrete boundaries.
        """
    )
    rules_messages = [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": system_instructions
                }
            ]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                }
            ]
        }
    ]

    # Make the API call to OpenAI
    response: str = get_response(rules_messages)

    # Extract and return the rules from the response
    return response


def get_environment(genre: str):
    """Interacts with GPT-4o-mini to describe the environment about a world when provided with a prompt.

    :param genre: The genre of the world.
    :return: A sentence describing the environment of the world.
    """
    system_instructions: str = textwrap.dedent(
        """
        Generate a one-sentence description of an environment based on a given genre.

        # Steps
        
        1. Identify the distinctive features and typical settings associated with the provided genre.
        2. Combine these features to create a vivid and concise depiction of an environment representative of the genre.
        
        # Output Format
        
        A single sentence that effectively describes the environment related to the given genre.
        
        # Examples
        
        **Input:** Fantasy  
        **Output:** In the heart of the enchanted forest, towering trees with luminescent leaves whisper secrets older than time itself.
        
        **Input:** Science Fiction  
        **Output:** Within the sleek, metallic corridors of the space station, stars glitter through panoramic windows, watching over the galaxy's last refuge.
        """
    )
    environment_messages = [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": system_instructions
                }
            ]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": genre
                }
            ]
        }
    ]
    # Make the API call to OpenAI
    response: str = get_response(environment_messages)

    # Extract and return the rules from the response
    return response


def check_condition(current_condition: str, status: str) -> str:
    """Determines whether a character's current condition is positive or negative, and then returns an updated
    condition. Note that this function does not save the history of ChatGPT's response, it starts a new chat
    every time this function is called.

    :param current_condition: A string that represents a character's current condition.
    :param status: A string that determines whether a positive or negative condition should be returned.
    :return: A string of the character's new condition.
            - If the condition is negative, and the status is "positive", the function will return a new
            "positive" condition.
            - If the condition is positive, and the status is "negative", the function will return a new
            "negative" condition.
            - If the condition is negative, and the status is "negative", the function will return a "False" string.
            - If the condition is positive, and the status is "positive", the function will return a "False" string.
    """
    messages = []
    system_instructions: str = textwrap.dedent("""
    **Steps:**
    
    1. You will be given the current physical condition of a character.
    2. Determine whether the condition is a positive one or a negative one.
        a. If it is a negative condition. Return a new positive condition ONLY.
        b. If it is a positive condition. Return "False" ONLY.
            i. If the condition indicates the character is dead. Return "False" ONLY
    """)
    if status == "negative":
        system_instructions: str = textwrap.dedent("""
            **Steps:**

            1. You will be given the current physical condition of a character.
            2. Determine whether the condition is a positive one or a negative one.
                a. If it is a negative condition. Return "False" ONLY.
                b. If it is a positive condition. Return a random negative condition ONLY.
                    i. If the condition indicates the character is dead. Return "False" ONLY
        """)

    messages.extend(
        [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": system_instructions
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": current_condition
                    }
                ]
            }
        ]
    )

    response: str = get_response(messages)
    return response


def get_new_relationship(relationship: str, status: str) -> str:
    """Updates the relationship between the main character and another character.
    The ``status`` parameter determines whether the relationship is deepened (positive) or soured (negative) as a result of the event.
    Note that this function does not save the response of ChatGPT, it starts a new chat every time this function is called.

    :param relationship: A string that describes the current relationship between the main character and another character.
    :param status: A string that instructs ChatGPT whether to sour or deepen the relationship based on the event.
                   - ``positive``: Deepens the relationship and updates it to something more positive.
                   - ``negative``: Sours the relationship and updates it to something more negative.
    :return: A string representing the updated relationship.
    """
    messages = []
    system_instruction: str = textwrap.dedent("""
    **Steps:**

    1. You will be given a string that represents a relationship the main character has with another character. 
    2. The relationship has been deepened due to an event.
    2. Please update the relationship to something positive.
    3. Return ONLY the updated relationship.

    """)
    if status == "negative":
        system_instruction = textwrap.dedent("""
        **Steps:**
        
        1. You will be given a string that represents a relationship the main character has with another character.
        2. The relationship has been soured due to an event.
        3. Please update the relationship to something negative.
        4. Return ONLY the updated relationship.
        """)

    messages.extend(
        [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": system_instruction
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": relationship
                    }
                ]
            }
        ]
    )

    response: str = get_response(messages)
    return response


def get_new_item(world_dict: str) -> str:
    """
    Generates a useful item that could exist within the world described by a given JSON dictionary.
    The item is based on the context of the world and is intended to be something useful for the story's progression.

    :param world_dict: A JSON string that represents the story's world.
                       This provides the necessary context for generating an item that fits within the world.

    :return: A string representing the name of a useful item that exists in the world. Only the name of the item is returned.
    """
    messages = []
    system_instruction: str = textwrap.dedent("""
    **Steps:**
    
    1. You will be given a JSON dictionary that represents what the world of a story is like.
    2. Please generate a useful item that you might find in the world.
    3. Return ONLY the name of the item.
    
    """)
    prompt: str = textwrap.dedent(f"""
    **World JSON Dictionary**
    {world_dict}
    """)

    messages.extend(
        [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": system_instruction
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
    )
    response: str = get_response(messages)
    return response


def get_history() -> List[Dict[str, Any]]:
    """Fetches ``story_messages``, which contains the history of the chat with ChatGPT.
    This function is specifically used for saving the game.

    :return: A list of dictionaries containing the story messages generated by ChatGPT.
    """
    return story_messages


def set_history(history: List[Dict[str, Any]]) -> None:
    """Sets the history of the chat with a new chat.
    This function should only be used when a new save is loaded.

    :param history: A new list of dictionaries containing story messages.
    :return: None
    """
    global story_messages
    story_messages = history
