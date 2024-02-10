import os
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from DatabaseHandler import executeQueryAndReturnJson, executeNonSelectQuery
import json
from DatabaseHandler import documents_table
import requests
from openai import OpenAI

import base64
from typing import List
from LLM.keys import OPENAI_API_KEY

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY


from LLM.config import (
    document_reformat_prompt_template,
    image_summary_prompt,
)

from typing import Dict, Union


class BaseChain:
    """Base class to hanlde all summary generation"""

    def __init__(self, prompt_str: str):
        # self.prompt = PromptTemplate.from_template(template=prompt_str)
        self.prompt = prompt_str
        # self.llm_chain = LLMChain(
        #     prompt=self.prompt,
        #     llm=ChatOpenAI(temperature=0, model="gpt-4-0125-preview"),
        # )
        self.llm_chain = OpenAI()

    def run(self, value_dict: Dict[str, Union[str, int, float, bool]]) -> str:
        """Runs the LLm chain and returns the resule

        Args:
            value_dict (Dict[str,str]): key value pair to substitue in the prompt template variable placeholders

        Returns:
            str: result
        """
        print("llm chain running...")
        self.prompt = self.prompt.format(**value_dict)
        # res: str = self.llm_chain.run(**value_dict)
        res: str = self.llm_chain.chat.completions.create(
            model="gpt-4-0125-preview",
            messages=[
                {"role": "system", "content": "You are a legal compliance expert."},
                {"role": "user", "content": self.prompt},
            ],
        )
        print("llm chain done running.")
        return res.dict()["choices"][0]["message"]["content"]


class DocumentReformatChain(BaseChain):
    """Guideline reformat generation"""

    def __init__(self):
        super().__init__(prompt_str=document_reformat_prompt_template)


def generateImageDescription(image_bytes: bytes) -> str:
    """Used to generate Image description from a given imagee bytes

    Args:
        image_bytes (bytes): bytes content of the image

    Returns:
        str
    """
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
    }

    payload: dict = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": image_summary_prompt,
                    },
                ],
            }
        ],
        "max_tokens": 4096,
    }

    payload["messages"][0]["content"].append(
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"},
        },
    )

    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
    )

    response_json = ""
    if response.status_code == 200:
        response_json: str = (
            response.json()
            .get(
                "choices",
                [
                    {},
                ],
            )[0]
            .get("message", {})
            .get("content")
        )

    return response_json
