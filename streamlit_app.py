import streamlit as st
import requests
import time
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Global base URL from environment variable
BASE_URL = os.getenv('API_BASE_URL')

st.set_page_config(
    page_title="PDF Analyzer",
    page_icon="📄",
    layout="wide"
)


def initialize_session_state():
    """Initialize session state variables"""
    if 'current_mode' not in st.session_state:
        st.session_state.current_mode = 'upload'  # 'upload', 'summary', 'chat'
    if 'summary_result' not in st.session_state:
        st.session_state.summary_result = None
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    if 'chat_ready' not in st.session_state:
        st.session_state.chat_ready = False
    if 'summary_ready' not in st.session_state:
        st.session_state.summary_ready = False
    if 'document_info' not in st.session_state:
        st.session_state.document_info = None
    if 'uploaded_file_data' not in st.session_state:
        st.session_state.uploaded_file_data = None
    if 'pdf_filename' not in st.session_state:
        st.session_state.pdf_filename = None
    if 'processing_status' not in st.session_state:
        st.session_state.processing_status = {'summary': False, 'chat': False}
    if 'processing_errors' not in st.session_state:
        st.session_state.processing_errors = {'summary': None, 'chat': None}


def process_pdf_for_summary(file_data):
    """Process PDF for summarization"""
    try:
        files = {
            'file': (file_data['name'], file_data['data'], 'application/pdf')
        }
        data = {'operation': 'summarize'}
        
        response = requests.post(
            f'{BASE_URL}/upload-pdf',
            files=files,
            data=data,
            timeout=300
        )
        
        if response.status_code == 200:
            result = response.json()
            return {'status': 'success', 'result': result}
        else:
            error_msg = f"Analysis failed: {response.status_code} - {response.text}"
            return {'status': 'error', 'message': error_msg}
            
    except requests.exceptions.Timeout:
        error_msg = "Request timed out. The document analysis is taking longer than expected."
        return {'status': 'error', 'message': error_msg}
    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        return {'status': 'error', 'message': error_msg}


