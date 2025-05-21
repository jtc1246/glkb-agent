import json
import time
from multi_thread_workers import map_infinite_retry
import sys
import os
BASE_PATH = os.path.dirname(os.path.abspath(__file__)) + '/'
sys.path.append(BASE_PATH + '../..')
from ai_assistant import chat_one_round
from llm import *
from config import LOG_PATH
from utils import FunctionPool, set_function_pool
from copy import deepcopy
import os
import random
random.seed(1246)
from _thread import start_new_thread
import argparse

parser = argparse.ArgumentParser(description="The testing code for GLKB agent, including multiple LLMs and multiple datasets.")
parser.add_argument('--llm', type=str, required=True, help="The LLM to use. Can only choose from: ['gpt_4o', 'claude_3_7_api', 'grok_3_api_openai', 'deepseek_v3', 'nebius_qwen3_235b', 'nebius_qwen25_72b', 'nebius_llama33_70b', 'nebius_llama31_405b'].")
parser.add_argument('--dataset', type=str, required=True, help="The dataset to use. Can only choose from: ['pubmed_qa', 'pubmed_qa_large' 'bioasq'].")
parser.add_argument('--num-workers', type=int, default=100, help="The number of workers to use. Default is 100.")
parser.add_argument('--llm-threads', type=int, default=50, help="The number of threads for LLM. Default is 50.")
parser.add_argument('--func-call-threads', type=int, default=15, help="The number of threads for function calling to GLKB. To avoid overloading the GLKB server and causing errors, this number should not exceed 15. Default is 15.")
parser.add_argument('--id', type=int, default=1, help="The id of the test. Default is 1. If all of llm, dataset, and id are the same, the test can be resumed from the previously runned results if you exit before the test finishes.")
parser.add_argument('--deepseek-modified-prompt', action='store_true', help="Whether to use the modified prompt for DeepSeek. Only valid for pubmed_qa and bioasq, if you use this in pubmed_qa_large, it will be ignored. Default is False.")
args = parser.parse_args()

print(os.path.abspath(__file__))
print(args)

FUNC_CALL_THREADS = args.func_call_threads
ID = args.id
LLM_THREADS = args.llm_threads
LLM_FUNC = args.llm
MAX_WAITING_NUM = args.num_workers
if (args.dataset == 'pubmed_qa'):
    DATA = json.loads(open(BASE_PATH + 'pubmedqa.json').read())
    DATA = [{'id': id, 'question': DATA[id]["QUESTION"], 'answer': DATA[id]['final_decision']} for id in DATA]
    TEST_FUNC = 'test_pubmed_qa' if not args.deepseek_modified_prompt else 'test_pubmed_qa_deepseek'
elif (args.dataset == 'pubmed_qa_large'):
    DATA = json.loads(open(BASE_PATH + 'pubmedqa_large.json').read())
    DATA = [{'id': id, 'question': DATA[id]["QUESTION"], 'answer': DATA[id]['final_decision']} for id in DATA]
    TEST_FUNC = 'test_pubmed_qa_large'
elif (args.dataset == 'bioasq'):
    DATA = json.loads(open(BASE_PATH + 'bioasq_618.json').read())
    choice_to_answer = {'A': 'yes', 'B': 'no'}
    DATA = [{'question': d["question"], 'answer': choice_to_answer[d['answer']]} for d in DATA]
    TEST_FUNC = 'test_bioasq' if not args.deepseek_modified_prompt else 'test_bioasq_deepseek'
else:
    assert (False), f"Dataset {args.dataset} not found. Please choose from ['pubmed_qa', 'pubmed_qa_large', 'bioasq']"
DATA = DATA[:50]  # for test
llm_pool = LlmPool(eval(LLM_FUNC), LLM_THREADS, f'{LOG_PATH}/llm_{TEST_FUNC}_{LLM_FUNC}_{ID}.txt',
                   0.6, 1.0, 4000, True)
result_path = f'{LOG_PATH}/{TEST_FUNC}_{LLM_FUNC}_{ID}.json'
log_dir = f'{LOG_PATH}/{TEST_FUNC}_{LLM_FUNC}_{ID}/'
function_pool = FunctionPool(FUNC_CALL_THREADS)
set_function_pool(function_pool)
num = len(DATA)
os.makedirs(log_dir, exist_ok=True)

def run_one_test(data: tuple[int, dict]) -> dict:
    index, input = data
    output_path = f'{log_dir}/{to_4_digits(index)}.json'
    try:
        with open(output_path, 'r') as f:
            result = json.loads(f.read())
            return result
    except:
        pass
    result = TEST_FUNC(input, llm_pool)
    with open(output_path, 'w') as f:
        f.write(json.dumps(result, indent=2, ensure_ascii=False))
    return result

def run_tests():
    inputs = [(i, DATA[i]) for i in range(num)]
    results = map_infinite_retry(run_one_test, inputs, max_workers=MAX_WAITING_NUM, print_progress=True)
    with open(result_path, 'w') as f:
        f.write(json.dumps(results, indent=2, ensure_ascii=False))


def to_4_digits(num: int):
    num = str(num)
    return '0' * (4 - len(num)) + num


