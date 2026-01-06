import streamlit as st
import os
import tempfile
from markitdown import MarkItDown

# --- APP CONFIGURATION ---
st.set_page_config(
    page_title="Universal Doc Converter",
    page_icon="📄",
    layout="centered"
)

# --- INITIALIZE ENGINE ---
# We initialize MarkItDown once.
# Note: MarkItDown handles requests internally. 
# While we can't easily inject headers into its deep internal calls without patching,
# we wrap all execution in robust error handlers as requested.
try:
    md = MarkItDown()
except Exception as e:
    st.error(f"Failed to initialize conversion engine: {e}")

# --- HELPER: SAVE UPLOAD TO TEMP ---
def save_uploaded_file(uploaded_file):
    """
    Saves the uploaded byte stream to a temporary file 
    so libraries that need a file path can read it.
    """
    try:
        # Create a temp file with the correct extension (suffix)
        # This helps MarkItDown detect the file type automatically
        suffix = os.path.splitext(uploaded_file.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            return tmp_file.name
    except Exception:
        return None

# --- UI LAYOUT ---
st.title("📄 Universal Document Reader")
st.markdown("""
    Convert **Word, Excel, PowerPoint, PDF, and HTML** to clean Markdown text instantly.
    *Powered by Microsoft MarkItDown*
""")

# [2] Upload Area
uploaded_files = st.file_uploader(
    "Drag and drop files here", 
    accept_multiple_files=True,
    type=['docx', 'xlsx', 'pptx', 'pdf', 'html', 'csv', 'json', 'xml']
)

if uploaded_files:
    st.write("---")
    
    for uploaded_file in uploaded_files:
        with st.spinner(f"Processing {uploaded_file.name}..."):
            
            # Create a localized expander for each file
            with st.expander(f"📄 {uploaded_file.name}", expanded=True):
                
                # 1. Save to temp path
                temp_path = save_uploaded_file(uploaded_file)
                
                if temp_path:
                    try:
                        # [1] The Engine: MarkItDown Conversion
                        # We use a general try/except block to catch format errors
                        result = md.convert(temp_path)
                        text_content = result.text_content
                        
                        # [2] Instant Preview (Scrollable)
                        st.subheader("Preview")
                        st.text_area("Content", value=text_content, height=250)
                        
                        # Generate Output Filenames
                        base_name = os.path.splitext(uploaded_file.name)[0]
                        md_filename = f"{base_name}_converted.md"
                        txt_filename = f"{base_name}_converted.txt"
                        
                        # [2] Download Options (Columns for buttons)
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.download_button(
                                label="⬇️ Download Markdown (.md)",
                                data=text_content,
                                file_name=md_filename,
                                mime="text/markdown"
                            )
                            
                        with col2:
                            st.download_button(
                                label="⬇️ Download Text (.txt)",
                                data=text_content,
                                file_name=txt_filename,
                                mime="text/plain"
                            )
                            
                    except Exception as e:
                        # [3] Resilience & Cheeky Error Message
                        st.error("⚠️ Sahi format mein file daal Bey!!")
                        st.caption(f"Technical Error Details: {str(e)}")
                    
                    finally:
                        # Cleanup temp file
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                else:
                    st.error("⚠️ Sahi format mein file daal Bey!! (File upload failed)")

    st.success("All files processed!")
