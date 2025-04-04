# Table of Contents

1.  [Installation](#1-installation)
2.  [Understanding the Repository Structure](#2-understanding-the-repository-structure)
3.  [Running the Streamlit App](#3-running-the-streamlit-app)
## 1. Installation

**Install Dependencies (using `requirements.txt`):** Navigate to the root directory of the our application's repository in your terminal. If the repository includes a `requirements.txt` file, install all the listed dependencies using the following command:
```bash
    pip install -r requirements.txt
```

## 2. Understanding the Repository Structure

A well-organized Streamlit project often follows a structure similar to this:

**Key Files and Folders:**

* **`.gitignore`:** Helps manage which files are tracked by Git, especially useful for excluding virtual environment folders, data files, or temporary files.
s ensures that anyone setting up the project has the necessary dependencies.
* **`data/`:** This folder typically stores the datasets used by the Streamlit application. Keeping data separate from the code makes the project more organized.
* **`assigment2.py`:** This file include the definition of streamlit application, how UI is structer
* **`gemini_model.py`:** This file include the definition of all function declaration as well as the services provided by Gemini model


## 3. Running the Streamlit App

To run the Streamlit application, follow these steps:

1  **Navigate to the home Directory:** Use the `cd` command in your terminal to navigate to the directory where the main Streamlit application file (`assignment2.py` file) is located.

2.  **Run the Streamlit App:**

    ```bash
    streamlit run assignment2.py
    ```