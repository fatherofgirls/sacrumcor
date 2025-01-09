import os
import streamlit as st
import anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def initialize_session_state():
    """Initialize or reset session state variables."""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'model_config' not in st.session_state:
        st.session_state.model_config = {
            'model': os.getenv('DEFAULT_MODEL', 'claude-3-opus-20240229'),
            'temperature': 0.7,  # Hardcoded temperature
            'max_tokens': int(os.getenv('DEFAULT_MAX_TOKENS', 1000))
        }

def sidebar_config():
    """Configure sidebar settings for the LLM."""
    st.sidebar.title("🤖 LLM Configuration")
    
    # Model selection from environment variable
    model_options = os.getenv('AVAILABLE_MODELS', '').split(',')
    
    # Fallback if no models defined
    if not model_options or model_options == ['']:
        model_options = [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229", 
            "claude-3-haiku-20240307"
        ]
    
    # Select model with current state as default
    st.session_state.model_config['model'] = st.sidebar.selectbox(
        "Select Model", 
        model_options, 
        index=model_options.index(st.session_state.model_config['model'])
    )

def display_chat_history():
    """Display previous chat messages."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def generate_llm_response(prompt):
    """Generate response from the LLM."""
    # Retrieve API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    
    # Validate API key
    if not api_key:
        st.error("API key not found. Please set ANTHROPIC_API_KEY in your .env file.")
        return "API key is required to use the model."
    
    try:
        # Initialize Anthropic client
        client = anthropic.Anthropic(api_key=api_key)
        
        # Prepare messages for API call
        messages = [
            {"role": m["role"], "content": m["content"]} 
            for m in st.session_state.messages
        ]
        
        # Create LLM response
        response = client.messages.create(
            model=st.session_state.model_config['model'],
            max_tokens=st.session_state.model_config['max_tokens'],
            temperature=st.session_state.model_config['temperature'],
            messages=messages
        )
        
        return response.content[0].text
    except Exception as e:
        st.error(f"Error generating response: {e}")
        return "An error occurred while generating the response."

def main():
    """Main function to run the Streamlit app."""
    # Initialize session state
    initialize_session_state()

    # Configure sidebar
    sidebar_config()

    # Main chat interface
    st.title("💬 LLM Chat Interface")

    # Display chat messages from history
    display_chat_history()

    # Chat input
    prompt = st.text_input("You:", key="input")

    if prompt:
        # Add user message to chat history
        st.session_state.messages.append({
            "role": "user", 
            "content": prompt
        })
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            response = generate_llm_response(prompt)
            st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({
            "role": "assistant", 
            "content": response
        })

    # Additional sidebar features
    st.sidebar.markdown("---")

    # Clear chat history button
    if st.sidebar.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.experimental_rerun()

    # About section
    st.sidebar.markdown("""
    ---
    ### About This App
    A customizable LLM chat interface built with Streamlit.
    """)

# Entry point for the application
if __name__ == "__main__":
    main()