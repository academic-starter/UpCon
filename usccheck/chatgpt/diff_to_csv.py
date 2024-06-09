import json
import csv
import pandas as pd
diff_changes = json.load(open("usccheck/chatgpt/diff_files.json"))
diff_classifications = json.load(
    open("usccheck/chatgpt/diff_classification.json"))
assert len(diff_changes) == len(diff_classifications)

TAXONOMY = """
Category	Heuristics
License Update	Use different open source license. e.g., GPL-3, MIT and etc
Copyright Update	Software copyright information, e.g., author, year, email etc., update
Comment Improvement	Fix comment error, Update comment to ensure documentation consistency with code; Delete Document;
Comment Addition	Add comments to explain code better.
Code Refactoring (Modularization)	Separate large function into different smaller/internal functions;
Feature Removal	Remove unused/useless function, log statements, state variables, events.
Redundancy Removal	Remove redundant event emissions, requirements, and etc.

Solidity Version Update	Change Solidity version from a legacy version to new version.
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
cats = ["License Update", "Copyright Update", "Comment Improvement", "Comment Addition", "Code Refactoring (Modularization)", "Feature Removal", "Redundancy Removal", "Solidity Version Update", "OpenZeppelin API Libary Update", "Functionality Addition", "Functionality Update",
        "Traceability Addition", "Interoperability Addition", "Exception Handling Enhancement", "Access Control Mangement", "Governance Update", "Reentrancy Prevention", "Safe Operations Use", "Wrong Logic Correction", "Code Typo Correction", "Error Message Correction"]
diff_change_classification_excel = "usccheck/chatgpt/diff_change_classifications.xlsx"
# with open(diff_change_classification_csv, "w") as diff_change_classification_file:
#     csvwriter = csv.writer(diff_change_classification_file, delimiter=' ',
#                             quotechar='|', quoting=csv.QUOTE_MINIMAL)
#     csvwriter.writerow(["source", "target", "textdiff", "gpt_diff_changes", "gpt_diff_classifications"])
#     for i in range(len(diff_changes)):
#         diff_change = diff_changes[i]
#         diff_classification = diff_classifications[i]
#         csvwriter.writerow(diff_change[0]+[diff_classification[0]] + [diff_change[1]] +[diff_classification[1]])
fp_txt = open("./usccheck/chatgpt/diff_change_classifications.txt", "w")
fp2_txt = open("./usccheck/chatgpt/diff_change_classifications_label.txt", "w")
fp2_txt.write(TAXONOMY+"\n")
fp2_txt.write("--"*40+"\n")
df = pd.DataFrame(columns=["source", "target", "textdiff",
                  "gpt_diff_changes", "gpt_diff_classifications"])


for i in range(len(diff_changes)):
    diff_change = diff_changes[i]
    diff_classification = diff_classifications[i]
    df.loc[i] = diff_change[0]+[diff_classification[0]] + \
        [diff_change[1]] + [diff_classification[1]]
    fp_txt.write(f"index: {i}\n")
    fp2_txt.write(f"index: {i}\n")
#     fp2_txt.writelines(diff_change[0])
    fp_txt.write("gpt_diff_changes summary:\n")
    fp_txt.writelines([diff_change[1]])
    fp_txt.write("\n\ngpt_diff_classification predication:\n")
    fp_txt.writelines([diff_classification[1]])
    fp_txt.write("\ntextdiff:\n")
    fp_txt.write(diff_classification[0]+"\n")

#     fp2_txt.write("**"*40+"\n")
#     fp_txt.write("**"*40+"\n\n")
    fp2_txt.write("Your Classification (1: Yes, 0: No, default is 0):\n")
    fp2_txt.write("\n".join([cat + " (0)" for cat in cats])+"\n")
    fp2_txt.write("**"*40+"\n")

with pd.ExcelWriter(diff_change_classification_excel) as writer:
    df.to_excel(writer, index=None, header=True,
                sheet_name="ContractChangesToLabel")
