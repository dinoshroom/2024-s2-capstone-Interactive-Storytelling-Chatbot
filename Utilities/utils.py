import os
import json
import random
import textwrap
from typing import Dict, TypeVar, List, Optional
import pygame
from Utilities import update_attr

V = TypeVar("V")
count = 1


def get_character_details(char_info) -> Dict[str, V]:
    """Formats the main character details into the correct format in preparation for
    creating a Character object. Adds the missing information, such as the id, relationship,
    and current_location.

    :param char_info: Information of the main character.
                      Information includes the name, physical_condition, occupation,
                      money, inventory, personality, stats, and appearance.
    :return: All the main character details.
    """
    char_details: Dict[str, V] = {"id": 1,
                                  "name": char_info[0],
                                  "physical_condition": char_info[1],
                                  "occupation": char_info[2],
                                  "money": round(float(char_info[5]), 2),
                                  "relationship": {}}

    inventory = char_info[3]
    if inventory != "":
        inventory = [item.strip() for item in inventory.split(",") if
                     item.strip()]  # Split by commas and strip whitespace
    else:
        inventory = []
    char_details["inventory"] = inventory  # Store the inventory in char_details

    personality = char_info[4]
    personality = [trait.strip() for trait in personality.split(",") if trait.strip()] # Split by commas and strip whitespace
    char_details["personality"] = personality  # Store the personality in char_details

    stats: Dict[str, int] = {"HP": int(char_info[6]), "LUCK": int(char_info[7]), "CHA": int(char_info[8])}
    char_details["stats"] = stats
    char_details["current_location"] = ""
    char_details["appearance"] = char_info[9]

    return char_details


def get_world_details(world_info) -> Dict[str, V]:
    """Formats the world details into the correct format in preparation for
    creating a World object. Adds the missing information, which is only the locations.

    :param world_info: Information of the world.
                       Information includes the genre, rules and environment.
    :return: All the world details.
    """
    world_details: Dict[str, V] = {"genre": world_info[0]}

    rules = world_info[1]
    if rules != "":
        rules = [item.strip() for item in rules.split(",") if
                 item.strip()]  # Split by commas and strip whitespace
    else:
        rules = []
    world_details["rules"] = rules

    world_details["environment"] = world_info[2]
    world_details["locations"] = []

    return world_details


def get_prompt(genre: str, character_name: str, character_charisma: int, is_starting_prompt: bool, **details) -> str:
    """Fetches the starting or continuation prompt.

    This function generates either the starting prompt or a continuation prompt for an interactive story
    based on the genre, character, and various story details. It dynamically incorporates provided
    information such as character, world, and timeline JSON strings, user inputs, character deaths, and
    random events.

    :param genre: The genre of the story.
    :param character_name: The name of the main character in the story.
    :param character_charisma: The charisma of the main character in the story.
                               The charisma is used to determine how often they meet new NPCs.
    :param is_starting_prompt: A boolean flag indicating whether to return the starting prompt (True) or
                               a continuation of the story (False).
    :param details: Additional keyword arguments:
        - json_dict_str (List[str]): A list containing the character, world, and timeline JSON strings.
        - user_input (str): The input from the user that drives the continuation of the story.
        - char_str (str): Updated character JSON string after changes.
        - new_char (bool): A boolean flag indicating whether to introduce new characters or not.
                           If there's more than five alive NPCs, stop prompting the LLM to introduce new characters (False).
                           Otherwise, introduce new characters according to the main character's charisma (True).
        - char_deceased (str): A comma-separated list of deceased characters to be incorporated into the story.
        - random_event (str): A random event to introduce naturally into the story.
    :return: The generated prompt for the story, formatted according to the provided inputs.
    """

    global count
    # count is used to determine when a character should be introduced.
    if is_starting_prompt:
        json_dict_str: List[str] = details['json_dict_str']
        characters: str = json_dict_str[0]
        world: str = json_dict_str[1]
        timeline: str = json_dict_str[2]
        prompt: str = textwrap.dedent(f"""
        **Character JSON dictionary:**
        {characters}
        **World JSON dictionary:**
        {world}
        **Timeline JSON dictionary:**
        {timeline}
        You are a storyteller. Create an interactive "{genre}" story that is in a style similar to a book and is only one paragraph that is 5 sentences long. The Main Character (ID: 1) is "{character_name}”.
        """)
    # Continuing Story Prompt
    else:
        user_input: str = details['user_input']
        char_str: str = details['char_str']
        prompt: str = textwrap.dedent(f"""
        You are a storyteller. Continue the interactive "{genre}" story that is in a style similar to a book and is only one paragraph that is 5 sentences long. The Main Character (ID: 1) is "{character_name}". This is what the user wants to do next: "{user_input}".

        """)

        try:
            char_deceased: str = details['char_deceased']
            if char_deceased is None:
                pass
            else:
                char_deceased_list: List[str] = char_deceased.split(", ")
                if len(char_deceased_list) == 1:
                    prompt += textwrap.dedent(f"""
                    A character has died in the story: {char_deceased} 
                    Please justify their death naturally in the story.
    
                    """)
                else:
                    prompt += textwrap.dedent(f"""
                    These characters have died: {char_deceased} 
                    Please justify their deaths naturally in the story.
    
                    """)
        except KeyError:
            pass

        try:
            random_event: str = details['random_event']
            if random_event is None:
                pass
            else:
                prompt += textwrap.dedent(f"""
                A random event has occurred in the story:
                {random_event} 
                Please justify this random event naturally in the story.
    
                """)
        except KeyError:
            pass

        new_char_check: bool = details['new_char']
        if count == 1 and new_char_check:
            prompt += textwrap.dedent(f"""
            Gradually introduce a new character to the story to interact with the Main Character. 
            Make the new character introduce themself with a name or alias.

            """)
            # after a new character is introduced, the count is reset
            count = 21 - character_charisma

        if new_char_check:
            # count is decremented after every continuation prompt
            count -= 1

        prompt += textwrap.dedent(f"""
        Below are the updated Character JSON dictionaries
        {char_str}
        """)

    return prompt


