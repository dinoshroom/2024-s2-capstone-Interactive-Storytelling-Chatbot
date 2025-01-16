from Classes.Character import Character
from Engine import engine
import pytest

pytest_plugins = ('pytest_asyncio',)


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


def test_add_character(main_engine, character):
    main_engine.add_character(character)
    assert len(main_engine.characters) == 1


def test_main_character(main_engine, character):
    main_character = Character(character["id"],
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
    main_engine.mainCharacter = character
    assert main_engine.mainCharacter.id == main_character.id


@pytest.mark.asyncio
async def test_physical_condition(main_engine, character):
    main_engine.mainCharacter = character
    prev_condition: str = main_engine.mainCharacter.physical_condition
    await main_engine.update_char_physical_condition([(1, "Injured")])
    assert main_engine.mainCharacter.physical_condition != prev_condition


@pytest.mark.asyncio
async def test_money(main_engine, character):
    main_engine.mainCharacter = character
    initial_money = main_engine.mainCharacter.money
    await main_engine.update_char_money([(1, "+", "10.0")])
    assert main_engine.mainCharacter.money == initial_money + 10.0


@pytest.mark.asyncio
async def test_relationship(main_engine, character, character2):
    main_engine.mainCharacter = character
    main_engine.add_character(character2)
    await main_engine.update_char_relationship([(1, 2, "Partners"), (2, 1, "Partnets")])
    assert main_engine.mainCharacter.relationship[2] == "Partners"


@pytest.mark.asyncio
async def test_inventory(main_engine, character):
    main_engine.mainCharacter = character
    item: str = "sword"
    await main_engine.update_char_inventory([(1, "+", item)])
    assert main_engine.mainCharacter.inventory[0] == item


@pytest.mark.asyncio
async def test_stats(main_engine, character):
    main_engine.mainCharacter = character
    await main_engine.update_char_hp([(1, "+", 10)])
    # character is already at 100 hp, it should stay at 100
    assert main_engine.mainCharacter.hp == 100


@pytest.mark.asyncio
async def test_stats2(main_engine, character):
    main_engine.mainCharacter = character
    prev_hp: int = main_engine.mainCharacter.hp
    await main_engine.update_char_hp([(1, "-", 10)])
    # character is already at 100 hp, it should stay at 100
    assert main_engine.mainCharacter.hp < prev_hp


@pytest.mark.asyncio
async def test_inventory_check(main_engine, character):
    main_engine.mainCharacter = character
    user_input: str = "I will use a sword"
    response: tuple[bool, str] = await main_engine.check_inventory(user_input)
    assert response[0]


@pytest.mark.asyncio
async def test_inventory_check_not_use_item(main_engine, character):
    main_engine.mainCharacter = character
    user_input: str = "I negotiate with my friend about buying a sword"
    response: tuple[bool, str] = await main_engine.check_inventory(user_input)
    assert not response[0]


def test_character_deceased(main_engine, character):
    main_engine.mainCharacter = character
    ret_tuple: tuple[bool, str] = main_engine.check_characters_deceased("cyberpunk")
    assert not ret_tuple[0]
