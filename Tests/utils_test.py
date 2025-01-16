from Utilities import utils
from Engine import engine
import pytest
import json


@pytest.fixture
def main_engine():
    return engine.Engine()


@pytest.fixture
def character():
    character = {
        "id": 1,
        "name": "Bob",
        "physical_condition": "Healthy",
        "occupation": "Scientist",
        "money": 50.0,
        "relationship": {},
        "personality": ["Kind", "Hot-blooded"],
        "inventory": [],
        "stats": {
            "HP": 100,
            "LUCK": 10,
            "CHA": 10
        },
        "current_location": "",
        "appearance": "male, brown hair, green eyes, wears armour"
    }
    return character


@pytest.fixture
def character2():
    character2 = {
        "id": 2,
        "name": "Josh",
        "physical_condition": "Healthy",
        "occupation": "Doctor",
        "money": 50.0,
        "relationship": {},
        "personality": ["Kind", "Rash"],
        "inventory": [],
        "stats": {
            "HP": 10,
        },
        "current_location": "",
        "appearance": "male, brown hair, green eyes, wears armour"
    }
    return character2


@pytest.fixture
def world():
    world = {
        "rules": [],
        "genre": "Fantasy",
        "environment": "",
        "locations": []
    }
    return world


@pytest.fixture
def timeline():
    timeline = {
        "key_events": []
    }
    return timeline


def test_get_prompt_starting(main_engine, character, character2, world, timeline):
    main_engine.mainCharacter = character
    main_engine.add_character(character2)
    main_engine.add_world(world)
    main_engine.add_timeline(timeline)
    formatted_str: str = main_engine.get_formatted_string_array()

    # Call the get_prompt function
    prompt: str = utils.get_prompt("Fantasy", character["name"], main_engine.mainCharacter.cha, True, json_dict_str=formatted_str)

    # Assert the starting prompt structure
    assert f"**Character JSON dictionary:**" in prompt
    assert f"**World JSON dictionary:**" in prompt
    assert f"**Timeline JSON dictionary:**" in prompt
    assert character["name"] in prompt
    assert character2["name"] in prompt
    assert "Fantasy" in prompt


def test_json_converter():
    str_to_convert: str = """
    {
        "id": 1,
        "name": "Bob",
        "physical_condition": "Headache",
        "occupation": "Knight",
        "money": 0.0,
        "relationship": {
            "2": "provider"
        },
        "personality": "Kind-hearted, Protective",
        "inventory": [
            "Claymore",
            "Shield"
        ],
        "stats": {
            "HP": 3,
            "MP": 5,
            "STR": 8
        },
        "current_location": "the bustling streets surrounding the noodle shop"
    }"""

    dict_list = utils.convert_to_json(str_to_convert)

    assert type(dict_list) is list
    assert type(dict_list[0]) is dict
    assert dict_list[0]["name"] == "Bob"


def test_fix_format():
    text_to_fix = '```plaintext([1, "+", "100"])```'
    new_string = utils.fix_format(text_to_fix)

    assert '```' not in new_string
    assert '(' not in new_string
    assert ')' not in new_string
    assert type(new_string) is str
    assert 'plaintext' not in new_string


def test_split_function():
    str_to_split: str = "1 += 10"
    split_tuple: tuple[list[str], str] = utils.split_function(str_to_split)
    assert type(split_tuple) is tuple
    assert split_tuple[1] == "+="
    assert split_tuple[0] == ["1 "," 10"]


def test_check_money():
    pending_updates: list[tuple[int, str, str]] = [(1, "+", "10"), (2, "-", "20")]
    id_list: list[int] = [1, 2]
    name_list: list[str] = ["Bob", "Josh"]
    money_list: list[int] = [100, 200]

    transactions: tuple[bool, list[tuple[int, str]]] = utils.check_money(pending_updates, id_list, name_list, money_list)
    assert transactions[0]
    assert len(transactions[1]) == 0


def test_check_money_broke():
    pending_updates: list[tuple[int, str, str]] = [(1, "+", "10"), (2, "-", "20")]
    id_list: list[int] = [1, 2]
    name_list: list[str] = ["Bob", "Josh"]
    money_list: list[int] = [0, 10]

    transactions: tuple[bool, list[tuple[int, str]]] = utils.check_money(pending_updates, id_list, name_list,
                                                                         money_list)
    assert not transactions[0]
    assert len(transactions[1]) == 1


