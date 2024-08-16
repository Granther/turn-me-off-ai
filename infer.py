import os
from groq import Groq
import re

from langchain_core.chat_history import (
    BaseChatMessageHistory,
    InMemoryChatMessageHistory,
)
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

class Inference:
    def __init__(self, sys_prompt, config = None):
        self.sys_prompt = sys_prompt
        self.config = config
        self.store = {}
        self.chat_config = {"configurable": {"session_id": "convo1"}}

    def _set_sys_prompt(self, new_sys_prompt):
        self.sys_prompt = new_sys_prompt

    def _add_ctx(self, search: str):
        prompt = self.char_data + "\n\n" + """Rephrase the below question to be about the above context, please use simple words and keep the question straight to the point. Keep the original intent of the question the same. Phrase the question more like a google search"""
        print(f"===== Add Ctx Prompt ===== : \n {prompt}")

        response = self.infer(sys_prompt=prompt, user_prompt=search)
        print(f"===== Add Ctx response =====: \n {response}")
        return response

    def _update_sys_prompt(self, user_prompt: str = None):
        self.char_data += "\n" + self.generic_search(self._add_ctx(user_prompt))
        self.sys_prompt = self.char_data + "\n\n" + self.rp_prompt

        print(f"===== Updated Sys prompt =====: \n {self.sys_prompt}")

    def _get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        if session_id not in self.store:
            self.store[session_id] = InMemoryChatMessageHistory()
        return self.store[session_id]

    def user_infer(self,  chatuuid: str = "abc123", user_prompt: str = None, model_name: str = "gemma2-9b-it"):
        model = ChatGroq(model=model_name)
        with_message_history = RunnableWithMessageHistory(model, self._get_session_history)

        response = with_message_history.invoke(
            [
                HumanMessage(content=user_prompt), 
                SystemMessage(content=self.sys_prompt)
            ],
            config={"configurable": {"session_id": chatuuid}},
        )

        return response.content