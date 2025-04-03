import requests
from google.genai import types
from google import genai
import os
from dotenv import load_dotenv
import json
import base64

load_dotenv()


def get_file_code(owner, repo, file_path):
    """
    Retrieves the content of a specific file from a GitHub repository.

    Args:
        owner (str): The owner of the repository.
        repo (str): The name of the repository.
        file_path (str): The path to the file within the repository.

    Returns:
        str: The decoded content of the file (as UTF-8), or None if an error occurs.
    """
    print("Trigger get file code")
    github_token = os.getenv("GITHUB_AUTH_TOKEN")
    headers = {
        "Accept": "application/vnd.github+json",
    }
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"
    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json()

        if "content" in data and "encoding" in data and data["encoding"] == "base64":
            content = base64.b64decode(data["content"]).decode(
                "utf-8", errors="ignore")
            return content
        elif "message" in data:
            print(f"Error: {data['message']}")
            return None
        else:
            print("Error: Unexpected response format.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error during API request: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")
        return None


def search_repo(owner, repo, query):
    print(f"Trigger search repo {query}")
    # GitHub API endpoint for searching code in a specific repository
    api_url = (
        f"https://api.github.com/search/code?q={query}+language:js+repo:{owner}/{repo}"
    )

    # Make the API request
    response = requests.get(
        api_url,
        headers={
            "Authorization": f'Bearer {os.getenv("GITHUB_AUTH_TOKEN")}',
            "Accept": "application/vnd.github+json",
        },
    ).json()

    response = {
        'total_count': response['total_count'],
        'items': [
            {
                'name': item['name'],
                'path': item['path']
            } for item in response['items']
        ]
    }

    return response


def get_repo_info(owner, repo):
    """
    Retrieves information about a GitHub repository.

    Args:
        owner (str): The owner of the repository.
        repo (str): The name of the repository.

    Returns:
        dict: A dictionary containing repository information.
    """
    print("Trigger get repo info")
    github_token = os.getenv("GITHUB_AUTH_TOKEN")
    headers = {
        "Accept": "application/vnd.github+json",
    }
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"

    api_url = f"https://api.github.com/repos/{owner}/{repo}"

    try:
        response = requests.get(api_url, headers=headers)
        response = response.json()
        response = {
            'full_name': response['full_name'],
            'private': response['private'],
            'owner_login': response['owner']['login'],
            'html_url': response['html_url'],
            'description': response['description'],
            'fork': response['fork'],
            'language': response['language'],
            'open_issues_count': response['open_issues_count'],
            'created_at': response['created_at'],
        }
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error during API request: {e}")
        return None


get_repo_info_function_declaration = types.FunctionDeclaration(
    name="get_repo_info",
    description="Get github repository's information",
    parameters={
        "type": "object",
        "properties": {
            "owner": {
                "type": "string",
                "description": "The owner of the repository.",
            },
            "repo": {
                "type": "string",
                "description": "The name of the repository.",
            },
        },
    },
)

get_file_code_function_declaration = types.FunctionDeclaration(
    name="get_file_code",
    description="Get the content of a specific file in the repository",
    parameters={
        "type": "object",
        "properties": {
            "owner": {
                "type": "string",
                "description": "The owner of the repository.",
            },
            "repo": {
                "type": "string",
                "description": "The name of the repository.",
            },
            "file_path": {
                "type": "string",
                "description": "The path to the file in the repository.",
            },
        },
    },
)

search_repo_function_declaration = types.FunctionDeclaration(
    name="search_repo",
    description="Search for a specific code in the repository",
    parameters={
        "type": "object",
        "properties": {
            "owner": {
                "type": "string",
                "description": "The owner of the repository.",
            },
            "repo": {
                "type": "string",
                "description": "The name of the repository.",
            },
            "query": {
                "type": "string",
                "description": "The code to search for in the repository.",
            },
        },
    },
)
available_tools = [
    get_repo_info_function_declaration,
    search_repo_function_declaration,
    get_file_code_function_declaration,
]
available_functions = {
    "get_repo_info": get_repo_info,
    "search_repo": search_repo,
    "get_file_code": get_file_code,
}


