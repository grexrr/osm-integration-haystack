from ast import Dict
from optparse import Option
from typing import List, Optional, Union
from haystack import Document, component

@component
class OSM_Fetcher:
    def __init__(
            self,
            top_k: Optional[int] = 10,
            max_result: Optional[int] = 10,
            ) -> None:
        self.top_k = top_k,
        self.max_result = max_result
    
    @component.output_types(documents=List[Document], links=List[str])
    def run(self, query:str) -> Dict[str, Union[List[Document], List[str]]]:
        return
    
    