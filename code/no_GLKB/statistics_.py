import sklearn
import json

path = './outputs/pubmedqa_large_gpt_4o_1747573066.9261131.json'  # MODIFY HERE
data = json.loads(open(path).read())

def calculate_statistics(data: list):
    ground_truth = []
    llm_answer = []
    correct_num = 0
    for d in data:
        ground_truth.append(d['answer'])
        llm_answer.append(d['llm_answer'])
        correct_num += int(d['correct'])
    print(f'Correct num: {correct_num} / {len(data)}')
    print(f'' + str(sklearn.metrics.precision_score(ground_truth, llm_answer, average='macro')))
    # print(f'Precision weighted: ' + str(sklearn.metrics.precision_score(ground_truth, llm_answer, average='weighted')))
    print(f'' + str(sklearn.metrics.recall_score(ground_truth, llm_answer, average='macro')))
    # print(f'Recall weighted: ' + str(sklearn.metrics.recall_score(ground_truth, llm_answer, average='weighted')))
    print(f'' + str(sklearn.metrics.f1_score(ground_truth, llm_answer, average='macro')))
    # print(f'F1 weighted: ' + str(sklearn.metrics.f1_score(ground_truth, llm_answer, average='weighted')))


if __name__ == '__main__':
    calculate_statistics(data) # type: ignore