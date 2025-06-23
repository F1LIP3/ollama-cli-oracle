# Search engine related utilities
# RUN THIS COMMAND TO INSTALL THE DEPENDENCY BELOW: pip install git+https://github.com/tasos-py/Search-Engines-Scraper
from search_engines import Google, Bing, Yahoo, Duckduckgo, Brave

def search_on_the_web(query, search_engine_name='google'):
    """
    Perform a web search using the specified search engine.

    Args:
        query (str): The search query.
        search_engine_name (str): Name of the search engine ('google', 'bing', etc.).

    Returns:
        str: Concatenated and formatted results from the search, or an error message.
    """
    NUM_OF_PAGES = 2  # Increased number of pages to scrape
    results_list = [] # Store individual formatted results

    # Select the search engine
    if search_engine_name == 'google':
        engine = Google()
    elif search_engine_name == 'bing':
        engine = Bing()
    elif search_engine_name == 'yahoo':
        engine = Yahoo()
    elif search_engine_name == 'duckduckgo':
        engine = Duckduckgo()
    elif search_engine_name == 'brave':
        engine = Brave()
    else: # Default to Google
        print(f"Unsupported search engine: {search_engine_name}. Defaulting to Google.")
        engine = Google()

    try:
        # The search_engines library returns a SearchResponse object.
        # The actual results are typically in an attribute like 'results' or 'links',
        # and each result is a dictionary.
        # Let's assume the structure is response.links and each link is a dict with 'text'.
        # This was based on the original code's structure: `for rs in search: results += "; " + rs['text']`
        # It seems the library's `search()` method directly returns the list of results.
        search_items = engine.search(query=query, pages=NUM_OF_PAGES) # This should be a list of dicts

        if not search_items: # Check if the list of search items is empty
             return f"No results found by {search_engine_name} for the query: '{query}'"

        for i, item in enumerate(search_items):
            if isinstance(item, dict):
                title = item.get('title', 'No title')
                snippet = item.get('text', item.get('snippet', 'No snippet')) # 'text' or 'snippet'
                link = item.get('link', item.get('url', 'No URL')) # 'link' or 'url'

                if snippet and snippet != 'No snippet': # Prioritize items with a snippet
                    formatted_result = f"Source {i+1}:\nTitle: {title}\nURL: {link}\nSnippet: {snippet}\n---"
                    results_list.append(formatted_result)
            # If the structure is different, this part will need adjustment.

        if results_list:
            return "\n\n".join(results_list) # Join formatted results with double newlines
        else:
            # This case means search_items was not empty, but no usable text content could be extracted.
            return f"Search returned results, but no usable text content (title, snippet, link) could be extracted for query: '{query}' with {search_engine_name}."

    except Exception as e:
        print(f"Error during web search with {search_engine_name} for query '{query}': {e}")
        return f"Not able to receive search service: {search_engine_name} results due to an error. Query: '{query}'"

if __name__ == '__main__':
    # Example Usage (for testing)
    test_query = "What is the capital of France?"
    print(f"Searching with Google for: '{test_query}'")
    google_results = search_on_the_web(test_query, 'google')
    print("Google Results:", google_results)

    print(f"\nSearching with DuckDuckGo for: '{test_query}'")
    ddg_results = search_on_the_web(test_query, 'duckduckgo')
    print("DuckDuckGo Results:", ddg_results)

    test_query_no_results = "asdfqwerlkjhzxcv"
    print(f"\nSearching with Google for (no results expected): '{test_query_no_results}'")
    no_results = search_on_the_web(test_query_no_results, 'google')
    print("No Results Test:", no_results)

    # Test unsupported engine
    print(f"\nSearching with NonExistentEngine for: '{test_query}'")
    unsupported_results = search_on_the_web(test_query, 'nonexistentengine')
    print("Unsupported Engine Test:", unsupported_results)
