# Upload 177
import os
import shutil
import sys

from wit_commit import commit
from wit_checkout import checkout, copy
from wit_status import get_status
from wit_checkout import update_activated_branch


def _get_commit_from_line(line):
    return line.split("=")[-1].strip("\r\n")


def get_reference_commit(is_master=False):
    parent_commit_id = "{}".format(None)
    if os.path.exists("references.txt"):
        with open("references.txt", "rb") as f:
            line = f.readline()
            if is_master:
                for line in f:
                    if "master" in line:
                        break
            parent_commit_id = _get_commit_from_line(line)
    return parent_commit_id


def get_activated_branch():
    if os.path.exists("activated.txt"):
        with open("activated.txt", "rb") as f:
            return f.readline()


def get_branch_commit_id(branch):
    branch_line = ""
    if not branch:
        return branch_line
    if os.path.exists("references.txt"):
        with open("references.txt", "rb") as f:
            for line in f:
                if branch in line:
                    branch_line = line
                    break
    return _get_commit_from_line(branch_line)


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


def is_parent_wit():
    while not os.path.isdir(".wit"):
        os.chdir('..')
        if os.getcwd() == os.path.dirname(os.path.abspath(os.getcwd())):
            return False
    return True


def find_common_commit(head_commit_id, branch_commit_id):
    head_tree = get_commit_tree(head_commit_id, {})
    branch_tree = get_commit_tree(branch_commit_id, {})
    first = next((a for a in head_tree.keys() if a in branch_tree), None)
    return first


def copy_diff_files(src_files, dst):
    for file_name in src_files:
        if os.path.isfile(file_name):
            shutil.copy(file_name, dst)


def merge(branch_name):
    if not is_parent_wit():
        return

    os.chdir(".wit")
    head_commit_id = get_reference_commit()
    branch_commit_id = get_branch_commit_id(branch_name)
    if head_commit_id == branch_commit_id:
        print("Nothing to merge. Exit")
        return
    activated_branch = get_activated_branch()
    common_commit = find_common_commit(head_commit_id, branch_commit_id)
    checkout(common_commit)

    head_path = "images\{head_commit_id}".format(head_commit_id=head_commit_id)
    branch_path = "images\{branch_commit_id}".format(branch_commit_id=branch_commit_id)

    _, head_diff_files, _, _ = get_status(compare_b=head_path)
    _, branch_diff_files, _, _ = get_status(compare_b=branch_path)

    wit_dir = os.getcwd()
    temp_staging_dir = os.path.join(wit_dir, 'temp_staging_area')
    staging_dir = os.path.join(wit_dir, 'staging_area')
    os.mkdir(temp_staging_dir)

    copy(staging_dir, temp_staging_dir)
    copy_diff_files(head_diff_files, temp_staging_dir)
    copy_diff_files(branch_diff_files, temp_staging_dir)

    checkout(head_commit_id)
    shutil.rmtree(staging_dir)
    os.mkdir(staging_dir)
    copy(temp_staging_dir, staging_dir)

    if activated_branch:
        update_activated_branch(activated_branch)
    commit("merge head with {branch_name}".format(branch_name=branch_name), branch_commit_id)

    shutil.rmtree(temp_staging_dir)


if __name__ == '__main__':
    # os.chdir('C:\Users\USER\Desktop\Etztrubal')
    # merge("meow")
    if len(sys.argv) != 3:
        print("Usage: python <filename> <merge> BRANCH_NAME")
    elif sys.argv[1] == "merge":
        branch_name = sys.argv[2]
        merge(branch_name)
