import ast
import random
from typing import List, Dict, TypeVar, Any
from Classes.Character import Character
from Classes.World import World
from Classes.Timeline import Timeline
import json
import os
import textwrap
from datetime import datetime
from Utilities import openai_api
from Utilities import update_attr
import subprocess

V = TypeVar("V")


class Engine:
    def __init__(self):
        """Initialise an Engine object.
        """
        self._world: World | None = None
        self._characters: List[Character] = []
        self._timeline: Timeline | None = None
        self._mainCharacter: Character | None = None

    @property
    def characters(self) -> List[Character]:
        """Fetches a list of Character classes representing the NPCs.
        This list does not include the Main Character.

        :return: A list of NPC Character classes.
        """
        return self._characters

    @property
    def world(self) -> World:
        """Fetches the World object.

        :return: The World object.
        """
        return self._world

    @property
    def timeline(self) -> Timeline:
        """Fetches the Timeline object.

        :return: The Timeline object.
        """
        return self._timeline

    def add_character(self, char_attributes: Dict[str, V]) -> None:
        """Initialises a Character class for a new NPC character and adds it to the characters list.

        :param char_attributes: A dictionary containing the new NPC character's attributes.
        :return: None
        """
        character: Character = Character(char_attributes["id"],
                                         char_attributes["name"],
                                         char_attributes["physical_condition"],
                                         char_attributes["occupation"],
                                         char_attributes["money"],
                                         char_attributes["relationship"],
                                         char_attributes["personality"],
                                         char_attributes["inventory"],
                                         char_attributes["stats"],
                                         char_attributes["current_location"],
                                         char_attributes["appearance"])

        # fix relationship dictionary by changing the key types from str to int
        relationship_keys_list = list(character.relationship.keys())
        for key in relationship_keys_list:
            character.relationship[int(key)] = character.relationship.pop(key)

        self._characters.append(character)

    def add_world(self, world_attributes: Dict[str, V]) -> None:
        """Initialises and sets a World class using the provided dictionary.

        :param world_attributes: A dictionary containing the world attributes.
        :return: None
        """
        world: World = World(world_attributes["rules"], world_attributes["genre"],
                             world_attributes["environment"], world_attributes["locations"])
        self._world = world

    def add_timeline(self, timeline_attributes: Dict[str, List[str]]) -> None:
        """Initialises and sets a Timeline class using the provided dictionary.

        :param timeline_attributes: A dictionary containing the timeline attributes.
        """
        timeline: Timeline = Timeline(timeline_attributes["key_events"])
        self._timeline = timeline

    @property
    def mainCharacter(self) -> Character:
        """Fetches the Character class for the main character.

        :return: The Character class for the main character.
        """
        return self._mainCharacter

    @mainCharacter.setter
    def mainCharacter(self, character: Dict[str, V]):
        """Initialises and sets a Character class for the main character using the provided dictionary.

        :param character: A dictionary containing the main character's attributes.
        """
        main_character: Character = Character(character["id"],
                                              character["name"],
                                              character["physical_condition"],
                                              character["occupation"],
                                              character["money"],
                                              character["relationship"],
                                              character["personality"],
                                              character["inventory"],
                                              character["stats"],
                                              character["current_location"],
                                              character["appearance"])
        self._mainCharacter = main_character

    def get_formatted_string_array(self) -> List[str]:
        """Fetches the string representation of the Character, World and Timeline classes.

        :return: A list containing the Character, World and Timeline classes as a string representation.
        """
        characters_str: str = f"{str(self._mainCharacter)}\n" + "\n".join(str(char) for char in self._characters)
        world_str: str = str(self._world)
        timeline_str: str = str(self._timeline)
        return [characters_str, world_str, timeline_str]

    def prepare_char_dictionaries(self, attribute: str) -> str:
        """Creates a JSON-like string representation of the characters based on the provided attribute.

        :param attribute: The attribute to include in the JSON-like string. Expected values are 'physical_condition',
                          'money', 'relationship', 'inventory', 'hp' or 'current_location'.
        :return: A JSON-like string representation, containing each character's ID, name and the provided attribute.
        """
        # main character
        char_dicts: str = textwrap.dedent(f'''
                    {{
                     "id": {self._mainCharacter.id}
                     "name": "{self._mainCharacter.name}"''')
        if attribute == "physical_condition":
            char_dicts += textwrap.dedent(f'''
                         "physical_condition": str "{self._mainCharacter.physical_condition}"
                        }}''')
        elif attribute == "money":
            char_dicts += textwrap.dedent(f'''
                         "money": float {self._mainCharacter.money}
                        }}''')
        elif attribute == "relationship":
            char_dicts += textwrap.dedent(f'''
                         "relationship": Dict[other_char_id: int, relationship_type: str] {self._mainCharacter.relationship}
                        }}''')
        elif attribute == "inventory":
            char_dicts += textwrap.dedent(f'''
                         "inventory": List[str] {self._mainCharacter.inventory}
                        }}''')
        elif attribute == "hp":
            char_dicts += textwrap.dedent(f'''
                         "physical_condition": str "{self._mainCharacter.physical_condition}"
                         "hp": int {self._mainCharacter.hp}
                        }}''')
        else:  # current_location
            char_dicts += textwrap.dedent(f'''
                         "current_location": str "{self._mainCharacter.current_location}"
                        }}''')
        # npcs
        for char in self._characters:
            char_dicts += ","
            char_dicts += textwrap.dedent(f'''
                        {{
                         "id": {char.id}
                         "name": "{char.name}"''')
            if attribute == "physical_condition" or attribute == "hp":
                char_dicts += textwrap.dedent(f'''
                             "physical_condition": str "{char.physical_condition}"
                             "hp": int {char.hp}
                            }}''')
            elif attribute == "money":
                char_dicts += textwrap.dedent(f'''
                             "money": float {char.money}
                            }}''')
            elif attribute == "relationship":
                char_dicts += textwrap.dedent(f'''
                             "relationship": Dict[other_char_id: int, relationship_type: str] {char.relationship}
                            }}''')
            elif attribute == "inventory":
                char_dicts += textwrap.dedent(f'''
                             "inventory": List[str] {char.inventory}
                            }}''')
            else:  # current_location
                char_dicts += textwrap.dedent(f'''
                             "current_location": str "{char.current_location}"
                            }}''')
        return char_dicts

    async def update_char_physical_condition(self, updates: List[tuple[int, str]]) -> None:
        """Updates the characters' physical condition based on the provided list of updates.
        If a character's physical condition is not specified and was left empty, it defaults to "Healthy".

        :param updates: A list of tuples, where each tuple contains the character's ID and their updated physical condition.
        :return: None
        """
        id_list: List[int] = [char.id for char in self._characters]
        for update in updates:
            char_id: int = update[0]
            new_status: str = update[1]
            if char_id == self._mainCharacter.id:
                self._mainCharacter.physical_condition = new_status
            else:
                index = id_list.index(char_id)
                self._characters[index].physical_condition = new_status
        # sets the physical_condition for a new NPC character if it was left empty
        for index in range(len(self._characters)):
            if self._characters[index].physical_condition == "":
                self._characters[index].physical_condition = "Healthy"

    async def update_char_money(self, updates: List[tuple[int, str, str]]) -> None:
        """Updates the characters' money based on the provided list of updates.

        :param updates: A list of tuples, where each tuple contains:
                        - The character's ID,
                        - An operation symbol ('+' to increase, '-' to decrease),
                        - The amount to increase/decrease the character's money by.
        :return: None
        """
        id_list: List[int] = [char.id for char in self._characters]
        for update in updates:
            char_id: int = update[0]
            symbol: str = update[1]
            new_amount: float = float(update[2])
            if symbol == "+":  # increase money
                if char_id == self._mainCharacter.id:
                    self._mainCharacter.increase_money(new_amount)
                else:
                    index = id_list.index(char_id)
                    self._characters[index].increase_money(new_amount)
            else:  # decrease money "-"
                if char_id == self._mainCharacter.id:
                    self._mainCharacter.decrease_money(new_amount)
                else:
                    index = id_list.index(char_id)
                    self._characters[index].decrease_money(new_amount)

    async def update_char_relationship(self, updates: List[tuple[int, int, str]]) -> None:
        """Updates the characters' relationship based on the provided list of updates.

        :param updates: A list of tuples, where each tuple contains:
                        - The character's ID,
                        - The other character's ID,
                        - The relationship between the two characters.
        :return: None
        """
        id_list: List[int] = [char.id for char in self._characters]
        for update in updates:
            char_id: int = update[0]
            other_char_id: int = update[1]
            relationship_type: str = update[2]
            if char_id == self._mainCharacter.id:
                self._mainCharacter.add_relationship(other_char_id, relationship_type)
            else:
                index = id_list.index(char_id)
                self._characters[index].add_relationship(other_char_id, relationship_type)

    async def update_char_inventory(self, updates: List[tuple[int, str, str]]) -> None:
        """Updates the characters' inventory based on the provided list of updates.

        :param updates: A list of tuples, where each tuple contains:
                        - The character's ID,
                        - An operation symbol ('+' to add, '-' to remove),
                        - The item to add/remove from the character's inventory.
        :return: None
        """
        id_list: List[int] = [char.id for char in self._characters]
        for update in updates:
            char_id: int = update[0]
            symbol: str = update[1]
            new_item: str = update[2]
            if symbol == "+":  # add to inventory
                if char_id == self._mainCharacter.id:
                    self._mainCharacter.add_inventory(new_item)
                else:
                    index = id_list.index(char_id)
                    self._characters[index].add_inventory(new_item)
            else:  # remove from inventory "-="
                if char_id == self._mainCharacter.id:
                    self._mainCharacter.remove_inventory(new_item)
                else:
                    index = id_list.index(char_id)
                    self._characters[index].remove_inventory(new_item)

    async def update_char_hp(self, updates: List[tuple[int, str, int]]) -> None:
        """Updates the characters' health (HP) based on the provided list of updates.

        For each update, this function either uses the specified amount or randomly generates
        the amount to increase or decrease a character's HP by (depending on which is lower).
        This approach prevents characters from losing too much HP, which could lead to premature
        deaths in the story.

        :param updates: A list of tuples, where each tuple contains:
                        - The character's ID,
                        - An operation symbol ('+' to increase, '-' to decrease),
                        - The amount to increase/decrease the hp by.
        :return: None
        """
        id_list: List[int] = [char.id for char in self._characters]
        for update in updates:
            char_id: int = update[0]
            symbol: str = update[1]
            new_hp: int = update[2]
            if self._mainCharacter.hp <= 5:
                new_hp = 1
            else:
                if char_id == self._mainCharacter.id:
                    random_hp: int = random.randint(1, (self._mainCharacter.hp // 5))
                else:
                    index: int = id_list.index(char_id)
                    random_hp = random.randint(1, (self._characters[index].hp // 5))
                new_hp = min(int(new_hp), int(random_hp))

            if symbol == "+":  # increase hp
                if char_id == self._mainCharacter.id:
                    self._mainCharacter.increase_hp(new_hp)
                else:
                    self._characters[index].increase_hp(new_hp)
            else:  # decrease hp "-="
                if char_id == self._mainCharacter.id:
                    self._mainCharacter.decrease_hp(new_hp)
                else:
                    self._characters[index].decrease_hp(new_hp)

    async def update_char_current_location(self, story: str, updates: List[tuple[int, str]]) -> None:
        """Updates the characters' current location based on the provided list of updates.

        This function also updates the location and environment attributes of the World object according to
        the main character's new location. The environment is fetched asynchronously based on the story context.

        :param story: A string representing the current story context.
        :param updates: A list of tuples, where each tuple contains the character's ID and their updated location.
        :return: None
        """
        id_list: List[int] = [char.id for char in self._characters]
        for update in updates:
            char_id: int = update[0]
            new_location: str = update[1]
            if char_id == self._mainCharacter.id:
                self._mainCharacter.current_location = new_location
                self._world.add_locations(new_location)
                new_environment = await update_attr.get_environment(story)
                self._world.environment = new_environment
            else:
                index = id_list.index(char_id)
                self._characters[index].current_location = new_location

    async def update_key_events(self, story: str) -> None:
        """"Updates the key events based on the current story context.

        :param story: A string representing the current story context.
        :return: None
        """
        summarised_key_event: str = await update_attr.get_key_events(story)
        self._timeline.add_event(summarised_key_event)

    async def check_inventory(self, user_input: str) -> tuple[bool, str]:
        """Checks whether the main character is attempting to use items that are not in their inventory.

        If any of the specified items are missing from the inventory, the function returns a
        False flag along with a message indicating which items are not available. If all items
        are found in the inventory, it returns a True flag along with a confirmation message.

        :param user_input: A string representing the user input, which specifies the items to check.
        :return: A tuple containing:
                 - A boolean flag (True if all items are in the inventory, False otherwise),
                 - A string message indicating the result of the check.
        """
        response = await update_attr.check_char_inventory(user_input)
        if response.used_item:
            items_used = response.items_list
            not_in_inventory = []

            for item in items_used:
                if not any(item.lower() in i.lower() for i in self._mainCharacter.inventory):
                    not_in_inventory.append(item)

            if not_in_inventory:
                return True, f"You are trying to use items not in your inventory or in the story: {', '.join(not_in_inventory)}"

        return False, "All items are available in your inventory."

    def check_characters_deceased(self, genre: str) -> tuple[bool, str]:
        """Checks if any characters, including the main character, have died based on their health (hp) and physical condition.

        This function ensures consistency between a character's hp and physical condition. If a character's hp reaches 0,
        their physical condition is updated to "Deceased" if it's not already. Similarly, if a character's physical condition
        is set to "Deceased" or "Dead," their hp is adjusted to 0 if it's not already.

        If the main character is found to be dead, the function generates a message to end the story and prompts ChatGPT to
        explain the death. If any NPCs have died, the function generates a message listing them and requests justification
        for their deaths in the story.

        :param genre: The genre of the world as a string. This is used in the message when the main character has died.
        :return: A tuple containing:
                 - A boolean flag (True if the main character is dead, False otherwise),
                 - A string message listing the characters who have died.
        """
        deceased_message: str = ""
        main_char_dead: bool = False
        dead_characters: List[Character] = []

        # checks if the main character is dead
        if self._mainCharacter.hp == 0 and (
                self._mainCharacter.physical_condition.lower() == "deceased" or self._mainCharacter.physical_condition.lower() == "dead"):
            main_char_dead = True
        # checks if the physical_condition and hp reflects the main character being deceased
        elif ((self._mainCharacter.hp == 0 and (
                self._mainCharacter.physical_condition.lower() != "deceased" or self._mainCharacter.physical_condition.lower() != "dead")) or
              (self._mainCharacter.hp != 0 and (
                      self._mainCharacter.physical_condition.lower() == "deceased" or self._mainCharacter.physical_condition.lower() == "dead"))):
            self._mainCharacter.physical_condition = "Deceased"
            self._mainCharacter.decrease_hp(100)
            # informs ChatGPT and main.py to end the story as the main character has died
            deceased_message += f"The main character {self._mainCharacter.name} (ID: {self._mainCharacter.id}) is now deceased, please end the {genre} story."
            main_char_dead = True

        # checks if the physical_condition and hp reflects the npcs being deceased
        for index in range(len(self._characters)):
            if ((self._characters[index].hp == 0 and (
                    self._characters[index].physical_condition.lower() != "deceased" or self._characters[
                index].physical_condition.lower() != "dead")) or
                    (self._characters[index].hp != 0 and (
                            self._characters[index].physical_condition.lower() == "deceased" or self._characters[
                        index].physical_condition.lower() == "dead"))):
                self._characters[index].physical_condition = "Deceased"
                self._characters[index].decrease_hp(100)
                dead_characters.append(self._characters[index])

        # generates a message listing the characters who have died
        if dead_characters:
            if main_char_dead:
                # if the main character is dead, add a line to prompt ChatGPT to provide an explanation for their deaths
                if len(dead_characters) == 1:  # if only one npc has died
                    deceased_message += f"\nThe character {dead_characters[0].name} (ID: {dead_characters[0].id}) is also now deceased, please justify their death in the story."
                else:  # if more than one npc has died
                    deceased_message += "\nThe characters "
                    for index in range(len(dead_characters)):
                        if index == len(dead_characters) - 1:
                            deceased_message += f"{dead_characters[index].name} (ID: {dead_characters[index].id})"
                        else:
                            deceased_message += f"{dead_characters[index].name} (ID: {dead_characters[index].id}), "
                    deceased_message += f" are also now deceased, please justify their deaths in the story."
            else:
                # if the main character didn't die, just list the character who have died
                for index in range(len(dead_characters)):
                    if index == len(dead_characters) - 1:
                        deceased_message += f"{dead_characters[index].name} (ID: {dead_characters[index].id})"
                    else:
                        deceased_message += f"{dead_characters[index].name} (ID: {dead_characters[index].id}), "
        return main_char_dead, deceased_message.strip()

    def update_world_rules(self, genre: str) -> None:
        """Generates a set of world rules for the provided genre if the user selects the default mode.
        These rules are created by ChatGPT and define the boundaries and principles of the world.

        :param genre: The genre of the world as a string, which will influence the rules generated.
        :return: None
        """

        # Get response from OpenAI using the existing openai_api module
        response = openai_api.get_rules(genre)

        # Extract rules from the response
        rules: list[str] = [rule.strip('-').strip() for rule in response.split('\n') if rule.strip()]

        if self._world:
            self._world.add_rules(rules)

        print(f"Updated world rules for {genre} storyline:")
        for rule in self._world.rules:
            print(f"- {rule}")
        print()

    def update_world_environment(self, genre: str):
        """Generates the environment of the world for the provided genre if the user selected the default mode.
        The description of the world is generated by ChatGPT and define the setting of the story.

        :param genre: The genre of the world as a string, which will influence the environment generated.
        :return: None
        """
        response: str = openai_api.get_environment(genre)

        if self._world:
            self._world.environment = response
        print("updated environment:", response)

    def save_game(self) -> None:
        """Saves the current game data to a JSON file in the "saved_games" directory.
        If the "saved_games" directory does not exist, it will be created.
        The saved data includes the world, characters, timeline, main character, and the conversation history.

        :return: None
        """
        # Create the directory if it doesn't exist
        if not os.path.exists("saved_games"):
            os.makedirs("saved_games")

        # Convert objects to dictionaries using to_dict()
        world = self._world.to_dict() if self._world else {}
        characters = [char.to_dict() for char in self._characters]
        timeline = self._timeline.to_dict() if self._timeline else {}
        main_char = self._mainCharacter.to_dict() if self._mainCharacter else {}
        history = openai_api.get_history()

        data = {
            "world": world,
            "characters": characters,
            "timeline": timeline,
            "main_character": main_char,
            "history": history
        }

        # Save the data to a JSON file
        with open(f"saved_games/{self._mainCharacter.name}_save_data.json", "w") as file:
            json.dump(data, file, indent=4)

        print(f'Game saved at {datetime.now().strftime("%Y%m%d_%H%M%S")}')

    def load_save(self, filename: str) -> None:
        """Loads a saved game state from a specified JSON file, restoring the game world, characters,
        timeline, main character, and chat history.

        :param filename: The name of the JSON file (with a .json extension) located in the "saved_games" directory.
                         Only JSON files are accepted for loading the saved game data.
        :return: None
        :raises: FileNotFoundError: If the specified JSON file does not exist in the "saved_games" directory.
        """
        path = f"saved_games/{filename}"

        if not os.path.exists(path):
            raise FileNotFoundError(f"'{filename}' is not found.")

        with open(path, 'r') as file:
            data = json.load(file)

        self.add_world(data["world"])

        for character_data in data["characters"]:
            self.add_character(character_data)

        self.add_timeline(data["timeline"])
        self._mainCharacter = Character(**data["main_character"])

        # fix relationship dictionary by changing the key types from str to int
        relationship_keys_list = list(self._mainCharacter.relationship.keys())
        for key in relationship_keys_list:
            self._mainCharacter.relationship[int(key)] = self._mainCharacter.relationship.pop(key)

        openai_api.set_history(data["history"])

        print(f'"{filename}" has been loaded.')

    def export_final_story(self, story_arr: List[str]) -> None:
        """Exports the final game data into separate files within the "exported_games" directory.
        If the "exported_games" directory does not already exist, it will be created.
        The exported data includes the world, timeline, main character and characters as JSON files,
        while the complete story will be saved as a txt file.

        :param story_arr: A list of strings representing the story.
        :return: None
        """
        if not os.path.exists("exported_games"):
            os.makedirs("exported_games")

        world = self._world.to_dict() if self._world else {}
        timeline = self._timeline.to_dict() if self._timeline else {}
        main_char = self._mainCharacter.to_dict() if self._mainCharacter else {}
        characters = [main_char] + [char.to_dict() for char in self._characters]

        path = f"exported_games/{main_char['name']}_{world['genre']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(path)

        with open(path + "/characters.json", "w") as fp:
            json.dump(characters, fp, indent=4)

        with open(path + "/world.json", "w") as fp:
            json.dump(world, fp, indent=4)

        with open(path + "/timeline.json", "w") as fp:
            json.dump(timeline, fp, indent=4)

        with open(path + "/story.txt", "w") as fp:
            for i in range(len(story_arr)):
                separated_story = story_arr[i].split("\n")
                for story in separated_story:
                    sentences = story.split(".")
                    for sentence in sentences:
                        sentence = sentence.strip()
                        if sentence == "":
                            continue
                        fp.write(sentence + ".\n")
                fp.write("\n")

    def random_event(self, luck_stat: int) -> list[str | int | tuple[str, str]]:
        """Triggers a random event that affects the main character based on the threshold value.
            Depending on whether the random number generated is higher or lower than the threshold,
            the event will have either positive or negative effects on the character.

            **The possible effects include:**

            - **Physical Condition**: Either improves or worsens the main character's physical condition.
            - **Relationship**: Deepens or sours a relationship with another character.
            - **Money**: Adds or removes a random amount of money from the main character.
            - **Inventory**: Adds or removes an item from the character's inventory.

            :param luck_stat: The main character's luck stat (integer) is used to determine whether the effects will be positive or negative.
                              If the added dice roll amount is greater than 13 - luck_stat, a positive effect occurs.
                              Otherwise, a negative effect occurs (added dice roll is less than or equal to 13 - luck_stat).
            :return: A list where:
                     - The first element is a string describing the event that occurred.
                     - The second element is a string indicating the type of effect.
                     - The third element is the new value resulting from the effect.
        """
        loop_count: int = 0
        random_num = subprocess.run(["python", "Frontend/dice_roll.py"], capture_output=True, text=True).stdout.split()
        try:
            random_num = int(random_num[-1])
        except IndexError:
            random_num = random.randint(2, 12)

        # list of effects that might occur
        effects: list[str] = ["physical_condition", "money", "relationship", "inventory"]
        status: str = ""

        threshold: int = 13 - luck_stat
        # random num is greater than threshold, so positive effects will happen
        if random_num > threshold:
            status = "positive"
        # random num is less than or equal to threshold, so negative effects will happen
        elif random_num <= threshold:
            status = "negative"

        random_effect: str = random.choice(effects)
        while True:
            loop_count += 1
            if loop_count >= 15:
                break
            if random_effect == "physical_condition":
                # checks the current condition of the main character and sets a new condition.
                new_condition: str = openai_api.check_condition(self._mainCharacter.physical_condition, status)
                if new_condition != "False":
                    prev_condition: str = self._mainCharacter.physical_condition
                    self._mainCharacter.physical_condition = new_condition
                    return [f"The main character's physical condition went from {prev_condition} to {new_condition}.",
                            "condition", new_condition]
                else:
                    # the main character's condition is already positive/negative, so we should pick another effect
                    random_effect = random.choice([effect for effect in effects if effect != "physical_condition"])
                    continue

            if random_effect == "relationship":
                # checks if there are at least one established relationship.
                if len(self._mainCharacter.relationship) > 0:
                    random_relationship: tuple[int, str] = random.choice(list(self._mainCharacter.relationship.items()))
                    new_relationship: str = openai_api.get_new_relationship(random_relationship[1], status)
                    self._mainCharacter.add_relationship(random_relationship[0], new_relationship)
                    return [
                        f"The main character's relationship's with ID {random_relationship[0]} went from {random_relationship[1]} to {new_relationship}.",
                        "relationship", (random_relationship[0], new_relationship)]
                else:
                    # the main character has not established any relationships yet, so we should pick a new effect
                    random_effect = random.choice(
                        [effect for effect in effects if effect not in ["relationship"]])
                    continue

            if random_effect == "money":
                # generates a random amount of money to be added
                if self._mainCharacter.money > 0:
                    random_money: int = random.randint(int(self._mainCharacter.money) // 2 + 1,
                                                       int(self._mainCharacter.money) + 1)
                    if status == "positive":
                        return [f"The main character's money has been increased by {random_money}.", "increase money",
                                random_money]
                    elif status == "negative":
                        return [f"The main character's money has been decreased by {random_money}.", "decrease money",
                                random_money]
                else:
                    random_effect = random.choice(
                        [effect for effect in effects if effect not in ["money"]])
                    continue

            if random_effect == "inventory":
                # ChatGPT will generate an item based on the world that can be added to a character's inventory
                if len(self._mainCharacter.inventory) > 0:
                    world_dict: str = str(self._world)
                    random_item: str = openai_api.get_new_item(world_dict)
                    if status == "positive":
                        return [f"The main character gained a new item called {random_item}", "gain item", random_item]
                    elif status == "negative":
                        # a random item will be removed from the main character's inventory
                        item_from_inv: str = random.choice(self._mainCharacter.inventory)
                        self._mainCharacter.remove_inventory(item_from_inv)
                        return [f"The main character has lost an item called {item_from_inv}", "lose item", item_from_inv]
                else:
                    random_effect = random.choice(
                        [effect for effect in effects if effect not in ["inventory"]])
                    continue

        return ["", "", ""]

    def double_update_check(self, status: str, new_value: int | str, prev_money: float) -> None:
        """Verifies that changes made by the random events function have been correctly applied to the main character's
            attributes and fixes any discrepancies. This function should only be called after ``random_events``
            and ``update_attr`` has been called to ensure the updates went through as expected.

            :param status: A string indicating the type of update made by the random event. Can be one of the following:
                   - "increase money": Verifies that the character's money was increased by the expected amount.
                   - "decrease money": Verifies that the character's money was decreased by the expected amount.
                   - "gain item": Verifies that the item was added to the inventory.
                   - "lose item": Verifies that the item was removed from the inventory.
            :param new_value: The value related to the update:
                  - For "increase money" and "decrease money", this is an integer representing the amount of money involved.
                  - For "gain item" and "lose item", this is a string representing the name of the item involved.
            :param prev_money: A float representing the character's money before the random event occurred.
                            This is used to cross-check if the money update was applied correctly.
            :return: None
        """
        if status == "increase money":
            if prev_money + new_value != self._mainCharacter.money:
                self._mainCharacter.money = round(prev_money + new_value, 2)
        if status == "decrease money":
            if prev_money - new_value != self._mainCharacter.money:
                self._mainCharacter.money = round(prev_money - new_value, 2)

        if status == "gain item":
            if new_value.lower() not in [item.lower() for item in self._mainCharacter.inventory]:
                self._mainCharacter.add_inventory(new_value)
        if status == "lose item":
            if new_value.lower() in [item.lower() for item in self._mainCharacter.inventory]:
                self._mainCharacter.remove_inventory(new_value)

    def get_char_id(self) -> int:
        """Fetches the next available character ID for a new NPC.
        This function finds the highest character ID currently in use by the existing characters
        and returns the next sequential ID for the new NPC.

        :return: TThe next available character ID for the new NPC.
        """
        ret_id = 1
        for char in self._characters:
            ret_id = max(ret_id, char.id)
        return ret_id + 1

    def relationship_to_name(self, npc_char: Character) -> str:
        """Changes the IDs in the relationship attribute to the characters' name for front-end.

        :param npc_char: The character object of the NPC.
        :return: A string of the relationship dictionary with the characters' name instead of ID.
        """
        current_char_id_list: List[int] = [char.id for char in self._characters]
        current_char_id_list.insert(0, self._mainCharacter.id)
        current_char_name_list: List[str] = [char.name for char in self._characters]
        current_char_name_list.insert(0, self._mainCharacter.name)

        count: int = 0
        relationship_name_str: str = "{"
        for other_char_id in npc_char.relationship:
            index: int = current_char_id_list.index(other_char_id)
            other_char_name: str = current_char_name_list[index]
            relationship_name_str += f"{other_char_name}: {npc_char.relationship[int(other_char_id)]}"
            if count != len(npc_char.relationship) - 1:
                relationship_name_str += ", "
            count += 1
        relationship_name_str += "}"

        return relationship_name_str
