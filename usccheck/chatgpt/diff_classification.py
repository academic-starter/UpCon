
import os
import dotenv
import json
from openai import OpenAI
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
dotenv.load_dotenv(dotenv_path)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

TAXONOMY = """
Category	Heuristics
License Update	Use different open source license. e.g., GPL-3, MIT and etc
Copyright Update	Software copyright information, e.g., author, year, email etc., update
Comment Improvement	Fix comment error, Update comment to ensure documentation consistency with code; Delete Document;
Comment Addition	Add comments to explain code better.
Code Refactoring (Modularization)	Separate large function into different smaller/internal functions;
Feature Removal	Remove unused/useless function, log statements, state variables, events.
Redundancy Removal	Remove redundant event emissions, requirements, and etc.
	
Solidity Version Update	Change Soldiity version from a legacy version to new version.
OpenZeppelin API Libary Update	Update OpenZeppelin library from a legacy version to new version.
	
Functionality Addition	Add new function
Functionality Update	Add new parameters; modify parameters types; insert external function call.
Traceability Addition	Add event / data accessibility.
Interoperability Addition	Inherit / Use new interface.
Exception Handling Enhancement	Add error code; add revert / try-catch statements.
Access Control Mangement	Add roles / blacklist / ownership checks / permission checks.
Governance Update	Add governance component.
Reentrancy Prevention Addition	Add reentrancy protection, e.g., noReentrancy modifier.
Safe Operations Use	Replace with safe operation versions, e.g., safeTransfer.
	
Wrong Logic Correction	Add input validation check; change operators. swap argument order; modify default return value.
Code Typo Correction	Fix typos in identifiers including variables, functions etc.
Error Message Correction	Correct inconsistent error message in codebase 
"""
PROMPT_DIFF_CLASSIFICATION_FORMAT = """
Given the below smart contract source code text diff information, please classify contract changes according to the following taxonomy including twenty categories and useful heuristics to identify it. 
You must examine all twenty categories one by one, and must report valid results that are supported by any actual code changes. 
The results must be a JSON array, where each item consists of category, heuristics, and the corresponding explained evidence.  

# Taxonomy of Smart Contract Changes Intent:		
"{0} "

# Source code text diff:
{1}
"""

diff_content = open("usccheck/diff_onchain.log").read()

items = diff_content.split("--- usccheck")
print(len(items[1:]), " file diffs")

results = []
for item in items[1:]:
    item = "--- usccheck"+item
    diff_files = item.splitlines()[:2]
    print(diff_files)
    # print(PROMPT_DIFF_MESSAGE_FORMAT.format(item))
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        temperature=0.5,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user",
                "content": PROMPT_DIFF_CLASSIFICATION_FORMAT.format(TAXONOMY, item)[:16385]}
        ]
    )

    print(completion.choices[0].message.content)
    results.append([item, completion.choices[0].message.content])
    json.dump(results, open(
        "usccheck/chatgpt/diff_classification.json", "w"), indent=4)
    # break
