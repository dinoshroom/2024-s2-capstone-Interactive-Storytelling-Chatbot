from typing import List, Dict, TypeVar

from typing_extensions import override

V = TypeVar("V")


class Character:
    def __init__(self, id: int = 1,
                 name: str = "",
                 physical_condition: str = "",
                 occupation: str = "",
                 money: float = 0.0,
                 relationship: Dict[int, str] = {},
                 personality: List[str] = [],
                 inventory: List[str] = [],
                 stats: Dict[str, int] = {},
                 current_location: str = "",
                 appearance: str = ""):
        """Initialises the Character class.

        :param id: The Character's ID.
        :param name: The Character's name.
        :param physical_condition: Shows the Character's status effects, e.g: healthy, injured, deceased, etc.
        :param occupation: The Character's occupation.
        :param money: How much money the Character has.
        :param relationship: The relationships between characters.
        :param personality: The personalities of the Character.
        :param inventory: The Character's inventory.
        :param stats: The Character's stats.
        :param current_location: The Character's current location.
        :param appearance: The Character's appearance.
        """
        self._id = id
        self._name = name
        self._physical_condition = physical_condition
        self._occupation = occupation
        self._money = money
        self._relationship = relationship
        self._personality = personality
        self._inventory = inventory
        self._stats = stats
        self._current_location = current_location
        self._appearance = appearance

    # Id
    @property
    def id(self) -> int:
        """Fetches the Character's ID.

        :return: The character's ID.
        """
        return self._id
    
    # Name
    @property
    def name(self) -> str:
        """Fetches the Character's name.

        :return: The character's name.
        """
        return self._name

    @name.setter
    def name(self, new_name: str) -> None:
        """Sets the Character's name.

        :param new_name: The new character's name.
        :return: None
        """
        self._name = new_name

    @property
    def physical_condition(self) -> str:
        """Fetches the Character's physical condition.

        :return: The character's physical condition.
        """
        return self._physical_condition

    @physical_condition.setter
    def physical_condition(self, new_status: str) -> None:
        """Sets the Character's physical condition.

        :param new_status: The new character's physical condition.
        :return: None
        """
        self._physical_condition = new_status

    @property
    def money(self) -> float:
        """Fetches the Character's money.

        :return: The character's money.
        """
        return self._money

    @money.setter
    def money(self, new_money):
        """Sets the character's money to a new value.

        :param new_money: The new amount.
        :return:
        """
        self._money = new_money

    def increase_money(self, amount: float) -> None:
        """Increases the Character's money.

        :param amount: The amount to increase the character's money.
        :return: None
        """
        self._money = round(self._money + amount, 2)

    def decrease_money(self, amount: float) -> None:
        """Decreases the Character's money.

        :param amount: The amount to decrease the character's money.
        :return: None
        """
        self._money = round(self._money - amount, 2)

    # Relationship
    @property
    def relationship(self) -> Dict[int, str]:
        """Fetches the Character's relationships with other characters.

        :return: The character's relationships with other characters.
        """
        return self._relationship

    def add_relationship(self, char_id: int, relation: str) -> None:
        """Adds or updates a relationship between characters.

        :param char_id: The other character's ID.
        :param relation: The relationship to add/update.
        :return: None
        """
        self._relationship[char_id] = relation

    # Personality
    @property
    def personality(self) -> List[str]:
        """Fetches the Character's personality.

        :return: The character's personality.
        """
        return self._personality

    # Inventory
    @property
    def inventory(self) -> List[str]:
        """Fetches the Character's inventory.

        :return: The character's inventory.
        """
        return self._inventory

    # Occupation
    @property
    def occupation(self) -> str:
        """Fetches the Character's occupation.

        :return: The character's occupation.
        """
        return self._occupation

    @occupation.setter
    def occupation(self, new_occupation: str) -> None:
        """Sets the Character's occupation.

        :param new_occupation: The new occupation.
        :return: None
        """
        self._occupation = new_occupation
    
    def add_inventory(self, new_item: str) -> None:
        """Adds an item to the Character's inventory.

        :param new_item: The new item to be added into the character's inventory.
        :return: None
        """
        self._inventory.append(new_item.lower())
    
    def remove_inventory(self, item: str) -> None:
        """Removes an item from the Character's inventory.

        :param item: The item to be removed from the Character's inventory.
        :return: None
        """
        # if item not in inventory, ignore the removal of the item
        if item in self._inventory:
            index: int = self._inventory.index(item)
            self._inventory.pop(index)

    # HP (STATS)
    @property
    def hp(self) -> int:
        """Fetches the Character's HP.

        :return: The character's HP.
        """
        return self._stats["HP"]
    
    def increase_hp(self, new_hp: int) -> None:
        """Increases the Character's HP by an amount.
        If the increased HP is over 100, sets it to 100.

        :param new_hp: The amount to increase the character's HP.
        :return: None
        """
        if self._stats["HP"] + new_hp >= 100:
            self._stats["HP"] = 100
        else:
            self._stats["HP"] += new_hp
    
    def decrease_hp(self, new_hp: int) -> None:
        """Decreases the Character's HP by an amount.
        If the decreased HP is less than 0, sets it to 0.

        :param new_hp: The amount to decrease the character's HP.
        :return: None
        """
        if self._stats["HP"] - new_hp <= 0:
            self._stats["HP"] = 0
        else:
            self._stats["HP"] -= new_hp

    # LUCK (STATS)
    @property
    def luck(self) -> int:
        """Fetches the Main Character's LUCK.

        :return: The character's LUCK.
        """
        return self._stats["LUCK"]

    # CHA (STATS)
    @property
    def cha(self) -> int:
        """Fetches the Main Character's charisma (CHA).

        :return: The character's charisma (CHA).
        """
        return self._stats["CHA"]

    # Current Location
    @property
    def current_location(self) -> str:
        """Fetches the Character's current location.

        :return: The Character's current location.
        """
        return self._current_location

    @current_location.setter
    def current_location(self, new_location: str) -> None:
        """Sets the Character's current location.

        :param new_location: The character's new location.
        :return: None
        """
        self._current_location = new_location

    # Appearance
    @property
    def appearance(self) -> str:
        """Fetches the Character's appearance.

        :return: The Character's appearance.
        """
        return self._appearance

    @override
    def __str__(self) -> str:
        """Creates a string representation of the Character.
        Includes typing for each attribute.

        :return: String representation of the Character.
        """
        return (f'{{\n'
                f'"id": int "{self._id}"\n'
                f'"name": str "{self._name}"\n'
                f'"physical_condition": str "{self._physical_condition}"\n'
                f'"occupation": str "{self._occupation}"\n'
                f'"money": float {self._money}\n'
                f'"relationship": Dict[other_char_id: int, relationship_type: str] {self._relationship}\n'
                f'"personality": List[str] {self._personality}\n'
                f'"inventory": List[str] {self._inventory}\n'
                f'"stats": Dict[stat: str, val: int] {self._stats}\n'
                f'"current_location": str "{self._current_location}"\n'
                f'"appearance": str "{self._appearance}"'
                f'}}')

    def to_dict(self) -> Dict[str, V]:
        """Creates a dictionary representation of the Character.

        :return: Dictionary object of the Character.
        """
        return {
            "id": self.id,
            "name": self.name,
            "physical_condition": self.physical_condition,
            "occupation": self._occupation,
            "money": self._money,
            "relationship": self._relationship,
            "personality": self._personality,
            "inventory": self._inventory,
            "stats": self._stats,
            "current_location": self._current_location,
            "appearance": self._appearance
        }
