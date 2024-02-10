"""Module to handle GPT functionalities"""

from typing import List, Optional, Dict
import os
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores.chroma import Chroma
from langchain.chains.conversation.memory import ConversationSummaryMemory
from langchain.agents import OpenAIFunctionsAgent
from langchain.prompts import MessagesPlaceholder
from langchain.chat_models import ChatOpenAI
from langchain.agents import AgentExecutor
from langchain.schema import SystemMessage
from pydantic import BaseModel, Field
from langchain.tools import Tool
from langchain.agents import tool
from LLM.gptTools import fetchSection
from pprint import pprint
import json
from LLM.gptTools import webSearchTool


from LLM.config import document_gpt_system_message


from DatabaseHandler import executeQueryAndReturnJson, documents_table


class BaseGPT:
    """Base GPT class"""

    def __init__(self, system_message: SystemMessage, tools: List[callable]):
        self.tools = tools
        self.llm = ChatOpenAI(temperature=0, model="gpt-4-0125-preview")

        memory = ConversationSummaryMemory(
            llm=self.llm, memory_key="memory", return_messages=True
        )

        self.prompt = OpenAIFunctionsAgent.create_prompt(
            system_message=system_message,
            extra_prompt_messages=[MessagesPlaceholder(variable_name="memory")],
        )

        agent = OpenAIFunctionsAgent(llm=self.llm, tools=self.tools, prompt=self.prompt)
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            memory=memory,
            max_iterations=100,
            max_execution_time=1000,
        )

    def run(self, query: str) -> str:
        """executes the given prompt and returns response.

        Args:
            query (str): prompt query

        Returns:
            str: prompt response
        """
        response = self.agent_executor.run(query)
        return response


class DocumentGpt(BaseGPT):
    """Document GPT class"""

    def __init__(
        self,
        index: Dict,
        content: List[str],
    ):
        """initializes document gpt

        Args:
            index (Dict): index of all the documents and its metadata present in the db.
            content (List[str]): Content for each of the index item, this is fed into vector db and used in RAG
        """

        msg = document_gpt_system_message.format(index=str(index))
        # print(msg)
        self.system_message = SystemMessage(content=msg)

        fetchSectionFunc = fetchSection(
            vector_db=Chroma.from_texts(
                content, OpenAIEmbeddings(disallowed_special=())
            )
        )
        fetchSectionTool = Tool.from_function(
            func=fetchSectionFunc,
            name=fetchSectionFunc.name,
            description=fetchSectionFunc.description,
            args_schema=fetchSectionFunc.args_schema,
        )

        super().__init__(
            system_message=self.system_message,
            tools=[fetchSectionTool, webSearchTool],
        )


def getDocumentGPT() -> DocumentGpt:
    """Returns a document gpt class

    Raises:
        FileNotFoundError: if ther are no documents in the db

    Returns:
        DocumentGpt: gpt used to run prompts on.
    """
    result = executeQueryAndReturnJson(
        f"select document_name, document_summary, document_tags from {documents_table} where document_summary is not null"
    )

    if not result:
        raise FileNotFoundError(f"There are no documents in the database")

    index = {}
    chunks = []

    for row in result:
        name = row["document_name"]
        sections = json.loads(row["document_summary"])
        tags = json.loads(row["document_tags"])

        section_names = [section_name for section_name in sections]
        index[name] = {"sections": section_names, "tags": tags}

        for section_name, section_info in sections.items():
            chunks.append(f"""{name} {section_name}: {section_info}""")

    # print(index)
    return DocumentGpt(index=index, content=chunks)
