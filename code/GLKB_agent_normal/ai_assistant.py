from llm_wrapper import *
from utils import *
from typing import Tuple
from copy import deepcopy
import json
from llm import LlmPool, gpt_4o
from config import LOG_PATH


MAX_ITER = 5
PRINT_FUNC_CALL = True
PRINT_FUNC_RESULT = True


# pseudo code:

# MAX_ITER = 5
# messages = []
# model = <the_ai_assistant>  # This is you
#
# def user_input(question: str) -> str:
#     function_call_num = 0
#     messages.append({"role": "user", "content": question})
#     while True:
#         output = model.get_response(messages)
#         if (output.is_to_user):
#             messages.append({"role": "assistant", "content": output})
#             return output.text
#         else:
#             # to system
#             if (function_call_num == MAX_ITER):
#                 assert (False)  # This should not happen, because you should not do function callings when it reaches MAX_ITER
#             function_call_num += 1
#             messages.append({"role": "assistant", "content": output})
#             functions_list = output.functions
#             function_results = run_functions(functions_list)
#             messages.append({"role": "user", "content": function_results})

llm_pool = LlmPool(gpt_4o, 50, f'{LOG_PATH}/llm_log_gpt4o.txt', 0.6, 1.0, 4000, True)

def chat_one_round(messages_history: list[dict], question: str) -> Tuple[list[dict], str]:
    '''
    return (messages_history, response)
    '''
    question = question.strip()
    if (question == ''):
        question = '<empty>'
    question = '====== From User ======\n' + question
    messages = deepcopy(messages_history)
    messages.append({"role": "user", "content": question})
    function_call_num = 0
    llm_pool.wait_empty()
    while True:
        messages, response = chat_and_get_formatted(messages, llm_pool)
        if (response['to'] == 'user'):
            return (messages, response['text'])
        if (function_call_num == MAX_ITER):
            assert (False)  # Currently not handle this error
        function_call_num += 1
        if (PRINT_FUNC_CALL):
            print('\033[92m', end='')
            print('\nCalling fucntions: \n')
            print(json.dumps(response, indent=2, ensure_ascii=False))
            print()
            print('\033[0m', end='')
        functions_result = run_functions(response['functions'])
        if (PRINT_FUNC_RESULT):
            print('\033[93m', end='')
            print('\nFunction results: \n')
            print(functions_result)
            print('\033[0m', end='')
        new_message = '====== From System ======\nThe results of function callings:\n' + functions_result + '\n'
        if (function_call_num == MAX_ITER):
            new_message += 'You already called functions 5 continuous times. Next message you must return to user.'
        else:
            func_num = MAX_ITER - function_call_num
            new_message += f'You can call functions {func_num} more times, after this you need to return to user.'
        messages.append({"role": "user", "content": new_message})


def chat_forever():
    messages = []
    while True:
        question = input('Your question: ')
        messages, response = chat_one_round(messages, question)
        print(f'\nResponse:\n\n{response}\n')


if __name__ == "__main__":
    chat_forever()