def process_question(question: str, llm_pool: LlmPool):
    history, answer = chat_one_round([], question, llm_pool)
    return {'chat_history': history, 'final_answer': answer}


def check_format_pubmed_qa(response: str) -> str:
    response = response.upper()
    if ('YES' in response):
        assert ('NO' not in response and 'MAYBE' not in response), f"Format error: contain more than one of YES, NO, MAYBE"
        return 'YES'
    if ('NO' in response):
        assert ('YES' not in response and 'MAYBE' not in response), f"Format error: contain more than one of YES, NO, MAYBE"
        return 'NO'
    if ('MAYBE' in response):
        assert ('YES' not in response and 'NO' not in response), f"Format error: contain more than one of YES, NO, MAYBE"
        return 'MAYBE'
    assert (False), f"Format error: not contain YES, NO, MAYBE"


def test_pubmed_qa(input: dict, llm_pool: LlmPool) -> dict:
    result = deepcopy(input)
    question = 'Please answer the following question, using "yes", "no", or "maybe".\nOnly answer "maybe" if really necessary. In most cases, you should not answer "maybe".\nONLY ANSWER "maybe" if you are really unsure about the question. IF YOU HAVE ANY TENDENCY to "yes" or "no", please answer "yes" or "no", not "maybe".\nIn your final output, you should only include one word, and should be one of "YES", "NO", or "MAYBE", in upper case.\n\n' + input['question']
    response = process_question(question, llm_pool)
    answer = check_format_pubmed_qa(response['final_answer']).lower()
    result['llm_answer'] = answer
    result['llm_response'] = response['final_answer']
    result['correct'] = (result['llm_answer'] == result['answer'])
    result['llm_chat_history'] = response['chat_history']
    return result


def check_format_pubmed_qa_large(response: str) -> str:
    response = response.upper()
    if ('YES' in response):
        assert ('NO' not in response), f"Format error: contain more than one of YES, NO"
        return 'YES'
    if ('NO' in response):
        assert ('YES' not in response ), f"Format error: contain more than one of YES"
        return 'NO'
    assert (False), f"Format error: not contain YES, NO"


def test_pubmed_qa_large(input: dict, llm_pool: LlmPool) -> dict:
    result = deepcopy(input)
    question = 'Please answer the following question, using "yes", or "no".\nIn your final output, you should only include one word, and should be one of "YES", or "NO", in upper case.\n\n' + input['question']
    response = process_question(question, llm_pool)
    answer = check_format_pubmed_qa_large(response['final_answer']).lower()
    result['llm_answer'] = answer
    result['llm_response'] = response['final_answer']
    result['correct'] = (result['llm_answer'] == result['answer'])
    result['llm_chat_history'] = response['chat_history']
    return result


check_format_bioasq = check_format_pubmed_qa_large


def test_bioasq(input: dict, llm_pool: LlmPool) -> dict:
    result = deepcopy(input)
    question = 'Please answer the following question, using "yes", or "no".\nIn your final output, you should only include one word, and should be one of "YES", or "NO", in upper case.\n\n' + input['question']
    response = process_question(question, llm_pool)
    answer = check_format_bioasq(response['final_answer']).lower()
    result['llm_answer'] = answer
    result['llm_response'] = response['final_answer']
    result['correct'] = (result['llm_answer'] == result['answer'])
    result['llm_chat_history'] = response['chat_history']
    return result


def test_pubmed_qa_deepseek(input: dict, llm_pool: LlmPool) -> dict:
    result = deepcopy(input)
    question = 'Please answer the following question, using "yes", "no", or "maybe".\nOnly answer "maybe" if really necessary.\nNote:\n1. In most cases, you should not answer "maybe".\n2. ONLY ANSWER "maybe" if you are really unsure about the question. IF YOU HAVE ANY TENDENCY to "yes" or "no", please answer "yes" or "no", not "maybe". The possibility of "maybe" in ground truth is LESS THAN 5%.\n3. In your final output, you should only include one word, and should be one of "YES", "NO", or "MAYBE", in upper case.\n4. You must call functions in GLKB. You are not allowed to answer user\'s question directly without calling functions.\n\n' + input['question']
    response = process_question(question, llm_pool)
    answer = check_format_pubmed_qa(response['final_answer']).lower()
    result['llm_answer'] = answer
    result['llm_response'] = response['final_answer']
    result['correct'] = (result['llm_answer'] == result['answer'])
    result['llm_chat_history'] = response['chat_history']
    return result


def test_bioasq_deepseek(input: dict, llm_pool: LlmPool) -> dict:
    result = deepcopy(input)
    question = 'Please answer the following question, using "yes", or "no".\nIn your final output, you should only include one word, and should be one of "YES", or "NO", in upper case.\nYou must call functions in GLKB. You are not allowed to answer user\'s question directly without calling functions.\n\n' + input['question']
    response = process_question(question, llm_pool)
    answer = check_format_bioasq(response['final_answer']).lower()
    result['llm_answer'] = answer
    result['llm_response'] = response['final_answer']
    result['correct'] = (result['llm_answer'] == result['answer'])
    result['llm_chat_history'] = response['chat_history']
    return result


if __name__ == "__main__":
    TEST_FUNC = eval(TEST_FUNC)
    run_tests()
