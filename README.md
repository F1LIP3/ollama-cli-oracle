# Local LLM Oracle with Web UI & Search

This project provides a flexible Local LLM Oracle that can connect to different LLM providers (Ollama, LM Studio) and optionally use web search engines to gather real-time information for its responses. It offers both a command-line interface (CLI) and a web-based UI (using Streamlit).

## Features

- **Multiple LLM Providers:**
    - **Ollama:** Connects to a running Ollama instance.
    - **LM Studio:** Connects to an LM Studio local server (OpenAI-compatible endpoint).
- **Web Search Integration:**
    - Can use search engines (Google, Bing, Yahoo, DuckDuckGo, Brave) to fetch information if the LLM's initial response is deemed insufficient or requires fact-checking.
    - Search results are summarized by an LLM before being used to generate the final answer.
- **Interfaces:**
    - **CLI:** For command-line interaction.
    - **Web UI:** A user-friendly interface built with Streamlit, allowing configuration and chat.
- **Configurable:** Model name, LLM provider, and search engine can be easily configured.
- **Conversation History:** Maintains context within a session.

## Project Structure

```
.
├── oracle_core/        # Core logic for the oracle
│   ├── __init__.py
│   ├── llm_providers.py  # Handles interaction with Ollama, LM Studio
│   ├── oracle.py         # Main Oracle class, orchestrates logic
│   └── search_utils.py   # Utilities for web searching
├── cli.py              # Command-Line Interface
├── web_ui.py           # Streamlit Web User Interface
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## Setup

1.  **Clone the repository (if you haven't already):**
    ```bash
    git clone <repository-url>
    cd <repository-name>
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    This will install `ollama`, `search_engines` (custom fork), `openai` (for LM Studio), and `streamlit`.

4.  **Ensure your chosen LLM provider is running:**
    *   **Ollama:** Make sure your Ollama application is running and you have pulled the desired models (e.g., `ollama pull llama3.2`).
    *   **LM Studio:** Start LM Studio, load your desired model, and start the local server (usually from the "Local Server" tab). The server typically runs at `http://localhost:1234/v1`.

## Usage

### Web UI (Recommended)

The web UI provides an easy way to interact with the oracle and configure its settings.

1.  **Start the Streamlit app:**
    ```bash
    streamlit run web_ui.py
    ```
2.  Open your browser and navigate to the URL provided by Streamlit (usually `http://localhost:8501`).
3.  Use the sidebar to:
    *   Set the **Model Name** (e.g., `llama3.2` for Ollama; for LM Studio, this should match the model identifier expected by its server, often the loaded model's name like `NousResearch/Hermes-2-Pro-Mistral-7B-GGUF` or a generic `local-model`).
    *   Choose the **LLM Provider** (Ollama or LM Studio).
    *   Select a **Search Engine** or disable search.
    *   Click "Apply Configuration".
4.  Chat with the oracle!

![image](https://github.com/user-attachments/assets/09423e76-2797-44fa-a8e6-c2ff025f3e25)
*(Note: The original image shows the old CLI. A new UI screenshot would be beneficial here.)*

### Command-Line Interface (CLI)

1.  **Run `cli.py` with desired arguments:**
    ```bash
    python cli.py --model <model_name> --provider <ollama|lm_studio> --search <search_engine_name>
    ```
    **Arguments:**
    *   `--model MODEL`: Name of the LLM model to use (default: `llama3.2`).
        *   For Ollama, this is the model tag (e.g., `llama3.2`, `mistral`).
        *   For LM Studio, this is the identifier your LM Studio server expects for the loaded model (e.g., `local-model`, or the model's full name if your server is set up that way).
    *   `--provider PROVIDER`: LLM provider to use (`ollama` or `lm_studio`, default: `ollama`).
    *   `--search SEARCH_ENGINE`: Optional. Activate search oracle. Specify search engine: `google`, `bing`, `yahoo`, `duckduckgo`, `brave`. If not provided, search is disabled.

    **Example (Ollama with Google search):**
    ```bash
    python cli.py --model llama3.2 --provider ollama --search google
    ```
    **Example (LM Studio, assuming model 'local-model' is loaded, no search):**
    ```bash
    python cli.py --model local-model --provider lm_studio
    ```

2.  Type your prompts and press Enter.
3.  Type `/clear` to clear conversation history.
4.  Type `/quit` to exit.

## How it Works

1.  The user submits a prompt through the CLI or Web UI.
2.  The `Oracle` class receives the prompt.
3.  It first gets a direct response from the configured LLM (Ollama or LM Studio).
4.  If search is enabled, an evaluation LLM call assesses if the direct response is factually sufficient or if it might benefit from web information.
5.  If web information is needed:
    *   The original prompt is refactored by an LLM to create an optimized search query.
    *   The `search_utils` module performs a web search using the chosen engine.
    *   The search results are summarized by an LLM to extract the most relevant information.
    *   This summarized information, along with the original prompt, is given to the LLM to generate a final, context-aware answer.
6.  If search is disabled or the initial response is deemed sufficient, the direct LLM response is used.
7.  The answer is returned to the user.

## Logging

The application uses Python's `logging` module. Log messages (INFO level and above) related to the oracle's operations (e.g., decisions to search, queries, summarized results) are printed to the console.

## Thanks To

-   **Tasos M Adamopoulos** for the original `Search-Engines-Scraper` library.
-   The **Ollama team** for their excellent local LLM software.
-   The **LM Studio team** for their versatile LLM management tool.
-   The **Streamlit team** for making web app creation straightforward.