def process_pdf_for_chat(file_data):
    """Process PDF for chat mode"""
    try:
        files = {
            'file': (file_data['name'], file_data['data'], 'application/pdf')
        }
        data = {'operation': 'chat'}
        
        response = requests.post(
            f'{BASE_URL}/upload-pdf',
            files=files,
            data=data,
            timeout=300
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                return {'status': 'success', 'result': result}
            else:
                error_msg = f"Chat setup failed: {result.get('message', 'Unknown error')}"
                return {'status': 'error', 'message': error_msg}
        else:
            error_msg = f"Error: {response.status_code} - {response.text}"
            return {'status': 'error', 'message': error_msg}
            
    except requests.exceptions.Timeout:
        error_msg = "Request timed out. The chat setup is taking longer than expected."
        return {'status': 'error', 'message': error_msg}
    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        return {'status': 'error', 'message': error_msg}


def process_uploaded_file(uploaded_file):
    """Process uploaded file for both summary and chat simultaneously"""
    # Store uploaded file data
    st.session_state.uploaded_file_data = {
        'name': uploaded_file.name,
        'data': uploaded_file.getvalue(),
        'size': uploaded_file.size
    }
    
    # Store document info
    st.session_state.document_info = {
        'filename': uploaded_file.name,
        'size_mb': uploaded_file.size / (1024 * 1024)
    }
    
    # Reset processing states
    st.session_state.processing_status = {'summary': False, 'chat': False}
    st.session_state.processing_errors = {'summary': None, 'chat': None}
    st.session_state.summary_ready = False
    st.session_state.chat_ready = False
    
    # Create containers for progress tracking
    progress_container = st.container()
    
    with progress_container:
        st.info("🔄 Processing document for both chat and summary modes... Please wait.")
        
        # Create progress indicators
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**💬 Chat Setup**")
            chat_placeholder = st.empty()
            chat_placeholder.text("⏳ Starting chat setup...")
        
        with col2:
            st.markdown("**📋 Summary Processing**")
            summary_placeholder = st.empty()
            summary_placeholder.text("⏳ Starting summary analysis...")

    # Process chat setup
    chat_placeholder.text("🔄 Setting up chat...")
    chat_result = process_pdf_for_chat(st.session_state.uploaded_file_data)
    
    if chat_result['status'] == 'success':
        st.session_state.pdf_filename = chat_result['result'].get('pdf_filename', uploaded_file.name)
        st.session_state.chat_ready = True
        st.session_state.processing_status['chat'] = True
        chat_placeholder.success("✅ Chat ready!")
    else:
        st.session_state.processing_errors['chat'] = chat_result['message']
        chat_placeholder.error("❌ Chat setup failed")
            
    # Process summary 
    summary_placeholder.text("🔄 Processing summary...")
    summary_result = process_pdf_for_summary(st.session_state.uploaded_file_data)
    
    if summary_result['status'] == 'success':
        st.session_state.summary_result = summary_result['result']
        st.session_state.summary_ready = True
        st.session_state.processing_status['summary'] = True
        summary_placeholder.success("✅ Summary ready!")
    else:
        st.session_state.processing_errors['summary'] = summary_result['message']
        summary_placeholder.error("❌ Summary failed")
    
    # Clear processing message and show results
    time.sleep(1)  # Brief pause to show final status
    progress_container.empty()
    
    # Check if at least one operation succeeded
    if st.session_state.summary_ready or st.session_state.chat_ready:
        st.success("✅ Document processed successfully! You can now switch between modes seamlessly.")
        
        # Show mode selector
        show_mode_selector()
        
        # Default to chat mode if available, otherwise summary mode
        if st.session_state.chat_ready:
            st.session_state.current_mode = 'chat'
        elif st.session_state.summary_ready:
            st.session_state.current_mode = 'summary'
        
    else:
        st.error("❌ Failed to process document for both modes. Please try again.")
        # Show error details
        if st.session_state.processing_errors['chat']:
            st.error(f"Chat Error: {st.session_state.processing_errors['chat']}")
        if st.session_state.processing_errors['summary']:
            st.error(f"Summary Error: {st.session_state.processing_errors['summary']}")
        st.session_state.current_mode = 'upload'


def show_mode_selector():
    """Show mode selector buttons"""
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        if st.session_state.document_info:
            doc_info = st.session_state.document_info
            st.markdown(f"**Document:** {doc_info['filename']} ({doc_info['size_mb']:.2f} MB)")
    
    with col2:
        # Chat button
        button_type = "primary" if st.session_state.current_mode == 'chat' else "secondary"
        disabled = not st.session_state.chat_ready
        
        if st.button("💬 Chat", type=button_type, disabled=disabled, use_container_width=True):
            st.session_state.current_mode = 'chat'
            st.rerun()

    with col3:
        # Summary button
        button_type = "primary" if st.session_state.current_mode == 'summary' else "secondary"
        disabled = not st.session_state.summary_ready
        
        if st.button("📋 Summary", type=button_type, disabled=disabled, use_container_width=True):
            st.session_state.current_mode = 'summary'
            st.rerun()
    
    with col4:
        # New Document button
        if st.button("🔄 New Document", type="secondary", use_container_width=True):
            reset_session_state()
            st.rerun()


def reset_session_state():
    """Reset session state to initial upload state"""
    st.session_state.current_mode = 'upload'
    st.session_state.summary_result = None
    st.session_state.chat_messages = []
    st.session_state.chat_ready = False
    st.session_state.summary_ready = False
    st.session_state.document_info = None
    st.session_state.uploaded_file_data = None
    st.session_state.pdf_filename = None
    st.session_state.processing_status = {'summary': False, 'chat': False}
    st.session_state.processing_errors = {'summary': None, 'chat': None}


def main():
    # Initialize session state first
    initialize_session_state()
    
    # Add sidebar info
    add_sidebar_info()

    st.title("📄 Universal PDF Analyzer")
    st.markdown("Upload any PDF document to analyze its content, generate summaries, and chat with the document")

    # Main interface logic based on current mode
    if st.session_state.current_mode == 'upload':
        show_upload_interface()
    elif st.session_state.current_mode == 'chat':
        show_mode_selector()
        st.markdown("---")
        show_chat_interface()
    elif st.session_state.current_mode == 'summary':
        show_mode_selector()
        st.markdown("---")
        show_summary_result()


def show_upload_interface():
    """Show the upload interface"""
    st.markdown("### Upload PDF Document")

    # File upload with enhanced description
    uploaded_file = st.file_uploader(
        "Choose any PDF file",
        type=['pdf'],
        help="Upload any PDF document - research papers, reports, manuals, articles, books, etc."
    )

    if uploaded_file is not None:
        # Display file info
        file_size_mb = uploaded_file.size / (1024 * 1024)
        st.success(f"📄 **File uploaded:** {uploaded_file.name}")
        st.info(f"📊 **Size:** {file_size_mb:.2f} MB | **Type:** {uploaded_file.type}")

        # Document type hint
        with st.expander("ℹ️ Document Type Detection", expanded=False):
            st.markdown("""
            The system will automatically detect and adapt to your document type:
            - **Research Papers**: Academic articles, studies, journals
            - **Business Reports**: Corporate documents, market analysis, financial reports
            - **Technical Manuals**: User guides, specifications, procedures
            - **Policy Documents**: Legal texts, regulations, compliance documents
            - **General Documents**: Books, articles, presentations, and more
            """)

        # Single process button
        if st.button("🚀 Process Document", use_container_width=True, type="primary"):
            process_uploaded_file(uploaded_file)

    else:
        # Enhanced welcome message
        st.markdown("""
        ### 🚀 Welcome to Universal PDF Analyzer
        
        This tool can analyze **any type of PDF document** and provide:
        
        📋 **Smart Summarization**
        - Automatically detects document type
        - Generates comprehensive analysis
        - Extracts key insights and findings
        
        💬 **Interactive Chat**
        - Ask questions about your document
        - Get detailed explanations
        - Explore specific sections or topics
        
        **Simply upload your PDF file and both modes will be prepared simultaneously for a seamless experience!**
        """)


def show_summary_result():
    """Display the PDF summary result"""
    if not st.session_state.summary_ready:
        if st.session_state.processing_errors['summary']:
            st.error(f"❌ Summary Error: {st.session_state.processing_errors['summary']}")
        else:
            st.info("📋 Summary is being prepared...")
        return

    st.markdown("### 📋 Document Analysis Result")

    # Display the summary
    if st.session_state.summary_result:
        try:
            # Get summary content from API response
            summary_content = st.session_state.summary_result.get('summary', 'No summary available')

            # Display summary with enhanced formatting
            st.markdown("#### 📊 Comprehensive Document Analysis")
            
            # Create tabs for different view modes
            tab1, tab2 = st.tabs(["📖 Formatted View", "📄 Raw Text"])
            
            with tab1:
                st.markdown(summary_content)
            
            with tab2:
                st.text_area("Raw summary text", summary_content, height=400)

            # Enhanced download options
            st.markdown("---")
            st.markdown("#### 📥 Download Options")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.download_button(
                    label="📄 Download as Text",
                    data=summary_content,
                    file_name=f"document_analysis_{int(time.time())}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            with col2:
                # Create markdown version
                markdown_content = f"# Document Analysis\n\n**File:** {st.session_state.document_info['filename']}\n\n**Analysis Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n---\n\n{summary_content}"
                st.download_button(
                    label="📝 Download as Markdown",
                    data=markdown_content,
                    file_name=f"document_analysis_{int(time.time())}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
            
            with col3:
                # Create JSON version
                json_content = json.dumps({
                    "document_info": st.session_state.document_info,
                    "analysis_date": time.strftime('%Y-%m-%d %H:%M:%S'),
                    "summary": summary_content
                }, indent=2)
                st.download_button(
                    label="📊 Download as JSON",
                    data=json_content,
                    file_name=f"document_analysis_{int(time.time())}.json",
                    mime="application/json",
                    use_container_width=True
                )

        except Exception as e:
            st.error(f"❌ Error displaying summary: {str(e)}")
            st.json(st.session_state.summary_result)  # Fallback to raw JSON


def show_chat_interface():
    """Display the chat interface"""
    if not st.session_state.chat_ready:
        if st.session_state.processing_errors['chat']:
            st.error(f"❌ Chat Error: {st.session_state.processing_errors['chat']}")
        else:
            st.info("💬 Chat is being prepared...")
        return

    pdf_name = st.session_state.get('pdf_filename', 'Document')
    
    # Enhanced header
    st.markdown(f"### 💬 Interactive Chat with **{pdf_name}**")
    
    if st.session_state.document_info:
        doc_info = st.session_state.document_info
        st.markdown(f"*Document size: {doc_info['size_mb']:.2f} MB | Ready for questions*")

    # Display chat messages
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask me anything about this document..."):
        # Add user message to chat history
        st.session_state.chat_messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate assistant response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing document and generating response..."):
                response = handle_chat_message(prompt)
                st.markdown(response)

        # Add assistant response to chat history
        st.session_state.chat_messages.append({"role": "assistant", "content": response})

    # Export chat option
    if st.session_state.chat_messages:
        st.markdown("---")
        st.markdown("#### 📥 Export Chat History")
        
        # Create both text and JSON versions
        chat_export = {
            "document": pdf_name,
            "export_date": time.strftime('%Y-%m-%d %H:%M:%S'),
            "messages": st.session_state.chat_messages
        }
        
        chat_text = f"# Chat History with {pdf_name}\n\n"
        chat_text += f"**Exported:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        chat_text += "---\n\n"
        
        for msg in st.session_state.chat_messages:
            role = "**You:**" if msg["role"] == "user" else "**Assistant:**"
            chat_text += f"{role} {msg['content']}\n\n"
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                label="📄 Download as Text",
                data=chat_text,
                file_name=f"chat_history_{int(time.time())}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with col2:
            st.download_button(
                label="📊 Download as JSON",
                data=json.dumps(chat_export, indent=2),
                file_name=f"chat_history_{int(time.time())}.json",
                mime="application/json",
                use_container_width=True
            )


def handle_chat_message(user_message):
    """Handle a chat message and get response from chat API"""
    try:
        # Get PDF filename from session state
        pdf_name = st.session_state.get('pdf_filename', 'Document')
        pdf_name = pdf_name.split('.')[0]

        # Prepare chat payload
        chat_payload = {
            "file_name": pdf_name,
            "query": user_message
        }

        # Make request to chat endpoint
        response = requests.post(
            f'{BASE_URL}/chat',
            json=chat_payload,
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()

            # Check if the response was successful
            if result.get('status') == 'success':
                return result.get('llm_reply', 'No response received from the AI.')
            else:
                error_message = result.get('message', 'Unknown error occurred')
                return f"❌ Sorry, I encountered an issue: {error_message}"

        else:
            return f"❌ Sorry, I couldn't process your request. Server returned status code: {response.status_code}"

    except requests.exceptions.Timeout:
        return "⏱️ Sorry, the request took too long to process. Please try again with a shorter question."

    except requests.exceptions.ConnectionError:
        return "🔌 Sorry, I couldn't connect to the chat service. Please ensure the API server is running."

    except requests.exceptions.RequestException as e:
        return f"🌐 Sorry, there was a network error: {str(e)}"

    except json.JSONDecodeError:
        return "❌ Sorry, I received an invalid response from the server. Please try again."

    except Exception as e:
        return f"❌ Sorry, I encountered an unexpected error: {str(e)}"


def add_sidebar_info():
    """Add information sidebar"""
    with st.sidebar:
        st.markdown("### 🔧 Server Status")
        try:
            health_response = requests.get(f'{BASE_URL}/health', timeout=5)
            if health_response.status_code == 200:
                st.success("✅ API Server Connected")
            else:
                st.error("❌ API Server Issues")
        except Exception as e: 
            print(f"Error checking server status: {e}")
            st.error("❌ API Server Offline")

        st.markdown("### ℹ️ About Universal PDF Analyzer")
        st.markdown("""
        This tool can analyze **any type of PDF document** and provide intelligent insights.

        **🎯 Features:**
        - 📋 **Smart Analysis**: Automatically detects document type and generates comprehensive summaries
        - 💬 **Interactive Chat**: Ask questions and get detailed explanations
        - 📊 **Multiple Export Options**: Download results in various formats
        - 🚀 **Seamless Experience**: Both modes are prepared simultaneously for instant switching

        **📄 Supported Document Types:**
        - Research papers & academic articles
        - Business reports & corporate documents
        - Technical manuals & specifications
        - Policy documents & legal texts
        - Books, articles, presentations, and more

        **💡 Tips:**
        - Upload your PDF once and both summary and chat modes will be ready
        - Switch between modes instantly without reprocessing
        - Use specific questions in chat mode for detailed answers
        - Export your results in multiple formats
        """)


if __name__ == "__main__":
    main()