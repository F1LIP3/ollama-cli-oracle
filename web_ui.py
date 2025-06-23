import streamlit as st
from oracle_core.oracle import Oracle

# Page configuration (optional, but good practice)
st.set_page_config(page_title="LLM Oracle", layout="wide")

st.title("Local LLM Oracle Interface")

# Initialize Oracle instance in session state if it doesn't exist
if 'oracle_instance' not in st.session_state:
    # Default values, can be made configurable later
    st.session_state.oracle_instance = Oracle(model_name='llama3.2', llm_provider='ollama', search_engine=None)
    st.session_state.chat_history = [] # To store and display chat messages: [ {'role': 'user'/'assistant', 'content': '...'} ]

# --- Sidebar for Configuration ---
with st.sidebar:
    st.header("Configuration")

    model_name = st.text_input("Model Name", value=st.session_state.oracle_instance.model_name)

    llm_provider = st.selectbox(
        "LLM Provider",
        options=['ollama', 'lm_studio'],
        index=0 if st.session_state.oracle_instance.llm_provider == 'ollama' else 1
    )

    search_engine_options = [None, 'google', 'bing', 'yahoo', 'duckduckgo', 'brave']
    current_search_engine = st.session_state.oracle_instance.search_engine
    search_engine_index = search_engine_options.index(current_search_engine) if current_search_engine in search_engine_options else 0

    search_engine = st.selectbox(
        "Search Engine (Optional)",
        options=search_engine_options,
        index=search_engine_index,
        format_func=lambda x: x if x else "Disabled"
    )

    if st.button("Apply Configuration"):
        try:
            st.session_state.oracle_instance = Oracle(
                model_name=model_name,
                llm_provider=llm_provider,
                search_engine=search_engine
            )
            # Clear chat history on re-configuration for simplicity
            st.session_state.chat_history = []
            st.session_state.oracle_instance.clear_context() # Also clear context in the oracle itself
            st.success("Configuration applied! Chat history cleared.")
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
