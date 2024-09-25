import streamlit as st
from transformers import pipeline

# Initialize summarization pipeline (using pre-trained BART model)
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Set page config for a wide layout
st.set_page_config(page_title="Text Summarizer", layout="wide")

# Create two columns: one for input and one for output
input_col, output_col = st.columns(2)

# Initialize summary_text variable
summary_text = ""

# Input text from user
with input_col:
    st.header("Input Text")
    # Text area for input (initially empty)
    input_text = st.text_area("Enter the text you want to summarize", height=300, value="")

    # Display word count for input text
    input_word_count = len(input_text.split())
    st.write(f"Word count: {input_word_count}")

    # Summarize button at the bottom of the input section
    if st.button("Summarize"):
        if input_text:
            # Generate summary with adjusted length parameters
            summary = summarizer(input_text, max_length=200, min_length=50, do_sample=False)
            summary_text = summary[0]['summary_text']  # Store the summary text

# Output section
with output_col:
    st.header("Summary")
    # Display summary text area (if summary_text is generated)
    st.text_area("Summary of the text:", summary_text, height=300)

    # Show the summary word count
    output_word_count = len(summary_text.split()) if summary_text else 0
    st.write(f"Word count: {output_word_count}")
