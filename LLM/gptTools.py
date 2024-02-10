from langchain.agents import tool
from langchain.vectorstores.chroma import Chroma
from pydantic.v1 import BaseModel, Field
from langchain.agents import Tool
from typing import List, Union
from langchain.tools import BraveSearch
from LLM.keys import BRAVE_API_KEY


class fetchSectionArgsSchema(BaseModel):
    section_name: Union[str, List[str]] = Field(
        title="Section Name/s",
        description="Name of the section of a list of sections whose information you want to fetch.",
    )


class fetchSection:
    def __init__(self, vector_db: Chroma = None):
        self.vector_db = vector_db
        self.name = "fetchSection"
        self.description = "Given a valid section name, or a list of section names it retrieves relevant information about the section/s from the document."
        self.args_schema = fetchSectionArgsSchema

    def __call__(self, section_name: Union[str, List[str]]) -> str:
        """Given a valid section name, or a list of section names it retrieves relevant information about the section/s from the document.

        Args:
            section_name (Union[str, List[str]]): Name of the section of a list of sections whose information you want to fetch.

        Returns:
            str: Relevant information about the given valid section or the list of sections conatenated into one single paragraph.
        """
        if isinstance(section_name, str):
            section_name = [
                section_name,
            ]

        result = []
        for section in section_name:
            result.append(self.vector_db.similarity_search(section)[0].page_content)

        return "\n".join(result)


webSearchTool = BraveSearch.from_api_key(
    api_key=BRAVE_API_KEY, search_kwargs={"count": 3}
)
