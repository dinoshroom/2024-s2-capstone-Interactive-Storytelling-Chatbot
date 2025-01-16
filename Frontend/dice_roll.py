import flet as ft
import random
import time
import pygame

"""Initialise pygame mixer and load sound effects for dice rolling.
Sets up sound effects for dice roll and button click events.
"""
pygame.mixer.init()
roll_sound = pygame.mixer.Sound("assets/Sounds/dice_roll.mp3")
button_sound = pygame.mixer.Sound("assets/Sounds/fate_sealed.mp3")


def dice_roll(page):
    """Creates and manages a dice rolling interface with animation.
    Displays two dice with rolling animation and calculates total score.
    Includes sound effects and result display.
    
    :param page: The Flet page object to display the dice interface
    :return: None
    """
    page.title = "Two Dice Rolling Animation"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    dice_faces = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]
    dice_values = {
        "⚀": 1, "⚁": 2, "⚂": 3,
        "⚃": 4, "⚄": 5, "⚅": 6
    }

    dice1 = ft.Text(
        value="⚄",
        size=200,
        color=ft.colors.BLUE,
        weight=ft.FontWeight.BOLD,
    )

    dice2 = ft.Text(
        value="⚄",
        size=200,
        color=ft.colors.RED,
        weight=ft.FontWeight.BOLD,
    )

    result_text = ft.Text(
        value="Roll the dice!",
        size=20,
        color=ft.colors.RED_400,
    )

    event_text = ft.Text(
        value="A random event is occurring! Roll the dice to decide your fate.",
        size=40,
        color=ft.colors.RED_400,
        weight=ft.FontWeight.BOLD,
    )

    def roll_dice(e):
        """Handles dice rolling animation and result calculation.
        Manages button state, plays sound effects, animates dice faces,
        and calculates final result.
    
        :param e: The click event that triggered the roll
        :return: int: The total sum of both dice values
        """
        roll_button.disabled = True
        page.update()

        button_sound.play()
        time.sleep(3)
        roll_sound.play()

        for _ in range(10):  # Simulate 10 rolls for animation
            dice1.value = random.choice(dice_faces)
            dice2.value = random.choice(dice_faces)
            page.update()
            time.sleep(0.1)

        # Final result
        final_dice1 = random.choice(dice_faces)
        final_dice2 = random.choice(dice_faces)
        dice1.value = final_dice1
        dice2.value = final_dice2

        # Calculate and display the result
        value1 = dice_values[final_dice1]
        value2 = dice_values[final_dice2]
        total = value1 + value2
        print(total)

        result_text.value = f"Dice 1: {value1}, Dice 2: {value2}, Total: {total}"
        page.update()
        time.sleep(4)
        page.window_close()
        return total

    roll_button = ft.ElevatedButton("Roll Dice", on_click=roll_dice)

    page.add(
        ft.Column(
            [
                event_text,
                ft.Row(
                    [dice1, dice2],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                roll_button,
                result_text,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )


def main(page):
    """Initialises the dice rolling application.
    Sets up the main dice rolling interface as a standalone application.
    
    :param page: The Flet page object for the application window
    :return: None
    """
    dice_roll(page)


if __name__ == "__main__":
    ft.app(target=main)
