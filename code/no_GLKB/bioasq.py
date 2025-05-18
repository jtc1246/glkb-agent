import traceback
import json
import sys
import os
BASE_PATH = os.path.dirname(os.path.abspath(__file__)) + '/'
sys.path.append(BASE_PATH + '../..')
from llm import *
from copy import deepcopy
from multi_thread_workers import map_infinite_retry
import time
import argparse

parser = argparse.ArgumentParser(description="The testing code for BioASQ (618 questions) with no GLKB or external resources.")
parser.add_argument('--llm', type=str, required=True, help="The LLM to use. Can only choose from: ['gpt_4o', 'claude_3_7_api', 'grok_3_api_openai', 'deepseek_v3', 'nebius_qwen3_235b', 'nebius_qwen25_72b', 'nebius_llama33_70b', 'nebius_llama31_405b'].")
parser.add_argument('--num-workers', type=int, default=20, help="The number of threads to use. Default is 20.")
args = parser.parse_args()


llm = args.llm
num_workers = args.num_workers
print(os.path.abspath(__file__))
print(args)

PROMPT = '''
Task: answer the following question, using "yes", or "no".
You need to first make a draft and analyze the question, and then answer.

Output format:
A json string, with 2 keys: "draft" and "answer".
The value of "draft" should be a string.
The value of "answer" should be a string, and its value can only be "yes", or "no".

Please output the json string directly, without any other explanations.
'''[1:-1]

ERROR_PROMPT = '''
Invalid response format. Please make sure your output can make the following function to return True.

def check_format(response: str) -> tuple[bool, str]:
    try:
        response = json.loads(response, strict=False)
        assert (type(response) == dict)
        assert ('draft' in response and 'answer' in response)
        assert (type(response['draft']) == str and type(response['answer']) == str)
        assert (response['answer'] in ['yes', 'no'])
        return (True, '')
    except:
        err_msg = traceback.format_exc()
        return (False, err_msg)
'''[1:-1]

data = json.loads(open(BASE_PATH + 'bioasq_618.json').read())
choice_to_answer = {'A': 'yes', 'B': 'no'}
data = [{'question': d["question"], 'answer': choice_to_answer[d['answer']]} for d in data]
# print(len(data))
LLM_FUNC = eval(llm)
os.makedirs('./outputs', exist_ok=True)
OUTPUT_PATH = f'./outputs/bioasq_{llm}_{time.time()}.json'
NUM_WORKERS = num_workers
print(OUTPUT_PATH)


def check_format(response: str) -> tuple[bool, str]:
    try:
        response = json.loads(response, strict=False)
        assert (type(response) == dict)
        assert ('draft' in response and 'answer' in response)
        assert (type(response['draft']) == str and type(response['answer']) == str)
        assert (response['answer'] in ['yes', 'no'])
        return (True, '')
    except:
        err_msg = traceback.format_exc()
        return (False, err_msg)


def process_one_question(input: dict) -> dict:
    result = deepcopy(input)
    response = LLM_FUNC(PROMPT, messages=[{'role': 'user', 'content': input['question']}], temperature=0.2, top_p=1.0, max_tokens=2000, json_output=True)[0]
    assert (check_format(response)[0])
    response_json = json.loads(response, strict=False)
    result['llm_answer'] = response_json['answer']
    result['llm_response'] = response
    result['correct'] = (result['llm_answer'] == result['answer'])
    return result


def run_bioasq_test():
    results = map_infinite_retry(process_one_question, data, max_workers=NUM_WORKERS, print_progress=True)
    open(OUTPUT_PATH, 'w').write(json.dumps(results, indent=2, ensure_ascii=False))
    correct_num = sum([1 if result['correct'] else 0 for result in results])
    total_num = len(results)
    print(f'Correct: {correct_num} / {total_num}')


if __name__ == '__main__':
    run_bioasq_test()