def get_money_message(check_valid_transaction: List[tuple[int, str]]) -> str:
    """
    Generate a message indicating that characters lack sufficient money for a transaction.

    :param check_valid_transaction: A list of tuples, each containing a character ID and name.
                                    Each tuple represents a character that does not have enough money.
    :return: A message indicating the characters that lack sufficient funds, suggesting a story regeneration.
    """
    broke_char: List[tuple[int, str]] = check_valid_transaction
    money_message: str = ""
    if len(broke_char) == 1:
        char_id: int = broke_char[0][0]
        char_name: str = broke_char[0][1]
        money_message += f"{char_name} (ID: {char_id}) doesn't have enough money to perform the transaction in the story. Please regenerate the story with the same conditions, but make {char_name} realize they don't have enough money."
    else:
        money_message += "These characters: "
        for index in range(len(broke_char)):
            char_id = broke_char[index][0]
            char_name = broke_char[index][1]
            if index == len(broke_char) - 1:
                money_message += f"{char_name} (ID: {char_id})"
            else:
                money_message += f"{char_name} (ID: {char_id}), "
        money_message += " don't have enough money to perform the transaction in the story. Please regenerate the story with the same conditions, but make the characters listed realize they don't have enough money."

    return money_message


def replace_id_with_name(input_str: str, current_char_id_list: List[int], current_char_name_list: List[str]) -> str:
    """
    Replaces character IDs in a string with their corresponding character names.

    The function searches for occurrences of "ID {id}" in the input string, where `{id}` corresponds to an integer
    from the `current_char_id_list`. Each ID is replaced by the respective character's name from the `current_char_name_list`.

    :param input_str: A string containing placeholders in the form "ID {id}".
    :param current_char_id_list: A list of character IDs (integers) that correspond to characters.
    :param current_char_name_list: A list of character names (strings) corresponding to the IDs in the same order.
    :return: A string where each "ID {id}" has been replaced with the respective character name.
    """
    for char_id, char_name in zip(current_char_id_list, current_char_name_list):
        input_str = input_str.replace(f"ID {char_id}", char_name)

    return input_str


