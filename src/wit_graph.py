# Upload 175
import os
import sys

from graphviz import Digraph


# from week10.wit import is_parent_wit, get_reference_commit


def get_reference_commit(is_master=False):
    parent_commit_id = "{}".format(None)
    if os.path.exists("references.txt"):
        with open("references.txt", "rb") as f:
            line = f.readline()
            if is_master:
                for line in f:
                    if "master" in line:
                        break
            parent_commit_id = line.split("=")[-1].strip("\r\n")
    return parent_commit_id


def is_parent_wit():
    while not os.path.isdir(".wit"):
        os.chdir('..')
        if os.getcwd() == os.path.dirname(os.path.abspath(os.getcwd())):
            return False
    return True


def _get_commit_from_line(line):
    return line.split("=")[-1].strip("\r\n")


def get_parent_commit(commit_id):
    parent_commit_id = [None]
    commit_file = "images\{commit_id}.txt".format(commit_id=commit_id)
    # commit_file = f"{commit_id}.txt"
    if os.path.exists(commit_file):
        with open(commit_file, "rb") as f:
            line = f.readline()
            parent_commit_id = _get_commit_from_line(line)
            parent_commit_id = [None] if parent_commit_id == "None" else parent_commit_id.split(",")
    return parent_commit_id


def get_commit_tree(commit_id, node_list=None):
    if commit_id is None:
        return node_list
    parent_commit = get_parent_commit(commit_id)
    node_list[commit_id] = parent_commit
    if parent_commit is None:
        return node_list
    for commit in parent_commit:
        node_list = get_commit_tree(commit, node_list)
    return node_list


def commits_to_references():
    references = {}
    if os.path.exists("references.txt"):
        with open("references.txt", "rb") as f:
            for line in f:
                if "=" not in line:
                    continue
                branch, commit_id = line.strip("\r\n").split("=")
                value = references.get(commit_id, [])
                value.append(branch)
                references[commit_id] = value
    return references


def graph():
    if not is_parent_wit():
        return
    os.chdir('.wit')
    current_commit_id = get_reference_commit()

    commits_graph = get_commit_tree(current_commit_id, node_list={})

    references = commits_to_references()

    g = Digraph('G')
    g.attr('node', shape='circle')
    g.attr(rankdir='RL')
    for commit, values in commits_graph.items():
        index = commit[:6]
        g.node(index, commit[:6])
        for parent in values:
            if parent:
                g.edge(index, parent[:6])
        if references.get(commit):
            labels = references[commit]
            fake_node = str(index * 10)
            g.node(fake_node, "", shape="none")
            for label in labels:
                g.edge(fake_node, index, label=label)

    print(g.source)
    # g.view('graph.png')


if __name__ == '__main__':
    # os.chdir('C:\Users\USER\Desktop\Etztrubal')
    # graph()
    if len(sys.argv) != 2:
        print("Usage: python <filename> <graph>")
    elif sys.argv[1] == "graph":
        graph()

# C:\Users\USER\Desktop\Etztrubal>C:\Users\USER\PycharmProjects\python_course\week10\wit\wit_graph.py graph
