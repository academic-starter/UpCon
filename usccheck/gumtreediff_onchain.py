import os
import json
import glob
import re
import random
from dataclasses import dataclass
from typing import List
import multiprocessing
import itertools
import numpy as np
import pandas as pd


identifer_pattern = re.compile("\w+")
code_ranges = re.compile(".*\[([0-9]+)\,([0-9]+)\]$")

workdir = "usccheck/OnchainContractData/proxy_implementations/category/ethereum_mainnet/multi_non_zero_impl/ethereum_mainnet"
gumtree_diff = "usccheck/OnchainContractData/gumtreediff/ethereum_mainnet"


def diff(a, b, implementation_dir):
    resultsA = glob.glob(os.path.join(implementation_dir, a, "**", "*.sol"))
    resultsB = glob.glob(os.path.join(implementation_dir, b, "**", "*.sol"))
    base_dir = os.path.basename(os.path.dirname(implementation_dir))

    if len(resultsA) == 1 and len(resultsB) == 1:
        if not os.path.exists(os.path.join(gumtree_diff, base_dir)):
            os.makedirs(os.path.join(gumtree_diff, base_dir))
        diff_file_name = "{0}-{1}".format(a, b)
        diff_file = os.path.join(gumtree_diff, base_dir, diff_file_name)
        cmd = "gumtree textdiff %s %s -f JSON -o %s.json" % (
            resultsA[0], resultsB[0], diff_file)
        print(cmd)
        os.system(cmd)
        cmd = "gumtree htmldiff %s %s -o %s.html" % (
            resultsA[0], resultsB[0], diff_file)
        print(cmd)
        os.system(cmd)
    else:
        diff_dir = os.path.join(gumtree_diff, base_dir, "{0}-{1}".format(a, b))
        if not os.path.exists(diff_dir):
            os.makedirs(diff_dir)
        for fileA in resultsA:
            for fileB in resultsB:
                # same file name means they belong to the same contract
                # FIXME: this may not be correct
                if os.path.basename(fileA) == os.path.basename(fileB):
                    diff_file = os.path.join(diff_dir, os.path.basename(fileA))
                    cmd = "gumtree textdiff %s %s -f JSON -o %s.json" % (
                        fileA, fileB, diff_file)
                    print(cmd)
                    os.system(cmd)
                    cmd = "gumtree htmldiff %s %s -o %s.html" % (
                        fileA, fileB, diff_file)
                    print(cmd)
                    os.system(cmd)


def gen_diff():
    a_b_impls = []
    for proxy in os.listdir(workdir):
        # print("Proxy: ", os.path.join(workdir, proxy))
        implementation_dir = os.path.join(workdir, proxy, "implementation")
        implementation_indice = sorted(
            map(int, os.listdir(implementation_dir)))
        for i in range(len(implementation_indice)-1):
            a = implementation_indice[i]
            b = implementation_indice[i+1]
            a_b_impls.append([str(a), str(b), implementation_dir])
            # diff(str(a), str(b), implementation_dir)

    with multiprocessing.Pool(28) as pool:
        pool.starmap(diff, a_b_impls)


class Action:
    action: str
    tree: str
    parent: str
    label: str
    at: int
    children: list

    def __init__(self, action, tree, parent=None, label=None, at=None) -> None:
        self.action = action
        self.tree = tree
        self.parent = parent
        self.at = at
        self.children: ActionTreeLink = ActionTreeLink([])

    def tree_code_range(self):
        m = code_ranges.match(self.tree)
        left, right = m.group(1), m.group(2)
        return int(left), int(right)

    def parent_code_range(self):
        m = code_ranges.match(self.parent)
        left, right = m.group(1), m.group(2)
        return int(left), int(right)

    def is_child(self, other_action):
        if self.parent is None:
            pleft, pright = self.tree_code_range()
        else:
            pleft, pright = self.parent_code_range()
        other_tleft, other_tright = other_action.tree_code_range()
        return other_tleft <= pleft and pright <= other_tright

    def test_and_appendChild(self, other_action):
        if other_action.is_child(self):
            if len(self.children.actions) > 0:
                for child in self.children.actions:
                    if child.test_and_appendChild(other_action):
                        return True
            self.children.actions.append(other_action)
            self.children.build_action_tree()
            return True
        else:
            return False


