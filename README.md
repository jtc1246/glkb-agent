# GLKB Agent

## 1. Datasets

#### 1.1 PubMedQA (1000 questions)

In [datasets/pubmedqa_1000.json](datasets/pubmedqa_1000.json), it contains 1000 questions generated from PubMedQA papers. The answers include "yes", "no", and "maybe". 

#### 1.2 PubMedQA Large (1500 questions)

In [datasets/pubmedqa_large_1500.json](datasets/pubmedqa_large_1500.json), it contains 1500 questions generated from PubMedQA papers. The answers only include "yes" and "no", and there is no "maybe" answer. This 1500 questions are randonly sampled from the original more than 200000 questions.

#### 1.3 BioASQ (618 questions)
In [datasets/bioasq_618.json](datasets/bioasq_618.json), these questions are from https://github.com/Teddy-XiongGZ/MIRAGE (the 618 BioASQ questions in it). It includes 618 questions, and the answers include "yes" and "no".

## 2. Results

We have tested these 3 datasets in multiple ways, including no GLKB agent (ask LLM directly), using GLKB agent, and only RAG. We also do these tests using different LLMs. The results are in [results](results) folder. Our results include the question, ground truth, answer from LLM, and also the original response from LLM.

In each json file, has following keys:

1. `"answer"`: the ground truth for this question
2. `"llm_answer"`: the answer from LLM
3. `"llm_response"`: the original response from LLM
4. `"correct"`: whether the answer from LLM is same as ground truth.

`"llm_chat_history"` key (only in GLKB agent), is the original chat history with LLM.

In RAG only test, it also has `"embedding_result"` and `"keyword_result"` keys, which are the information retrieved from GLKB using embedding search and keyword search (these are provided to the LLM to generate the answer).


## 3. Tesing codes

The code include 3 parts, one is for no GLKB (ask LLM directly), one is normal GLKB agent (normal usage, not for testing), another one is GLKB agent for testing on the above datasets.

Before running the code, you need to have python >=3.9 installed, and install the dependencies in [`requirements.txt`](requirements.txt). You can use `pip3 install -r requirements.txt`.

#### 3.1 No GLKB

It is in [code/no_GLKB](code/no_GLKB) directory.

You can run one of [`pubmed_qa.py`](code/no_GLKB/pubmed_qa.py), [`pubmed_qa_large.py`](code/no_GLKB/pubmed_qa_large.py), or [`bioasq.py`](code/no_GLKB/bioasq.py). 

To run these, you need to specify the LLM to use, by passing `--llm` argument, and you can also set the number of workers to use. You can use `-h` to see the details. (`--llm` can be chosen from `gpt_4o`, `claude_3_7_api`, `grok_3_api_openai`, `deepseek_v3`, `nebius_qwen3_235b`, `nebius_qwen25_72b`, `nebius_llama33_70b`, or `nebius_llama31_405b`)

Before running these files, you also need to set the API keys in [`config.py`](config.py), please note that [`config.py`](config.py) is in root directory of this repo, not in `code/no_GLKB` directory.

You can run these files in any directory, and the results will be saves in `outputs` directory in your current directory.

#### 3.2 Normal GLKB agent

This is only for narmal usage like chatting or online services, not for testing on the datasets here. It is in [code/GLKB_agent_normal](code/GLKB_agent_normal) directory.

For interactive usage, you can run [`ai_assistant.py`](code/GLKB_agent_normal/ai_assistant.py). It will ask you to input your question, and then you can chat with it interactively.

To use it in the code or program, you can see [`example.py`](code/GLKB_agent_normal/example.py) (and also [`ai_assistant.py`](code/GLKB_agent_normal/ai_assistant.py)) for the usage. In general, you can use `chat_one_round` function from [`ai_assistant.py`](code/GLKB_agent_normal/ai_assistant.py), you need to input the chat history and current question to it, and it will return a tuple of the updated chat history and current answer.

You also need to set the API key in [`code/GLKB_agent_normal/config.py`](code/GLKB_agent_normal/config.py). Please note that this is in `code/GLKB_agent_normal` directory, not in root directory, which is different from above. Here you only need to set the API key for OpenAI, because it only uses GPT for LLM.

To use the GLKB agent, you need to connect to UMich vpn. Currently GLKB server only accepts connections from UMich network.

#### 3.3 GLKB agent for testing

This is for testing on the datasets above. It is in [code/GLKB_agent_testing](code/GLKB_agent_testing) directory.

You need to run [`test_resumable.py`](code/GLKB_agent_testing/test_resumable.py) with following arguments:

1. `--llm`: the LLM to use. Choose from `gpt_4o`, `claude_3_7_api`, `grok_3_api_openai`, `deepseek_v3`, `nebius_qwen3_235b`, `nebius_qwen25_72b`, `nebius_llama33_70b`, or `nebius_llama31_405b`.

2. `--dataset`: the dataset to test, please choose from `pubmed_qa`, `pubmed_qa_large`, or `bioasq`.

There are also some optional arguments, you can use `-h` to see details.

You also need to set the API keys in [`config.py`](config.py), please note that [`config.py`](config.py) is in root directory of this repo, not in `code/GLKB_agent_testing` directory. And also no that no matter which LLM you choose, you always need to set the OpenAI API key, because the cypher agent will always use GPT.

To use the GLKB agent, you need to connect to UMich vpn. Currently GLKB server only accepts connections from UMich network.

You can run [`test_resumable.py`](code/GLKB_agent_testing/test_resumable.py) in any directory, and the results will be saves in `outputs` directory in your current directory.

The progress can be resumed if the program exits unexpectedly, as long as the config is same (same llm, same dataset, and same id, and run in the same directory).

## 4. MCP and deep research

For MCP, please see the README in [mcp-code/README.md](mcp-code/README.md).
