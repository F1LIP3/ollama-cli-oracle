# Placeholder for LLM provider interaction (Ollama, LM Studio)
# We'll move the 'chat' related functions here.
import requests # Added for making HTTP requests
import json     # Added for parsing JSON responses

# Standard library imports if any, e.g.
# import os

# Third-party library imports, e.g.
# from some_library import SomeClass


def get_available_models(provider: str, host: str = 'localhost') -> list[str]:
    """
    Fetches the list of available models from the specified LLM provider.

    Args:
        provider (str): The LLM provider ('ollama' or 'lm_studio').
        host (str): The hostname or IP address of the provider server.

    Returns:
        list[str]: A list of model names. Returns an empty list if an error occurs
                   or no models are found.
    """
    models = []
    if provider == 'ollama':
        ollama_port = 11434
        url = f"http://{host}:{ollama_port}/api/tags"
        try:
            response = requests.get(url, timeout=5) # Added timeout
            response.raise_for_status()  # Raise an exception for HTTP errors
            data = response.json()
            models = [model['name'] for model in data.get('models', [])]
        except requests.exceptions.RequestException as e:
            print(f"Error fetching models from Ollama: {e}")
            # Optionally, could return a more specific error or raise it
        except json.JSONDecodeError:
            print(f"Error decoding JSON response from Ollama: {response.text}")
        except KeyError:
            print(f"Unexpected JSON structure from Ollama: {data}")

    elif provider == 'lm_studio':
        lm_studio_port = 1234
        url = f"http://{host}:{lm_studio_port}/v1/models"
        try:
            response = requests.get(url, timeout=5) # Added timeout
            response.raise_for_status()
            data = response.json()
            # Standard OpenAI API response has models in a 'data' list, each with an 'id'
            models = [model['id'] for model in data.get('data', []) if 'id' in model]
        except requests.exceptions.RequestException as e:
            print(f"Error fetching models from LM Studio: {e}")
        except json.JSONDecodeError:
            print(f"Error decoding JSON response from LM Studio: {response.text}")
        except KeyError:
            print(f"Unexpected JSON structure from LM Studio: {data}")
    else:
        print(f"Unsupported provider for get_available_models: {provider}")
        # Or raise ValueError(f"Unsupported provider: {provider}")

    return models


def call_llm(messages, model_name, provider='ollama'):
    """
    Calls the specified LLM provider with the given messages.

    Args:
        messages (list): A list of message dictionaries.
        model_name (str): The name of the model to use.
        provider (str): The LLM provider ('ollama' or 'lm_studio').

    Returns:
        str: The LLM's response content.
    """
    if provider == 'ollama':
        # Assuming ollama library is installed and configured
        from ollama import chat
        try:
            response = chat(model=model_name, messages=messages)
            return response['message']['content']
        except Exception as e:
            print(f"Error calling Ollama: {e}")
            return f"Error communicating with Ollama: {e}"
    elif provider == 'lm_studio':
        try:
            from openai import OpenAI
            # LM Studio default server URL
            # The model name in LM Studio is often just 'local-model' or the model file name,
            # but we'll pass the user-provided model_name. The user needs to ensure this model is loaded in LM Studio.
            client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

            completion = client.chat.completions.create(
                model=model_name, # This should be the model identifier LM Studio expects, often the loaded model's name or a placeholder.
                messages=messages,
                temperature=0.7, # Default temperature, can be made configurable
            )
            return completion.choices[0].message.content
        except ImportError:
            print("OpenAI library not found. Please install it with 'pip install openai'")
            return "OpenAI library not found. Please install it to use LM Studio."
        except Exception as e:
            print(f"Error calling LM Studio (OpenAI compatible endpoint): {e}")
            return f"Error communicating with LM Studio: {e}"
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")

