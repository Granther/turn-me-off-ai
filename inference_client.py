from groq import Groq
from openai import OpenAI
from dotenv import load_dotenv
import json
import re
import os

class InferenceClient():
    def __init__(
        self,
        model: str=None,
        api_key: str=None,
        inference_url: str=None,
        max_new_tokens: int=3000,
        global_sys_prompt: str=None,
        backend: str="groq", 
        temperature: float=1.0,
        groq_key_name: str="GROQ_API_KEY",
        openai_key_name: str="OPENAI_API_KEY",
        verbose: bool=False
    ):
        load_dotenv()

        if not model:
            return ValueError("Must specify model") 

        self.backends = ['groq', 'openai']
        self.api_key = api_key
        self.model = model
        self.inference_url = inference_url
        self.max_new_tokens = max_new_tokens
        self.global_sys_prompt = global_sys_prompt
        self.backend = backend.lower()
        self.temperature = temperature
        self.history = dict()
        self.verbose = verbose

        if backend not in self.backends:
            raise ValueError(f"backend must be one of these: {self.backends}")
        
        if verbose:
            print(f"InferenceClient: Using {backend} backend")
            if not api_key:
                print(f"InferenceClient: Attempting to use API key from .env since api_key was not passed")
        
        if backend == "groq":
            self.client = Groq(api_key=api_key or os.getenv(groq_key_name))
        elif backend == "openai":
            self.client = OpenAI(api_key=api_key or os.getenv(openai_key_name), base_url=inference_url)

    
    def get_session_history(self, chatuuid: str) -> list:
        if chatuuid not in self.history:
            self.history[chatuuid] = list()

        if chatuuid is None:
            return list()
        
        return self.history[chatuuid]
    
    def clear_session_history(self, chatuuid: str):
        self.history[chatuuid] = []

    def user_infer_stream(self, chatuuid: str = "abc123", user_prompt: str = None, sys_prompt: str = None):
        history = self.get_session_history(chatuuid)

        if sys_prompt != None:
            history.append({"role":"user", "content":user_prompt})
            history.append({"role":"system", "content":sys_prompt})
        else:
            history.append({"role":"user", "content":user_prompt})


    def simple_infer(self, prompt, sys_prompt:str=None, model:str=None, max_new_tokens:int=None, temperature:float=None, chatuuid:str=None):
        model = model or self.model
        sys_prompt = sys_prompt or self.global_sys_prompt
        max_new_tokens = max_new_tokens or self.max_new_tokens
        temperature = temperature or self.temperature

        history = self.get_session_history(chatuuid)

        if sys_prompt:
            history.append({"role": "system", "content": sys_prompt})
        history.append({"role":"user", "content": prompt})

        if self.verbose:
            print(f"InferenceClient: chat history {history}")

        response = self.client.chat.completions.create(
            messages=history,
            model=model,
            temperature=temperature,
            max_tokens=max_new_tokens,
            top_p=1,
            stream=False,
        )

        message = response.choices[0].message.content
        history.append({"role":"assistant", "content": message})
        return message
    
    def simple_infer_stream(self, prompt, sys_prompt:str=None, model:str=None, max_new_tokens:int=None, temperature:float=None, chatuuid:str=None):
        print("PROMPT", prompt)
        model = model or self.model
        sys_prompt = sys_prompt or self.global_sys_prompt
        max_new_tokens = max_new_tokens or self.max_new_tokens
        temperature = temperature or self.temperature

        history = self.get_session_history(chatuuid)

        if sys_prompt:
            history.append({"role": "system", "content": sys_prompt})
        history.append({"role":"user", "content": prompt})

        if self.verbose:
            print(f"InferenceClient: chat history {history}")

        response = self.client.chat.completions.create(
            messages=history,
            model=model,
            temperature=temperature,
            max_tokens=max_new_tokens,
            stream=True,
        )

        partial_message = ""
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                partial_message = partial_message + chunk.choices[0].delta.content
                partial_message = self.htmlify(partial_message)
                yield f"data: {json.dumps({'message': partial_message})}\n\n"

        if "quantum" in partial_message.lower():
            yield "event: shutdown\n"
            yield f"data: {True}\n\n"
        
        yield "event: end\n"
        yield "data: done\n\n"

        history.append({"role":"assistant", "content": partial_message})
    
    def htmlify(self, response):
        # response = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', response)
        # return re.sub(r'\n', r'<br>', response)
        return response.replace("\n", "<br>").replace("\r", "<br>")
    
    def set_sys_prompt(self, new_sys):
        self.global_sys_prompt = new_sys

    def set_model(self, new_model):
        self.model = new_model

if __name__ == "__main__":
    # infer = InferenceClient(model="gemma2-9b-it", api_key="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", verbose=True)
    # x = infer.simple_infer("My name is bob", stream=False, chatuuid="123")
    # print(x)
    # x = infer.simple_infer("What is my name", stream=False, chatuuid="123")
    # print(x)
    pass
