import streamlit as st
import requests
import os
from dotenv import load_dotenv
import json
import base64
from gemini_model import generate_test_report
load_dotenv()
        
def test_report_generation():
    st.title("Test Report Generation")
    st.write("Gain valuable insights into website code with our Test Report Generation tool. Input any URL and instantly receive a detailed report to understand its structure, technologies, and potential areas for improvement.")
    repo_url = st.text_input(label="Enter your repository's url", placeholder="https://github.com/DKER2/personalwebsite")
    if st.button("Generate Report"):
        if repo_url:
            try:
                repo_path = repo_url.replace("https://github.com/", "").strip("/")
                owner, repo = repo_path.split("/")
            except ValueError:
                st.error("Invalid repository URL. Please ensure it follows the format: https://github.com/owner/repo")
                return
            report = generate_test_report(owner=owner, repo=repo)
            st.markdown(report)
            st.success("Report generated successfully!")
        else:
            st.warning("Please enter a repository URL.")
    
def main():
    page = st.sidebar.radio(
        "What would you like to do today?", ["Test Report Generation", "View Profile"]
    )
    if page == "Test Report Generation":
        test_report_generation()

if __name__=="__main__":
    main()