def submit_for_evaluation(question, response, model_name, provider='ollama'):
    """
    Submit the question and response to an evaluation model to assess correctness.

    Args:
        question (str): The original question asked by the user.
        response (str): The AI-generated response.
        model_name (str): The name of the evaluation model to use.
        provider (str): The LLM provider for evaluation.

    Returns:
        bool: True if the evaluation result is 'Yes', False otherwise.
    """
    EVALUATION_PROMPT = [
        "Assess if this question pertains to a well-established fact or concept in a particular domain, such as history, science, technology, or culture: ",
        "If yes, evaluate whether the answer at the end provides a clear and concise explanation of the concept, avoiding ambiguity or oversimplification. Consider the following criteria: relevance, accuracy, timeliness, and potential biases. Provide a clear '[Evaluation] - Yes' or '[Evaluation] - No' assessment of the answer accuracy to that question. This was the answer: "
    ]

    evaluation_messages = []
    evaluation_prompt = EVALUATION_PROMPT[0] + question + EVALUATION_PROMPT[1] + response
    evaluation_messages.append({'role': 'user', 'content': evaluation_prompt})

    evaluation_result_content = call_llm(evaluation_messages, model_name, provider)

    return "[Evaluation] - Yes" in evaluation_result_content

def refactor_search_input(user_input, model_name, provider='ollama'):
    """
    Refactor the user input to optimize it for search engines.

    Args:
        user_input (str): The original search query.
        model_name (str): The model to use for refactoring.
        provider (str): The LLM provider.

    Returns:
        str: The refactored search query.
    """
    SEARCH_ENGINE_OPTIMIZATION_PROMPT = "Optimize the following information request to be the most effective to retrieve the needed information when submitted to google search, your output should be only the optimized query, do not add anything else, because this will be used as input for a search query: "

    refactor_messages = []
    refactor_prompt = SEARCH_ENGINE_OPTIMIZATION_PROMPT + user_input
    refactor_messages.append({'role': 'user', 'content': refactor_prompt})

    refactored_query = call_llm(refactor_messages, model_name, provider)
    return refactored_query

def process_search_result_with_llm(search_result, information_needed, model_name, provider='ollama'):
    """
    Process the search results to answer a specific query using an LLM.

    Args:
        search_result (str): The concatenated search results.
        information_needed (str): The user's query that needs answering.
        model_name (str): The model to use for processing.
        provider (str): The LLM provider.

    Returns:
        str: The processed result.
    """
    PROCESS_SEARCH_RESULT_PROMPT = [
        "Based on this information: ",
        ", answer the following query: "
    ]

    process_messages = []
    process_prompt = PROCESS_SEARCH_RESULT_PROMPT[0] + search_result + PROCESS_SEARCH_RESULT_PROMPT[1] + information_needed
    process_messages.append({'role': 'user', 'content': process_prompt})

    processed_answer = call_llm(process_messages, model_name, provider)
    return processed_answer

def summarize_search_results(search_results_text, query, model_name, provider='ollama', max_length=1500):
    """
    Uses an LLM to summarize extensive search results based on the original query.
    Args:
        search_results_text (str): The concatenated text from search results.
        query (str): The original user query to focus the summary.
        model_name (str): The model to use for summarization.
        provider (str): The LLM provider.
        max_length (int): Approximate maximum length for the input to the summarizer LLM to avoid overly long prompts.
    Returns:
        str: Summarized and relevant information from the search results.
    """
    # Truncate search_results_text if it's too long to prevent excessive token usage
    if len(search_results_text) > max_length:
        search_results_text = search_results_text[:max_length] + "..."

    SUMMARIZATION_PROMPT = (
        f"Based on the following search results, extract and synthesize the information "
        f"that is most relevant to answering the query: '{query}'. "
        f"Provide a concise summary of the key findings. Avoid making up information not present in the text. "
        f"Search results snippet:\n\n{search_results_text}"
    )

    summarize_messages = [{'role': 'user', 'content': SUMMARIZATION_PROMPT}]

    try:
        summary = call_llm(summarize_messages, model_name, provider)
        return summary
    except Exception as e:
        print(f"Error during search result summarization: {e}")
        # Fallback to using a snippet of the original results if summarization fails
        return search_results_text[:500] + "..." if len(search_results_text) > 500 else search_results_text
