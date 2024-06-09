import os
import dotenv
import json
from openai import OpenAI
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
dotenv.load_dotenv(dotenv_path)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)


PROMPT_DIFF_MESSAGE_FORMAT = """
Given the below smart contract source code diff information, please summarize the main changes and must also generate an overall description. Secondly, please predict the corresponding software upgradability intention using several common keywords and shows its evidence. 
{0}
"""

diff_files = json.load(open("usccheck/chatgpt/diff_files.json"))

software_upgradability_intentions = []
for diff_file in diff_files:
    print(diff_file[0])
    diff_summary = diff_file[1]
    diff_lines = diff_summary.split('\n')
    for line in diff_lines:
        # We search for the correct section
        if line.startswith("##"):
            section = line.strip()
        else:
            if section.find("Software Upgradability Intention")!=-1:
                software_upgradability_intentions.append(line)

print(software_upgradability_intentions)
with open("usccheck/chatgpt/software_upgradability_itentions.txt", "w") as fo:
    fo.write("\n".join(software_upgradability_intentions))