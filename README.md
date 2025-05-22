# GLKB Agent

## 1. Dataset

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

Before running the code, you need to have python >=3.9 installed, and install the dependencies in [requirements.txt](requirements.txt). You can use `pip3 install -r requirements.txt`。 

## 3. Tesing code

The code include 3 parts, one is for no GLKB (ask LLM directly), one is normal GLKB agent (normal usage, not for testing), another one is GLKB agent for testing on the above datasets.

#### 3.1 No GLKB

It is in [code/no_GLKB](code/no_GLKB) directory.

You can run one of [`pubmed_qa.py`](code/no_GLKB/pubmed_qa.py), [`pubmed_qa_large.py`](code/no_GLKB/pubmed_qa_large.py), or [`bioasq.py`](code/no_GLKB/bioasq.py). 

To run these, you need to specify the LLM to use, by passing `--llm` argument, and you can also set the number of workers to use. You can use `-h` to see the details. 

Before running these files, you also need to set the API keys in [`config.py`](config.py), please note that [`config.py`](config.py) is in root directory of this repo, not in `code/no_GLKB` directory.

You can run these files in any directory, and the results will be saves in `outputs` directory in your current directory.