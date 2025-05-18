import asyncio
import json
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import argparse

from client import MCPClient
async def ask_client(question: str, client: MCPClient, server_type: str) -> str:
    """Ask the LLM a question and interpret answer as 'A' or 'B'."""
    if server_type == "search":
        server_type = "websearch"
    system_instruction = f"""
        - ensure your response only has the characters "yes", "no", or "maybe". Do not include explanation or justification. Do not reflect on {server_type} tool's results
        - Only answer "maybe" if really necessary. In most cases, you should not answer "maybe".\nONLY ANSWER "maybe" if you are really unsure about the question. IF YOU HAVE ANY TENDENCY to "yes" or "no", please answer "yes" or "no", not "maybe".
        - you must call {server_type} tool first.
        - you may only call the {server_type} function one single time. 
        - if {server_type} does not give a satisfactory information, or if there is no relevant article, answer the question without the {server_type} function
        - Your query to {server_type} should only be maximum 2 or 3 terms
    """
    
    print(f"Question: {question}")
    response = await client.process_query(question, system_instruction)
    print(f"Response: {response}")

    response_lower = response.strip().lower()
    if "yes" in response_lower[-7:]:
        print("Yes")
        print("########################")
        return "yes"
    elif "no" in response_lower[-7:]:
        print("No")
        print("########################")
        return "no"
    elif "maybe" in response_lower[-7:]:
        print("Maybe")
        print("########################")
        return "maybe"
    else:
        print(f"Unexpected response!")
        print("########################")
        return "unknown"

async def run_test_suite(client: MCPClient, test_suite_path="pubmedqa.json", server_type = "wikipedia"):
    with open(test_suite_path, "r") as f:
        test_cases = json.load(f)

    y_true = []
    y_pred = []

    for case_id, case in test_cases.items():
        question = case["QUESTION"]
        correct = case["reasoning_required_pred"]
        predicted = await ask_client(question, client, server_type)

        if predicted != "unknown":
            y_true.append(correct)
            y_pred.append(predicted)

    print("\n--- Evaluation Metrics (Multiclass) ---")
    print(f"Accuracy:  {accuracy_score(y_true, y_pred):.6f}")
    print(f"Precision (macro): {precision_score(y_true, y_pred, average='macro'):.6f}")
    print(f"Recall (macro):    {recall_score(y_true, y_pred, average='macro'):.6f}")
    print(f"F1 Score (macro):  {f1_score(y_true, y_pred, average='macro'):.6f}")

async def main(server_type: str):
    client = MCPClient()
    await client.connect_to_server(f"../{server_type}-server/{server_type}-server.py")
    await run_test_suite(client, server_type=server_type)
    await client.cleanup()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run MCP test suite for a specified server.")
    parser.add_argument("server_type", choices=["search", "arxiv", "wikipedia", "pubmed"], help="The server type to test (e.g. 'wikipedia', 'pubmed').")
    args = parser.parse_args()

    asyncio.run(main(args.server_type))
