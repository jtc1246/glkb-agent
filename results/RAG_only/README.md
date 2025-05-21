# Algorithms and prompts for the RAG-only method

## 1. Embedding search

The entire question is used to calculate the embedding and search for the most relevant abstracts in the database. The raw question is used directly, not processed.

## 2. Keyword search

The keywords are extracted with the following algorithm, and them use keyword search to search the extracted keywords in the database. The keywords are only extracted through static algorithm, not processed by LLM.

```python
from wordfreq import word_frequency

ALLOWED_CHARACTERS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_'
THRESHOLD = 5e-6
SECOND_THRESHOLD = 3e-6

DATA = json.loads(open('bioasq_618.json', 'r').read())


def format_text(text: str):
    text = list(text)
    for i in range(len(text)):
        if text[i] not in ALLOWED_CHARACTERS:
            text[i] = ' '
    text = ''.join(text).strip()
    text = text.replace(' - ', ' ').replace(' -- ', ' ')
    prev = text.replace('  ', ' ')
    while prev != text:
        prev = text
        text = text.replace('  ', ' ')
    return text


def extract_keywords(text: str) -> str:
    text = format_text(text)
    words = text.split(' ')
    keywords = {}
    keywords_score = {}
    num = 0
    for w in words:
        if word_frequency(w, 'en') < THRESHOLD:
            if (w not in keywords):
                keywords[w] = num
                keywords_score[w] = word_frequency(w, 'en')
                num += 1
    if (len(keywords) == 0):
        keywords['default'] = 0
    if (len(keywords) <= 3):
        return ' '.join(list(keywords))
    keywords_list = list(keywords)
    keywords_sorted = sorted(keywords_list, key=lambda x: keywords_score[x])
    new_keywords = keywords_sorted[:3]
    for i in range(3, 6):
        if (i >= len(keywords_sorted)):
            break
        if (keywords_score[keywords_sorted[i]] > SECOND_THRESHOLD):
            break
        new_keywords.append(keywords_sorted[i])
    new_keywords.sort(key=lambda x: keywords[x])
    return ' '.join(new_keywords)
```

## 3. LLM prompt

The prompts are following. PROMPT and PROMPT_2 are system prompts, and `f"Question:\n{input['question']}\n\n\nMaterials:\n{input['embedding_result']}\n{input['keyword_result']}"` is user message.

PROMPT is for PubMedQA (1000 questions), which has "maybe" as an answer. PROMPT_2 is for PubMedQA Large (2000 questions) and BioASQ, which only has "yes" and "no" as answers.

```python
PROMPT = '''
Task: answer the following question, using "yes", "no", or "maybe", with the given materials.
You need to first make a draft and analyze the question, and then answer.
Only answer "maybe" if really necessary. In most cases, you should not answer "maybe".

Output format:
A json string, with 2 keys: "draft" and "answer".
The value of "draft" should be a string.
The value of "answer" should be a string, and its value can only be "yes", "maybe", or "no".

Please output the json string directly, without any other explanations.
'''[1:-1]


PROMPT_2 = '''
Task: answer the following question, using "yes", or "no".
You need to first make a draft and analyze the question, and then answer.

Output format:
A json string, with 2 keys: "draft" and "answer".
The value of "draft" should be a string.
The value of "answer" should be a string, and its value can only be "yes", or "no".

Please output the json string directly, without any other explanations.
'''[1:-1]

def process_one_question(input: dict) -> dict:
    result = deepcopy(input)
    user_message = f"Question:\n{input['question']}\n\n\nMaterials:\n{input['embedding_result']}\n{input['keyword_result']}"
    response = LLM_FUNC(PROMPT_2, messages=[{'role': 'user', 'content': user_message}], temperature=0.2, top_p=1.0, max_tokens=2000, json_output=True)[0]
    assert (check_format(response)[0])  # check json format, and answer is one of "yes", "no", "maybe"
    response_json = json.loads(response, strict=False)
    result['llm_answer'] = response_json['answer']
    result['llm_response'] = response
    result['correct'] = (result['llm_answer'] == result['answer'])
    return result
```