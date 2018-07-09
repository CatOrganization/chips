import json
import os
from abc import abstractmethod
from datetime import datetime


class PersistentDataStore(object):

    @abstractmethod
    def store(self, data):
        """Stores data in some kind of persistent storage"""


class LocalJsonStore(PersistentDataStore):
    """Stores data in a local JSON file (not preferred)"""

    def __init__(self, event_day: str):
        self.event_day = event_day

    def store(self, data):
        time = datetime.utcnow()
        data_filename = f'data/data-{self.event_day}-{time}.json'

        if not os.path.exists(data_filename):
            with open(data_filename, 'w', encoding='utf-8') as f:
                json.dump([], f)
        with open(data_filename, 'r', encoding='utf-8') as f:
            current_data = json.load(f)
        with open(data_filename, 'w', encoding='utf-8') as f:
            current_data.extend(data)
            json.dump(current_data, f)


class LocalDBStore(PersistentDataStore):
    """Stores data in a local data base"""

    def store(self, data):
        pass
