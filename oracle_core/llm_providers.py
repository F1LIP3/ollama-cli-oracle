# Placeholder for LLM provider interaction (Ollama, LM Studio)
# We'll move the 'chat' related functions here.
import requests # Added for making HTTP requests
import json     # Added for parsing JSON responses
import re       # Added for regular expression operations

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
        str: The LLM's response content, with <think> tags removed.
    """
    raw_response_content = ""
    if provider == 'ollama':
        # Assuming ollama library is installed and configured
        from ollama import chat
        try:
            response = chat(model=model_name, messages=messages)
            raw_response_content = response['message']['content']
        except Exception as e:
            print(f"Error calling Ollama: {e}")
            raw_response_content = f"Error communicating with Ollama: {e}"
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
            raw_response_content = completion.choices[0].message.content
        except ImportError:
            print("OpenAI library not found. Please install it with 'pip install openai'")
            raw_response_content = "OpenAI library not found. Please install it to use LM Studio."
        except Exception as e:
            print(f"Error calling LM Studio (OpenAI compatible endpoint): {e}")
            raw_response_content = f"Error communicating with LM Studio: {e}" # Ensure this path also sets raw_response_content
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")

    # Filter out <think>...</think> tags
    if isinstance(raw_response_content, str):
        cleaned_response_content = re.sub(r"<think>.*?</think>", "", raw_response_content, flags=re.DOTALL).strip()
        # Also remove any leading/trailing whitespace that might be left after tag removal or was part of original response.
        return cleaned_response_content
    else:
        # Should not happen if providers return strings or string error messages
        return str(raw_response_content)


def submit_for_evaluation(question, response, model_name, provider='ollama'):
    """
    Submit the question and response to an evaluation model to assess correctness.

    Args:
        question (str): The original question asked by the user.
        response (str): The AI-generated response.
        model_name (str): The name of the evaluation model to use.
        provider (str): The LLM provider for evaluation.

    Returns:
        bool: True if the evaluation result is deemed 'Yes', False otherwise.
    """
    # New, more direct prompt focusing on answer quality
    EVALUATION_PROMPT_TEMPLATE = """\
You are an AI assistant tasked with evaluating the quality of an answer provided to a given question.

Question:
{question}

Answer:
{response}

Based on the Question and Answer:
1. Is the Answer accurate and factually correct based on general knowledge?
2. Is the Answer relevant to the Question and does it directly address what was asked?
3. Is the Answer clear, concise, and easy to understand?
4. Does the Answer avoid significant ambiguity or oversimplification for the likely context of the question?

Considering these criteria, especially accuracy and relevance, provide your assessment.
Conclude your response with either "[Yes]" if the answer is satisfactory, or "[No]" if it is not, on a new line by itself.
Example:
The answer seems mostly correct but misses a key detail.
[No]

Another Example:
The answer is clear, accurate, and directly addresses the question.
[Yes]
"""
    # import re # Import regular expressions -> Moved to top of file

    evaluation_prompt = EVALUATION_PROMPT_TEMPLATE.format(question=question, response=response)
    evaluation_messages = [{'role': 'user', 'content': evaluation_prompt}]

    evaluation_result_content = call_llm(evaluation_messages, model_name, provider)

    # More robust parsing:
    # Look for [Yes] or [No] at the end of the string, case-insensitive, allowing for optional whitespace.
    match = re.search(r"\[(Yes|No)\]\s*$", evaluation_result_content.strip(), re.IGNORECASE)

    if match:
        return match.group(1).lower() == 'yes'
    else:
        # Fallback or logging if the expected pattern isn't found
        print(f"Warning: Evaluation output did not contain a clear [Yes] or [No] at the end. Output: '{evaluation_result_content}'")
        # Defaulting to False if no clear Yes/No is found, to be conservative.
        return False

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
    NEW_SEARCH_ENGINE_OPTIMIZATION_PROMPT_TEMPLATE = """\