def convert_to_json(input_string: str) -> list[dict[str, V]] | str:
    """Converts a JSON string to a JSON dictionary.
    Note that ``input_string`` must have the exact format as a JSON dictionary.
    The input string can have \`\`\`\json at the beginning and ``` at the end, as those will be automatically removed.

    :param input_string: A JSON string, has to be in the same format as a JSON dictionary
    :return: A list of dictionaries. If there are errors, returns a string instead
    """
    try:
        # Remove the ```json at the beginning and ``` at the end if present
        if input_string.startswith("```json"):
            input_string = input_string[8:-3].strip()
        elif input_string.startswith("```"):
            input_string = input_string[4:-3].strip()

        # Convert the string to a JSON object
        json_data = json.loads(input_string)

        # If the input is a single dictionary, wrap it in a list for consistency
        if isinstance(json_data, dict):
            return [json_data]
        else:
            return json_data
    except json.JSONDecodeError as e:
        return f"Error decoding JSON: {e}"


def fix_format(text: str) -> str:
    """Cleans up the formatting of an attribute update line by removing unnecessary symbols and characters.

    :param text: A string representing the character attribute update line that requires formatting adjustments.
    :return: A cleaned-up version of the update line with the unnecessary symbols and characters removed.
    """
    if "`" in text:
        text = text.replace("`", "").strip()
    if "plaintext" in text:
        text = text.replace("plaintext", "").strip()
    if '(' in text:
        text = text.replace('(', "").strip()
    if ')' in text:
        text = text.replace(')', "").strip()
    if "<" in text:
        text = text.replace("<", "").strip()
    if ">" in text:
        text = text.replace(">", "").strip()
    if "_" in text:
        text = text.replace("_", " ").strip()
    if '\\"' in text:
        text = text.replace('\\"', "").strip()
    if '\"' in text:
        text = text.replace('\"', "").strip()
    if "'" in text:
        text = text.replace("'", "").strip()
    if '"' in text:
        text = text.replace('"', "").strip()
    return text.strip()


def split_function(update: str) -> tuple[List[str], str]:
    """Splits the character attribute update line based on the operator used.

    :param update: A string representing the character attribute update line.
    :return: A tuple containing a list of strings split by the operator and the operator itself as a string.
    """
    separate_list: List[str] = update.split("+=")
    if len(separate_list) != 1:
        symbol: str = "+="
    else:
        separate_list = update.split("-=")
        symbol = "-="
    return separate_list, symbol


async def requery_updates_relationship(story: str, char_dicts: str, update: str, char_id: str, other_char_id: str,
                                       id_list: List[int], name_list: List[str]) -> tuple[int, int, bool]:
    """Fixes the format of the relationship update line by matching character names to their corresponding IDs,
    or requerying until the format is corrected.

    This function checks if the `char_id` and `other_char_id` provided are valid IDs or names. If they are names, it
    attempts to match them with the corresponding IDs from the `id_list`. If the IDs cannot be matched, the function
    will requery the update until the format is corrected.

    :param story: A string of the 3 most recent story events.
    :param char_dicts: A JSON-like string representation, containing each character's ID, name and relationships.
    :param update: A string representing the relationship attribute update line for a character.
    :param char_id: The character's ID or name.
    :param other_char_id: The ID or name of the other character involved in the relationship.
    :param id_list: A list containing the IDs of all characters.
    :param name_list: A list containing the names of all characters.
    :return: A tuple containing the fixed `char_id` and `other_char_id` as integers and the update_succeed as a boolean.
             - update_succeed is a boolean flag that is True if the update went through successfully and False otherwise.

    """
    update_count: int = 0  # If the updates_count is more than 30 times, it will skip the update as it failed to fix the format.
    update_succeed: bool = True

    while char_id not in id_list or other_char_id not in id_list:
        # check if the char_id is the character's name, if yes then fix
        if char_id in name_list and name_list.count(char_id) == 1:
            index1: int = name_list.index(char_id)
            char_id: int = id_list[index1]
        # check if the other_char_id is the character's name, if yes then fix
        if other_char_id in name_list and name_list.count(other_char_id) == 1:
            index2: int = name_list.index(other_char_id)
            other_char_id: int = id_list[index2]
        # if both char_id and other_char_id are fixed, break out of the loop
        if char_id in id_list and other_char_id in id_list:
            break
        else:  # requery if format is incorrect
            separate_list: List[str] = (await update_attr.requery("relationship", story, char_dicts, update)).split(
                "=")
            char_id: str = fix_format(separate_list[0].strip())
            other_char_id: str = ((separate_list[1].strip()).split(","))[0]
            other_char_id: str = fix_format(other_char_id)
            try:
                char_id: int = int(char_id)
                other_char_id: int = int(other_char_id)
            except ValueError:
                pass

        if update_count > 30:
            update_succeed = False
            break
        update_count += 1

    return char_id, other_char_id, update_succeed


