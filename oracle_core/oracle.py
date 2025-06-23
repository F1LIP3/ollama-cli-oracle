# Main Oracle class that orchestrates LLM calls and web searches
import logging
from .llm_providers import call_llm, submit_for_evaluation, refactor_search_input, process_search_result_with_llm, summarize_search_results
from .search_utils import search_on_the_web

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
logger = logging.getLogger(__name__)

class Oracle:
    def __init__(self, model_name='llama3.2', llm_provider='ollama', search_engine=None):
        self.model_name = model_name
        self.llm_provider = llm_provider
        self.search_engine = search_engine # e.g., 'google', 'bing'
        self.messages = [] # Stores the conversation history

    def get_response(self, user_prompt):
        """
        Gets a response from the LLM, potentially using web search if configured.
        """
        self.messages.append({'role': 'user', 'content': user_prompt})

        llm_response_content = call_llm(self.messages, self.model_name, self.llm_provider)

        if self.search_engine:
            # Evaluate if the LLM's direct response is sufficient
            is_sufficient = submit_for_evaluation(
                question=user_prompt,
                response=llm_response_content,
                model_name=self.model_name, # Or a specific model for evaluation
                provider=self.llm_provider
            )

            if is_sufficient:
                logger.info("Initial LLM response deemed sufficient by evaluation.")
                final_answer = llm_response_content
            else:
                logger.info(f"LLM response deemed insufficient or needs fact-checking. Proceeding with web search via {self.search_engine}.")

                # Refactor input for search
                optimized_query = refactor_search_input(user_prompt, self.model_name, self.llm_provider)
                logger.info(f"Optimized search query: {optimized_query}")

                # Perform web search
                raw_search_results = search_on_the_web(optimized_query, self.search_engine)

                # Check for search errors or no results
                if "Not able to receive search service" in raw_search_results or \
                   "No results found" in raw_search_results or \
                   "no text content could be extracted" in raw_search_results:
                    logger.warning(f"Web search failed or returned no usable results: {raw_search_results}. Falling back to direct LLM response.")
                    final_answer = llm_response_content # Fallback to direct LLM response
                else:
                    logger.info(f"Raw search results received (first 500 chars): {raw_search_results[:500]}")
                    # Summarize search results
                    summarized_results = summarize_search_results(
                        raw_search_results,
                        user_prompt, # Use original user_prompt for relevance in summarization
                        self.model_name,
                        self.llm_provider
                    )
                    logger.info(f"Summarized search results: {summarized_results}")

                    # Process summarized search results with LLM to get the final answer
                    final_answer = process_search_result_with_llm(
                        search_result=summarized_results,
                        information_needed=user_prompt,
                        model_name=self.model_name,
                        provider=self.llm_provider
                    )
        else:
            logger.info("Search not enabled. Using direct LLM response.")
            final_answer = llm_response_content

        self.messages.append({'role': 'assistant', 'content': final_answer})
        return final_answer

    def clear_context(self):
        self.messages = []
        print("Conversation context cleared.")

if __name__ == '__main__':
    # Basic test (requires Ollama running with llama3.2 or specified model)
    # To run this test: python -m oracle_core.oracle (from the project root)

    # Test without search
    print("--- Testing Oracle without search ---")
    oracle_no_search = Oracle(model_name='llama3.2') # Ensure this model is available in Ollama
    prompt1 = "What is the capital of France?"
    print(f">>> User: {prompt1}")
    response1 = oracle_no_search.get_response(prompt1)
    print(f"<<< Oracle: {response1}")

    prompt2 = "Tell me a fun fact about it."
    print(f"\n>>> User: {prompt2}")
    response2 = oracle_no_search.get_response(prompt2)
    print(f"<<< Oracle: {response2}")

    oracle_no_search.clear_context()
    prompt3 = "What was the first question I asked?"
    print(f"\n>>> User: {prompt3} (after clearing context)")
    response3 = oracle_no_search.get_response(prompt3)
    print(f"<<< Oracle: {response3}")

    # Test with search (will require search_engines to work and network access)
    # The evaluation LLM call might decide to search or not.
    # Forcing a search scenario is tricky without mocking the evaluation.
    # We assume the evaluation will often lead to search for specific factual queries.
    print("\n--- Testing Oracle with Google search ---")
    # Make sure ollama is running and the model is available.
    # Also, ensure the search_engines library is installed and working.
    try:
        oracle_with_search = Oracle(model_name='llama3.2', search_engine='google')
        search_prompt = "What is the current weather in London?" # A query likely to trigger search
        print(f">>> User: {search_prompt}")
        search_response = oracle_with_search.get_response(search_prompt)
        print(f"<<< Oracle: {search_response}")

        search_prompt_2 = "How many people live in Tokyo according to the latest estimates?"
        print(f"\n>>> User: {search_prompt_2}")
        search_response_2 = oracle_with_search.get_response(search_prompt_2)
        print(f"<<< Oracle: {search_response_2}")

    except ImportError:
        print("\nSkipping search test: ollama or search_engines library not found or not configured.")
    except Exception as e:
        print(f"\nError during search test: {e}")

    print("\n--- Testing Oracle with DuckDuckGo search for a specific factual question ---")
    try:
        oracle_ddg = Oracle(model_name='llama3.2', search_engine='duckduckgo')
        ddg_prompt = "Who won the Nobel Prize in Physics in 2023?"
        print(f">>> User: {ddg_prompt}")
        ddg_response = oracle_ddg.get_response(ddg_prompt)
        print(f"<<< Oracle: {ddg_response}")
    except Exception as e:
        print(f"\nError during DuckDuckGo search test: {e}")
