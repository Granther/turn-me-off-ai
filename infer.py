import os
from groq import Groq
from openai import OpenAI
import re

from langchain_core.chat_history import (
    BaseChatMessageHistory,
    InMemoryChatMessageHistory,
)
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

class Inference:
    def __init__(self, sys_prompt: str = None, config = None):
        self.sys_prompt = sys_prompt
        self.history = {}
        self.config = config
        self.store = {}
        self.chat_config = {"configurable": {"session_id": "convo1"}}

    # def _get_session_history(self, session_id: str) -> list:
    #     if session_id not in self.store:
    #         self.store[session_id] = list()
    #     return self.store[session_id]

    def _get_session_history(self, chatuuid: str) -> list:
        if chatuuid not in self.history:
            self.history[chatuuid] = list()
        return self.history[chatuuid]
    
    def clear_session_history(self, chatuuid: str):
        history = self._get_session_history(chatuuid)
        return history.clear()

    def user_infer(self, chatuuid: str = "abc123", user_prompt: str = None, sys_prompt: str = None, model_name: str = "gemma2-9b-it"):
        model = ChatGroq(model=model_name)
        with_message_history = RunnableWithMessageHistory(model, self._get_session_history)

        print(with_message_history)

        response = with_message_history.invoke(
            [
                HumanMessage(content=user_prompt), 
                SystemMessage(content=sys_prompt)
            ],
            config={"configurable": {"session_id": chatuuid}},
        )

        return response.content

    def user_infer_stream(self, chatuuid: str = "abc123", user_prompt: str = None, sys_prompt: str = None):
        history = self._get_session_history(chatuuid)

        if sys_prompt != None:
            history.append({"role":"user", "content":user_prompt})
            history.append({"role":"system", "content":sys_prompt})
        else:
            history.append({"role":"user", "content":user_prompt})

        print(history)

        api_key = "rc_58c93098d1b3c0ca152c4e31f6a8f7a331c7edd4959c46a6e15898faa733a87c"
        client = OpenAI(
            base_url="https://api.featherless.ai/v1",
            api_key=api_key
        )

        response = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3-8B-Instruct",
            messages=history,
            temperature=1.0,
            stream=True,
            max_tokens=2000
        )

        partial_message = ""
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                partial_message = partial_message + chunk.choices[0].delta.content
                yield f"data: {partial_message}\n\n"

        history.append({"role":"assistant", "content":partial_message})