async def get_updates(attribute: str, story: str, char_dicts: str, id_list: List[int], name_list: List[str]) -> \
        List[V]:
    """Retrieves updates for a given attribute based on the most recent story events.

    This function sends a request to ChatGPT to retrieve updates for a specific attribute (such as 'physical_condition',
    'money', 'relationship', 'inventory', 'hp', or 'current_location') for characters in the provided story. It parses
    the updates, matches the character IDs, and returns a list of updates for only the affected characters.

    :param attribute: The attribute to retrieve updates for. Expected values are 'physical_condition',
                      'money', 'relationship', 'inventory', 'hp', or 'current_location'.
    :param story: A string of the 3 most recent story events.
    :param char_dicts: A JSON-like string representation, containing each character's ID, name and the provided attribute.
    :param id_list: A list containing the IDs of all characters.
    :param name_list: A list containing the names of all characters.
    :return: A list of updates for the affected characters. The format of the list depends on the attribute:
             - For 'physical_condition' and 'current_location', the return is List[Tuple[int, str]] where each tuple
               contains (char_id: int, new_value: str).
             - For 'relationship', the return is List[Tuple[int, int, str]] where each tuple contains
               (char_id: int, other_char_id: int, new_value: str).
             - For 'money', 'inventory', and 'hp', the return is List[Tuple[int, str, str]] where each tuple contains
               (char_id: int, operator: str, new_value: str), with the operator being either '+' or '-'.
    """
    pending_updates: List[V] = []
    # call the function responsible for sending the update attribute prompt to ChatGPT
    if attribute == "physical_condition":
        update_check: str = await update_attr.get_physical_condition_update(story, char_dicts)
    elif attribute == "money":
        update_check = await update_attr.get_money_update(story, char_dicts)
    elif attribute == "relationship":
        update_check = await update_attr.get_relationship_update(story, char_dicts)
    elif attribute == "inventory":
        update_check = await update_attr.get_inventory_update(story, char_dicts)
    elif attribute == "hp":
        update_check = await update_attr.get_hp_update(story, char_dicts)
    else:  # current_location
        update_check = await update_attr.get_current_location_update(story, char_dicts)
    update_check = fix_format(update_check)

    # if update_check is False, that means there's no updates to be done
    if update_check.lower() != "false":
        update_list: List[str] = update_check.split("\n")
        for update in update_list:
            update_count: int = 0  # if the updates count is more than 30 times, skip update as it failed to fix format
            update_succeed: bool = True  # if update went through successfully

            if attribute == "physical_condition" or attribute == "relationship" or attribute == "current_location":
                separate_list: List[str] = update.split("=")
            else:
                separate_list, symbol = split_function(update)

            char_id: str = fix_format(separate_list[0].strip())
            try:
                char_id: int = int(char_id)
            except ValueError:
                pass

            if attribute == "relationship":
                other_char_id: str = ((separate_list[1].strip()).split(","))[0]
                other_char_id = fix_format(other_char_id)
                try:
                    other_char_id: int = int(other_char_id)
                except ValueError:
                    pass
                char_id, other_char_id, update_succeed = await requery_updates_relationship(story, char_dicts, update,
                                                                                            char_id,
                                                                                            other_char_id, id_list,
                                                                                            name_list)
                if update_succeed:
                    new_value: str = ((separate_list[1].strip()).split(","))[1]
                    new_value = fix_format(new_value)
                else:
                    new_value = "false"
            else:
                while char_id not in id_list:
                    # check if the char_id is the character's name, if yes then fix
                    if char_id in name_list and name_list.count(char_id) == 1:
                        index: int = name_list.index(char_id)
                        char_id: int = id_list[index]
                    else:
                        # requery if format is incorrect
                        if attribute == "physical_condition":
                            separate_list = (
                                await update_attr.requery("physical_condition", story, char_dicts, update)).split(
                                "=")
                        elif attribute == "money":
                            new_update: str = await update_attr.requery("money", story, char_dicts, update)
                            separate_list, symbol = split_function(new_update)
                        elif attribute == "inventory":
                            new_update = await update_attr.requery("inventory", story, char_dicts, update)
                            separate_list, symbol = split_function(new_update)
                        elif attribute == "hp":
                            new_update = await update_attr.requery("hp", story, char_dicts, update)
                            separate_list, symbol = split_function(new_update)
                        else:  # current_location
                            separate_list = (
                                await update_attr.requery("current_location", story, char_dicts, update)).split("=")

                        char_id = fix_format(separate_list[0].strip())
                        try:
                            char_id: int = int(char_id)
                        except ValueError:
                            pass

                        if update_count > 30:
                            update_succeed = False
                            break
                        update_count += 1

                if update_succeed:
                    new_value = fix_format(separate_list[1].strip())
                    if attribute == "money":
                        try:
                            float(new_value)
                        except ValueError:
                            new_value = "false"
                    if attribute == "hp":
                        try:
                            int(new_value)
                        except ValueError:
                            new_value = "false"
                else:
                    new_value = "false"

            if new_value.lower() != "false":
                if attribute == "relationship":
                    pending_updates.append((char_id, other_char_id, new_value))
                elif attribute == "physical_condition" or attribute == "current_location":
                    pending_updates.append((char_id, new_value))
                else:  # inventory, money & hp
                    if symbol == "+=":
                        pending_updates.append((char_id, '+', new_value))
                    else:  # "-="
                        pending_updates.append((char_id, '-', new_value))
            else:
                print(f"{attribute} update failed. Schema returned was incorrect.")
    return pending_updates


