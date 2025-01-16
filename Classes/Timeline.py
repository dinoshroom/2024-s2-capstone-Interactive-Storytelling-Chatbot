from typing import List, TypeVar

from typing_extensions import override

V = TypeVar("V")


class Timeline:
    def __init__(self, event: List[str] = []):
        """Initialise a Timeline object.

        :param event: The timeline.
        """
        self._key_events = event

    @property
    def get_event(self) -> List[str]:
        """Fetches the list of events.

        :return: The list of events.
        """
        return self._key_events

    def add_event(self, new_event: str) -> None:
        """Adds an event to the timeline.

        :param new_event: The new event.
        :return: None
        """
        if new_event not in self._key_events:
            self._key_events.append(new_event)

    @override
    def __str__(self) -> str:
        """Creates a string representation of the timeline.
        This also includes the typing of each attribute.

        :return: String representation of the timeline.
        """
        return (f'{{\n'
                f'"key_events": list[str] {self._key_events}\n'
                f'}}')

    def to_dict(self) -> dict[str, list[str]]:
        """Creates a dictionary representation of the timeline.

        :return: Dictionary object of the timeline.
        """
        return {
            "key_events": self._key_events
        }
