# Upload 174
import filecmp
import fileinput
import os
import shutil
import sys


# from wit_commit import update_references, is_parent_wit, get_reference_commit
# from wit_status import get_status


def report(diff):
    changes_not_staged_for_commit = []
    changes_to_be_committed = []
    untracked_files = []
    if diff.right_only:
        diff.right_only.sort()
        for rd in diff.right_only:
            # path = f"{diff.right}\{rd}"
            path = r"{d}\{rd}".format(d=diff.right, rd=rd)
            changes_to_be_committed.append(path)
        # print "Changes to be committed:", diff.right, ':', diff.right_only,

    if diff.diff_files:
        diff.diff_files.sort()
        changes_not_staged_for_commit = diff.diff_files
        # print "Changes not staged for commit:", diff.diff_files

    if diff.left_only:
        diff.left_only.sort()
        for ld in diff.left_only:
            if ld != ".wit":
                # path = f"{diff.left}\{ld}"
                path = r"{d}\{ld}".format(d=diff.left, ld=ld)
                untracked_files.append(path)
        # print "Untracked files: ", diff.left, ':', diff.left_only

    return changes_to_be_committed, changes_not_staged_for_commit, untracked_files


def get_diff(diff):
    changes_to_be_committed, changes_not_staged_for_commit, untracked_files = report(diff)

    for sd in diff.subdirs.itervalues():
        new_changes_to_be_committed, new_changes_not_staged_for_commit, new_untracked_files = get_diff(sd)

        changes_to_be_committed.extend(new_changes_to_be_committed)
        changes_not_staged_for_commit.extend(new_changes_not_staged_for_commit)
        untracked_files.extend(new_untracked_files)

    return changes_to_be_committed, changes_not_staged_for_commit, untracked_files


def get_status(compare_b="staging_area"):
    current_commit_id = get_reference_commit()
    last_image_path = "images\{}".format(current_commit_id)

    diff = filecmp.dircmp(last_image_path, compare_b)
    changes_to_be_committed, content_changes_to_be_committed, _ = get_diff(diff)
    changes_to_be_committed.extend(content_changes_to_be_committed)

    diff = filecmp.dircmp("..", compare_b)
    _, changes_not_staged_for_commit, untracked_files = get_diff(diff)

    return current_commit_id, changes_to_be_committed, changes_not_staged_for_commit, untracked_files


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
    return branch_line.split("=")[-1].strip("\r\n")


def update_references(head_commit_id):
    current_head_commit_id = get_reference_commit()
    current_master_commit_id = get_reference_commit(is_master=True)
    activated_branch = get_activated_branch()

    master_commit_id = current_master_commit_id
    if current_head_commit_id == current_master_commit_id and activated_branch == "master":
        master_commit_id = head_commit_id

    branch_commit_id = get_branch_commit_id(activated_branch)
    if activated_branch != "master" and activated_branch and branch_commit_id == current_head_commit_id:
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


def update_branch_reference(activated_branch, branch_commit_id):
    for line in fileinput.input("references.txt", inplace=True):
        if activated_branch in line:
            print("{activated_branch}={branch_commit_id}".format(activated_branch=activated_branch,
                                                                 branch_commit_id=branch_commit_id))
        else:
            print(line)


def get_activated_branch():
    if os.path.exists("activated.txt"):
        with open("activated.txt", "rb") as f:
            return f.readline()


def is_parent_wit():
    while not os.path.isdir(".wit"):
        os.chdir('..')
        if os.getcwd() == os.path.dirname(os.path.abspath(os.getcwd())):
            return False
    return True


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


def copy(root_src_dir, root_dst_dir):
    for src_dir, _, files in os.walk(root_src_dir):
        dst_dir = src_dir.replace(root_src_dir, root_dst_dir, 1)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        for file_ in files:
            src_file = os.path.join(src_dir, file_)
            dst_file = os.path.join(dst_dir, file_)
            if os.path.exists(dst_file):
                os.remove(dst_file)
            shutil.copy(src_file, dst_dir)


def checkout(commit_id):
    if not is_parent_wit():
        return

    _, changes_to_be_committed, changes_not_staged_for_commit, _ = get_status()

    if changes_not_staged_for_commit:
        print("There are changes which are not staged for commit. Exit")
        return
    if changes_to_be_committed:
        print("There are changes to be committed. Exit")
        return

    branch_name = ""
    if is_branch_exists(commit_id):
        branch_name = commit_id
        commit_id = get_branch_commit_id(commit_id)
    update_activated_branch(branch_name)

    os.chdir("..")
    path = r".wit\images\{commit_id}".format(commit_id=commit_id)
    if not os.path.exists(path):
        print("Commit or branch {commit_id} does not exist!".format(commit_id=commit_id))
        return

    copy(path, ".")

    shutil.rmtree(".wit\staging_area")
    copy(path, ".wit\staging_area")

    os.chdir(".wit")
    update_references(head_commit_id=commit_id)


if __name__ == '__main__':
    # os.chdir('C:\Users\USER\Desktop\Etztrubal')
    # checkout("41dbfcc26916b3f2201db233fb91db9c3b28ad5e")
    if len(sys.argv) != 3:
        print("Usage: python <filename> <checkout> commit_id")
    elif sys.argv[1] == "checkout":
        commit_id = sys.argv[2]
        checkout(commit_id)

# C:\Users\USER\Desktop\Etztrubal>C:\Users\USER\PycharmProjects\python_course\week10\wit\wit_checkout.py checkout 23535