def check_money(pending_updates: List[tuple[int, str, str]], id_list: List[int], name_list: List[str],
                money_list: List[float]) -> tuple[bool, List[tuple[int, str]]]:
    """Validates whether characters involved in money updates (such as transactions or random losses) have enough funds to complete the changes.

    This function checks a list of pending money updates and verifies whether each affected character has sufficient funds
    to handle the money deduction (where the operator is '-'). The functions ensure no balance becomes negative and
    identifies characters who don't have enough funds by adding their name and ID to a list of failed money updates.
    Invalid updates caused by non-numeric amounts (i.e., not a valid float) will also be flagged.

    :param pending_updates: A list of pending money updates, where each tuple consists of (char_id, operator, new_amount).
                            The operator is either '+' (for adding money) or '-' (for deducting money).
    :param id_list: A list containing the IDs of all characters.
    :param name_list: A list containing the names of all characters.
    :param money_list: A list containing the current money balance for each character.
    :return: A tuple:
             - bool: True if all money changes are valid (i.e., no negative balances), or
                     False if any changes would result in negative money or an error (amount is not a numeric value).
             - List[tuple[int, str]]: A list of tuples containing the ID and name of characters who don't have enough money
               to handle the loss or who encounter an error in the update.
    """
    # names and ids of the characters who don't have enough money to do the transaction
    broke_char_list: List[tuple[int, str]] = []
    valid_transaction_check: bool = True

    for index in range(len(pending_updates)):
        char_id: int = pending_updates[index][0]
        symbol: str = pending_updates[index][1]
        new_amount: str = pending_updates[index][2]
        index: int = id_list.index(char_id)
        char_name: str = name_list[index]

        try:
            new_amount: float = float(new_amount)
            if symbol == "-":
                # check if money will go into the negatives
                if money_list[index] - new_amount < 0:
                    valid_transaction_check = False
                    broke_char_list.append((char_id, char_name))
        except ValueError:
            valid_transaction_check = False
            broke_char_list.append((char_id, char_name))

    return valid_transaction_check, broke_char_list


async def list_saved_games() -> list[str]:
    """Returns a list of files inside the saved_games directory.
    If the saved_games directory does not exist, creates it.

    :return: A list of files inside the directoy.
    """
    directory = "saved_games"
    if not os.path.exists(directory):
        os.makedirs(directory)
    return os.listdir(directory)


async def play_background_music() -> None:
    """Plays background music in the title screen."""
    num = random.randint(1, 100)
    if num == 100:
        sound = 'assets/Sounds/title_bg.mp3'
    else:
        sound = 'assets/Sounds/title_bg.WAV'
    pygame.mixer.music.load(sound)
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)  # -1 means the music will loop indefinitely


async def stop_background_music() -> None:
    """Stops the background music"""
    pygame.mixer.music.stop()
