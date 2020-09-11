# Upload 171
from distutils.dir_util import copy_tree

import os
import shutil
import sys


def normalize_path(path_to_copy):
    if not os.path.isabs(path_to_copy):
        path_to_copy = os.path.join(os.getcwd(), path_to_copy)
    return path_to_copy


def create_directories_path(path_to_copy):
    rel_path = os.path.relpath(path_to_copy)
    folders = []
    while not os.path.isdir(".wit"):
        folders.append(os.path.basename(os.getcwd()))
        os.chdir('..')
        if os.getcwd() == os.path.dirname(os.path.abspath(os.getcwd())):
            raise OSError(".wit directory does not exist")
    folders.reverse()
    if os.path.isdir(path_to_copy):
        folders.extend(rel_path.split("/"))
    return "/".join(folders)


def add(path_to_copy, dst="staging_area"):
    if not os.path.exists(path_to_copy):
        raise OSError("Path to copy does not exist.")

    path_to_copy = normalize_path(path_to_copy)

    directories_path = create_directories_path(path_to_copy)

    os.chdir(os.path.join(".wit", dst))
    if directories_path:
        try:
            os.makedirs(os.path.join(os.getcwd(), directories_path))
        except WindowsError:
            pass
        os.chdir(directories_path)
    current_directory = os.getcwd()
    if os.path.isfile(path_to_copy):
        shutil.copy(path_to_copy, current_directory)
    else:
        copy_tree(path_to_copy, current_directory)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python <filename> <add> <path/to/copy>")
    elif sys.argv[1] == "add":
        path = sys.argv[2]
        add(path)

# C:\Users\USER\Desktop\Etztrubal\lms>C:\Users\USER\PycharmProjects\python_course\week10\wit\wit_add.py add extractors
