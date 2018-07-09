import json
from datetime import datetime

from bs4 import BeautifulSoup, Tag
import requests
from typing import List, Set, Dict, Tuple

from store import PersistentDataStore, LocalJsonStore

StackElements = Set[Tag]
Stacks = List[int]

HTML_PARSER = 'lxml'
CHIPSTACK_CLASS = 'chipstack'
PLAYER__NAME_CLASS = 'player'
TITLE_CLASS = 'titlebg'
RANK_CLASS = 'place'

EVENT_DAYS = ['1a', '1b', '1c', '2ab', '2c']
EVENT_DAYS.extend(str(i) for i in range(3, 11))
URL_DAYS = range(6527, 6527 + len(EVENT_DAYS))

DAYS_MAP = {EVENT_DAYS[i]: str(url_day) for i, url_day in enumerate(URL_DAYS)}


class EmptyPage(Exception):
    """Raises when a page is empty"""


class Player(object):
    """Represents a player in the WSOP Main Event"""

    def __init__(self, name: str, **kwargs) -> None:
        """Creates a player with a name and sets the chip history to an empty list

        :param str name: Name of the player
        :param dict kwargs: Optional attributes that might be used in the future, such as hometown...
        """
        self.name = name
        self.chip_history: List(ChipHistory) = []
        self.optional_attributes = kwargs

    def __repr__(self) -> str:
        """Represents a player by their name"""
        return f'{self.name}'

    def __eq__(self, o: object) -> bool:
        """Tests equality by checking player's name"""
        if isinstance(o, Player):
            return self.name == o.name
        return False

    def json(self):
        data = {
            'name': self.name,
            'history': [history.json() for history in self.chip_history],
        }

        return json.dumps(data, sort_keys=True, default=str)


class ChipHistory(object):
    """Pairs a date with a chip stack"""

    def __init__(self, chip_count: int, rank, day: str) -> None:
        """Creates a chip history with the count paired with the day

        :param int chip_count: Number of chips
        :param int rank: Rank of the chipstack for the given day
        :param str day: Event day the stack count took place on
        """
        self.chip_count = chip_count
        self.rank = rank
        self.event_day = day
        self.timestamp = datetime.utcnow()

    def __repr__(self) -> str:
        """Represents a chip history as (day, count) (ex: (1b, 13,450)"""
        return f"({self.event_day}, {self.chip_count})"

    def json(self):
        data = {
            'timestamp': str(self.timestamp),
            'day': self.event_day,
            'rank': self.rank,
            'chip_count': self.chip_count,
        }

        return json.dumps(data, sort_keys=True)


def chipstack(div_list):
    pass


def elements_no_title(soup: BeautifulSoup, element_class: str) -> StackElements:
    title_elements = set(soup.find_all('li', class_=TITLE_CLASS))
    return set(soup.find_all('li', class_=element_class)) - title_elements


def parse_stats(soup: BeautifulSoup, day: str) -> Tuple[Player, ChipHistory]:
    rank_elements = elements_no_title(soup, RANK_CLASS)
    if not rank_elements:
        raise EmptyPage

    for rank_element in rank_elements:
        rank = rank_element.contents[0]
        curr_element: Tag = rank_element.find_next_sibling('li')
        player_attributes = {}
        chip_attributes = {'rank': rank}

        while isinstance(curr_element, Tag) and RANK_CLASS not in curr_element.attrs['class']:
            if PLAYER__NAME_CLASS in curr_element.attrs['class']:
                player_attributes['name'] = curr_element.text.strip()
            elif CHIPSTACK_CLASS in curr_element.attrs['class']:
                chip_attributes['chip_count'] = clean_stack_number(curr_element.text)
            else:
                player_attributes[curr_element.attrs['class'][0]] = curr_element.text
            curr_element = curr_element.next_sibling

        chip_attributes['day'] = day
        player = Player(**player_attributes)
        chip_stack = ChipHistory(**chip_attributes)
        yield (player, chip_stack)


def clean_stack_number(dirty_stack_number: str) -> int:
    return int(dirty_stack_number.strip().replace(',', ''))


def all_chipstacks(elements: StackElements) -> Stacks:
    return [clean_stack_number(stack.contents[0]) for stack in elements]


def html(url):
    return requests.get(url).content


def parse_day(event_day: str):
    url_day = DAYS_MAP[event_day]
    base_url = 'http://www.wsop.com/tournaments/chipcounts'

    player_map: Dict[str, Player] = {}

    page = 1

    while True:
        url = f'{base_url}/?aid=2&grid=1487&tid=16465&dayof={url_day}&rr=5&curpage={str(page)}'
        soup = BeautifulSoup(html(url), HTML_PARSER)

        try:
            for player, chip_stack in parse_stats(soup, event_day):
                if player.name not in player_map:
                    player_map[player.name] = player
                player_map[player.name].chip_history.append(chip_stack)
            page += 1
        except EmptyPage:
            break

    return player_map


def collect_data(data_store: PersistentDataStore, day: str):
    data = [player.json() for player in parse_day(day).values()]

    data_store.store(data)


def main():
    event_day = '10'
    data_store = LocalJsonStore(event_day)
    collect_data(data_store, event_day)


if __name__ == '__main__':
    main()
