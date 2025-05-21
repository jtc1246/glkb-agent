from openai import OpenAI
import anthropic
import json
import traceback
import sys
from config import OPENAI_API_KEY, CLAUDE_API_KEY, GROK_API_KEY, DEEPSEEK_API_KEY, NEBIUS_API_KEY
from time import sleep
from copy import deepcopy
from openai import NOT_GIVEN
from queue import LifoQueue, Queue
from _thread import start_new_thread

__all__ = ['llm_api_service', 'claude_3_7_api', 'grok_2_api', 'grok_2_api_openai',
           'gpt_4o', 'claude_3_7_api', 'grok_3_api_openai',
           'deepseek_v3', 'nebius_qwen3_235b', 'nebius_qwen25_72b', 'nebius_llama33_70b',
           'nebius_llama31_405b', "LlmPool"]

openai_client = OpenAI(api_key=OPENAI_API_KEY)
claude_client = anthropic.Client(api_key=CLAUDE_API_KEY)
grok_client = anthropic.Client(api_key=GROK_API_KEY, base_url="https://api.x.ai/")
grok_client_openai = OpenAI(api_key=GROK_API_KEY, base_url="https://api.x.ai/v1/")
deepseek_client = OpenAI(base_url="https://api.deepseek.com/v1", api_key=DEEPSEEK_API_KEY)
nebius_client = OpenAI(base_url="https://api.studio.nebius.com/v1/", api_key=NEBIUS_API_KEY)


def llm_api_service(system_message: str,
                    messages: list[dict],  # not include system message
                    temperature: float = 0.5,
                    top_p: float = 1.0,
                    max_tokens: int = 4000) -> tuple[str, dict]:
    '''
    LLM API interface.
    Returns: (response, usage dict)
    Usage dict: contain 4 keys, "input", "output", "cache_input", "cache_write", be None if that API service does not support.
    Should raise error if not successful, and (contain "429" or (contain "rate" and "limit")) if is rate limit error. (use lower case)
    '''
    pass


def gpt_4o(system_message: str,
           messages: list[dict],  # not include system message
           temperature: float = 0.5,
           top_p: float = 1.0,
           max_tokens: int = 4000,
           json_output: bool = False) -> tuple[str, dict]:
    messages = [{'role': 'system', 'content': system_message}] + messages
    resp_format = {'type': 'json_object'} if json_output else NOT_GIVEN
    response = openai_client.chat.completions.create(model='gpt-4o-2024-08-06',
                                                     messages=messages,
                                                     temperature=temperature,
                                                     top_p=top_p,
                                                     max_tokens=max_tokens,
                                                     response_format=resp_format)
    result = response.choices[0].message.content
    usage = {"input": response.usage.prompt_tokens, "output": response.usage.completion_tokens, "cache_input": None, "cache_write": None}
    return (result, usage)


def claude_3_7_api(system_message: str,
                   messages: list[dict],  # not include system message
                   temperature: float = 0.5,
                   top_p: float = 1.0,
                   max_tokens: int = 4000,
                   json_output: bool = False) -> tuple[str, dict]:
    response = claude_client.messages.create(model='claude-3-7-sonnet-20250219',
                                             system=system_message,
                                             messages=messages,
                                             temperature=temperature,
                                             top_p=top_p,
                                             max_tokens=max_tokens)
    result = response.content[0].text
    usage = {"input": response.usage.input_tokens, "output": response.usage.output_tokens, "cache_input": None, "cache_write": None}
    return (result, usage)


def grok_2_api(system_message: str,
               messages: list[dict],  # not include system message
               temperature: float = 0.5,
               top_p: float = 1.0,
               max_tokens: int = 4000,
               json_output: bool = False) -> tuple[str, dict]:
    response = grok_client.messages.create(model='grok-2-latest',
                                           system=system_message,
                                           messages=messages,
                                           temperature=temperature,
                                           top_p=top_p,
                                           max_tokens=max_tokens)
    result = response.content[0].text
    usage = {"input": response.usage.input_tokens, "output": response.usage.output_tokens, "cache_input": None, "cache_write": None}
    return (result, usage)


