from config import OPENAI_API_KEY
from .test_prompt import test_questions, generate_my_prompt, get_answers_for_my_prompt, run_cypher

__all__ = ['generate_cypher_query', 'run_cypher']

my_prompt = generate_my_prompt(test_questions)

def generate_cypher_query(question: str):
    cypher = get_answers_for_my_prompt(my_prompt, [{'q': question}])[0]
    return cypher