class ActionTreeLink(object):
    actions: List[Action]

    def __init__(self, action_array):
        self.actions = list()
        for action in action_array:
            self.actions.append(Action(**action))

    def build_action_tree(self):
        size = 0
        while size != len(self.actions):
            size = len(self.actions)
            rm = -1
            for i in range(size):
                for j in range(size):
                    if i == j:
                        continue
                    ret = self.actions[i].test_and_appendChild(self.actions[j])
                    if ret == True:
                        rm = j
                        break
                if rm != -1:
                    break
            if rm != -1:
                self.actions.pop(rm)
        return


statistics = {}


def analyze_per_diff(diff_file):
    global statistics
    if not diff_file.endswith(".json"):
        return []
    implementations = os.path.basename(diff_file).split(".json")[0].split("-")
    if len(implementations) == 1:
        implementations = os.path.basename(os.path.dirname(
            diff_file)).split("-")
    a, b = implementations[0], implementations[1]
    if int(b) != int(a)+1:
        return []

    print(diff_file.replace(".json", ".html"))
    with open(diff_file) as fp:
        diff_json = json.load(fp)

    treeLink = ActionTreeLink(diff_json["actions"])
    treeLink.build_action_tree()

    # lock = multiprocessing.Lock()

    results = []
    for item in treeLink.actions:
        syntax_type = item.tree.split(":")[0].split("[")[0]

        if item.parent is not None:
            syntax_type = item.parent.split(":")[0].split(
                "[")[0].strip() + "->" + syntax_type

        key = (item.action, syntax_type.strip())
        results.append([key, diff_file.replace(".json", ".html")])
        # lock.acquire()
        # statistics["--".join(key)] = statistics.get(key, list()) + [(treeLink.actions.index(
        # item), diff_file.replace(".json", ".html"))]
        # lock.release()
    return results