def grok_2_api_openai(system_message: str,
                      messages: list[dict],  # not include system message
                      temperature: float = 0.5,
                      top_p: float = 1.0,
                      max_tokens: int = 4000,
                      json_output: bool = False) -> tuple[str, dict]:
    messages = [{'role': 'system', 'content': system_message}] + messages
    resp_format = {'type': 'json_object'} if json_output else NOT_GIVEN
    response = grok_client_openai.chat.completions.create(model='grok-2-latest',
                                                          messages=messages,
                                                          temperature=temperature,
                                                          top_p=top_p,
                                                          max_tokens=max_tokens,
                                                          response_format=resp_format)
    result = response.choices[0].message.content
    usage = {"input": response.usage.prompt_tokens, "output": response.usage.completion_tokens, "cache_input": None, "cache_write": None}
    return (result, usage)


def grok_3_api_openai(system_message: str,
                      messages: list[dict],  # not include system message
                      temperature: float = 0.5,
                      top_p: float = 1.0,
                      max_tokens: int = 4000,
                      json_output: bool = False) -> tuple[str, dict]:
    messages = [{'role': 'system', 'content': system_message}] + messages
    resp_format = {'type': 'json_object'} if json_output else NOT_GIVEN
    response = grok_client_openai.chat.completions.create(model='grok-3-beta',
                                                          messages=messages,
                                                          temperature=temperature,
                                                          top_p=top_p,
                                                          max_tokens=max_tokens,
                                                          response_format=resp_format)
    result = response.choices[0].message.content
    usage = {"input": response.usage.prompt_tokens, "output": response.usage.completion_tokens, "cache_input": None, "cache_write": None}
    return (result, usage)


def deepseek_v3(system_message: str,
                messages: list[dict],  # not include system message
                temperature: float = 0.5,
                top_p: float = 1.0,
                max_tokens: int = 4000,
                json_output: bool = False) -> tuple[str, dict]:
    messages = [{'role': 'system', 'content': system_message}] + messages
    resp_format = {'type': 'json_object'} if json_output else NOT_GIVEN
    response = deepseek_client.chat.completions.create(model='deepseek-chat',
                                                       messages=messages,
                                                       temperature=temperature,
                                                       top_p=top_p,
                                                       max_tokens=max_tokens,
                                                       response_format=resp_format)
    result = response.choices[0].message.content
    usage = {"input": response.usage.prompt_tokens, "output": response.usage.completion_tokens, "cache_input": None, "cache_write": None}
    return (result, usage)


def nebius_qwen3_235b(system_message: str,
                      messages: list[dict],  # not include system message
                      temperature: float = 0.5,
                      top_p: float = 1.0,
                      max_tokens: int = 4000,
                      json_output: bool = False) -> tuple[str, dict]:
    messages = [{'role': 'system', 'content': system_message}] + messages
    resp_format = {'type': 'json_object'} if json_output else NOT_GIVEN
    response = nebius_client.chat.completions.create(model='Qwen/Qwen3-235B-A22B',
                                                     messages=messages,
                                                     temperature=temperature,
                                                     top_p=top_p,
                                                     max_tokens=max_tokens,
                                                     response_format=resp_format)
    result = response.choices[0].message.content
    usage = {"input": response.usage.prompt_tokens, "output": response.usage.completion_tokens, "cache_input": None, "cache_write": None}
    return (result, usage)


def nebius_qwen25_72b(system_message: str,
                      messages: list[dict],  # not include system message
                      temperature: float = 0.5,
                      top_p: float = 1.0,
                      max_tokens: int = 4000,
                      json_output: bool = False) -> tuple[str, dict]:
    messages = [{'role': 'system', 'content': system_message}] + messages
    resp_format = {'type': 'json_object'} if json_output else NOT_GIVEN
    response = nebius_client.chat.completions.create(model='Qwen/Qwen2.5-72B-Instruct',
                                                     messages=messages,
                                                     temperature=temperature,
                                                     top_p=top_p,
                                                     max_tokens=max_tokens,
                                                     response_format=resp_format)
    result = response.choices[0].message.content
    usage = {"input": response.usage.prompt_tokens, "output": response.usage.completion_tokens, "cache_input": None, "cache_write": None}
    return (result, usage)


