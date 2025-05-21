import os
from copy import deepcopy
from typing import Tuple
import json
import traceback
import sys
from llm import LlmPool

file_path = os.path.abspath(__file__)
file_path = os.path.dirname(file_path) + '/'

prompt = open(file_path + 'prompts/general_prompt.txt').read()
error_prompt = open(file_path + 'prompts/error_prompt.txt').read()

__all__ = ['chat_and_get_formatted']

LLM_POOL = None


def chat(messages: list, llm_pool: LlmPool) -> Tuple[bool, str]:
    max_trail = 3
    system_message = messages[0]['content']
    messages = messages[1:]
    while (max_trail > 0):
        try:
            result = llm_pool.chat(system_message, messages)
            return (True, result[0])
        except:
            max_trail -= 1
    return (False, '')


def check_json(response: str) -> Tuple[bool, dict]:
    try:
        response = json.loads(response, strict=False)
        assert (type(response) == dict)
        assert ('draft' in response)
        assert (response['to'] in ('system', 'user'))
        if (response['to'] == 'user'):
            assert (type(response['text']) == str)
        else:
            assert (type(response['functions'] == list))
            assert (len(response['functions']) > 0)
            for function in response['functions']:
                assert (type(function) == dict)
                assert ('name' in function)
                assert (type(function['name']) == str)
                assert ('input' in function)
                assert (type(function['input']) == str)
                assert (function['name'] in ('text_embedding', 'cypher_query', 'keyword_search'))
        return (True, response)
    except:
        err_msg = traceback.format_exc()
        print(err_msg, file=sys.stderr)
        return (False, err_msg)


def chat_and_get_formatted(messages: list, llm_pool: LlmPool) -> Tuple[list, dict]:
    '''
    Use messages to chat with GPT, and append the response to messages, but return
    json format with another chat

    messages don't include system message
    '''
    trials = 3
    messages = deepcopy(messages)
    messages.insert(0, {"role": "system", "content": prompt})
    valid = False
    response = ''
    json_response = {}
    for _ in range(0, trials):
        success, response = chat(messages, llm_pool)
        assert (success), 'Failed to get response from LLM'
        messages.append({"role": "assistant", "content": response})
        valid, json_response = check_json(response)
        if (valid):
            break
        print(json_response, file=sys.stderr)
        messages.append({"role": "user", "content": error_prompt.replace('$err-msg$', json_response)})
    assert (valid), f"LLM continously return invalid format, for {trials} times"
    messages.pop(0)
    return (messages, json_response)


if __name__ == "__main__":
    a = chat_and_get_formatted([{"role": "user", "content": "====== From User ======\nWhat is TP 53"}])
    print(a)
