import streamlit as st
import os
import tempfile
import pandas as pd
from markitdown import MarkItDown

# --- APP CONFIGURATION ---
st.set_page_config(
    page_title="Universal Doc Converter",
    page_icon="📄",
    layout="centered"
)

# --- INITIALIZE ENGINE ---
try:
    md = MarkItDown()
except Exception as e:
    st.error(f"Failed to initialize conversion engine: {e}")

# --- HELPER: SAVE UPLOAD TO TEMP ---
def save_uploaded_file(uploaded_file):
    try:
        suffix = os.path.splitext(uploaded_file.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            return tmp_file.name
    except Exception:
        return None

# --- HELPER: FORMAT FILE SIZE ---
def format_size(size_in_bytes):
    if size_in_bytes < 1024:
        return f"{size_in_bytes} bytes"
    elif size_in_bytes < 1024 * 1024:
        return f"{size_in_bytes / 1024:.2f} KB"
    else:
        return f"{size_in_bytes / (1024 * 1024):.2f} MB"

# --- UI LAYOUT ---
st.title("📄 Universal Document Reader")
st.markdown("""
    Convert **Word, Excel, PowerPoint, PDF, and HTML** to clean Markdown text instantly.
    *Powered by Microsoft MarkItDown*
""")

# Upload Area
uploaded_files = st.file_uploader(
    "Drag and drop files here", 
    accept_multiple_files=True,
    type=['docx', 'xlsx', 'pptx', 'pdf', 'html', 'csv', 'json', 'xml']
)

if uploaded_files:
    st.write("---")
    
    for uploaded_file in uploaded_files:
        with st.spinner(f"Processing {uploaded_file.name}..."):
            
            with st.expander(f"📄 {uploaded_file.name}", expanded=True):
                
                temp_path = save_uploaded_file(uploaded_file)
                
                if temp_path:
                    try:
                        # 1. Conversion
                        result = md.convert(temp_path)
                        text_content = result.text_content
                        
                        # 2. Size Calculations
                        original_size = uploaded_file.size
                        # Estimate txt size by encoding string to bytes
                        converted_size = len(text_content.encode('utf-8'))
                        
                        reduction_filesize = original_size - converted_size
                        reduction_pct = (reduction_filesize / original_size) * 100 if original_size > 0 else 0
                        
                        # 3. Create Tabs
                        tab_preview, tab_stats = st.tabs(["👁️ Preview & Download", "📊 File Size Comparison"])
                        
                        # --- TAB 1: PREVIEW & DOWNLOAD ---
                        with tab_preview:
                            st.text_area("Content", value=text_content, height=250)
                            
                            base_name = os.path.splitext(uploaded_file.name)[0]
                            col1, col2 = st.columns(2)
                            with col1:
                                st.download_button(
                                    label="⬇️ Download Markdown (.md)",
                                    data=text_content,
                                    file_name=f"{base_name}_converted.md",
                                    mime="text/markdown"
                                )
                            with col2:
                                st.download_button(
                                    label="⬇️ Download Text (.txt)",
                                    data=text_content,
                                    file_name=f"{base_name}_converted.txt",
                                    mime="text/plain"
                                )

                        # --- TAB 2: FILE SIZE COMPARISON ---
                        with tab_stats:
                            st.write("### Optimization Analysis")
                            
                            # Create a clean DataFrame for the table
                            data = {
                                "Metric": ["Original File Size", "Converted .txt File Size"],
                                "Value": [format_size(original_size), format_size(converted_size)]
                            }
                            df = pd.DataFrame(data)
                            
                            # Display the table without the index
                            st.table(df)
                            
                            # Display the percentage impact
                            if reduction_pct > 0:
                                st.success(f"🚀 **Efficiency:** Text version is **{reduction_pct:.1f}% smaller** than the original.")
                            else:
                                st.info(f"ℹ️ Text version is roughly the same size or larger (common for small text-heavy files).")

                    except Exception as e:
                        st.error("⚠️ Sahi format mein file daal Bey!!")
                        st.caption(f"Technical Error Details: {str(e)}")
                    
                    finally:
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                else:
                    st.error("⚠️ Sahi format mein file daal Bey!! (File upload failed)")

    st.success("All files processed!")
