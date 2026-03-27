from abc import ABC, abstractmethod 
from pathlib import Path
from app.models.document import FileFormat,ParsedDocument


class BaseParser(ABC):

    @property
    @abstractmethod 
    def supported_format(self)->FileFormat:


    @property
    @abstractmethod
    def supported_extensions(self)->set[str]:

    
    @abstractmethod
    def parse(self,filePath:Path)->ParsedDocument:


    def can_handle(self,extension:str)->bool:
        return extension.lower().lstrip(".") in self.supported_extensions

