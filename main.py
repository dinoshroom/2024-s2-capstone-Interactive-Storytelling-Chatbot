import asyncio
import os
import re
import threading
from typing import Dict, List, TypeVar
import random
import flet as ft
import pygame
from screeninfo import get_monitors
from Engine import engine
from Utilities import utils, openai_api, update_attr
from Frontend import front_end_helpers, character_screen, world_screen
from Frontend.front_end_helpers import generate_image, process__value, create_text_field, create_error_message, \
    create_stats_text, format_inventory, get_title_image_height, get_title_image_top, get_button_width

V = TypeVar("V")


class GameApp:
    def __init__(self):
        """Initialises a new game application instance.
        Sets up initial game state, engine, audio, and UI variables.
        
        :return: None
        """
        self.main_engine = engine.Engine()
        self.story_msgs = []
        self.page = None
        self.reset_count = 0
        self.event_count = random.randint(1, 10)
        self.recent_stories: List[str] = []
        self.deceased_character_line: str = ""
        self.start_message: str = ""
        self.is_dead = False

        # Attributes to store text field values
        self.name_value = ""
        self.physical_condition_value = ""
        self.occupation_value = ""
        self.appearance_value = ""
        self.inventory_value = ""
        self.personality_value = ""
        self.money_value = ""
        self.hp_value = ""
        self.luck_value = ""
        self.cha_value = ""
        self.genre_value = ""
        self.world_rules_value = ""
        self.environment_value = ""

        pygame.mixer.init()
        self.button_click_sound = pygame.mixer.Sound('assets/Sounds/button_click.mp3')

    async def main(self, page: ft.Page):
        """Initialises and configures the main application window.
        Sets up window properties, theme, and displays the title screen.
        
        :param page: The Flet page object representing the main application window
        :return: None
        """
        self.page = page
        self.page.title = "OnlyFantasies"
        self.page.theme_mode = "dark"

        # Get the native screen width and height
        monitor = get_monitors()[0]
        self.page.window.width = monitor.width
        self.page.window.height = monitor.height

        self.page.bgcolor = ft.colors.BLACK
        self.page.padding = 0
        self.page.fonts = {
            "Pixelify Sans": "fonts/PixelifySans-VariableFont_wght.ttf"
        }
        self.page.window.full_screen = False
        self.page.window.maximized = True

        await self.show_title_screen()

    async def on_text_change(self, e):
        """Handles text input validation and updates for all text fields in real-time.
        Validates input against specific rules for each field type and updates error messages.
        
        :param e: The text change event containing the control and new value
        :return: None
        :raises ValueError: If input format is invalid (multiple spaces, invalid characters, etc.)
        """
        if e.control == self.name_field:  # Name
            try:
                name_value = e.control.value  # e.control.value - Literally resticts what user can type
                new_str = re.sub(' +', ' ', name_value)
                if name_value == "" or name_value == " ":
                    e.control.value = ""
                    self.name_value = ""
                    self.name_error_message.value = "Name cannot be empty."
                elif name_value != new_str:  # Checks for more than one space between words
                    raise ValueError
                else:
                    if re.match(r"^[a-zA-Z ]*$", name_value):  # Alphabet only
                        self.name_value = e.control.value
                        self.name_error_message.value = ""
                    else:
                        e.control.value = self.name_value
                        self.name_error_message.value = "Only letters are allowed."
                self.page.update()
            except ValueError:
                e.control.value = ' '.join(self.name_value.split()) + " "
                self.page.update()

        elif e.control == self.physical_condition_field:  # Physical Condition
            try:
                physical_condition_value = e.control.value
                if physical_condition_value == "":
                    e.control.value = ""
                    self.physical_condition_value = ""
                    self.physical_condition_error_message.value = "Physical Condition cannot be empty."
                elif " " in physical_condition_value:
                    e.control.value = self.physical_condition_value
                    self.physical_condition_value = e.control.value
                    self.physical_condition_error_message.value = "Physical Condition can have only one word."
                else:
                    if re.match(r"^[a-zA-Z]*$", physical_condition_value):
                        self.physical_condition_value = ' '.join(
                            e.control.value.split())  # Looks normal when you go back to character page
                        self.physical_condition_error_message.value = ""
                    else:
                        e.control.value = self.physical_condition_value
                        self.physical_condition_error_message.value = "Only letters are allowed."
                self.page.update()
            except ValueError:
                e.control.value = self.physical_condition_value
                self.physical_condition_error_message.value = "Invalid input."
                self.page.update()

        elif e.control == self.occupation_field:  # Occupation
            try:
                occupation_value = e.control.value
                new_str = re.sub(' +', ' ', occupation_value)
                if occupation_value == "" or occupation_value == " ":
                    e.control.value = ""
                    self.occupation_value = ""
                    self.occupation_error_message.value = "Occupation cannot be empty."
                elif occupation_value != new_str:  # Checks for more than one space between words
                    raise ValueError
                else:
                    if re.match(r"^[a-zA-Z ]*$", occupation_value):
                        self.occupation_value = e.control.value
                        self.occupation_error_message.value = ""
                    else:
                        e.control.value = self.occupation_value
                        self.occupation_error_message.value = "Only letters are allowed."
                self.page.update()
            except ValueError:
                e.control.value = ' '.join(self.occupation_value.split()) + " "
                self.page.update()

        elif e.control == self.appearance_field:  # Appearance
            try:
                appearance_value = e.control.value
                new_space_str = re.sub(' +', ' ', appearance_value)  # Checks if more than one space
                new_line_str = re.sub('\n+', '\n', appearance_value)  # Checks if more than one \n
                new_comma_str = re.sub(',+', ',', appearance_value)
                if appearance_value == "" or appearance_value == " " or appearance_value == "\n":
                    e.control.value = ""
                    self.appearance_value = ""
                    self.appearance_error_message.value = "Appearance cannot be empty."
                elif (
                        appearance_value != new_space_str or appearance_value != new_line_str or appearance_value != new_comma_str or
                        "\n " in appearance_value or "\n," in appearance_value or " ," in appearance_value or appearance_value == ","):  # Checks for more than one space between words
                    raise ValueError
                else:
                    if re.match(r"^[a-zA-Z, \n]*$", appearance_value):
                        self.appearance_value = e.control.value
                        self.appearance_error_message.value = ""
                    else:
                        e.control.value = self.appearance_value
                        self.appearance_error_message.value = "Only letters and commas are allowed."
                self.page.update()
            except ValueError:
                e.control.value = self.appearance_value
                self.page.update()

        elif e.control == self.inventory_field:  # Inventory
            try:
                inventory_value = e.control.value
                new_space_str = re.sub(' +', ' ', inventory_value)  # Checks if more than one space
                new_line_str = re.sub('\n+', '\n', inventory_value)  # Checks if more than one \n
                new_comma_str = re.sub(',+', ',', inventory_value)
                if inventory_value == "" or inventory_value == " " or inventory_value == "\n":
                    e.control.value = ""
                    self.inventory_value = ""
                    self.inventory_error_message.value = ""
                elif (
                        inventory_value != new_space_str or inventory_value != new_line_str or inventory_value != new_comma_str or
                        "\n " in inventory_value or "\n," in inventory_value or " ," in inventory_value or inventory_value == ","):  # Checks for more than one space between words
                    raise ValueError
                else:
                    if re.match(r"^[a-zA-Z, \n]*$", inventory_value):
                        self.inventory_value = e.control.value
                        self.inventory_error_message.value = ""
                    else:
                        e.control.value = self.inventory_value
                        self.inventory_error_message.value = "Only letters and commas are allowed."
                self.page.update()
            except ValueError:
                e.control.value = self.inventory_value
                self.page.update()

        elif e.control == self.personality_field:  # Personality
            try:
                personality_value = e.control.value
                new_space_str = re.sub(' +', ' ', personality_value)  # Checks if more than one space
                new_line_str = re.sub('\n+', '\n', personality_value)  # Checks if more than one \n
                new_comma_str = re.sub(',+', ',', personality_value)
                if personality_value == "" or personality_value == " " or personality_value == "\n":
                    e.control.value = ""
                    self.personality_value = ""
                    self.personality_error_message.value = "Personality cannot be empty."
                elif (
                        personality_value != new_space_str or personality_value != new_line_str or personality_value != new_comma_str or
                        "\n " in personality_value or "\n," in personality_value or " ," in personality_value or personality_value == ","):  # Checks for more than one space between words
                    raise ValueError
                else:
                    if re.match(r"^[a-zA-Z, \n]*$", personality_value):
                        self.personality_value = e.control.value
                        self.personality_error_message.value = ""
                    else:
                        e.control.value = self.personality_value
                        self.personality_error_message.value = "Only letters and commas are allowed."
                self.page.update()
            except ValueError:
                e.control.value = self.personality_value
                self.page.update()

        elif e.control == self.money_field:  # Money
            try:
                money_value = e.control.value
                if money_value == "" or money_value == " ":  # If input cleared
                    self.money_value = ""  # Set value to empty
                    self.money_error_message.value = "Money field cannot be empty."  # Show error
                    e.control.value = self.money_value
                elif " " in money_value or money_value[0] == "+" or (money_value[0] == "0" and money_value != "0"):
                    e.control.value = self.money_value
                    self.money_value = e.control.value
                elif money_value == "-0":
                    e.control.value = self.money_value
                    self.money_error_message.value = "Why. Stop it."
                else:
                    money_value = float(money_value)
                    if money_value < 0:
                        e.control.value = self.money_value
                        self.money_error_message.value = "You cannot be in debt yet."
                    elif len(str(money_value)) > 12:
                        e.control.value = self.money_value
                        self.money_error_message.value = "Too rich. No."
                    else:
                        self.money_value = e.control.value  # Set the valid numerical value
                        self.money_error_message.value = ""  # Clear error when valid
                self.page.update()
            except ValueError:
                e.control.value = self.money_value  # Reset to previous value if invalid
                self.money_error_message.value = "Enter a number."  # Show type error
                self.page.update()

        elif e.control == self.hp_field:  # Hp
            try:
                hp_value = e.control.value
                if hp_value == "" or hp_value == " ":  # If input cleared
                    self.hp_value = ""  # Set value to empty
                    self.hp_error_message.value = "Hp field cannot be empty."
                    e.control.value = self.hp_value
                elif " " in hp_value or hp_value[0] == "+" or (hp_value[0] == "0" and hp_value != "0"):
                    e.control.value = self.hp_value
                    self.hp_value = e.control.value
                else:
                    hp_value = int(hp_value)
                    if hp_value > 100:  # Checks if within range
                        e.control.value = self.hp_value
                        self.hp_error_message.value = "Hp must be between 30-100."
                    elif hp_value < 1:
                        e.control.value = self.hp_value
                        self.hp_error_message.value = "You cannot be dead yet."
                    elif hp_value < 30:  # Checks if within range
                        self.hp_error_message.value = "Hp must be between 30-100."
                    else:
                        self.hp_value = e.control.value
                        self.hp_error_message.value = ""
                self.page.update()
            except ValueError:
                e.control.value = self.hp_value
                self.hp_error_message.value = "Enter a number."
                self.page.update()

        elif e.control == self.luck_field:  # Luck
            try:
                luck_value = e.control.value
                if luck_value == "" or luck_value == " ":
                    self.luck_value = ""
                    self.luck_error_message.value = "Luck field cannot be empty."
                    e.control.value = self.luck_value
                elif " " in luck_value or luck_value[0] == "+" or (luck_value[0] == "0" and luck_value != "0"):
                    e.control.value = self.luck_value
                    self.luck_value = e.control.value
                else:
                    luck_value = int(luck_value)
                    if luck_value < 1 or luck_value > 11:
                        e.control.value = self.luck_value
                        self.luck_error_message.value = "Luck must be between 2-11."
                    elif luck_value == 1:
                        self.luck_error_message.value = "Luck must be between 2-11."
                    else:
                        self.luck_value = e.control.value
                        self.luck_error_message.value = ""
                self.page.update()
            except ValueError:
                e.control.value = self.luck_value
                self.luck_error_message.value = "Enter a number."
                self.page.update()

        elif e.control == self.cha_field:  # Cha (Charisma)
            try:
                cha_value = e.control.value
                if cha_value == "" or cha_value == " ":
                    self.cha_value = ""
                    self.cha_error_message.value = "Cha field cannot be empty."
                    e.control.value = self.cha_value
                elif " " in cha_value or cha_value[0] == "+" or (cha_value[0] == "0" and cha_value != "0"):
                    e.control.value = self.cha_value
                    self.cha_value = e.control.value
                elif cha_value == "-0":
                    e.control.value = self.cha_value
                    self.cha_error_message.value = "You are not funny."
                else:
                    cha_value = int(cha_value)
                    if (cha_value < 0) or (cha_value > 10):
                        e.control.value = self.cha_value
                        self.cha_error_message.value = "Cha must be between 0-10."
                    else:
                        self.cha_value = e.control.value
                        self.cha_error_message.value = ""
                self.page.update()
            except ValueError:
                e.control.value = self.cha_value
                self.cha_error_message.value = "Enter a number."
                self.page.update()

        elif e.control == self.genre_field:  # Genre
            try:
                genre_value = e.control.value  # e.control.value - Literally resticts what user can type
                new_str = re.sub(' +', ' ', genre_value)
                if genre_value == "" or genre_value == " ":
                    e.control.value = ""
                    self.genre_value = ""
                    self.genre_error_message.value = "Genre cannot be empty."
                elif genre_value != new_str:  # Checks for more than one space between words
                    raise ValueError
                else:
                    if re.match(r"^[a-zA-Z ]*$", genre_value):  # Alphabet only
                        self.genre_value = e.control.value
                        self.genre_error_message.value = ""
                    else:
                        e.control.value = self.genre_value
                        self.genre_error_message.value = "Only letters are allowed."
                self.page.update()
            except ValueError:
                e.control.value = ' '.join(self.genre_value.split()) + " "
                self.page.update()

        elif e.control == self.world_rules_field:  # World Rules
            if self.rules_dropdown.value == "Default":
                self.world_rules_error_message.value = ""
                self.page.update()
                return
            try:
                world_rules_value = e.control.value
                new_space_str = re.sub(' +', ' ', world_rules_value)  # Checks if more than one space
                new_line_str = re.sub('\n+', '\n', world_rules_value)  # Checks if more than one \n
                new_comma_str = re.sub(',+', ',', world_rules_value)
                if world_rules_value == "" or world_rules_value == " " or world_rules_value == "\n":
                    e.control.value = ""
                    self.world_rules_value = ""
                    self.world_rules_error_message.value = "World Rules in Custom Mode cannot be empty."
                elif (
                        world_rules_value != new_space_str or world_rules_value != new_line_str or world_rules_value != new_comma_str or
                        "\n " in world_rules_value or "\n," in world_rules_value or " ," in world_rules_value or world_rules_value == ","):  # Checks for more than one space between words
                    raise ValueError
                else:
                    if re.match(r"^[a-zA-Z, \n]*$", world_rules_value):
                        self.world_rules_value = e.control.value
                        self.world_rules_error_message.value = ""
                    else:
                        e.control.value = self.world_rules_value
                        self.world_rules_error_message.value = "Only letters and commas are allowed."
                self.page.update()
            except ValueError:
                e.control.value = self.world_rules_value
                self.page.update()

        elif e.control == self.environment_field:  # Environment
            if self.environment_dropdown.value == "Default":
                self.environment_error_message.value = ""
                self.page.update()
                return
            try:
                environment_value = e.control.value
                new_space_str = re.sub(' +', ' ', environment_value)  # Checks if more than one space
                new_line_str = re.sub('\n+', '\n', environment_value)  # Checks if more than one \n
                new_comma_str = re.sub(',+', ',', environment_value)
                if environment_value == "" or environment_value == " " or environment_value == "\n":
                    e.control.value = ""
                    self.environment_value = ""
                    self.environment_error_message.value = "Environment in Custom Mode cannot be empty."
                elif (
                        environment_value != new_space_str or environment_value != new_line_str or environment_value != new_comma_str or
                        "\n " in environment_value or "\n," in environment_value or " ," in environment_value or environment_value == ","):  # Checks for more than one space between words
                    raise ValueError
                else:
                    if re.match(r"^[a-zA-Z, \n]*$", environment_value):
                        self.environment_value = e.control.value
                        self.environment_error_message.value = ""
                    else:
                        e.control.value = self.environment_value
                        self.environment_error_message.value = "Only letters and commas are allowed."
                self.page.update()
            except ValueError:
                e.control.value = self.environment_value
                self.page.update()

    async def show_title_screen(self):
        """Displays the game's title screen with start and load options.
        Creates and displays the initial game interface with background and buttons.
        
        :return: None
        """
        self.page.controls.clear()
        monitor = get_monitors()[0]
        await utils.play_background_music()
        background = ft.Image(
            src="Images/background.png",
            width=monitor.width,
            height=monitor.height,
            fit=ft.ImageFit.FILL,
            top=monitor.height * 0,
        )

        gradient_container = ft.Container(
            width=monitor.width * 0.6,  # title screen blue box
            height=monitor.height * 0.47,  # title screen blue box
            left=monitor.width * 0.2,  # title screen blue box
            top=monitor.height * 0.2,  # title screen blue box
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_center,
                end=ft.alignment.bottom_center,
                colors=["#263372", ft.colors.with_opacity(0.85, ft.colors.BLACK)],
                # Blue gradient background colour opacity
            ),
            border=ft.border.all(5, "#131e5c"),
            border_radius=10,
            shadow=ft.BoxShadow(
                color=ft.colors.with_opacity(0.25, ft.colors.BLACK),
                blur_radius=6.10,
                offset=ft.Offset(6, 3),
                spread_radius=5,
            ),
        )

        title_image = ft.Image(
            src="Images/title.png",
            width=monitor.width * 0.59,  # title screen title
            height=get_title_image_height(monitor),  # title screen title
            left=monitor.width * 0.2,  # title screen title
            top=get_title_image_top(monitor),  # title screen title
            fit=ft.ImageFit.COVER,
        )

        start_button = await self.create_button("START", monitor.width * 0.25, monitor.height * 0.71,
                                                get_button_width("START", monitor), monitor.height * 0.11)
        load_button = await self.create_button("LOAD", monitor.width * 0.52, monitor.height * 0.71,
                                               get_button_width("LOAD", monitor), monitor.height * 0.11)

        stack = ft.Stack([
            background,
            gradient_container,
            title_image,
            start_button,
            load_button,
        ])

        self.page.add(stack)
        self.page.update()

    async def create_button(self, text, left, top, width, height):
        """Creates a styled button with specified text and position.
        
        :param text: The text to display on the button
        :param left: The left position of the button
        :param top: The top position of the button
        :return: ft.Container: A container with the styled button
        """
        monitor = get_monitors()[0]
        return ft.Container(
            content=ft.Stack(
                controls=[
                    ft.Image(
                        src="Images/button.png",
                        fit=ft.ImageFit.COVER,
                    ),
                    ft.Container(
                        content=ft.Text(
                            text,
                            size=monitor.width * 0.027,
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.WHITE,
                            font_family="Pixelify Sans"
                        ),
                        alignment=ft.alignment.center,
                        width=width,
                        height=height,
                    ),
                ],
            ),
            width=monitor.width * 0.25,
            height=monitor.height * 0.12,
            left=left,
            top=top,
            alignment=ft.alignment.center,
            on_click=self.button_clicked,
        )

    async def button_clicked(self, e):
        """Handles button click events on the title screen.
        Plays sound effect and triggers appropriate screen transition.
        
        :param e: The click event containing button information
        :return: None
        """
        self.button_click_sound.play()
        if e.control.content.controls[1].content.value == "LOAD":
            await self.show_load_popup()
        elif e.control.content.controls[1].content.value == "START":
            await utils.stop_background_music()
            await self.show_create_character()
        else:
            print(f"Button clicked: {e}")

    async def show_load_popup(self):
        """Displays a popup dialog for loading saved games.
        Lists available save files and handles selection.
        
        :return: None
        """
        files = await utils.list_saved_games()
        file_list = ft.ListView(
            controls=[
                ft.ListTile(
                    title=ft.Text(file, size=18, color=ft.colors.WHITE),
                    on_click=self.create_load_game_handler(file)
                ) for file in files
            ],
            expand=True,
            # auto_scroll=True
        )

        popup = ft.AlertDialog(
            title=ft.Text("Load Game", size=24, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=file_list,
                height=300,  # Set a fixed height for the container
                width=400,  # Set a fixed width for the container
            ),
            actions=[
                ft.TextButton("Close", on_click=lambda e: self.close_popup())
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.dialog = popup
        popup.open = True
        self.page.update()

    def create_load_game_handler(self, file):
        """Creates a handler function for loading a specific save file.
        
        :param file: The filename of the save file to load
        :return: callable: An async function that handles loading the specified save file
        """

        async def load_game_handler(e):
            """Handles the loading of a saved game file when selected.
            
            :param e: The click event that triggered the load
            """
            await self.load_game(file)

        return load_game_handler

    def close_popup(self):
        """Closes the currently active popup dialog.
        
        :return: None
        """
        self.page.dialog.open = False
        self.page.update()

    async def load_game(self, file):
        """Loads a saved game state and resumes the game.
        
        :param file: The filename of the save file to load
        :return: None
        :raises FileNotFoundError: If the save file is not found
        """
        done_event = asyncio.Event()
        asyncio.create_task(self.show_loading_screen(done_event))  # Show loading screen

        # Process data while loading screen is displayed
        await asyncio.sleep(0)  # Yield control to allow loading screen to display

        self.main_engine.load_save(file)  # Load the game state

        openai_api.begin_story()
        openai_api.begin_char_creation(self.main_engine.mainCharacter.name)
        update_attr.begin_update_attr()

        done_event.set()  # Signal that loading is complete
        await utils.stop_background_music()
        self.page.dialog.open = False

        self.start_message = "Previously:\n" + self.main_engine.timeline.get_event[
            -1] + "\n\nIf you want the full recap of the story from the start, click on the Timeline button!"
        await self.show_story()  # Transition to the story screen

    def start_game_button(self, e):
        """Handles the start game button click.
        Validates all required fields and shows confirmation dialog.
        
        :param e: The click event
        :return: None
        """

        def close_popup():
            """Closes the currently active popup dialog.
        
            :return: None
            """
            self.page.dialog.open = False
            self.page.update()

        # List of all fields and their corresponding error messages
        fields = {
            "Name": self.name_value,
            "Physical Condition": self.physical_condition_value,
            "Occupation": self.occupation_value,
            "Appearance": self.appearance_value,
            "Personality": self.personality_value,
            "Money": self.money_value,
            "HP": self.hp_value,
            "Luck": self.luck_value,
            "Charisma": self.cha_value,
            "Genre": self.genre_value,
        }

        # Check for missing fields
        missing_fields = [field for field, value in fields.items() if not value]

        # Hp will default back to valid version if existed
        try:
            int(self.hp_value)
        except ValueError:
            missing_fields.append("\nHP must be at least 30")

        # Luck will default back to valid version if existed
        try:
            int(self.luck_value)
        except ValueError:
            missing_fields.append("\nLuck must be at least 2")

        if missing_fields:
            missing_fields_str = ', '.join(missing_fields)
            alert_popup = ft.AlertDialog(
                title=ft.Text("Incomplete Fields", size=24, weight=ft.FontWeight.BOLD),
                content=ft.Text(f"Please fill in the following fields: {missing_fields_str}."),
                actions=[ft.TextButton("OK", on_click=lambda e: close_popup())],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            self.page.dialog = alert_popup
            alert_popup.open = True
            self.page.update()
        else:
            # If all fields are filled, show confirmation popup
            popup = ft.AlertDialog(
                title=ft.Text("Confirmation", size=24, weight=ft.FontWeight.BOLD),
                content=ft.Text("Are you satisfied with your creation?"),
                actions=[
                    ft.TextButton("Yes", on_click=self.start_game),
                    ft.TextButton("No", on_click=lambda e: close_popup())
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            self.page.dialog = popup
            popup.open = True
            self.page.update()

    def home_button(self, e):
        """Handles the home button click.
        Shows confirmation dialog for returning to main menu.
        
        :param e: The click event
        :return: None
        """

        def close_popup():
            """Closes the currently active popup dialog.
            
            :return: None
            """
            self.page.dialog.open = False
            self.page.update()

        popup = ft.AlertDialog(
            title=ft.Text("Back to main menu", size=24, weight=ft.FontWeight.BOLD),
            content=ft.Text("Are you sure you want to go back to the main menu?"),
            actions=[
                ft.TextButton("Yes", on_click=self.show_title_screen),
                ft.TextButton("No", on_click=lambda e: close_popup())
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.dialog = popup
        popup.open = True
        self.page.update()

    async def show_create_character(self):
        """Displays the character creation interface.
        Sets up all character creation fields and validation.
        
        :return: None
        """
        self.page.controls.clear()
        monitor = get_monitors()[0]
        text_style = ft.TextStyle(font_family="Pixelify Sans", color=ft.colors.WHITE, size=30)  # Note: Don't Change
        error_message_size = monitor.width * 0.009

        self.name_field = create_text_field("Name", monitor.width * 0.4, self.name_value, self.on_text_change,
                                            text_style, self.on_text_change)

        self.physical_condition_field = create_text_field("Physical Condition", monitor.width * 0.4,
                                                          self.physical_condition_value, self.on_text_change,
                                                          text_style, self.on_text_change)

        self.occupation_field = create_text_field("Occupation", monitor.width * 0.5, self.occupation_value,
                                                  self.on_text_change, text_style, self.on_text_change)

        self.appearance_field = create_text_field("Appearance", monitor.width * 0.26, self.appearance_value,
                                                  self.on_text_change, text_style, self.on_text_change, multiline=True,
                                                  height=monitor.height * 0.2)

        self.inventory_field = create_text_field("Inventory", monitor.width * 0.225, self.inventory_value,
                                                 self.on_text_change, text_style, self.on_text_change, multiline=True,
                                                 height=monitor.height * 0.2)

        self.personality_field = create_text_field("Personality", monitor.width * 0.235, self.personality_value,
                                                   self.on_text_change, text_style, self.on_text_change, multiline=True,
                                                   height=monitor.height * 0.2)

        self.money_field = create_text_field("Money", monitor.width * 0.15, self.money_value, self.on_text_change,
                                             text_style, self.on_text_change)

        self.hp_field = create_text_field("Hp", monitor.width * 0.09, self.hp_value, self.on_text_change, text_style,
                                          self.on_text_change)

        self.luck_field = create_text_field("Luck", monitor.width * 0.09, self.luck_value, self.on_text_change,
                                            text_style, self.on_text_change)

        self.cha_field = create_text_field("Cha", monitor.width * 0.09, self.cha_value, self.on_text_change,
                                           text_style, self.on_text_change)

        # Error messages
        self.name_error_message = create_error_message(error_message_size)
        self.physical_condition_error_message = create_error_message(error_message_size)
        self.occupation_error_message = create_error_message(error_message_size)
        self.appearance_error_message = create_error_message(error_message_size)
        self.inventory_error_message = create_error_message(error_message_size)
        self.personality_error_message = create_error_message(error_message_size)
        self.money_error_message = create_error_message(error_message_size)
        self.hp_error_message = create_error_message(error_message_size)
        self.luck_error_message = create_error_message(error_message_size)
        self.cha_error_message = create_error_message(error_message_size)

        main_container = ft.Container(
            width=monitor.width,
            height=monitor.height,
            bgcolor="#142158",
            content=ft.Stack(
                controls=character_screen.character_screen(
                    monitor=monitor,
                    world_button=self.world_button,
                    name_field=self.name_field,
                    name_error_message=self.name_error_message,
                    physical_condition_field=self.physical_condition_field,
                    physical_condition_error_message=self.physical_condition_error_message,
                    occupation_field=self.occupation_field,
                    occupation_error_message=self.occupation_error_message,
                    money_field=self.money_field,
                    money_error_message=self.money_error_message,
                    hp_field=self.hp_field,
                    hp_error_message=self.hp_error_message,
                    luck_field=self.luck_field,
                    luck_error_message=self.luck_error_message,
                    cha_field=self.cha_field,
                    cha_error_message=self.cha_error_message,
                    appearance_field=self.appearance_field,
                    appearance_error_message=self.appearance_error_message,
                    personality_field=self.personality_field,
                    personality_error_message=self.personality_error_message,
                    inventory_field=self.inventory_field,
                    inventory_error_message=self.inventory_error_message,
                    start_game_button=self.start_game_button
                ),
            ),
        )

        self.page.add(main_container)
        self.page.update()

    async def world_button(self, e):
        """Handles world creation button click.
        Validates character data and transitions to world creation.
        
        :param e: The click event
        :return: None
        """
        self.name_field.value = self.name_field.value.strip()
        self.occupation_field.value = self.occupation_field.value.strip()

        # Converting to list
        self.inventory_field.value = (','.join(self.inventory_field.value.split("\n"))).split(",")
        self.personality_field.value = (','.join(self.personality_field.value.split("\n"))).split(",")

        # Print the values of the text fields
        print("---")
        print("Name:", self.name_field.value)
        print("Physical Condition:", self.physical_condition_field.value)
        print("Occupation:", self.occupation_field.value)
        print("Inventory:", self.inventory_field.value)
        print("Personality:", self.personality_field.value)
        print("Money:", self.money_field.value)
        print("Hp:", self.hp_field.value)
        print("Luck:", self.luck_field.value)
        print("Cha:", self.cha_field.value)
        print("---")
        self.button_click_sound.play()

        await self.show_world_creation()

    async def show_world_creation(self):
        """Displays the world creation interface.
        Sets up world creation fields and validation.
        
        :return: None
        """
        self.page.controls.clear()
        monitor = get_monitors()[0]
        self.page.bgcolor = "#142158"
        text_style = ft.TextStyle(font_family="Pixelify Sans", color=ft.colors.WHITE, size=30)
        error_message_size = monitor.width * 0.009

        def on_rules_dropdown_change(e):
            """Handles changes in the world rules dropdown selection.
            Updates the world rules text field appearance and behaviour based on selection
            between Default and Custom modes.
            
            :param e: The dropdown change event containing the selected value
            :return: None
            """
            self.button_click_sound.play()
            if self.rules_dropdown.value == "Default":
                self.world_rules_field.bgcolor = "#3C4A87"  # Changes colour when default
                self.world_rules_field.disabled = True
                self.world_rules_field.value = ""
                self.world_rules_value = ""

            else:
                self.world_rules_field.height = monitor.height * 0.2
                self.world_rules_field.border_width = 3
                self.world_rules_field.bgcolor = "#142158"  # Changes colour when custom
                self.world_rules_field.disabled = False  # Can type
                self.world_rules_field.multiline = True
            self.page.update()

        def on_environment_dropdown_change(e):
            """Handles changes in the environment dropdown selection.
            Updates the environment text field appearance and behaviour based on selection
            between Default and Custom modes.
            
            :param e: The dropdown change event containing the selected value
            :return: None
            """
            self.button_click_sound.play()
            if self.environment_dropdown.value == "Default":
                self.environment_field.bgcolor = "#3C4A87"  # Changes colour when default
                self.environment_field.disabled = True
                self.environment_field.value = ""
                self.environment_value = ""

            else:
                self.environment_field.height = monitor.height * 0.2
                self.environment_field.border_width = 3
                self.environment_field.bgcolor = "#142158"  # Changes colour when custom
                self.environment_field.disabled = False  # Can type
                self.environment_field.multiline = True
            self.page.update()

        self.genre_field = create_text_field("Genre", monitor.width * 0.4, self.genre_value, self.on_text_change,
                                             text_style, self.on_text_change)

        self.world_rules_field = create_text_field(
            label="World Rules",
            width=monitor.width * 0.345,
            height=monitor.width * 0.1,
            value=self.world_rules_value,
            on_change=self.on_text_change,
            text_style=text_style,
            multiline=True,
            on_blur=self.on_text_change
        )

        self.environment_field = create_text_field(
            label="Environment",
            width=monitor.width * 0.345,
            value=self.environment_value,
            on_change=self.on_text_change,
            text_style=text_style,
            on_blur=self.on_text_change
        )

        # Error message
        self.genre_error_message = create_error_message(error_message_size)
        self.world_rules_error_message = create_error_message(error_message_size)
        self.environment_error_message = create_error_message(error_message_size)

        # Dropdown
        self.rules_dropdown = front_end_helpers.create_dropdown(
            on_change=on_rules_dropdown_change,
            monitor=monitor,
            content=self.world_rules_value
        )

        self.environment_dropdown = front_end_helpers.create_dropdown(
            on_change=on_environment_dropdown_change,
            monitor=monitor,
            content=self.environment_value
        )

        main_container = ft.Container(
            width=monitor.width,
            height=monitor.height,
            content=ft.Stack(
                controls=world_screen.world_screen(
                    monitor=monitor,
                    character_button=self.character_button,
                    genre_field=self.genre_field,
                    genre_error_message=self.genre_error_message,
                    world_rules_field=self.world_rules_field,
                    rules_dropdown=self.rules_dropdown,
                    world_rules_error_message=self.world_rules_error_message,
                    environment_field=self.environment_field,
                    environment_dropdown=self.environment_dropdown,
                    environment_error_message=self.environment_error_message,
                    start_game_button=self.start_game_button
                )
            )
        )

        self.page.add(main_container)
        self.page.update()

    async def start_game(self, e):
        """Initialises and starts a new game.
        Creates character and world objects, generates initial story.
        
        :param e: The click event
        :return: None
        :raises ValueError: If required game data is invalid
        """
        self.page.dialog.open = False  # Exits out of Confirmation popup
        self.page.update()

        self.button_click_sound.play()

        def generate_image_thread(prompt, character, done_event):
            """Creates a separate thread for character image generation.
            Handles asynchronous image generation to prevent UI blocking.
            
            :param prompt: The image generation prompt describing the character
            :param character: The character's name for the image filename
            :param done_event: Event to signal when image generation is complete
            :return: None
            """

            def target():
                """Target function for the image generation thread.
                Generates the character image and signals completion.
                
                :return: None
                """
                generate_image(prompt, character, "Character")
                done_event.set()

            thread = threading.Thread(target=target)
            thread.start()

        self.name_field.value = self.name_field.value.strip()
        self.occupation_field.value = self.occupation_field.value.strip()
        self.genre_field.value = self.genre_field.value.strip()

        self.inventory_field.value = process__value(self.inventory_field.value)
        self.personality_field.value = process__value(self.personality_field.value)
        self.world_rules_field.value = process__value(self.world_rules_field.value)
        self.environment_field.value = process__value(self.environment_field.value)

        done_event = asyncio.Event()  # Event to signal when image generation is done
        asyncio.create_task(self.show_loading_screen(done_event))  # Show loading screen

        generate_image_thread(
            f'''Style: Pixel art.
                    Dimensions: 16 x 16 pixels.
                    Genre: {self.genre_value}
                    Character: {self.appearance_value} with the occupation {self.occupation_value}.
                    physical condition: {self.physical_condition_value}.
                    Personality: {self.personality_value}.
                    Background: Use a white background.
                    Lighting: Simulate natural lighting to enhance colours and details.
                    Pose: Front-facing portrait, close-up.''',
            self.name_value,
            done_event
        )

        # Wait for the image generation to complete
        await done_event.wait()

        # Process data while loading screen is displayed
        char_details = [self.name_value, self.physical_condition_value, self.occupation_value, self.inventory_value,
                        self.personality_value, self.money_value, self.hp_value, self.luck_value, self.cha_value,
                        self.appearance_value]
        char_attributes: Dict[str, V] = utils.get_character_details(char_details)
        world_details = [self.genre_value, self.world_rules_value, self.environment_value]
        world_attributes: Dict[str, V] = utils.get_world_details(world_details)

        timeline_attributes: Dict[str, List[str]] = {"key_events": []}

        self.main_engine.mainCharacter = char_attributes
        self.main_engine.add_world(world_attributes)
        self.main_engine.add_timeline(timeline_attributes)

        if not self.main_engine.world.rules:
            self.main_engine.update_world_rules(self.genre_value)

        if self.main_engine.world.environment == "":
            self.main_engine.update_world_environment(self.genre_value)

        openai_api.begin_story()
        openai_api.begin_char_creation(self.main_engine.mainCharacter.name)
        update_attr.begin_update_attr()

        genre: str = self.main_engine.world.genre

        current_char_str: list[str] = self.main_engine.get_formatted_string_array()
        continuation_prompt: str = utils.get_prompt(genre, self.main_engine.mainCharacter.name,
                                                    self.main_engine.mainCharacter.cha,
                                                    True, json_dict_str=current_char_str)
        self.start_message: str = openai_api.get_story(continuation_prompt)

        # updates
        self.recent_stories.append(self.start_message)
        current_char_id_list: List[int] = [char.id for char in self.main_engine.characters]
        current_char_id_list.insert(0, self.main_engine.mainCharacter.id)
        current_char_name_list: list[str] = [char.name for char in self.main_engine.characters]
        current_char_name_list.insert(0, self.main_engine.mainCharacter.name)

        # checks if the characters have enough money
        money_char_dicts: str = self.main_engine.prepare_char_dictionaries("money")
        current_char_money_list: List[float] = [char.money for char in self.main_engine.characters]
        current_char_money_list.insert(0, self.main_engine.mainCharacter.money)
        money_updates: List[tuple[int, str, str]] = await utils.get_updates("money", self.start_message,
                                                                            money_char_dicts,
                                                                            current_char_id_list,
                                                                            current_char_name_list)
        check_valid_transaction: tuple[bool, List[tuple[int, str]]] = utils.check_money(money_updates,
                                                                                        current_char_id_list,
                                                                                        current_char_name_list,
                                                                                        current_char_money_list)

        while not check_valid_transaction[0]:
            money_message: str = utils.get_money_message(check_valid_transaction[1])

            # send a prompt to ChatGPT to ask it to regenerate the story
            self.start_message = openai_api.get_story(money_message)

            self.recent_stories.pop()
            self.recent_stories.append(self.start_message)

            money_updates = await utils.get_updates("money", self.start_message, money_char_dicts,
                                                    current_char_id_list, current_char_name_list)
            check_valid_transaction = utils.check_money(money_updates, current_char_id_list,
                                                        current_char_name_list, current_char_money_list)

        physical_condition_char_dicts: str = self.main_engine.prepare_char_dictionaries(
            "physical_condition")
        relationship_char_dicts: str = self.main_engine.prepare_char_dictionaries("relationship")
        inventory_char_dicts: str = self.main_engine.prepare_char_dictionaries("inventory")
        hp_char_dicts: str = self.main_engine.prepare_char_dictionaries("hp")
        current_location_char_dicts: str = self.main_engine.prepare_char_dictionaries("current_location")

        await asyncio.gather(
            self.main_engine.update_char_physical_condition(
                await utils.get_updates("physical_condition", self.start_message, physical_condition_char_dicts,
                                        current_char_id_list, current_char_name_list)),
            self.main_engine.update_char_money(money_updates),
            self.main_engine.update_char_relationship(
                await utils.get_updates("relationship", self.start_message, relationship_char_dicts,
                                        current_char_id_list, current_char_name_list)),
            self.main_engine.update_char_inventory(
                await utils.get_updates("inventory", self.start_message, inventory_char_dicts, current_char_id_list,
                                        current_char_name_list)),
            self.main_engine.update_char_hp(
                await utils.get_updates("hp", self.start_message, hp_char_dicts, current_char_id_list,
                                        current_char_name_list)),
            self.main_engine.update_char_current_location(self.start_message,
                                                          await utils.get_updates("current_location",
                                                                                  self.start_message,
                                                                                  current_location_char_dicts,
                                                                                  current_char_id_list,
                                                                                  current_char_name_list)),
            self.main_engine.update_key_events(self.start_message)
        )
        self.reset_count += 1
        update_attr.reset_chat(self.reset_count)

        self.main_engine.save_game()

        await self.show_story()

    async def character_button(self, e):
        """Handles character button click in world creation.
        Returns to character creation screen.
        
        :param e: The click event
        :return: None
        """
        self.button_click_sound.play()
        self.genre_field.value = self.genre_field.value.strip()

        # Converting to list
        if isinstance(self.world_rules_field.value, str):
            self.world_rules_field.value = (','.join(self.world_rules_field.value.split("\n"))).split(",")
        if isinstance(self.world_rules_field.value, str):
            self.environment_field.value = (','.join(self.environment_field.value.split("\n"))).split(",")

        # Print the values of the text fields
        print("---")
        print("Genre:", self.genre_field.value)
        print("World Rules:", self.world_rules_field.value)
        print("Environment:", self.environment_field.value)
        print("---")
        await self.show_create_character()

    async def show_loading_screen(self, done_event: asyncio.Event):
        """Displays an animated loading screen.
        Shows loading messages until the done_event is set.
        
        :param done_event: Event that signals when loading is complete
        :return: None
        """
        self.page.controls.clear()
        monitor = get_monitors()[0]

        loading_text = loading_text = ft.Text(
            "Loading...",
            size=monitor.width * 0.05,
            color="white",
            font_family="Pixelify Sans",
            text_align=ft.TextAlign.CENTER
        )

        loading_container = ft.Container(
            width=monitor.width,
            height=monitor.height,
            bgcolor="#263372",
            padding=20,
            content=ft.Stack(
                controls=[loading_text],
                alignment=ft.alignment.center
            )
        )

        self.page.add(loading_container)
        self.page.update()

        messages = ["Loading", "Please wait", "Almost there", "Preparing your adventure",
                    f"Out of everything, you chose {self.name_value}?", "Just a moment", "Loading your character",
                    "Loading your world", "Loading your story", "Loading your adventure",
                    f"Personally not a fan of {self.genre_value} but okay","Fun Fact one of our members leaked another members API Key",
                    "This is taking longer than expected", "Fun Fact this project was the start of a youtube career for someone in our group",
                    "Interesting appearance you chose",f"Seriously your fantasy was to be a {self.occupation_value}?","ᚺᚢᛊᚺ, ᛚᛁᛏᛏᛚᛖ ᛒᚨᛒᛁ, ᛞᛟᚾ×ᛏ ᛊᚨᛁ ᚨ ᚹᛟᚱᛞ",
                    "We are Team PK Fire and Ness is our mascot","Fun Fact one of our team members made 7 google docs on prompt engineering",
                    "Fun Fact The number of one member's commits skyrocketed after working on documentation","Fun Fact we were initially going to be called owen and his pals",]

        async def update_message():
            """Updates the loading screen message periodically.
            Cycles through a list of predefined messages while loading is in progress.
            Uses asyncio for non-blocking message updates.
            
            :return: None
            """
            i = 0
            while not done_event.is_set():
                loading_text.value = random.choice(messages)
                self.page.update()
                await asyncio.sleep(4)  # Adjust the delay as needed
                i += 1

        async def update_dots():
            """Animates loading dots after the current message.
            Creates a visual loading animation by cycling through dot patterns (., .., ..., ....).
            Uses asyncio for non-blocking animation updates.
            
            :return: None
            """
            j = 0
            while not done_event.is_set():
                loading_text.value = loading_text.value.split(".")[0] + "." * (j % 4)
                self.page.update()
                await asyncio.sleep(0.5)  # Adjust the delay as needed
                j += 1

        await asyncio.gather(update_message(), update_dots())

    async def show_death_popup(self):
        """Displays death notification popup when character dies.
        
        :return: None
        """
        self.close_popup()
        death_popup = ft.AlertDialog(
            title=ft.Text("Character Deceased"),
            content=ft.Text("Your character has died. The game will now end."),
            actions=[
                ft.TextButton("OK", on_click=lambda e: self.close_popup())
            ],
            on_dismiss=lambda e: self.page.dialog.close()
        )
        self.page.dialog = death_popup
        death_popup.open = True
        self.page.update()

    async def show_low_hp_popup(self):
        """Displays warning popup when character HP is low.
        
        :return: None
        """
        low_hp_popup = ft.AlertDialog(
            title=ft.Text("Low HP Warning"),
            content=ft.Text("Your character's HP is low. Please take action to restore health."),
            actions=[
                ft.TextButton("OK", on_click=lambda e: self.close_popup())
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog = low_hp_popup
        low_hp_popup.open = True
        self.page.update()

    async def show_story(self):
        """Displays the main story interface.
        Sets up story display, input field, and UI elements.
        
        :return: None
        """
        self.page.controls.clear()
        monitor = get_monitors()[0]
        self.page.window.width = monitor.width
        self.page.window.height = monitor.height
        self.page.padding = 0  # Remove screen padding

        self.page.bgcolor = ft.colors.WHITE
        self.page.fonts = {
            "Pixelify Sans": "fonts/PixelifySans-VariableFont_wght.ttf"
        }

        self.page.window.full_screen = False
        self.page.window.maximized = True

        conversation = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, auto_scroll=True)
        typing_sound = pygame.mixer.Sound('assets/Sounds/typing_sound.mp3')
        typing_sound.set_volume(0.5)
        effect_sound = pygame.mixer.Sound('assets/Sounds/effect_triggered.mp3')
        self.hp_sound = False

        async def type_effect(text, display_field, speed=0.02):
            """Creates a typewriter effect for text display with sound.
            Displays text character by character with a typing sound effect
            and automatic scrolling.
            
            :param text: The text to display with the typing effect
            :param display_field: The text field to display the characters in
            :param speed: The delay between each character (default: 0.02 seconds)
            :return: None
            """
            display_field.value = ""
            typing_sound.play(loops=-1)
            for char in text:
                display_field.value += char
                display_field.scroll_to_end = True  # Enable autoscroll
                display_field.update()
                await asyncio.sleep(speed)
            typing_sound.stop()

        async def add_message(sender, message):
            """Adds a new message to the conversation with appropriate styling.
            Creates a container for the message with different colors based on
            the sender (User/Event/AI) and applies the typewriter effect.
            
            :param sender: The sender of the message ("User", "Event", or "AI")
            :param message: The content of the message to display
            :return: None
            """
            message_container = ft.Container(
                content=create_stats_text(value="", size=20),
                width=monitor.width * 0.75,
                padding=10,
                bgcolor="#283460" if sender == "User" else ("#562135" if sender == "Event" else ft.colors.BLACK),
                border=ft.border.all(3, "#EE8067" if sender == "User" else (
                    "#ffb7c5" if sender == "Event" else ft.colors.TRANSPARENT)),
                border_radius=5,
                margin=ft.margin.only(bottom=10)
            )
            conversation.controls.append(message_container)
            self.page.update()

            await type_effect(message, message_container.content)

        genre: str = self.main_engine.world.genre

        stats_size = monitor.width * 0.014
        physical_condition_size = monitor.width * 0.01

        self.hp_stats = create_stats_text(f"{self.main_engine.mainCharacter.hp}", stats_size)
        self.luck_stats = create_stats_text(f"{self.main_engine.mainCharacter.luck}", stats_size)
        self.cha_stats = create_stats_text(f"{self.main_engine.mainCharacter.cha}", stats_size)
        self.money_stats = create_stats_text(f"{self.main_engine.mainCharacter.money}", stats_size)
        self.physical_condition_stats = create_stats_text(f"{self.main_engine.mainCharacter.physical_condition}",
                                                          physical_condition_size)

        async def on_input_submit(e):
            """Handles user input submission in the story interface.
            Processes user messages, checks inventory requirements, manages story progression,
            and updates character states.
            
            :param e: The submit event containing the user's input
            :return: None
            :raises: ValueError: If story generation fails
            """
            if input_box.value:
                user_message = input_box.value
                input_box.value = ""
                await add_message("User", user_message)
                input_box.update()

                # Perform inventory check before any updates
                check_responses: tuple[bool, str] = await self.main_engine.check_inventory(user_message)
                while check_responses[0]:
                    inventory_message = f"{check_responses[1]}\nPlease use an item in your inventory: {self.main_engine.mainCharacter.inventory}"
                    await add_message("AI", inventory_message)

                    # Wait for user input from the UI
                    user_input_event = asyncio.Event()
                    original_on_submit = input_box.on_submit
                    input_box.on_submit = lambda e: user_input_event.set()
                    await user_input_event.wait()

                    user_message = input_box.value
                    input_box.value = ""
                    await add_message("User", user_message)

                    check_responses = await self.main_engine.check_inventory(user_message)

                    # Restore original on_submit handler
                    input_box.on_submit = original_on_submit

                input_box.disabled = True
                await asyncio.sleep(1)  # 1 second delay
                await add_message("AI", "Response generating please wait...")

                async def story(story_cont):
                    """Processes story progression and updates game state based on user input.
                    Controls story generation, character updates, random events, and manages game state
                    including money transactions, character stats, and saving functionality.
                    
                    :param story_cont: User's story continuation input
                    :return: None
                    :raises ValueError: If story generation or updates fail
                    """
                    prev_money: float = self.main_engine.mainCharacter.money
                    current_char_str: str = self.main_engine.get_formatted_string_array()[0]
                    current_char_id_list: List[int] = [char.id for char in self.main_engine.characters]
                    current_char_id_list.insert(0, self.main_engine.mainCharacter.id)
                    current_char_name_list: List[str] = [char.name for char in self.main_engine.characters]
                    current_char_name_list.insert(0, self.main_engine.mainCharacter.name)
                    current_alive_characters: List[int] = [char.id for char in self.main_engine.characters if
                                                           char.hp != 0]
                    new_char_check: bool = False if len(current_alive_characters) >= 10 else True

                    if self.event_count == 1:
                        # random events
                        effect_sound.play()
                        event: list[str | int | tuple[str, str]] = self.main_engine.random_event(
                            self.main_engine.mainCharacter.luck)
                        name_event_string: str = utils.replace_id_with_name(event[0], current_char_id_list,
                                                                            current_char_name_list)
                        self.page.window.focused = True
                        conversation.controls.pop()
                        await add_message("Event", f"A random event has occurred! {name_event_string}")
                        await add_message("AI", "Response generating please wait...")
                        random_event = event[0]
                    else:
                        random_event = None

                    char_deceased = self.deceased_character_line if self.deceased_character_line != "" else None

                    continuation_prompt: str = utils.get_prompt(
                        genre,
                        self.main_engine.mainCharacter.name,
                        self.main_engine.mainCharacter.cha,
                        False,
                        user_input=story_cont,
                        char_str=current_char_str,
                        new_char=new_char_check,
                        random_event=random_event,
                        char_deceased=char_deceased
                    )
                    print(continuation_prompt)
                    continuation_story: str = openai_api.get_story(continuation_prompt)
                    if len(self.recent_stories) < 3:
                        self.recent_stories.append(continuation_story)
                    else:
                        self.recent_stories.pop(0)
                        self.recent_stories.append(continuation_story)
                    full_story: str = "\n".join(self.recent_stories)

                    # checks if the characters have enough money
                    money_char_dicts: str = self.main_engine.prepare_char_dictionaries("money")
                    current_char_money_list: List[float] = [char.money for char in self.main_engine.characters]
                    current_char_money_list.insert(0, self.main_engine.mainCharacter.money)
                    money_updates: List[tuple[int, str, str]] = await utils.get_updates("money", continuation_story,
                                                                                        money_char_dicts,
                                                                                        current_char_id_list,
                                                                                        current_char_name_list)
                    check_valid_transaction: tuple[bool, List[tuple[int, str]]] = utils.check_money(money_updates,
                                                                                                    current_char_id_list,
                                                                                                    current_char_name_list,
                                                                                                    current_char_money_list)

                    while not check_valid_transaction[0]:
                        money_message: str = utils.get_money_message(check_valid_transaction[1])

                        # send a prompt to ChatGPT to ask it to regenerate the story
                        continuation_story = openai_api.get_story(money_message)

                        self.recent_stories.pop()
                        self.recent_stories.append(continuation_story)
                        full_story = "\n".join(self.recent_stories)

                        money_updates = await utils.get_updates("money", continuation_story, money_char_dicts,
                                                                current_char_id_list, current_char_name_list)
                        check_valid_transaction = utils.check_money(money_updates, current_char_id_list,
                                                                    current_char_name_list, current_char_money_list)
                    conversation.controls.pop()
                    self.page.update()
                    await add_message("AI", continuation_story)
                    self.story_msgs.append(continuation_story)

                    current_char_name_list.pop(0)  # remove the main character's name
                    npc_bool, new_char_list = openai_api.npc_creation_check(continuation_story, current_char_name_list)

                    if npc_bool:
                        new_char_id: int = self.main_engine.get_char_id()
                        print(new_char_id)
                        char_str: str = openai_api.create_npc(new_char_list, continuation_story, genre, new_char_id)
                        char_dicts = utils.convert_to_json(char_str)
                        for char in char_dicts:
                            self.main_engine.add_character(char)

                    current_char_id_list = [char.id for char in self.main_engine.characters]
                    current_char_id_list.insert(0, self.main_engine.mainCharacter.id)
                    current_char_name_list = [char.name for char in self.main_engine.characters]
                    current_char_name_list.insert(0, self.main_engine.mainCharacter.name)

                    physical_condition_char_dicts: str = self.main_engine.prepare_char_dictionaries(
                        "physical_condition")
                    relationship_char_dicts: str = self.main_engine.prepare_char_dictionaries("relationship")
                    inventory_char_dicts: str = self.main_engine.prepare_char_dictionaries("inventory")
                    hp_char_dicts: str = self.main_engine.prepare_char_dictionaries("hp")
                    current_location_char_dicts: str = self.main_engine.prepare_char_dictionaries("current_location")

                    await asyncio.gather(
                        self.main_engine.update_char_physical_condition(
                            await utils.get_updates("physical_condition", full_story, physical_condition_char_dicts,
                                                    current_char_id_list, current_char_name_list)),
                        self.main_engine.update_char_money(money_updates),
                        self.main_engine.update_char_relationship(
                            await utils.get_updates("relationship", full_story, relationship_char_dicts,
                                                    current_char_id_list, current_char_name_list)),
                        self.main_engine.update_char_inventory(
                            await utils.get_updates("inventory", continuation_story, inventory_char_dicts,
                                                    current_char_id_list,
                                                    current_char_name_list)),
                        self.main_engine.update_char_hp(
                            await utils.get_updates("hp", full_story, hp_char_dicts, current_char_id_list,
                                                    current_char_name_list)),
                        self.main_engine.update_char_current_location(full_story,
                                                                      await utils.get_updates("current_location",
                                                                                              full_story,
                                                                                              current_location_char_dicts,
                                                                                              current_char_id_list,
                                                                                              current_char_name_list)),
                        self.main_engine.update_key_events(continuation_story)
                    )
                    self.reset_count += 1
                    update_attr.reset_chat(self.reset_count)

                    if self.event_count == 1:
                        # make sure the random event don't double update
                        self.main_engine.double_update_check(event[1], event[2], prev_money)
                        self.event_count = random.randint(2, 10)

                    # update the stats visually
                    self.hp_stats.value = self.main_engine.mainCharacter.hp
                    if int(self.hp_stats.value) < 10:
                        if not self.hp_sound:
                            pygame.mixer.Sound('assets/Sounds/Please_heal.mp3').play()
                            self.hp_sound = True
                            await self.show_low_hp_popup()
                    else:
                        self.hp_sound = False
                    self.luck_stats.value = self.main_engine.mainCharacter.luck
                    self.cha_stats.value = self.main_engine.mainCharacter.cha
                    self.money_stats.value = self.main_engine.mainCharacter.money
                    self.physical_condition_stats.value = self.main_engine.mainCharacter.physical_condition

                    # save game
                    self.main_engine.save_game()

                    mc_deceased_check, self.deceased_character_line = self.main_engine.check_characters_deceased(genre)
                    if mc_deceased_check:
                        await self.show_death_popup()
                        story_cont = "end"
                        if self.deceased_character_line != "":
                            # call the continuing story prompt with the new user message to wrap up the story
                            ending_story: str = openai_api.get_story(self.deceased_character_line)
                            await add_message("AI", ending_story)
                            self.story_msgs.append(ending_story)

                            # final updates
                            await asyncio.gather(
                                self.main_engine.update_char_relationship(
                                    await utils.get_updates("relationship", ending_story, relationship_char_dicts,
                                                            current_char_id_list, current_char_name_list)),
                                self.main_engine.update_char_inventory(
                                    await utils.get_updates("inventory", ending_story, inventory_char_dicts,
                                                            current_char_id_list, current_char_name_list)),
                                self.main_engine.update_char_current_location(ending_story,
                                                                              await utils.get_updates(
                                                                                  "current_location", ending_story,
                                                                                  current_location_char_dicts,
                                                                                  current_char_id_list,
                                                                                  current_char_name_list)),
                                self.main_engine.update_key_events(ending_story)
                            )
                        input_box.disabled = True
                        self.is_dead = True
                        await add_message("AI", "The end! Thank you for playing!")

                    self.story_msgs.append(f"Your input: {story_cont}")
                    print()
                    self.event_count -= 1

                # await add_message("AI", ai_message)
                await story(user_message)
                input_box.disabled = self.is_dead

                self.page.update()

        def show_popup(label):
            """Displays a popup window with specific game information.
            Shows different content based on the label (Inventory, Relationship, Location, Timeline, or Characters).
            
            :param label: The type of information to display
            :return: None
            """

            def close_popup(e):
                """Removes the current popup from the page overlay.
                Handles cleanup of popup UI elements when closing.
                
                :param e: The event that triggered the popup closure
                :return: None
                """
                self.page.overlay.remove(popup)
                self.page.update()

            if label == "Inventory":
                content = []
                for item in self.main_engine.mainCharacter.inventory:
                    file_path = f"assets/Item_portraits/{item}.png"
                    if os.path.isfile(file_path):
                        item_row = ft.Row([
                            ft.Image(
                                src=f"Item_portraits/{item}.png",
                                width=monitor.width * 0.03,
                                height=monitor.width * 0.03,
                                fit=ft.ImageFit.CONTAIN
                            ),
                            ft.Text(
                                item,
                                width=monitor.width * 0.14,
                                size=monitor.width * 0.01,
                                color=ft.colors.WHITE,
                                selectable=True,
                            )
                        ])
                        content.append(item_row)
                    else:
                        # Generate the image in the background
                        def generate_image_background():
                            """Generates a pixel art image for a game item in the background.
                            Creates a 16-bit style pixel art image for an inventory item
                            that matches the game's genre.
                            
                            :return: None
                            """
                            generate_image(
                                f"Generate a 16 bit pixel art image for a game item called {item} that will be used in a game with the genre{genre},",
                                item, "Item")

                        threading.Thread(target=generate_image_background).start()
                        item_row = ft.Row([
                            ft.Text(
                                f"Generating image for {item}...\n",
                                width=monitor.width * 0.18,
                                size=monitor.width * 0.01,
                                color=ft.colors.WHITE,
                            )
                        ])
                        content.append(item_row)
            elif label == "Relationship":
                content = [ft.Text(
                    "".join([
                        f"- {char.name}: {self.main_engine.mainCharacter.relationship[char.id] if char.id in self.main_engine.mainCharacter.relationship.keys() else ''}\n"
                        for char in self.main_engine.characters if char.name != self.main_engine.mainCharacter.name]),
                    size=monitor.width * 0.01,
                    color=ft.colors.WHITE,
                    selectable=True,
                )]
            elif label == "Location":
                content = [ft.Text(
                    "".join([
                        f"- {location} {'(Current Location)' if location == self.main_engine.mainCharacter.current_location else ''}\n"
                        for location in self.main_engine.world.locations]),
                    size=monitor.width * 0.01,
                    color=ft.colors.WHITE,
                    selectable=True,
                )]
            elif label == "Timeline":
                content = [ft.Text(
                    "".join([f"- {event}\n\n" for event in self.main_engine.timeline.get_event]),
                    size=monitor.width * 0.01,
                    color=ft.colors.WHITE,
                    selectable=True,
                )]
            elif label == "Characters":
                content = []
                for char in self.main_engine.characters:
                    print(genre)
                    file_path = f"assets/NPC_portraits/{genre}/{char.name}.png"
                    if os.path.isfile(file_path):
                        file_path = f"NPC_portraits/{genre}/{char.name}.png"
                        content.append(ft.Image(src=file_path, width=100, height=100))
                    else:
                        content.append(ft.Text(f"Generating image for {char.name}..."))

                        def generate_image_background():
                            """Generates a pixel art portrait for an NPC character in the background.
                            Creates a detailed 16x16 pixel character portrait incorporating the NPC's
                            appearance, occupation, and personality traits.
                            
                            :return: None
                            """
                            generate_image(
                                f'''Style: Pixel art.
                                    Dimensions: 16 x 16 pixels.
                                    Character: {char.appearance} with the occupation {char.occupation}.
                                    Personality: {char.personality}.
                                    Background: Use a white background.
                                    Lighting: Simulate natural lighting to enhance colours and details.
                                    Pose: Front-facing portrait, close-up.
                                    Genre: {genre}''',
                                char.name, "NPC",genre)

                        file_path = f"images/default.png"
                        threading.Thread(target=generate_image_background).start()
                        print("Generating image for character...")
                        content.append(ft.Image(src=file_path, width=100, height=100))
                    content.append(ft.Text(
                        f"Name: {char.name}\n"
                        f"Occupation: {char.occupation}\n"
                        f"Physical Condition: {char.physical_condition}\n"
                        f"HP: {char.hp}\n"
                        f"Money: {char.money}\n"
                        f"Inventory: {format_inventory(char.inventory)}\n"
                        f"Personality: {char.personality}\n"
                        f"Relationship: {self.main_engine.relationship_to_name(char)}\n"
                        f"Current Location: {char.current_location}\n"
                        f"**************************************************\n",
                        selectable=True,
                    ))

            popup = ft.Container(
                top=monitor.height * 0.45,
                left=monitor.width * 0.014,
                width=monitor.width * 0.2,
                height=monitor.height * (0.24 + 0.14),
                bgcolor="#040B26",
                content=ft.Stack([
                    ft.Container(
                        padding=monitor.width * 0.01,
                        content=create_stats_text(value=f"{label}", size=monitor.width * 0.0125),
                    ),
                    ft.Container(
                        padding=ft.padding.only(top=monitor.height * 0.05, left=monitor.width * 0.01,
                                                bottom=monitor.height * 0.018, right=monitor.width * 0.014),
                        content=ft.ListView(
                            controls=content,
                            height=monitor.height * 0.3,
                        ),
                    ),
                    ft.Container(
                        height=monitor.height * 0.046,
                        on_click=close_popup,
                        alignment=ft.alignment.top_right,
                        padding=ft.padding.only(right=monitor.width * 0.005, top=monitor.height * 0.009),
                        content=create_stats_text(value="x", size=monitor.width * 0.0125),
                    ),
                ]),
            )
            self.page.overlay.append(popup)
            self.page.update()

        def create_button(label, top):
            """Creates a styled button for the game interface sidebar.
            
            :param label: The text to display on the button
            :param top: The top position of the button
            :return: ft.Container: A container with the styled button
            """
            return ft.Container(
                left=monitor.width * 0.014,
                top=top,
                width=monitor.width * 0.2,
                height=monitor.height * 0.05,
                bgcolor="#8E9DDA",
                content=ft.Row(
                    controls=[
                        ft.Container(
                            content=create_stats_text(value=label, size=monitor.width * 0.014),
                            padding=ft.padding.only(left=monitor.width * 0.0125)
                        )
                    ],
                    expand=True,
                    alignment="start"
                ),
                shadow=ft.BoxShadow(
                    color=ft.colors.with_opacity(0.25, ft.colors.BLACK),
                    blur_radius=2,
                    offset=ft.Offset(3, 3),
                    spread_radius=3,
                ),
                on_click=lambda e: show_popup(label)
            )

        button_labels = ["Inventory", "Relationship", "Location", "Timeline", "Characters"]
        button_positions = [monitor.height * 0.45, monitor.height * (0.45 + 0.08), monitor.height * (0.45 + 0.16),
                            monitor.height * (0.45 + 0.24), monitor.height * (0.45 + 0.32)]
        buttons = [create_button(label, top) for label, top in zip(button_labels, button_positions)]

        def end_button():
            """Creates the end game button with confirmation dialogs.
            Handles game ending logic including story export options.
            
            :return: ft.Container: A container with the end game button
            """

            def end_action(e):
                """Displays end game confirmation dialog.
                Shows a popup asking user to confirm if they want to end the game.
                
                :param e: The event that triggered the end action
                :return: None
                """
                popup = ft.AlertDialog(
                    title=ft.Text("End Game", size=24, weight=ft.FontWeight.BOLD),
                    content=ft.Text("Are you sure you want to end the game?"),
                    actions=[
                        ft.TextButton("Yes", on_click=lambda e: end_game()),
                        ft.TextButton("No", on_click=lambda e: close_popup())
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )

                self.page.dialog = popup
                popup.open = True
                self.page.update()

            def close_popup():
                """Closes the currently active popup dialog.
                
                :return: None
                """
                self.page.dialog.open = False
                self.page.update()

            def end_game():
                """Handles the game ending process.
                Closes confirmation popup and initiates story export dialog.
                
                :return: None
                """
                close_popup()
                export_story_popup()

            def export_story_popup():
                """Displays story export confirmation dialog.
                Shows a popup asking user if they want to export their story
                before closing the application.
                
                :return: None
                """
                popup = ft.AlertDialog(
                    title=ft.Text("Export Story", size=24, weight=ft.FontWeight.BOLD),
                    content=ft.Text("Do you want to export your story?"),
                    actions=[
                        ft.TextButton("Yes", on_click=lambda e: export_story()),
                        ft.TextButton("No", on_click=lambda e: close_application())
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )

                self.page.dialog = popup
                popup.open = True
                self.page.update()

            def export_story():
                """Handles story export and application closure.
                Exports the story to a file and closes the application.
                
                :return: None
                """
                self.main_engine.export_final_story(self.story_msgs)
                print("Story exported")
                close_popup()
                self.page.window.close()  # Close the application

            def close_application():
                """Closes the application without exporting.
                Handles clean application shutdown when export is declined.
                
                :return: None
                """
                close_popup()
                self.page.window.close()  # Close the application

            return ft.Container(
                left=monitor.width * 0.014,
                top=monitor.height * 0.85,
                width=monitor.width * 0.05,
                height=monitor.height * 0.05,
                bgcolor="#FF6961",  # Red
                content=ft.Row(
                    controls=[
                        ft.Container(
                            content=create_stats_text(value="End", size=monitor.width * 0.014),
                            padding=ft.padding.only(left=monitor.width * 0.0125)
                        )
                    ],
                    expand=True,
                    alignment="start"
                ),
                shadow=ft.BoxShadow(
                    color=ft.colors.with_opacity(0.25, ft.colors.BLACK),
                    blur_radius=2,
                    offset=ft.Offset(3, 3),
                    spread_radius=3,
                ),
                on_click=end_action
            )

        input_box = ft.TextField(
            label="What will you do?",
            width=monitor.width * 0.75,
            border_width=3,
            bgcolor="#313131",
            color=ft.colors.WHITE,
            text_size=24,
            text_style=ft.TextStyle(font_family="Pixelify Sans"),
            on_submit=on_input_submit,
            cursor_color=ft.colors.WHITE,
            max_lines=3,
        )

        input_container = ft.Container(
            content=input_box,
            left=monitor.width * 0.23,
            top=monitor.height * 0.835,
            height=(input_box.text_size * 1.5) * 3,
            padding=20
        )

        main_container = ft.Container(
            width=monitor.width,
            height=monitor.height,
            content=ft.Stack([
                ft.Container(
                    width=monitor.width * 0.23,
                    height=monitor.height,
                    bgcolor="#263372"
                ),
                ft.Container(
                    left=monitor.width * 0.01,
                    top=monitor.height * 0.02,
                    width=monitor.width * 0.0677,
                    height=monitor.height * 0.1203,
                    border=ft.border.all(5, "#8E9DDA"),
                    content=ft.Image(
                        src=f"Character_portraits/{self.main_engine.mainCharacter.name}.png",
                        fit=ft.ImageFit.COVER
                    )
                ),
                ft.Container(
                    left=monitor.width * 0.09,
                    top=monitor.height * 0.018,
                    content=ft.Column(
                        controls=[
                            ft.Container(
                                content=ft.Text(
                                    f"{self.main_engine.mainCharacter.name}",
                                    color=ft.colors.WHITE,
                                    size=monitor.width * 0.017,
                                    font_family="Pixelify Sans",
                                ),
                                padding=ft.Padding(top=0, bottom=0, left=10, right=20),
                            ),
                        ],
                        scroll=ft.ScrollMode.ALWAYS,  # Enable scrolling
                        width=monitor.width * 0.13,
                        height=monitor.height * 0.13
                    ),
                ),
                ft.Container(
                    left=monitor.width * 0.01,
                    top=monitor.height * 0.15,
                    content=self.physical_condition_stats
                ),
                ft.Column(
                    [
                        ft.Text("Hp", color=ft.colors.WHITE, size=monitor.width * 0.014, font_family="Pixelify Sans"),
                        ft.Text("Luck", color=ft.colors.WHITE, size=monitor.width * 0.014, font_family="Pixelify Sans"),
                        ft.Text("Cha", color=ft.colors.WHITE, size=monitor.width * 0.01428,
                                font_family="Pixelify Sans"),
                        ft.Text("$$$", color=ft.colors.WHITE, size=monitor.width * 0.014, font_family="Pixelify Sans")
                    ],
                    left=monitor.width * 0.014,
                    top=monitor.height * 0.21,
                    spacing=5,
                ),
                ft.Column(
                    [
                        self.hp_stats,
                        self.luck_stats,
                        self.cha_stats,
                        self.money_stats

                    ],
                    left=monitor.width * (0.014 + 0.08),
                    top=monitor.height * 0.21,
                    spacing=5,
                ),
                ft.Container(
                    left=monitor.width * 0.23,
                    width=monitor.width * 0.77,
                    height=monitor.height * 0.14,
                    bgcolor="#050C27",
                    content=ft.Image(
                        src="images/background.png",
                        fit=ft.ImageFit.FIT_WIDTH
                    ),
                ),
                ft.Container(
                    left=monitor.width * 0.23,
                    width=monitor.width * 0.77,
                    height=monitor.height * 0.14,
                    content=ft.Image(
                        src="images/title.png",
                        fit=ft.ImageFit.CONTAIN
                    ),
                ),
                *buttons,
                end_button(),
                ft.Container(
                    left=monitor.width * 0.23,
                    top=monitor.height * 0.14,
                    width=monitor.width * 0.78,
                    height=monitor.height * 0.86,
                    bgcolor=ft.colors.BLACK
                ),
                ft.Container(
                    left=monitor.width * 0.24,
                    top=monitor.height * 0.14,
                    width=monitor.width * 0.78,
                    height=monitor.height * 0.69,
                    content=conversation,
                ),
                input_container,
            ])
        )

        self.page.add(main_container)
        self.page.update()
        input_box.disabled = True
        await add_message("AI", self.start_message)
        input_box.disabled = False
        self.page.update()


if __name__ == '__main__':
    app = GameApp()
    asyncio.run(ft.app(target=app.main, assets_dir="assets"))
