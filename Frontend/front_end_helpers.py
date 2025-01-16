from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
import requests
import os
import time
import flet as ft
from screeninfo import Monitor

load_dotenv()
HF_TOKEN = os.getenv('HF_TOKEN')


def generate_image(prompt, character, thing,genre=""):
    """Generates pixel art images using Hugging Face's API.
    Creates and saves character portraits, NPC images, or item images based on provided prompts.
    
    :param prompt: The text prompt describing the image to generate
    :param character: The name of the character or item
    :param thing: The type of image to generate ("Character", "NPC", or "Item")
    :param genre: the genre of the NPC
    :return: None
    :raises requests.RequestException: If API request fails
    :raises IOError: If image saving fails
    """
    if HF_TOKEN and len(prompt) >= 5:
        # API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-dev" #Slower but generates bettter detailed images
        API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"  # Faster but generates less detailed images
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        max_retries = 5
        retries = 0
        if thing == "NPC":
            save_path = f"assets/{thing}_portraits/{genre}/{character}.png"
            print(save_path)
        else:
            save_path = f"assets/{thing}_portraits/{character}.png"
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        while retries < max_retries:
            response = requests.post(API_URL, headers=headers, json={"inputs": str(prompt)})

            if response.status_code == 200:
                try:
                    i = Image.open(BytesIO(response.content))
                    i.save(save_path)
                    print("Image saved successfully.")
                    break
                except Exception as e:
                    print(f"Error opening image: {e}")
                    break
            else:
                print(f"Failed to get image. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                retries += 1
                time.sleep(1)  # Optional: wait for a second before retrying

        if retries == max_retries:
            print("Failed to get image after 5 attempts.")


def process__value(value):
    """Processes string or list values by removing whitespace and standardising format.
    Converts newline-separated strings or lists into comma-separated lists.
    
    :param value: The string or list to process
    :return: list: A cleaned list of comma-separated values
    :raises TypeError: If value is neither string nor list
    """
    if isinstance(value, str):
        return (','.join(value.split("\n"))).split(",")
    elif isinstance(value, list):
        processed_list = []
        for item in value:
            processed_list.append(item.strip())
        return ','.join(processed_list).split(",")
    else:
        raise TypeError("Unsupported value type. Only strings and lists are allowed.")


def create_text_field(
    label: str,
    width: float,
    value: str,
    on_change: callable,
    text_style: ft.TextStyle,
    on_blur: callable = None,
    multiline: bool = False,
    height: float = None,
) -> ft.TextField:
    """Creates a styled text field with specified properties.
    Generates a consistent UI text input field with custom styling and behavior.
    
    :param label: The label text for the field
    :param width: The width of the text field
    :param value: The initial value of the field
    :param on_change: Callback function for text change events
    :param text_style: The style to apply to the text
    :param on_blur: Optional callback function for blur events
    :param multiline: Whether the field accepts multiple lines
    :param height: Optional height for the field
    :return: ft.TextField: A configured text field widget
    """
    if (label == "World Rules" or  label == "Environment") and value == "":
        disabled: bool = True
    else:
        disabled = False

    return ft.TextField(
        label=label,
        width=width,
        height=height,
        border_color="#8E9CD9",
        focused_border_color="#FFFFFF",
        border_width=3,
        bgcolor="#142158",
        color=ft.colors.WHITE,
        multiline=multiline,
        disabled=disabled,
        text_style=text_style,
        value=value,
        on_change=on_change,
        on_blur=on_blur
    )


def create_error_message(size: float, value: str = "") -> ft.Text:
    """Creates a standardised error message text widget.
    Generates red error text with consistent styling.
    
    :param size: The font size of the error message
    :param value: The error message text
    :return: ft.Text: A configured error message text widget
    """
    return ft.Text(
        value=value,
        size=size,
        color=ft.colors.RED,
        font_family="Pixelify Sans",
        weight=ft.FontWeight.W_400,
    )


def create_stats_text(value: str, size: float) -> ft.Text:
    """Creates a standardised stats text widget.
    Generates white text with pixel font styling for stats display.
    
    :param value: The text to display
    :param size: The font size of the text
    :return: ft.Text: A configured stats text widget
    """
    selectable: bool = False
    if value == "": # make the contents of the story section selectable
        selectable = True
    return ft.Text(
        value=value,
        size=size,
        color=ft.colors.WHITE,
        font_family="Pixelify Sans",
        selectable=selectable,
    )


def create_text(content, size, left, top, color=ft.colors.WHITE, weight=ft.FontWeight.W_400):
    """Creates a positioned text container with specified styling.
    Generates a text widget within a container at specific coordinates.
    
    :param content: The text content to display
    :param size: The font size
    :param left: Left position coordinate
    :param top: Top position coordinate
    :param color: Text color (default: white)
    :param weight: Font weight (default: W_400)
    :return: ft.Container: A container with configured text
    """
    return ft.Container(
        left=left,
        top=top,
        content=ft.Text(
            content,
            size=size,
            color=color,
            font_family="Pixelify Sans",
            weight=weight,
        ),
    )

def create_tooltip(message, left, top, text_size, padding, margin_left, monitor):
    """Creates a tooltip widget with help text.
    Generates a question mark icon with hover tooltip containing help text.
    
    :param message: The help text to display
    :param left: Left position coordinate
    :param top: Top position coordinate
    :param text_size: Font size for the tooltip text
    :param padding: Padding around the tooltip text
    :param margin_left: Left margin for the tooltip
    :param monitor: Monitor object for screen-relative positioning
    :return: ft.Container: A container with configured tooltip
    """
    return ft.Container(
        left=left,
        top=top,
        content=ft.Text(
            "?",
            size=text_size,
            color=ft.colors.WHITE,
            font_family="Pixelify Sans",
        ),
        tooltip=ft.Tooltip(
            message=message,
            bgcolor=ft.colors.with_opacity(0.8, ft.colors.BLACK),
            padding=padding,
            margin=ft.Margin(top=-monitor.width * 0.025, right=0, left=margin_left, bottom=0),
            text_style=ft.TextStyle(size=monitor.width * 0.01, color=ft.colors.WHITE, font_family="Pixelify Sans"),
        ),
    )

def create_textbox(field, left, top):
    """Creates a positioned container for a text input field.
    Places a text input field at specific coordinates.
    
    :param field: The text field control to position
    :param left: Left position coordinate
    :param top: Top position coordinate
    :return: ft.Container: A container with positioned text field
    """
    return ft.Container(
        left=left,
        top=top,
        content=field,
    )


def create_dropdown(on_change: callable, monitor: Monitor, content: str) -> ft.Dropdown:
    """Creates a styled dropdown menu with default/custom options.
    Generates a dropdown widget with consistent styling and behavior.
    
    :param on_change: Callback function for selection changes
    :param monitor: Monitor object for screen-relative sizing
    :param content: The contents of the textbox
    :return: ft.Dropdown: A configured dropdown widget
    """
    if content == "": # Set initial value to "Default"
        initial_value = "Default"
    else:
        initial_value = "Custom"
    return ft.Dropdown(
        width=monitor.width * 0.14,
        height=monitor.height * 0.058,
        options=[
            ft.dropdown.Option("Default"),
            ft.dropdown.Option("Custom"),
        ],
        value=initial_value,
        bgcolor="#030A26",
        border_color=ft.colors.WHITE,
        text_style=ft.TextStyle(color=ft.colors.WHITE, font_family="Pixelify Sans", size=20),
        on_change=on_change,
    )

def get_title_image_height(monitor: Monitor) -> float:
    """Calculates appropriate title image height based on screen resolution.
    Adjusts title image positioning for different screen sizes.

    :param monitor: Monitor object containing screen information
    :return: The calculated height value for title image positioning
    """
    if (monitor.width / monitor.height) <= 1.6:  # Mac ratio
        return monitor.height * 0.18
    else:
        return monitor.height * 0.2

def get_title_image_top(monitor: Monitor) -> float:
    """Calculates appropriate title image top based on screen resolution.
    Adjusts title image positioning for different screen sizes.

    :param monitor: Monitor object containing screen information
    :return: The calculated top value for title image positioning
    """
    if (monitor.width / monitor.height) <= 1.6:  # Mac ratio
        return monitor.width * 0.215
    else:
        return monitor.width * 0.19

def get_error_msg_height(monitor: Monitor) -> float:
    """Calculates appropriate error message height based on screen resolution.
    Adjusts error message positioning for different screen sizes.
    
    :param monitor: Monitor object containing screen information
    :return: The calculated height value for error message positioning
    """
    # attempt to fix error message formatting for different resolutions
    if monitor.height >= 1140:
        return 0.055
    elif monitor.height >= 1080:
        return 0.06
    elif monitor.height >= 1020:
        return 0.065
    elif monitor.height >= 960:
        return 0.07
    else:
        return 0.075  # Mac height of 900 fits here

def get_button_width(content, monitor: Monitor) -> float:
    """Calculates appropriate button text width based on screen resolution.
    Adjusts button text positioning for different screen sizes.
    :param content: The button text as a string
    :param monitor: Monitor object containing screen information
    :return: The calculated width value for button text positioning
    """
    # attempt to fix the button formatting for different resolutions
    if content == "START":
        if (monitor.width / monitor.height) <= 1.6: # Mac ratio
            return monitor.width * 0.163
        else:
            return monitor.width * 0.145
    else: # LOAD
        if (monitor.width / monitor.height) <= 1.6: # Mac ratio
            return monitor.width * 0.165
        else:
            return monitor.width * 0.148
        
def format_inventory(inventory: list[str]) -> str:
    """Formats the NPCs' inventory for the Character Button UI

    :param inventory: A list of the character's items
    :return: A formatted string of the inventory
    """
    formatted_inventory_str: str = ""
    for item in inventory:
        formatted_inventory_str += f"\n  - {item}"
    return formatted_inventory_str