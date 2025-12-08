# Task 3: Turn a script into a reusable library
# Starting script:
#
# import requests
#
# def main():
#     url = "https://example.com/data"
#     print(requests.get(url).json())
#
# Task:
# Turn this into a package that provides:
# 	•	A module with reusable functions
# 	•	A CLI tool (myfetch) installed via entrypoints
# 	•	Tests for the API stub (mock requests.get)
# 	•	Ability to configure the URL via env var or CLI flag
#
# What this tests
# 	•	Packaging (pyproject.toml)
# 	•	CLI design (argparse / click)
# 	•	Mocking and testability
# 	•	Separation of concerns