def analysis_diff():
    global statistics
    statistic_file = os.path.join(
        gumtree_diff, "../", "gumtreediff_ethereum_mainnet_classification.json")
    if os.path.exists(statistic_file):
        statistics = json.load(open(statistic_file))
    else:
        Parallel_Flag = True
        if not Parallel_Flag:
            proxies = os.listdir(gumtree_diff)
            statistics = {}
            for proxy in proxies:
                diffs = glob.glob(os.path.join(
                    gumtree_diff, proxy, "**", "*.json"), recursive=True)
                for diff in diffs:
                    if not diff.endswith(".json"):
                        continue
                    implementations = os.path.basename(
                        diff).split(".json")[0].split("-")
                    if len(implementations) == 1:
                        implementations = os.path.basename(os.path.dirname(
                            diff)).split("-")
                    a, b = implementations[0], implementations[1]
                    if int(b) != int(a)+1:
                        continue
                    print(diff.replace(".json", ".html"))
                    with open(diff) as fp:
                        diff_json = json.load(fp)

                    treeLink = ActionTreeLink(diff_json["actions"])
                    treeLink.build_action_tree()

                    for item in treeLink.actions:
                        syntax_type = item.tree.split(":")[0].split("[")[0]

                        while item.parent is not None:
                            syntax_type = item.parent.split(":")[0].split(
                                "[")[0].strip() + "->" + syntax_type
                            item = item.parent

                        key = (item.action, syntax_type.strip())
                        statistics["--".join(key)] = statistics.get("--".join(key), list()) + [
                            diff.replace(".json", ".html")]
        else:
            proxies = os.listdir(gumtree_diff)
            all_diffs = []
            for proxy in proxies:
                diffs = glob.glob(os.path.join(
                    gumtree_diff, proxy, "**", "*.json"), recursive=True)
                all_diffs.extend(diffs)
            with multiprocessing.Pool(28) as pool:
                map_results = pool.map(analyze_per_diff, all_diffs)
                for result in itertools.chain.from_iterable(map_results):
                    key, src_diff = result[0], result[1]
                    statistics["--".join(key)] = statistics.get(
                        "--".join(key), list()) + [src_diff]
        json.dump(statistics, open(statistic_file, "w"), indent=4)

    print("Summary of Gumtree Diff:")
    print("**"*10)
    print("Action\t Count")
    for action in statistics:
        print("{0} \t {1}".format(action, len(statistics[action])))
    print("Overall {0} types of actions".format(len(statistics)))

    print("**"*10)
    print("Action\t Count of updates")
    cnt = 0
    for action in statistics:
        if action.split("--")[0].startswith("update"):
            print("{0} \t {1}".format(action, len(statistics[action])))
            cnt += 1
    print("Overall {0} types of update actions".format(cnt))

    # category = [
    #     "comment",
    #     "solidity",
    #     "library",
    #     "interface",
    #     "contract",
    #     "state_variable_declaration",
    #     "constructor_definition",
    #     "modifier_definition",
    #     "fallback_receive_definition",
    #     "event",
    #     "error",
    #     "function_definition",
    #     "modifier_invocation",
    #     "assembly_statement",
    #     "expression_statement",
    #     "if_statement",
    #     "for_statement",
    #     "while_statement",
    #     "revert_statement",
    #     "try_statement",
    #     "emit_statement",
    #     "return_statement",
    #     "visibility",
    #     "public",
    #     "private",
    #     "external",
    #     "internal",
    #     "state_mutability",
    #     "pure",
    #     "view",
    #     "parameter",
    #     "calldata",
    #     "memory",
    #     "expression",
    #     "argument",
    #     "literal",
    #     "identifier"
    # ]
    # category_results = {}
    # for action in statistics:
    #     syntax_type = action.split("--")[1].split("->")[-1].strip()
    #     # matched = list(filter(lambda item: syntax_type == item or syntax_type.find(
    #     # item+"_") != -1 or syntax_type.find("_"+item) != -1, category))
    #     matched = list(filter(lambda item: syntax_type == item or syntax_type.find(
    #         item) != -1 or syntax_type.find("_"+item) != -1, category))
    #     for item in matched:
    #         category_results[item] = category_results.get(
    #             item, list()) + [(action, len(statistics[action]))]

    #     if len(matched) == 0:
    #         print("uncategorized {0} \t {1}".format(
    #             action, len(statistics[action])))

    # print("categorized results:")
    # print("**"*10)
    # array_list = []
    # index = []
    # columns = ["insert", "delete", "update", "move"]
    # for cat_item in category:
    #     if cat_item in category_results:
    #         print("{0} \t {1}\n".format(cat_item, category_results[cat_item]))
    #         index.append(cat_item)
    #         array_list.append([sum(map(lambda x: x[1], filter(lambda x: x[0].find(
    #             column) != -1,  category_results[cat_item]))) for column in columns])

    # data = np.array(array_list)

    # df = pd.DataFrame(data=data, index=index, columns=columns)
    # df.to_csv(os.path.join(
    #     gumtree_diff, "../", "gumtreediff_ethereum_mainnet_main_classification.csv"))

    # concept
    asts = {
        "contract": ["library_declaration", "interface_declaration", "contract_declaration"],
        "state variable": ["state_variable_declaration"],
        "event": ["event_declaration", "event_definition"],
        "modifier": ["modifier_definition"],
        "function": ["constructor_definition", "fallback_receive_definition", "function_definition"],
        "parameter": ["parameter"],
        "modifier invocation": ["modifier_invocation"],
        "assembly statement": ["assembly_statement"],
        "expression statement": ["expression_statement"],
        "if statement": ["if_statement"],
        "for statement": ["for_statement"],
        "while statement": ["while_statement"],
        "revert statement": ["revert_statement"],
        "try statement": ["try_statement"],
        "emit statement": ["emit_statement"],
        "return statement": ["return_statement"]
    }

    category_results = {}
    for action in statistics:
        macthed = False
        pure_action = action.split("--")[0].split("-")[0]
        for ast in asts:
            astComponents = asts[ast]
            for astComponent in astComponents:
                if action.find(astComponent) != -1:
                    if action.endswith(astComponent) is True:
                        category_results[ast] = category_results.get(
                            ast, list()) + [(pure_action, action, len(statistics[action]))]
                        macthed = True
                    else:
                        if not any([action.endswith(delimeter) for delimeter in [")", "(", ",", ":"]]):
                            category_results[ast] = category_results.get(
                                ast, list()) + [("update", action, len(statistics[action]))]
                            macthed = True

        if not macthed:
            print("uncategorized {0} count: \t {1}".format(
                action, len(statistics[action])))

    print("categorized results:")
    print("**"*10)
    array_list = []
    index = []
    columns = ["insert", "delete", "update", "move"]
    for cat_item in asts:
        if cat_item in category_results:
            print("{0} \t {1}\n".format(cat_item, category_results[cat_item]))
            index.append(cat_item)
            array_list.append(
                [sum(map(lambda x: x[-1], filter(lambda x: x[0].find(
                 column) != -1,  category_results[cat_item]))) for column in columns])

    data = np.array(array_list)

    df = pd.DataFrame(data=data, index=index, columns=columns)
    df.to_csv(os.path.join(
        gumtree_diff, "../", "gumtreediff_ethereum_mainnet_main_classification_refined.csv"))


