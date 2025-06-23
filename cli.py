import argparse
from oracle_core.oracle import Oracle

def main():
    parser = argparse.ArgumentParser(description="CLI for Local LLM Oracle")
    parser.add_argument('--model', default='llama3.2', help='The name of the LLM model to use (default: llama3.2)')
    parser.add_argument('--provider', default='ollama', choices=['ollama', 'lm_studio'], help='The LLM provider (default: ollama)')
    parser.add_argument('--search', default=None, help='Activate search oracle. Specify search engine: google, bing, yahoo, duckduckgo, brave (default: None)')

    args = parser.parse_args()

    # Initialize the Oracle
    oracle_instance = Oracle(
        model_name=args.model,
        llm_provider=args.provider,
        search_engine=args.search
    )

    print(f"Oracle CLI initialized. Using model: {args.model} via {args.provider}. Search: {args.search or 'Disabled'}")
    print("Type '/clear' to clear conversation history, or '/quit' to exit.")

    while True:
        try:
            prompt = input(">>> ")
            if prompt.lower() == '/quit':
                print("Exiting Oracle CLI.")
                break
            elif prompt.lower() == '/clear':
                oracle_instance.clear_context()
                # No print here, clear_context in Oracle already prints a message
            else:
                response = oracle_instance.get_response(prompt)
                print(f"<<< {response}")
        except KeyboardInterrupt:
            print("\nExiting Oracle CLI.")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            # Optionally, decide if the app should exit on other errors or try to recover.

if __name__ == "__main__":
    main()
