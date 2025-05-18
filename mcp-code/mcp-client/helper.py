import asyncio
import json
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

y_pred = []

with open("test_output.txt", "r") as file:
    lines = file.readlines()
    for i in range(1, len(lines)):
        if lines[i].strip() == "########################":
            answer = lines[i - 1].strip().lower()
            if answer == "yes":
                y_pred.append("A")
            elif answer == "no":
                y_pred.append("B")
                
y_true = []

with open("bioasq_618.json", "r") as f:
        test_cases = json.load(f)
        
for case in test_cases:
    correct = case["answer"]
    y_true.append(correct)

pos_label = "A"
print("\n--- Evaluation Metrics ---")
print(f"Accuracy:  {accuracy_score(y_true, y_pred):.6f}")
print(f"Precision: {precision_score(y_true, y_pred, pos_label=pos_label):.6f}")
print(f"Recall:    {recall_score(y_true, y_pred, pos_label=pos_label):.6f}")
print(f"F1 Score:  {f1_score(y_true, y_pred, pos_label=pos_label):.6f}")
print("--------------------------\n")