def analysis_project_diff():
    global statistics
    project_proxys = json.load(open(
        "usccheck/OnchainContractData/proxy_implementations/etherscan_mainnet.project.multi_impls.statistics.json"))
    projects = json.load(open("usccheck/OnchainContractData/ads_project.json"))

    statistic_file = os.path.join(
        gumtree_diff, "../", "gumtreediff_ethereum_mainnet_classification.json")
    if os.path.exists(statistic_file):
        statistics = json.load(open(statistic_file))
    else:
        assert False, "Couldn't open the file for reading"

    print("Summary of Gumtree Diff:")
    print("**"*10)
    print("Action\t Count")
    for action in statistics:
        print("{0} \t {1}".format(action, len(statistics[action])))
    print("Overall {0} types of actions".format(len(statistics)))

    print("**"*10)
    print("Action\t Count")
    cnt = 0
    for action in statistics:
        if action.split("--")[0].startswith("update"):
            print("{0} \t {1}".format(action, len(statistics[action])))
            cnt += 1
    print("Overall {0} types of update actions".format(cnt))

    category = [
        "comment",
        "solidity",
        "library",
        "interface",
        "contract",
        "state_variable_declaration",
        "constructor_definition",
        "modifier_definition",
        "fallback_receive_definition",
        "event",
        "error",
        "function_definition",
        "modifier_invocation",
        "variable_declaration_statement",
        "block_statement",
        "assembly_statement",
        "expression_statement",
        "if_statement",
        "for_statement",
        "while_statement",
        "revert_statement",
        "try_statement",
        "emit_statement",
        "return_statement",
        "visibility",
        "public",
        "private",
        "external",
        "internal",
        "state_mutability",
        "pure",
        "view",
        "parameter",
        "calldata",
        "memory",
        "expression",
        "argument",
        "literal",
        "identifier"
    ]

    category_results = {}
    for action in statistics:
        syntax_type = action.split("--")[1].split("->")[-1].strip()
        matched = list(filter(lambda item: syntax_type == item or syntax_type.find(
            item+"_") != -1 or syntax_type.find("_"+item) != -1, category))
        for item in matched:
            category_results[item] = category_results.get(
                item, list()) + [[action, statistics[action]]]

        if len(matched) == 0:
            print("uncategorized {0} \t {1}".format(
                action, len(statistics[action])))

    print("categorized results across projects:")
    print("**"*10)
    array_list = []
    index = []
    columns = category
    for project in project_proxys:
        project_id = project["id"]
        project_name = list(map(lambda x: x["name"], filter(
            lambda x: x["id"] == project_id, projects)))[0]
        contract_addresses = list(
            filter(lambda x: x != "EOF", project["proxy_impls"]))
        index.append(project_name)
        array_list.append([sum(map(lambda x: len(list(x[1])), map(lambda x: [x[0], filter(lambda y: any(map(
            lambda address: address.lower() in y.lower(), contract_addresses)), x[1])],  category_results[cat_item]))) for cat_item in category])

    data = np.array(array_list)

    df = pd.DataFrame(data=data, index=index, columns=columns)
    df.to_csv(os.path.join(
        gumtree_diff, "../", "gumtreediff_ethereum_mainnet_main_project_classification.csv"))


def sample_100cases():
    proxies = os.listdir(gumtree_diff)
    all_diffs = []
    for proxy in proxies:
        diffs = glob.glob(os.path.join(gumtree_diff, proxy,
                          "**", "*.html"), recursive=True)
        all_diffs.extend(diffs)
    print("Overall {} diff pairs".format(len(all_diffs)))
    sampled_diffs = random.sample(all_diffs, 100)
    json.dump(sampled_diffs, open(os.path.join(gumtree_diff,
              "../", "sampled_ethereum_mainnet.json"), "w"))


if __name__ == "__main__":
    # gen_diff()
    analysis_diff()
    # analysis_project_diff()
    # sample_100cases()
