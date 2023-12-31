#!/usr/bin/env python3
from langchain.llms import Ollama

import sys
import shutil
import os

ollama = Ollama(base_url='http://localhost:11434',
model="code-review")

DEBUG_HUMAN_INPUT = True
# Get first argument
path = sys.argv[1]

exit = False
comments = []

def align_text_in_terminal(text, alignment):
    """
    Aligns text within the current terminal width either left or right.

    :param text: The text to be aligned.
    :param alignment: The alignment direction ('left' or 'right').
    :return: The aligned text as a string.
    """
    # Getting the terminal size
    columns, _ = shutil.get_terminal_size()

    if alignment.lower() == 'left':
        # Align text to the left
        aligned_text = text.ljust(columns)
    elif alignment.lower() == 'right':
        # Align text to the right
        aligned_text = text.rjust(columns)
    else:
        raise ValueError("Invalid alignment. Choose 'left' or 'right'.")

    return aligned_text

def list_files(file_path):
    global path
    return get_directory_tree(path, file_path, 2)

def get_directory_tree(root_path, dir_path, depth):
    """
    Generate a string representing the tree structure of files and directories within a given directory.

    :param root_path: The root directory from where the scan starts.
    :param dir_path: The specific directory to generate the tree structure for.
    :param depth: The depth of the tree structure to generate.
    :return: A string representing the tree structure.
    """
    tree_str = ""
    prefix = "|-- "
    if depth < 0:
        # Negative depth means no limit
        depth = float('inf')

    def _build_tree(current_path, current_depth):
        nonlocal tree_str
        if current_depth > depth:
            return
        if os.path.isdir(current_path):
            tree_str += prefix * current_depth + os.path.basename(current_path) + "/\n"
            for item in os.listdir(current_path):
                _build_tree(os.path.join(current_path, item), current_depth + 1)
        else:
            tree_str += prefix * current_depth + os.path.basename(current_path) + "\n"

    _build_tree(os.path.join(root_path, dir_path), 0)
    return tree_str


def read_file(file_path):
    global path
    reststr = ""

    file = path + "/" + file_path
    # print("Reading file:", file)
    with open(file, "r") as f:
        reststr = f.read()
    return reststr

# Append string to log file
def append_to_log(log_string):
    with open("./log.txt", "a") as f:
        f.write(log_string + "\n")

first_output = """You are in an interactive shell, with access to the source code for a project,
plase start your output with 'command ` followed by one of the following commands
 - `ls {filepath}`
 - `cat {filename}`
type 'exit' to exit. Type 'help' for help.
Here is the root file structure:
""" + list_files(".")
help_output =  "Type 'exit' to exit. Type 'command ls {filepath}' to list all files in a given path. Type 'command cat <filename>' to read a file. Type 'help' for help."
print(">>> " + first_output)
if DEBUG_HUMAN_INPUT:
    response = ""
else:
    response = ollama(first_output)

# print("<<< " + response)

while not exit:
    output = ""
    # if response == "exit":
        # exit = True
    if response.startswith("help"):
        output = help_output

    for line in response.replace("`", "").replace("  ", " ").split("\n"):
        # print("line:", line)
        if "command" in line:
            # Get first line of response
            words = line.split(" ")
            # reomve empty strings from words
            words = list(filter(None, words))
            command = words[1]
            # print("command:", command)
            # print("command:", line.split(" "))
            if "ls" in command :
                if len(words) < 3:
                    output += "\n List root:"   + "\n" +  list_files(".") + "\n"
                else:
                    # List all files in directory

                    file_path = words[2]
                    try:
                        output += "\n List: " + file_path  + "\n" +  list_files(file_path) + "\n"
                    except:
                        pass
            elif "cat" in command :
                # Read file
                filename = words[2]
                try:
                    output += "\n File: " + filename + "\n```" + read_file(filename) + "```"
                except:
                    output += "\n Was not able to read file: " + filename
        elif "comment" in line:
            # Read file
            comment = response
            comments.append(comment)
            append_to_log(comment)
            output += "\nComment added"
    # else:
    #     output = "Command not found. Type 'help' for help."

    if output == "":
        output = "What do you want to do?"

    align_text_in_terminal(output, 'right')
    # print("\n\nOUTPUT:")
    # print(">>> " + "\n>>> ".join(output.split("\n")))
    if DEBUG_HUMAN_INPUT:
        response = input(">>> ")
        response += "\r\n"
    else:
        response = ollama(output)
    # response = input(">>> ")

    # print("\n\nRESPONSE:")
    # print("<<< " + response)
    align_text_in_terminal(response, 'left')
    # Get input to freeze flow
    # input("Press Enter to continue...")
