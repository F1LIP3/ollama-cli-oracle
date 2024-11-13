import argparse
from ollama import chat
# RUN THIS COMMAND TO INSTALL THE DEPENDENCY BELOW: pip install git+https://github.com/tasos-py/Search-Engines-Scraper
from search_engines import Google, Bing, Yahoo, Duckduckgo, Brave

def get_prompt():
    """
    Get user input as a prompt.

    Returns:
        str: The user's input.
    """
    return input(">>> ")

def submit_for_evaluation(question, response):
    """
    Submit the question and response to an evaluation model to assess correctness.

    Args:
        question (str): The original question asked by the user.
        response (str): The AI-generated response.

    Returns:
        bool: True if the evaluation result is 'Yes', False otherwise.
    """
    EVALUATION_PROMPT = [
    "Assess if this question pertains to a well-established fact or concept in a particular domain, such as history, science, technology, or culture: ",
    "If yes, evaluate whether the answer at the end provides a clear and concise explanation of the concept, avoiding ambiguity or oversimplification. Consider the following criteria: relevance, accuracy, timeliness, and potential biases. Provide a clear '[Evaluation] - Yes' or '[Evaluation] - No' assessment of the answer accuracy to that question. This was the answer: "
    ]

    evaluation = []
    evaluation_prompt = EVALUATION_PROMPT[0] + question + EVALUATION_PROMPT[1] + response
    evaluation.append({'role': 'user', 'content': evaluation_prompt})
    evaluation_result = chat(model=args.model, messages=evaluation)

    if "[Evaluation] - Yes" in evaluation_result['message']['content']:
        return True
    else:
        return False

def refactor_search_input(input):
    """
    Refactor the user input to optimize it for search engines.

    Args:
        input (str): The original search query.

    Returns:
        str: The refactored search query.
    """
    SEARCH_ENGINE_OPTIMIZATION_PROMPT = "Optimize the following information request to be the most effective to retrieve the needed information when submitted to google search, your output should be only the optimized query, do not add anything else, because this will be used as input for a search query: "

    refactored_search_input = []
    refactored_search_prompt = SEARCH_ENGINE_OPTIMIZATION_PROMPT + input
    refactored_search_input.append({'role': 'user', 'content': refactored_search_prompt})
    refactored_search_result = chat(model=args.model, messages=refactored_search_input)

    return refactored_search_result['message']['content']

def search_on_the_web(query):
    """
    Perform a web search using the specified search engine.

    Args:
        query (str): The search query.

    Returns:
        str: Concatenated results from the search.
    """
    NUM_OF_PAGES = 1
    results = ""

    match args.search:
        case 'google':
            engine = Google()
        case 'bing':
            engine = Bing()
        case 'yahoo':
            engine = Yahoo()
        case 'duckduckgo':
            engine = Duckduckgo()
        case 'brave':
            engine = Brave()
        case _:
            engine = Google()

    search = engine.search(query=query, pages=NUM_OF_PAGES)

    for rs in search:
        results += "; " + rs['text']

    if results:
        return results
    else:
        print('Not able to receive search service: ' 
              + args.search + 
              ' results.')
        return('Not able to receive search service: ' 
               + args.search + 
               ' results.')

def process_search_result(search_result, information_needed):
    """
    Process the search results to answer a specific query.

    Args:
        search_result (str): The concatenated search results.
        information_needed (str): The user's query that needs answering.

    Returns:
        str: The processed result.
    """
    PROCESS_SEARCH_RESULT_PROMPT = [
        "Based on this information: ",
        ", answer the following query: "
    ]

    processed_search_result = []
    processed_search_result_prompt = PROCESS_SEARCH_RESULT_PROMPT[0] + search_result + PROCESS_SEARCH_RESULT_PROMPT[1] + information_needed
    processed_search_result.append({'role': 'user', 'content': processed_search_result_prompt})

    result_processed_search = chat(model=args.model, messages=processed_search_result)

    return result_processed_search['message']['content']

def search_the_internet(information_needed):
    """
    Orchestrates the process of refactoring input, searching on the web, and processing results.

    Args:
        information_needed (str): The user's query that needs answering.

    Returns:
        str: The final processed result.
    """
    refactored_search_input = refactor_search_input(information_needed)
    search_result = search_on_the_web(refactored_search_input)
    result = process_search_result(search_result, information_needed)

    return result

def main():
    messages = []
    while True:
        prompt = get_prompt()
        if '/clear' == prompt:
            messages.clear()
        else:
            messages.append({'role': 'user', 'content': prompt})

            response = chat(model=args.model, messages=messages)

            if args.search:
                if submit_for_evaluation(prompt, response['message']['content']):
                    print(response['message']['content'])
                    messages.append({'role': 'assistant', 'content': response['message']['content']})
                else:
                    answer = search_the_internet(prompt)
                    print(answer)
                    messages.append({'role': 'assistant', 'content': answer})
            else:
                print(response['message']['content'])
                messages.append({'role': 'assistant', 'content': response['message']['content']})

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', default='llama3.2', help='The name of the model to use (default: llama3.2)')
    parser.add_argument('--search', default=None, help='Activate if you want to have an oracle to search the internet for information . (default: None), google, bing, yahoo, duckduckgo, brave, etc')
    args = parser.parse_args()
    main()