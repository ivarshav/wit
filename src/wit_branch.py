# Upload 176
import os
import sys


def is_branch_exists(name):
    if os.path.exists("references.txt"):
        with open("references.txt", "rb") as f:
            for line in f:
                if "{name}=".format(name=name) in line:
                    return True
    return False


def update_activated_branch(name):
    activated_branch = ""
    if is_branch_exists(name):
        activated_branch = name
    with open("activated.txt", "wb") as f:
        f.write(activated_branch)


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


def add_branch_reference(name):
    head_commit_id = get_reference_commit()
    text = "{name}={head_commit_id}".format(name=name, head_commit_id=head_commit_id)
    with open("references.txt", "a") as f:
        f.write(text)


def branch(name):
    if not is_parent_wit():
        return
    os.chdir(".wit")
    add_branch_reference(name)
    update_activated_branch(name)
    print("Branch named {name} was created".format(name=name))


if __name__ == '__main__':
    # os.chdir('C:\Users\USER\Desktop\Etztrubal')
    # branch("git")
    if len(sys.argv) != 3:
        print("Usage: python <filename> <branch> NAME")
    elif sys.argv[1] == "branch":
        name = sys.argv[2]
        branch(name)
