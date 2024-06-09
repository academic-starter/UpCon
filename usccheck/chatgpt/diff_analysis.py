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
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user",
                "content": PROMPT_DIFF_MESSAGE_FORMAT.format(item)[:16385]}
        ]
    )

    print(completion.choices[0].message.content)
    results.append([diff_files, completion.choices[0].message.content])
    json.dump(results, open("usccheck/chatgpt/diff_files.json", "w"), indent=4)
