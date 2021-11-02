import logging


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class MetadataBuffer(metaclass=Singleton):
    def __init__(self) -> None:
        logging.debug("Init MetadataBuffer!")
        super().__init__()
        self._buffer = {}

    def put(self, tag_id, metadata):
        logging.info(f"Metadata Buffer: add metadata for tag {tag_id}!")
        if id not in self._buffer.keys():
            self._buffer[tag_id] = metadata

    def has(self, tag_id):
        found = tag_id in self._buffer.keys()
        logging.info(f"Metadata Buffer: metadata for tag {tag_id} in buffer: {found}!")
        return found

    def get(self, tag_id):
        if self.has(tag_id):
            logging.info(f"Metadata Buffer: found metadata for tag {tag_id}!")
            return self._buffer[tag_id].copy()
        else:
            logging.info(f"MetadataBuffer: did not find metadata for tag {tag_id}!")
            return None

    def clear(self):
        logging.debug("MetadataBuffer cleared!")
        self._buffer.clear()


    def has(self, id):
        return id in self._buffer.keys()

    def get(self, id):
        if self.has(id):
            return self._buffer[id].copy()
        else:
            return None

    def clear(self):
        self._buffer.clear()