def nebius_llama33_70b(system_message: str,
                       messages: list[dict],  # not include system message
                       temperature: float = 0.5,
                       top_p: float = 1.0,
                       max_tokens: int = 4000,
                       json_output: bool = False) -> tuple[str, dict]:
    messages = [{'role': 'system', 'content': system_message}] + messages
    resp_format = {'type': 'json_object'} if json_output else NOT_GIVEN
    response = nebius_client.chat.completions.create(model='meta-llama/Llama-3.3-70B-Instruct',
                                                     messages=messages,
                                                     temperature=temperature,
                                                     top_p=top_p,
                                                     max_tokens=max_tokens,
                                                     response_format=resp_format)
    result = response.choices[0].message.content
    usage = {"input": response.usage.prompt_tokens, "output": response.usage.completion_tokens, "cache_input": None, "cache_write": None}
    return (result, usage)


def nebius_llama31_405b(system_message: str,
                        messages: list[dict],  # not include system message
                        temperature: float = 0.5,
                        top_p: float = 1.0,
                        max_tokens: int = 4000,
                        json_output: bool = False) -> tuple[str, dict]:
    messages = [{'role': 'system', 'content': system_message}] + messages
    resp_format = {'type': 'json_object'} if json_output else NOT_GIVEN
    response = nebius_client.chat.completions.create(model='meta-llama/Meta-Llama-3.1-405B-Instruct',
                                                     messages=messages,
                                                     temperature=temperature,
                                                     top_p=top_p,
                                                     max_tokens=max_tokens,
                                                     response_format=resp_format)
    result = response.choices[0].message.content
    usage = {"input": response.usage.prompt_tokens, "output": response.usage.completion_tokens, "cache_input": None, "cache_write": None}
    return (result, usage)


class LlmPool:
    def __init__(self, llm_func: callable, num_threads: int, log_file: str, temperature: float, top_p: float, max_tokens: int, json_output: bool):
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        self.json_output = json_output
        self.llm_func = llm_func
        self.num_threads = num_threads
        self.log_file = log_file
        self.request_queue = Queue()
        self.log_queue = Queue()
        start_new_thread(self.log_thread, ())
        for i in range(num_threads):
            start_new_thread(self.llm_thread, (i,))

    def chat(self, system_message: str, messages: list[dict]) -> tuple[str, dict]:
        q = Queue()
        self.request_queue.put((system_message, messages, q))
        result = q.get()
        assert (result != None), "LLM API service error"
        return result

    def llm_thread(self, index: int):
        while True:
            system_message, messages, q = self.request_queue.get()
            try:
                result = self.llm_func(system_message, messages,
                                       temperature=self.temperature,
                                       top_p=self.top_p,
                                       max_tokens=self.max_tokens,
                                       json_output=self.json_output)
            except Exception as e:
                err_msg = traceback.format_exc()
                if ('429' in err_msg or ('rate' in err_msg.lower() and 'limit' in err_msg.lower())):
                    self.request_queue.put((system_message, messages, q))
                    print("Rate limit exceeded, waiting for 2 seconds ...", file=sys.stderr)
                    sleep(2)
                    continue
                print(err_msg, file=sys.stderr)
                q.put(None)
                continue
            q.put(result)
            log_message = f'Worker {index} REQUEST:\n\n' + json.dumps(messages, ensure_ascii=False, indent=2) + '\n\n' + \
                          'RESPONSE:\n\n' + json.dumps(result[0], ensure_ascii=False) + '\n\n\n'
            self.log_queue.put(log_message)

    def log_thread(self):
        f = open(self.log_file, 'a')
        while True:
            log_message = self.log_queue.get()
            f.write(log_message)
            f.flush()

    def wait_empty(self):
        pass


if __name__ == '__main__':
    system_message = "Always double the result of calculation."
    messages = [{"role": "user", "content": "what is 100 + 200"}]
    print(claude_3_7_api(system_message, messages))
