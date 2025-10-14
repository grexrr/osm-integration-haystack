from ast import Dict
from typing import List, Union
from haystack import Document, component

@component
class OSM_Fetcher:
    def __init__(self) -> None:
        pass
    
    @component.output_types(documents=List[Document], links=List[str])
    def run(self, query:str) -> Dict[str, Union[List[Document], List[str]]]:
        return
    
    