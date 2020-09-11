# Upload 170
import os
import sys


def init(path=None):
    if path:
        os.chdir(path)
    current_directory = os.getcwd()
    final_directory = os.path.join(current_directory, '.wit')
    folders = (final_directory, os.path.join(final_directory, 'images'), os.path.join(final_directory, 'staging_area'))
    for folder_path in folders:
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)

    os.chdir(".wit")
    with open("activated.txt", "wb") as f:
        f.write("master")


if __name__ == '__main__':
    if len(sys.argv) > 3 or len(sys.argv) < 2:
        print("Usage: python <filename> <init> [path/to/cwd]")
    elif sys.argv[1] == "init":
        path = sys.argv[2] if len(sys.argv) == 3 else None
        init(path)

# C:\Users\USER\PycharmProjects\python_course\week10\wit\wit_init.py init "C:\Users\USER\Desktop\Etztrubal"