You are an expert at crafting effective search engine queries.
User's information request: "{user_input}"

1. Identify the key entities, concepts, and intent in the user's request.
2. Formulate a single, concise, and highly effective search query that is likely to yield the most relevant results for this request.
3. Output *only* the optimized search query itself, without any preamble, labels, or explanation.

Optimized Search Query:""" # The LLM should complete this line

    refactor_prompt = NEW_SEARCH_ENGINE_OPTIMIZATION_PROMPT_TEMPLATE.format(user_input=user_input)
    refactor_messages = [{'role': 'user', 'content': refactor_prompt}]

    refactored_query = call_llm(refactor_messages, model_name, provider)
    # Ensure only the query is returned, strip potential newlines or leading "Optimized Search Query:" if LLM adds it.
    # A more robust way would be to parse if LLM doesn't strictly follow "only the query".
    # For now, simple stripping.
    if "Optimized Search Query:" in refactored_query:
        refactored_query = refactored_query.split("Optimized Search Query:")[-1]
    return refactored_query.strip()

def process_search_result_with_llm(search_result, information_needed, model_name, provider='ollama'):
    """
    Process the search results to answer a specific query using an LLM.

    Args:
        search_result (str): The concatenated search results.
        information_needed (str): The user's query that needs answering.
        model_name (str): The model to use for processing.
        provider (str): The LLM provider.

    Returns:
        str: The processed result (final answer to the query).
    """
    # Updated prompt for processing the summarized search results
    PROCESS_SEARCH_RESULT_PROMPT_TEMPLATE = """\
You have been provided with a summary of information gathered from web search results. Your task is to use this summary to directly answer the user's original query.

User's Original Query: "{information_needed}"

Summary of Web Search Results:
{search_result_summary}

Based *only* on the provided "Summary of Web Search Results", formulate a clear, concise, and direct answer to the "User's Original Query".
Do not add any information that is not present in the summary.
If the summary does not contain enough information to answer the query, explicitly state that the summary does not provide a sufficient answer.
Your final output should be just the answer to the query.
"""

    process_prompt = PROCESS_SEARCH_RESULT_PROMPT_TEMPLATE.format(
        information_needed=information_needed,
        search_result_summary=search_result # Renamed variable for clarity in prompt
    )
    process_messages = [{'role': 'user', 'content': process_prompt}]

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
        # Simple truncation for now. A more sophisticated approach might summarize chunks.
        search_results_text = search_results_text[:max_length] + "\n... [Results Truncated] ..."

    # Updated prompt to acknowledge the structure of search_results_text
    SUMMARIZATION_PROMPT_TEMPLATE = """\
You are provided with a series of search result snippets, each potentially containing a title, URL, and snippet text, formatted like:
Source [Number]:
Title: [Title of the page]
URL: [URL of the page]
Snippet: [Text snippet from the page]
---

Original User Query: "{query}"

Review all the provided search result snippets. Extract and synthesize the information that is most relevant to answering the Original User Query.
Provide a concise, consolidated summary of the key findings. Focus on information that directly addresses the query.
Avoid making up information not present in the text. If multiple sources provide similar information, synthesize it.
If sources provide conflicting information, you may note that.
Your summary should be a coherent text, not just a list of facts.
"""
    # We add the actual search results below this instruction block.
    full_summarization_prompt = SUMMARIZATION_PROMPT_TEMPLATE.format(query=query) + \
                                f"\n\nSearch Results to Summarize:\n{search_results_text}"

    summarize_messages = [{'role': 'user', 'content': full_summarization_prompt}]

    try:
        summary = call_llm(summarize_messages, model_name, provider)
        return summary
    except Exception as e:
        print(f"Error during search result summarization: {e}")
        # Fallback to using a snippet of the original results if summarization fails
        return search_results_text[:500] + "..." if len(search_results_text) > 500 else search_results_text
