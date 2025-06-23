import streamlit as st
from oracle_core.oracle import Oracle
from oracle_core.llm_providers import get_available_models # Import the new function

# Page configuration (optional, but good practice)
st.set_page_config(page_title="LLM Oracle", layout="wide")

st.title("Local LLM Oracle Interface")

# --- Utility Functions ---
def update_models_list(provider_key):
    """Fetches and updates the list of available models for the given provider."""
    provider = st.session_state[provider_key]
    if not provider:
        st.session_state.available_models = []
        st.session_state.current_model_name = None
        st.warning("Please select an LLM provider.")
        if 'update_models_list_rerun_guard' not in st.session_state or not st.session_state.update_models_list_rerun_guard:
            st.session_state.update_models_list_rerun_guard = True
            st.rerun()
        else:
            st.session_state.update_models_list_rerun_guard = False # Reset guard
        return

    with st.spinner(f"Fetching models from {provider}..."):
        models = get_available_models(provider)
        if models:
            st.session_state.available_models = models
            if st.session_state.get('current_model_name') not in models:
                st.session_state.current_model_name = models[0]
            # st.success(f"Found {len(models)} models for {provider}.") # Can be too verbose with reruns
        else:
            st.session_state.available_models = []
            st.session_state.current_model_name = None
            st.warning(f"No models found or error fetching from {provider}. Ensure the server is running and models are available.")

    # Guard against multiple reruns if called in quick succession or during widget change handling
    if 'update_models_list_rerun_guard' not in st.session_state or not st.session_state.update_models_list_rerun_guard:
        st.session_state.update_models_list_rerun_guard = True
        st.rerun()
    else:
        st.session_state.update_models_list_rerun_guard = False # Reset guard

# Initialize Oracle instance and other session state variables if they don't exist
if 'oracle_instance' not in st.session_state:
    default_provider = 'ollama'
    default_model = 'llama3.2' # Placeholder, will be updated if possible
    st.session_state.oracle_instance = Oracle(model_name=default_model, llm_provider=default_provider, search_engine=None)
    st.session_state.chat_history = []
    st.session_state.current_llm_provider = default_provider
    st.session_state.current_model_name = default_model # Try to keep this, will be validated against fetched list
    st.session_state.available_models = []
    st.session_state.initial_model_fetch_done = False


# --- Sidebar for Configuration ---
with st.sidebar:
    st.header("Configuration")

    # LLM Provider Selection
    # The on_change callback will handle the model list update.
    st.selectbox(
        "LLM Provider",
        options=['ollama', 'lm_studio'],
        key='current_llm_provider', # This key directly updates st.session_state.current_llm_provider
        on_change=update_models_list,
        args=('current_llm_provider',) # Pass the key of the selectbox itself to the callback
    )

    if st.button("Refresh Model List", key="refresh_models_button"):
        update_models_list('current_llm_provider') # Use the state key

    # Attempt initial model fetch after the first render if not done
    if not st.session_state.initial_model_fetch_done and st.session_state.current_llm_provider:
        update_models_list('current_llm_provider')
        st.session_state.initial_model_fetch_done = True


    # Model Selection
    if not st.session_state.available_models and st.session_state.current_llm_provider:
        st.info(f"No models loaded for {st.session_state.current_llm_provider}. Click 'Refresh Model List' or ensure models are available on the server.")
    elif not st.session_state.current_llm_provider:
        st.info("Select an LLM provider to see available models.")


    # Ensure current_model_name is valid, select first if not or if list changed
    if st.session_state.available_models:
        if st.session_state.current_model_name not in st.session_state.available_models:
            st.session_state.current_model_name = st.session_state.available_models[0]
        current_model_idx = st.session_state.available_models.index(st.session_state.current_model_name)
    else:
        current_model_idx = 0 # Default index if no models

    st.selectbox(
        "Model Name",
        options=st.session_state.available_models,
        index=current_model_idx,
        key='current_model_name', # This key directly updates st.session_state.current_model_name
        disabled=not st.session_state.available_models,
        help="Select a model. Refresh list if empty or models have changed."
    )

    search_engine_options = [None, 'google', 'bing', 'yahoo', 'duckduckgo', 'brave']
    # Ensure oracle_instance exists before accessing its attributes
    current_search_engine = st.session_state.oracle_instance.search_engine if hasattr(st.session_state.oracle_instance, 'search_engine') else None
    search_engine_index = search_engine_options.index(current_search_engine) if current_search_engine in search_engine_options else 0

    selected_search_engine = st.selectbox(
        "Search Engine (Optional)",
        options=search_engine_options,
        index=search_engine_index,
        format_func=lambda x: x if x else "Disabled",
        key='current_search_engine'
    )

    if st.button("Apply Configuration"):
        if not st.session_state.current_model_name:
            st.error("Please select a model first, or refresh the model list.")
        else:
            try:
                st.session_state.oracle_instance = Oracle(
                    model_name=st.session_state.current_model_name,
                    llm_provider=st.session_state.current_llm_provider,
                    search_engine=st.session_state.get('current_search_engine') # Use .get for safety
                )
                # Clear chat history on re-configuration for simplicity
                st.session_state.chat_history = []
                st.session_state.oracle_instance.clear_context() # Also clear context in the oracle itself
                st.success(f"Configuration applied! Model: {st.session_state.current_model_name}, Provider: {st.session_state.current_llm_provider}. Chat history cleared.")
                st.rerun() # Rerun to update the main interface info
            except Exception as e:
                st.error(f"Error applying configuration: {e}")

    st.markdown("---")
    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        if 'oracle_instance' in st.session_state:
            st.session_state.oracle_instance.clear_context()
        st.rerun()

# --- Main Chat Interface ---
# Display chat messages from history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask the oracle..."):
    # Add user message to chat history and display it
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get response from the oracle
    oracle = st.session_state.oracle_instance
    try:
        with st.spinner("Oracle is thinking..."):
            # Note: The Oracle class manages its own internal message history for context.
            # The web_ui's chat_history is primarily for display.
            # When a new Oracle instance is created (e.g. on config change), its internal history is fresh.
            response = oracle.get_response(prompt)

        # Add oracle response to chat history and display it
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)

        # If we want to ensure the latest oracle messages are exactly what's in chat_history:
        # st.session_state.oracle_instance.messages = st.session_state.chat_history
        # However, Oracle class already appends to its internal messages.

    except Exception as e:
        st.error(f"Error getting response from oracle: {e}")
        st.session_state.chat_history.append({"role": "assistant", "content": f"Error: {e}"})

# Instructions for running
st.sidebar.markdown("---")
st.sidebar.info("To run this Web UI: `streamlit run web_ui.py`")
st.sidebar.info(f"Currently using: {st.session_state.oracle_instance.model_name} via {st.session_state.oracle_instance.llm_provider}. Search: {st.session_state.oracle_instance.search_engine or 'Disabled'}")

# For debugging session state if needed
# st.sidebar.expander("Session State").write(st.session_state)
