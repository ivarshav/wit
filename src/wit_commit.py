# Upload 172
from datetime import datetime
from distutils.dir_util import copy_tree

import fileinput
import os
import random
import string
import sys


from wit_status import get_status


def generate_commit_directory(length=40):
    return ''.join((random.choice('abcdef' + string.digits) for _ in range(length)))


def is_parent_wit():
    while not os.path.isdir(".wit"):
        os.chdir('..')
        if os.getcwd() == os.path.dirname(os.path.abspath(os.getcwd())):
            return False
    return True


def create_commit_file(commit_id, msg, branch_commit=None):
    parent_commit_id = get_reference_commit()
    if branch_commit:
        parent_commit_id += ",{branch_commit}".format(branch_commit=branch_commit)

    time = datetime.now().strftime("%a %b %d %X %Y %z")
    text = "parent={parent_commit_id}\ndate={time}\nmessage={msg}".format(parent_commit_id=parent_commit_id, time=time,
                                                                          msg=msg)
    # text = f"parent={parent_commit_id}\ndate={time}\nmessage={msg}"
    with open("images\{}.txt".format(commit_id), "wb") as f:
        f.write(text)


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


def update_references(head_commit_id):
    current_head_commit_id = get_reference_commit()
    current_master_commit_id = get_reference_commit(is_master=True)
    activated_branch = get_activated_branch()

    master_commit_id = current_master_commit_id
    if current_head_commit_id == current_master_commit_id and activated_branch == "master":
        master_commit_id = head_commit_id

    branch_commit_id = get_branch_commit_id(activated_branch)
    if activated_branch and activated_branch != "master" and branch_commit_id == current_head_commit_id:
        branch_commit_id = head_commit_id
        update_branch_reference(activated_branch, branch_commit_id)

    if not os.path.exists("references.txt"):
        text = "HEAD={head_commit_id}\nmaster={master_commit_id}\n".format(
            head_commit_id=head_commit_id, master_commit_id=master_commit_id)
        # text = f"HEAD={head_commit_id}\nmaster={master_commit_id}\n{name}={head_commit_id}"
        with open("references.txt", "wb") as f:
            f.write(text)
    else:
        for line in fileinput.input("references.txt", inplace=True):
            if 'HEAD' in line:
                print("HEAD={head_commit_id}".format(
                    head_commit_id=head_commit_id))
            elif 'master' in line:
                print("master={master_commit_id}".format(
                    master_commit_id=master_commit_id))
            else:
                print(line)


def get_activated_branch():
    if os.path.exists("activated.txt"):
        with open("activated.txt", "rb") as f:
            return f.readline()


def get_branch_commit_id(branch):
    branch_line = ""
    if os.path.exists("references.txt"):
        with open("references.txt", "rb") as f:
            for line in f:
                if branch in line:
                    branch_line = line
                    break
    return branch_line.split("=")[-1].strip("\r\n")


def update_branch_reference(activated_branch, branch_commit_id):
    for line in fileinput.input("references.txt", inplace=True):
        if activated_branch in line:
            print("{activated_branch}={branch_commit_id}".format(activated_branch=activated_branch,
                                                                 branch_commit_id=branch_commit_id))
        else:
            print(line)


def commit(msg, branch_commit=None):
    if not is_parent_wit():
        return
    cwd = os.getcwd()
    os.chdir(".wit")
    current_commit_id = get_reference_commit()
    if current_commit_id != "None" and not get_status()[1]:
        print("Noting to commit. Exit")
        return

    os.chdir(cwd)
    os.chdir('.wit/images')
    commit_id = generate_commit_directory()
    if not os.path.exists(commit_id):
        os.mkdir(commit_id)

    os.chdir('..')
    wit_dir = os.getcwd()
    staging_dir = os.path.join(wit_dir, 'staging_area')
    commit_dir = os.path.join(wit_dir, 'images\{}'.format(commit_id))
    copy_tree(staging_dir, commit_dir)

    create_commit_file(commit_id, msg, branch_commit)

    update_references(commit_id)
    print("Commit {commit_id} created.".format(commit_id=commit_id))
    # print(f"Commit {commit_id} created.")


if __name__ == '__main__':
    # os.chdir('C:\Users\USER\Desktop\Etztrubal')
    # commit("hey")
    if len(sys.argv) != 3:
        print("Usage: python <filename> <commit> MESSAGE")
    elif sys.argv[1] == "commit":
        message = sys.argv[2]
        commit(message)

# C:\Users\USER\Desktop\Etztrubal>C:\Users\USER\PycharmProjects\python_course\week10\wit\wit_commit.py commit hello
