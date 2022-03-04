import abc
from lib.json import Json
from lib.log  import logger
from abc import abstractmethod, ABC
from lib.types import cbsdAction


class MessagePrimitive(ABC):

    def __init__(self):
        self.json = Json()
        self.logger = logger()

    @abstractmethod
    def Run(self) -> cbsdAction:
        pass