def initialize_gemini_model(model_name="gemini-2.0-flash"):
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    tool = types.Tool(function_declarations=available_tools)
    config = types.GenerateContentConfig(
        system_instruction="""
        You are an AI designed to analyze code repositories. When provided with a URL pointing to a code repository (e.g., on platforms like GitHub, GitLab, Bitbucket), you will perform the following steps:


        **1. Search Repository:**
        - Based on the file list and your understanding of common software vulnerabilities and security best practices, identify potentially interesting or risky files and keywords to examine further.
        - Perform targeted searches within the repository content for patterns, keywords, or file names that might indicate security concerns (e.g., "secret", "password", "API_KEY", "TODO: SECURITY", common vulnerability patterns in specific languages/frameworks).
        - Briefly note the files and the search terms that yielded results.

        **2. Get Content of Specific Files:**
        - Retrieve the content of the files identified in the "Search Repository" step as being potentially relevant to security.
        - Also, retrieve the content of key configuration files (e.g., `.env`, `config.yaml`, `settings.py`), dependency management files (e.g., `requirements.txt`, `package.json`, `pom.xml`), and any files that appear to handle authentication or authorization.

        **3. Generate Detailed Test Report and Identify Security Risks:**
        - Analyze the content of the retrieved files, considering:
            - Potential vulnerabilities based on common coding errors and security weaknesses.
            - Misconfigurations or exposed sensitive information.
            - Outdated dependencies with known vulnerabilities.
            - Insecure coding practices.
        - Generate a detailed test report summarizing your findings. This report should:
            - List the files analyzed.
            - Describe any identified security risks, explaining the potential impact and location in the code.
            - Categorize the severity of the identified risks (e.g., High, Medium, Low).

        **4. Suggest Additional Tests:**
        - Based on your analysis of the repository structure, programming languages used, and identified risks, suggest specific tests that could be added to further evaluate the security of the codebase. These suggestions should be actionable and clearly describe what the test should aim to achieve. Examples include:
            - Specific static analysis checks.
            - Dynamic testing approaches.
            - Manual code review areas to focus on.
            - Dependency scanning tools to use.

        **Output Format:**

        Your final output should be structured clearly and structred start from 1, including sections for each of the above steps:
        - **Repository Information:** (A summary of the repository, including its purpose and technologies used)
        - **Repository Owner and Name:** (The owner and name of the repository)
        - **Repository File List:** (A well-formatted list of files and directories)
        - **Search Repository Findings:** (List of files and the keywords that triggered attention)
        - **Analyzed File Content:** (Provide relevant snippets or summaries of the content of key files)
        - **Detailed Test Report and Security Risks:** (A comprehensive report detailing identified risks, their location, and severity)
        - **Suggested Additional Tests:** (A list of specific and actionable test recommendations)""",
        tools=[tool],
    )
    return client.chats.create(model="gemini-2.0-flash", config=config)


def generate_test_report(owner, repo):
    """
    Generates a test report for a given GitHub repository.
    """
    chat = initialize_gemini_model()
    response = chat.send_message(
        f"Analyze test coverage of this repo? Suggest unit test code also repo name: {repo} owner is {owner}"
    )
    while response.function_calls:
        concat_function_call_results = []
        for function_call in response.function_calls:
            function_name = function_call.name
            arguments = function_call.args
            if function_name in available_functions:
                result = available_functions[function_name](**arguments)
            concat_function_call_results.append(
                types.Part.from_function_response(
                    name=function_call.name, response={"response": result}
                )
            )
        response = chat.send_message(concat_function_call_results)
    return response.text


if __name__ == "__main__":
    # Example usage
    owner = "DKER2"
    repo = "tic-tac-toe"
    report = search_repo(owner, repo, "test")
    print(json.dumps(report, indent=4))
