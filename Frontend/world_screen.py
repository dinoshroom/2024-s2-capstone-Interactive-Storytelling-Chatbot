from screeninfo import Monitor
import flet as ft
from Frontend import front_end_helpers


def world_screen(monitor: Monitor,
                 character_button: callable,
                 genre_field: ft.TextField,
                 genre_error_message: ft.Text,
                 world_rules_field: ft.TextField,
                 rules_dropdown: ft.Dropdown,
                 world_rules_error_message: ft.Text,
                 environment_field: ft.TextField,
                 environment_dropdown: ft.Dropdown,
                 environment_error_message: ft.Text,
                 start_game_button: callable):
    """This function controls the World customisation screen in the application.

    :param monitor: a Monitor object
    :param character_button: Function that changes from the world screen to the character customisation screen.
    :param genre_field: Flet TextField object for the user to input.
    :param genre_error_message: Flet Text object for when the user inputs something wrong.
    :param world_rules_field: Flet TextField object for the user to input.
    :param rules_dropdown: Flet Dropdown object for the user to select default or custom
    :param world_rules_error_message: Flet Text object for when the user inputs something wrong.
    :param environment_field: Flet TextField object for the user to input.
    :param environment_dropdown: Flet Dropdown object for the user to select default or custom
    :param environment_error_message: Flet Text object for when the user inputs something wrong.
    :param start_game_button: Function that changes from the world screen to the main screen.
    """
    return [
        ft.Container(  # World Creation tab Shadow
            left=monitor.width * (0.032 + 0.514 - 0.0025),  # Character creation left + width - 0.0025
            top=monitor.height * 0.041,
            width=monitor.width * (0.93 - 0.514 + 0.008),
            height=monitor.height * 0.122,
            shadow=ft.BoxShadow(
                color=ft.colors.with_opacity(0.25, ft.colors.BLACK),
                blur_radius=4,
                offset=ft.Offset(10, 10),
            ),
        ),
        ft.Container(  # World Detail Body
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
        ft.Container(  # World Creation tab
            left=monitor.width * (0.032 + 0.514 - 0.0025),  # Character creation left + width - 0.0025
            top=monitor.height * 0.041,
            width=monitor.width * (0.93 - 0.514 + 0.008),
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
        ft.Container(  # Characeter creation tab border
            left=monitor.width * 0.032,
            top=monitor.height * 0.05,
            width=monitor.width * 0.514,
            height=monitor.height * 0.122,
            bgcolor="#1A1B42",
            border=ft.Border(
                left=ft.border.BorderSide(10, "#A7A7A7"),
                top=ft.border.BorderSide(5, "#A7A7A7"),
                right=ft.border.BorderSide(5, ft.colors.WHITE),
                bottom=ft.border.BorderSide(5, ft.colors.WHITE),
            ),
        ),
        ft.Container(  # Character Creation tab text
            left=monitor.width * 0.08,
            top=monitor.height * 0.07,
            content=ft.Text(
                "Character Creation",
                size=monitor.width * 0.04,
                font_family="Pixelify Sans",
                color="#A7A7A7",
            ),
            on_click=character_button,
        ),
        ft.Container(  # World Detail Body Border
            left=monitor.width * 0.032,
            top=monitor.height * 0.1675,
            width=monitor.width * 0.9355,
            height=monitor.height * 0.747,
            border=ft.Border(
                right=ft.BorderSide(5, ft.colors.WHITE),
                left=ft.BorderSide(5, ft.colors.WHITE),
                bottom=ft.BorderSide(5, ft.colors.WHITE),
            ),
        ),
        ft.Container(  # World Creation tab border
            left=monitor.width * (0.032 + 0.514 - 0.0025),  # Character creation left + width - 0.0025
            top=monitor.height * 0.041,
            width=monitor.width * (0.93 - 0.514 + 0.008),
            height=monitor.height * 0.13,
            border=ft.border.only(
                top=ft.border.BorderSide(10, ft.colors.WHITE),
                left=ft.border.BorderSide(5, ft.colors.WHITE),
                right=ft.border.BorderSide(5, ft.colors.WHITE),
            ),
        ),
        ft.Container(  # World Creation Tab Text
            left=monitor.width * 0.6,
            top=monitor.height * 0.07,
            content=ft.Text(
                "World Creation",
                size=monitor.width * 0.04,
                font_family="Pixelify Sans",
                color=ft.colors.WHITE,
            ),
        ),

        # Genre
        front_end_helpers.create_text(
            content="Genre",
            size=monitor.width * 0.022,
            left=monitor.width * 0.07,
            top=monitor.height * 0.24,
        ),
        # Genre ? Tooltip
        front_end_helpers.create_tooltip(
            message="Genre of the story.\n"
                    "[Eg. Fanstasy, Romance]",
            left=monitor.width * (0.07 + 0.07),
            top=monitor.height * (0.24 - 0.01),
            text_size=monitor.width * 0.015,
            padding=monitor.width * 0.007,
            margin_left=monitor.width * 0.155,
            monitor=monitor
        ),

        # Genre textbox
        front_end_helpers.create_textbox(genre_field, monitor.width * 0.375,
                                         monitor.height * 0.24),
        # Genre Error message
        front_end_helpers.create_textbox(genre_error_message, monitor.width * 0.375,
                                         monitor.height * (0.24 + front_end_helpers.get_error_msg_height(monitor))),

        # World Rules
        front_end_helpers.create_text(
            content="World Rules",
            size=monitor.width * 0.022,
            left=monitor.width * 0.07,
            top=monitor.height * 0.425,
        ),

        # World Rules ? Tooltip
        front_end_helpers.create_tooltip(
            message="Set rules for your world.\n"
                    "Default: Automatically generated.\n"
                    "Custom: You make your own rules.\n"
                    "[Eg. No gravity]",
            left=monitor.width * (0.07 + 0.13),
            top=monitor.height * (0.425 - 0.01),
            text_size=monitor.width * 0.015,
            padding=monitor.width * 0.007,
            margin_left=monitor.width * 0.215,
            monitor=monitor
        ),

        # World Rules textbox
        front_end_helpers.create_textbox(world_rules_field, monitor.width * 0.375,
                                         monitor.height * 0.425),
        # World Rules dropdown
        front_end_helpers.create_textbox(rules_dropdown, monitor.width * 0.72,
                                         monitor.height * 0.425),
        # World Rules Error message
        front_end_helpers.create_textbox(world_rules_error_message, monitor.width * 0.375,
                                         monitor.height * (0.425 - 0.03)),

        # Environment
        front_end_helpers.create_text(
            content="Environment",
            size=monitor.width * 0.022,
            left=monitor.width * 0.07,
            top=monitor.height * 0.673,
        ),
        # Environment ? Tooltip
        front_end_helpers.create_tooltip(
            message="Environment that the story is in.\n"
                    "Default: Automatically generated.\n"
                    "Custom: Describe the environment.\n"
                    "[Eg. Tavern, Park]",
            left=monitor.width * (0.07 + 0.145),
            top=monitor.height * (0.673 - 0.01),
            text_size=monitor.width * 0.015,
            padding=monitor.width * 0.007,
            margin_left=monitor.width * 0.225,
            monitor=monitor
        ),

        # Environment textbox
        front_end_helpers.create_textbox(environment_field, monitor.width * 0.375,
                                         monitor.height * 0.673),
        # Environment dropdown
        front_end_helpers.create_textbox(environment_dropdown, monitor.width * 0.72,
                                         monitor.height * 0.673),
        # Environment Error message
        front_end_helpers.create_textbox(environment_error_message, monitor.width * 0.375,
                                         monitor.height * (0.673 - 0.03)),

        ft.Container(  # Start Game
            left=monitor.width * 0.83,
            top=monitor.height * 0.2,
            bgcolor="#142158",
            border=ft.border.all(5, "#FFFFFF"),
            shadow=ft.BoxShadow(
                color=ft.colors.with_opacity(0.25, ft.colors.BLACK),
                blur_radius=4,
                offset=ft.Offset(5, 5),
            ),
            padding=ft.padding.only(top=monitor.height * 0.01, left=monitor.width * 0.01,
                                    bottom=monitor.height * 0.01, right=monitor.width * 0.01),
            content=ft.Text(
                "Start Game",
                size=monitor.width * 0.013,
                font_family="Pixelify Sans",
                weight=ft.FontWeight.W_400,
            ),
            visible=True,
            on_click=start_game_button,
        )
    ]
