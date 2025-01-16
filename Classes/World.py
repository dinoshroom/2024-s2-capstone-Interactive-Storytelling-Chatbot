from typing import List, Dict, TypeVar

from typing_extensions import override

V = TypeVar("V")


class World:
    def __init__(self, rules: List[str] = [], genre: str = "", environment: str = "", locations: List[str] = []):
        """Initialises a World object.

        :param rules: Rules of the world.
        :param genre: The genre of the world.
        :param environment: A description of the current location of the main character.
        :param locations: Previous locations the main character has been to.
        """
        self._rules = rules
        self._genre = genre
        self._environment = environment
        self._locations = locations

    @property
    def rules(self) -> List[str]:
        """Fetches the rules of the world.

        :return: Rules of the world as a list of strings.
        """
        return self._rules

    def add_rules(self, rules: List[str]):
        for rule in rules:
            self._rules.append(rule)

    @property
    def environment(self) -> str:
        """Fetches the description of the current location of the main character.

        :return: The description of the current location as a string.
        """
        return self._environment

    @environment.setter
    def environment(self, value: str) -> None:
        """Sets a new description of the current location of the main character.

        :param value: New description of the current location as a string.
        :return: None
        """
        self._environment = value

    @property
    def genre(self) -> str:
        """Fetches the genre of the world.

        :return: The genre of the world as a string.
        """
        return self._genre

    @property
    def locations(self) -> List[str]:
        """Fetches the previous locations of the main character.

        :return: A list of all previous locations the main character has been to.
        """
        return self._locations

    def add_locations(self, value: str) -> None:
        """Adds a previous location.

        :param value: The previous location to add as a string.
        :return: None
        """
        if value not in self._locations:
            self._locations.append(value)

    @override
    def __str__(self) -> str:
        """Creates a string representation of the world.
        This also includes the typing of each attribute.

        :return: String representation of the world.
        """
        return (f'{{\n'
                f'"rules": List[str] {self._rules}\n'
                f'"genre": str "{self._genre}"\n'
                f'"environment": str  "{self._environment}"\n'
                f'"locations": List[str] {self._locations}\n'
                f'}}')

    def to_dict(self) -> dict[str, V]:
        """Creates a dictionary representation of the world.

        :return: Dictionary object of the world.
        """
        return {
            "rules": self.rules,
            "genre": self.genre,
            "environment": self.environment,
            "locations": self.locations
        }
