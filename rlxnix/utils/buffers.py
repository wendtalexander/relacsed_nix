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
        logging.debug(f"Metadata Buffer: add metadata for tag {tag_id}!")
        if id not in self._buffer.keys():
            self._buffer[tag_id] = metadata

    def has(self, tag_id):
        found = tag_id in self._buffer.keys()
        logging.debug(f"Metadata Buffer: metadata for tag {tag_id} in buffer: {found}!")
        return found

    def get(self, tag_id):
        if self.has(tag_id):
            logging.debug(f"Metadata Buffer: found metadata for tag {tag_id}!")
            return self._buffer[tag_id].copy()
        else:
            logging.debug(f"MetadataBuffer: did not find metadata for tag {tag_id}!")
            return None

    def clear(self, show_log=True):
        self._buffer.clear()
        if show_log:
            logging.debug(f"MetadataBuffer cleared! {len(self._buffer)}")


class FeatureBuffer(metaclass=Singleton):
    def __init__(self) -> None:
        super().__init__()
        self._buffer = {}

    def put(self, tag_id, feature_name, feature_data):
        logging.debug(f"FeatureBuffer: add feature data feature {feature_name} for tag {tag_id}!")
        if tag_id not in self._buffer.keys():
            self._buffer[tag_id] = {feature_name: feature_data}
        else:
            if feature_name not in self._buffer[tag_id].keys():
                self._buffer[tag_id][feature_name] = feature_data

    def has(self, tag_id, feature_name):
        found = tag_id in self._buffer.keys()
        found = found and feature_name in self._buffer[tag_id].keys()
        logging.debug(f"FeatureBuffer: feature data for feature {feature_name} and tag {tag_id} in buffer: {found}!")
        return found

    def get(self, tag_id, feature_name):
        if self.has(tag_id, feature_name) :
            logging.debug(f"FeatureBuffer: found feature data for feature {feature_name} and tag {tag_id}!")
            return self._buffer[tag_id][feature_name].copy()
        else:
            logging.debug(f"FeatureBuffer: did not find Feature {feature_name} for tag {tag_id}!")
            return None

    def clear(self, show_log=True):
        if show_log:
            logging.debug("FeatureBuffer cleared!")
        self._buffer.clear()
