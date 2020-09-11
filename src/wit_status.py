# Upload 173
import filecmp
import os
import sys


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


def status():
    if not is_parent_wit():
        return

    os.chdir('.wit')
    current_commit_id = get_reference_commit()
    if current_commit_id == "None":
        return
    current_commit_id, changes_to_be_committed, changes_not_staged_for_commit, untracked_files = get_status()

    text = """
    Commit id: {current_commit_id}
    Changes to be committed: {changes_to_be_committed}
    Changes not staged for commit: {changes_not_staged_for_commit}
    Untracked files: {untracked_files}
    """.format(current_commit_id=current_commit_id, changes_to_be_committed=changes_to_be_committed,
               changes_not_staged_for_commit=changes_not_staged_for_commit, untracked_files=untracked_files)
    # text = f"""Commit id: {current_commit_id}
    #         Changes to be committed: {changes_to_be_committed}
    #         Changes not staged for commit: {changes_not_staged_for_commit}
    #         Untracked files: {untracked_files}
    #         """
    print(text)
    return


if __name__ == '__main__':
    # os.chdir('C:\Users\USER\Desktop\Etztrubal')
    # status()
    if len(sys.argv) != 2:
        print("Usage: python <filename> <status>")
    elif sys.argv[1] == "status":
        status()

# C:\Users\USER\Desktop\Etztrubal> C:\Users\USER\PycharmProjects\python_course\week10\wit\wit_status.py status
