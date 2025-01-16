from screeninfo import Monitor
import flet as ft
from Frontend import front_end_helpers


def character_screen(monitor: Monitor,
                     world_button: callable,
                     name_field: ft.TextField,
                     name_error_message: ft.Text,
                     physical_condition_field: ft.TextField,
                     physical_condition_error_message: ft.Text,
                     occupation_field: ft.TextField,
                     occupation_error_message: ft.Text,
                     money_field: ft.TextField,
                     money_error_message: ft.Text,
                     hp_field: ft.TextField,
                     hp_error_message: ft.Text,
                     luck_field: ft.TextField,
                     luck_error_message: ft.Text,
                     cha_field: ft.TextField,
                     cha_error_message: ft.Text,
                     appearance_field: ft.TextField,
                     appearance_error_message: ft.Text,
                     personality_field: ft.TextField,
                     personality_error_message: ft.Text,
                     inventory_field: ft.TextField,
                     inventory_error_message: ft.Text,
                     start_game_button: callable):
    """
    Sets up and displays the character creation screen in the application interface.

    :param monitor: The display or control monitor for rendering the character screen.
    :param world_button: A callback function that, when triggered, redirects the user to the
                         world customisation screen.
    :param name_field: Input field for the character's name.
    :param name_error_message: Text element to display errors related to the name input.
    :param physical_condition_field: Input field for the character's physical condition.
    :param physical_condition_error_message: Text element to display errors related to the
                                             physical condition input.
    :param occupation_field: Input field for the character's occupation.
    :param occupation_error_message: Text element to display errors related to the occupation input.
    :param money_field: Input field for the character's monetary assets.
    :param money_error_message: Text element to display errors related to the money input.
    :param hp_field: Input field for the character's health points (HP).
    :param hp_error_message: Text element to display errors related to the HP input.
    :param luck_field: Input field for the character's luck stat.
    :param luck_error_message: Text element to display errors related to the luck input.
    :param cha_field: Input field for the character's charisma (CHA) stat.
    :param cha_error_message: Text element to display errors related to the charisma input.
    :param appearance_field: Input field for the character's appearance description.
    :param appearance_error_message: Text element to display errors related to the appearance input.
    :param personality_field: Input field for the character's personality traits.
    :param personality_error_message: Text element to display errors related to the personality input.
    :param inventory_field: Input field for listing items in the character's inventory.
    :param inventory_error_message: Text element to display errors related to the inventory input.
    :param start_game_button: A callback function that initiates the game when the user completes
                              character setup.
    """
    return [
        ft.Container(  # World Creation tab Shadow
            left=monitor.width * (0.032 + 0.514 - 0.0025),  # Character creation left + width - 0.0025
            top=monitor.height * 0.05,
            width=monitor.width * (0.93 - 0.514 + 0.008),
            height=monitor.height * 0.122,
            shadow=ft.BoxShadow(
                color=ft.colors.with_opacity(0.25, ft.colors.BLACK),
                blur_radius=4,
                offset=ft.Offset(10, 10),
            ),
        ),
        ft.Container(  # Character Detail Body
            left=monitor.width * 0.032,
            top=monitor.height * 0.16,
            width=monitor.width * 0.9355,
            height=monitor.height * 0.75,
            bgcolor="#393B77",
            shadow=ft.BoxShadow(
                color=ft.colors.with_opacity(0.25, ft.colors.BLACK),
                blur_radius=4,
                offset=ft.Offset(10, 10),
            ),
        ),
        ft.Container(  # Character Creation Tab
            left=monitor.width * 0.032,
            top=monitor.height * 0.041,
            width=monitor.width * 0.514,
            height=monitor.height * 0.122,
            bgcolor="#393B77",
        ),
        ft.Container(  # Grid
            left=monitor.width * 0.032,
            top=monitor.height * 0.05,
            width=monitor.width * 0.93,
            height=monitor.height * 0.862,
            image_src="Images/grid.png",
            image_fit=ft.ImageFit.COVER,
        ),
        ft.Container(  # World Creation tab border
            left=monitor.width * (0.032 + 0.514 - 0.0025),  # Character creation left + width - 0.0025
            top=monitor.height * 0.05,
            width=monitor.width * (0.93 - 0.514 + 0.008),  # Grid - Character tab
            height=monitor.height * 0.122,
            bgcolor="#191B41",
            border=ft.Border(
                top=ft.BorderSide(10, "#A7A7A7"),
                right=ft.BorderSide(5, "#A7A7A7"),
                left=ft.BorderSide(5, ft.colors.WHITE),
                bottom=ft.BorderSide(5, ft.colors.WHITE),
            ),
        ),
        ft.Container(  # World Creation text
            left=monitor.width * 0.6,
            top=monitor.height * 0.07,
            content=ft.Stack(
                controls=[
                    ft.Container(
                        content=ft.Text(
                            "World Creation",
                            size=monitor.width * 0.04,  # Font Size
                            font_family="Pixelify Sans",  # Ensure the font matches the pixel art theme
                            color="#A7A7A7",
                        ),
                    ),
                ],
            ),
            on_click=world_button,
        ),
        ft.Container(  # Character Detail Body Border
            left=monitor.width * 0.032,  # box around character detail
            top=monitor.height * 0.1675,  # box around character detail
            width=monitor.width * 0.9355,  # box around character detail
            height=monitor.height * 0.747,  # box around character detail
            border=ft.Border(
                right=ft.BorderSide(5, ft.colors.WHITE),
                left=ft.BorderSide(5, ft.colors.WHITE),
                bottom=ft.BorderSide(5, ft.colors.WHITE),
            ),
        ),
        ft.Container(  # Character Tab Border
            left=monitor.width * 0.032,  # box around the character creation
            top=monitor.height * 0.041,  # box around the character creation
            width=monitor.width * 0.514,  # box around the character creation
            height=monitor.height * 0.13,  # box around the character creation
            border=ft.Border(
                top=ft.BorderSide(10, ft.colors.WHITE),
                right=ft.BorderSide(5, ft.colors.WHITE),
                left=ft.BorderSide(5, ft.colors.WHITE),
            )
        ),
        ft.Container(  # Character Creation Tab Text
            left=monitor.width * 0.08,
            top=monitor.height * 0.07,
            content=ft.Text(
                "Character Creation",
                size=monitor.width * 0.04,
                color=ft.colors.WHITE,
                font_family="Pixelify Sans",
                weight=ft.FontWeight.W_400,
            ),
        ),
        # Name
        front_end_helpers.create_text("Name", monitor.width * 0.022, monitor.width * 0.07, monitor.height * 0.24),
        # Name ? Tooltip
        front_end_helpers.create_tooltip(
            message="Character's name.\nNumbers and Symbols\nare NOT allowed.",
            left=monitor.width * (0.07 + 0.06),
            top=monitor.height * (0.24 - 0.01),
            text_size=monitor.width * 0.015,
            padding=monitor.width * 0.007,
            margin_left=monitor.width * 0.14,
            monitor=monitor
        ),

        # Name textbox
        front_end_helpers.create_textbox(name_field, monitor.width * 0.375, monitor.height * 0.24),
        # Name Error message
        front_end_helpers.create_textbox(name_error_message, monitor.width * 0.375,
                                         monitor.height * (0.24 + front_end_helpers.get_error_msg_height(monitor))),

        # Physical Condition
        front_end_helpers.create_text("Physical Condition", monitor.width * 0.022, monitor.width * 0.07,
                                      monitor.height * 0.335),
        # Physical Condition ? Tooltip
        front_end_helpers.create_tooltip(
            message="Use one word to describe\nthe physical condition.\n[Eg. Health, Poisoned]",
            left=monitor.width * (0.07 + 0.2),
            top=monitor.height * (0.335 - 0.01),
            text_size=monitor.width * 0.015,
            padding=monitor.width * 0.007,
            margin_left=monitor.width * 0.17,
            monitor=monitor
        ),

        # Physical Condition textbox
        front_end_helpers.create_textbox(physical_condition_field, monitor.width * 0.375,
                                         monitor.height * 0.335),
        # Physical Condition Error message
        front_end_helpers.create_textbox(physical_condition_error_message, monitor.width * 0.375,
                                         monitor.height * (0.335 + front_end_helpers.get_error_msg_height(monitor))),

        # Occupation
        front_end_helpers.create_text("Occupation", monitor.width * 0.022, monitor.width * 0.07,
                                      monitor.height * 0.43),
        # Occupation ? Tooltip
        front_end_helpers.create_tooltip(
            message="Character's occupation.\n[Eg. Knight, Student]",
            left=monitor.width * (0.07 + 0.13),
            top=monitor.height * (0.43 - 0.01),
            text_size=monitor.width * 0.015,
            padding=monitor.width * 0.007,
            margin_left=monitor.width * 0.17,
            monitor=monitor
        ),

        # Occupation textbox
        front_end_helpers.create_textbox(occupation_field, monitor.width * 0.375, monitor.height * 0.43),
        # Occupation Error message
        front_end_helpers.create_textbox(occupation_error_message, monitor.width * 0.375,
                                         monitor.height * (0.43 + front_end_helpers.get_error_msg_height(monitor))),

        # Money
        front_end_helpers.create_text("Money", monitor.width * 0.022, monitor.width * 0.07, monitor.height * 0.525),
        # Money ? Tooltip
        front_end_helpers.create_tooltip(
            message="Amount of money\nyour character has.\nLimit: 9999999999",
            left=monitor.width * (0.07 + 0.075),
            top=monitor.height * (0.525 - 0.01),
            text_size=monitor.width * 0.015,
            padding=monitor.width * 0.007,
            margin_left=monitor.width * 0.15,
            monitor=monitor
        ),

        # Money textbox
        front_end_helpers.create_textbox(money_field, monitor.width * 0.175, monitor.height * 0.525),
        # Money Error message
        front_end_helpers.create_textbox(money_error_message, monitor.width * 0.175,
                                         monitor.height * (0.525 + front_end_helpers.get_error_msg_height(monitor))),

        # Hp
        front_end_helpers.create_text("Hp", monitor.width * 0.022, monitor.width * 0.355,
                                      monitor.height * 0.525),

        # Hp ? Tooltip
        front_end_helpers.create_tooltip(
            message="Health Points.\nA character has full\nhealth at 100 HP.\nRange: 30-100.",
            left=monitor.width * (0.355 + 0.03),
            top=monitor.height * (0.525 - 0.01),
            text_size=monitor.width * 0.015,
            padding=monitor.width * 0.007,
            margin_left=monitor.width * 0.13,
            monitor=monitor
        ),

        # Hp textbox
        front_end_helpers.create_textbox(hp_field, monitor.width * (0.355 + 0.05), monitor.height * 0.525),
        # Hp Error message
        front_end_helpers.create_textbox(hp_error_message, monitor.width * (0.355 + 0.05),
                                         monitor.height * (0.525 + front_end_helpers.get_error_msg_height(monitor))),

        # Luck
        front_end_helpers.create_text("Luck", monitor.width * 0.022, monitor.width * 0.526,
                                      monitor.height * 0.525),
        # Luck ? Tooltip
        front_end_helpers.create_tooltip(
            message="How lucky your character is.\n"
                    "A higher luck stat increases\n"
                    "the chances of positive\n"
                    "outcomes in random events.\n"
                    "Range: 2-11.",
            left=monitor.width * (0.547 + 0.035),
            top=monitor.height * (0.525 - 0.01),
            text_size=monitor.width * 0.015,
            padding=monitor.width * 0.007,
            margin_left=monitor.width * 0.175,
            monitor=monitor
        ),

        # Luck textbox
        front_end_helpers.create_textbox(luck_field, monitor.width * (0.546 + 0.055),
                                         monitor.height * 0.525),
        # Luck Error message
        front_end_helpers.create_textbox(luck_error_message, monitor.width * (0.546 + 0.055),
                                         monitor.height * (0.525 + front_end_helpers.get_error_msg_height(monitor))),

        # Cha
        front_end_helpers.create_text("Cha", monitor.width * 0.022, monitor.width * 0.72,
                                      monitor.height * 0.525),
        # Cha ? Tooltip
        front_end_helpers.create_tooltip(
            message="Charisma.\nA higher charisma stat\nincreases the number of\npeople you meet.\nRange: 0-10.",
            left=monitor.width * (0.72 + 0.045),
            top=monitor.height * (0.525 - 0.01),
            text_size=monitor.width * 0.015,
            padding=monitor.width * 0.007,
            margin_left=monitor.width * 0.155,
            monitor=monitor
        ),

        # Cha textbox
        front_end_helpers.create_textbox(cha_field, monitor.width * (0.725 + 0.06),
                                         monitor.height * 0.525),
        # Cha Error message
        front_end_helpers.create_textbox(cha_error_message, monitor.width * (0.725 + 0.06),
                                         monitor.height * (0.525 + front_end_helpers.get_error_msg_height(monitor))),

        # Appearance
        front_end_helpers.create_text("Appearance", monitor.width * 0.022, monitor.width * 0.07,
                                      monitor.height * 0.615),
        # Appearance ? Tooltip
        front_end_helpers.create_tooltip(
            message="Character's Appearance.\n"
                    "Use a few words to describe the\n"
                    "appearance of your character.\n"
                    "[Eg. Green eyes, Tall, Has wings]",
            left=monitor.width * (0.09 + 0.12),
            top=monitor.height * (0.615 - 0.005),
            text_size=monitor.width * 0.015,
            padding=monitor.width * 0.007,
            margin_left=monitor.width * 0.17,
            monitor=monitor
        ),

        # Appearance textbox
        front_end_helpers.create_textbox(appearance_field, monitor.width * 0.07,
                                         monitor.height * (0.62 + 0.07)),
        # Appearance Error message
        front_end_helpers.create_textbox(appearance_error_message, monitor.width * 0.07,
                                         monitor.height * (0.615 + 0.05)),

        # Inventory
        front_end_helpers.create_text("Inventory", monitor.width * 0.022, monitor.width * 0.65,
                                      monitor.height * 0.615),
        # Inventory ? Tooltip
        front_end_helpers.create_tooltip(
            message="Character's inventory.\n"
                    "If nothing, leave it blank.\n"
                    "[Eg. Shield, Sword]",
            left=monitor.width * (0.65 + 0.118),
            top=monitor.height * (0.615 - 0.005),
            text_size=monitor.width * 0.015,
            padding=monitor.width * 0.007,
            margin_left=monitor.width * 0.17,
            monitor=monitor
        ),

        # Inventory textbox
        front_end_helpers.create_textbox(inventory_field, monitor.width * 0.65,
                                         monitor.height * (0.62 + 0.07)),
        # Inventory Error message
        front_end_helpers.create_textbox(inventory_error_message, monitor.width * 0.65,
                                         monitor.height * (0.615 + 0.05)),

        # Personality
        front_end_helpers.create_text("Personality", monitor.width * 0.022, monitor.width * 0.375,
                                      monitor.height * 0.615),
        # Personality ? Tooltip
        front_end_helpers.create_tooltip(
            message="Personality of your character.\n"
                    "Use a few words to describe the\n"
                    "personality of your character.\n"
                    "[Eg. Anxious, Jolly, Hot-headed]",
            left=monitor.width * (0.375 + 0.135),
            top=monitor.height * (0.615 - 0.005),
            text_size=monitor.width * 0.015,
            padding=monitor.width * 0.007,
            margin_left=monitor.width * 0.205,
            monitor=monitor
        ),

        # Personality textbox
        front_end_helpers.create_textbox(personality_field, monitor.width * 0.375,
                                         monitor.height * (0.62 + 0.07)),
        # Personality Error message
        front_end_helpers.create_textbox(personality_error_message, monitor.width * 0.375,
                                         monitor.height * (0.615 + 0.05)),

        ft.Container(  # Start Game
            left=monitor.width * 0.85,
            top=monitor.height * 0.2,
            # width=monitor.width * 0.1,
            # height=monitor.height * 0.05,
            bgcolor="#142158",
            border=ft.border.all(5, "#FFFFFF"),
            shadow=ft.BoxShadow(
                color=ft.colors.with_opacity(0.25, ft.colors.BLACK),
                blur_radius=4,
                offset=ft.Offset(5, 5),
            ),
            padding=ft.padding.only(top=monitor.height * 0.005, left=monitor.width * 0.01,
                                    bottom=monitor.height * 0.005, right=monitor.width * 0.01),
            content=ft.Text(
                "Start Game",
                size=monitor.width * 0.013,
                font_family="Pixelify Sans",
                weight=ft.FontWeight.W_400,
            ),
            visible=False,
            on_click=start_game_button,
        )
    ]
