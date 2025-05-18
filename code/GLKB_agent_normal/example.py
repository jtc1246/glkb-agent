from ai_assistant import chat_one_round

if __name__ == '__main__':
    question = 'What is gene TP53?'
    result = chat_one_round([], question)
    histiory, answer = result
    print(answer)
    print()
    print(histiory)

    new_result = chat_one_round(histiory, 'what\'s the function of it?')
    print(new_result[1])
