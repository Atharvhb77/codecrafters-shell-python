import sys
import shutil
import os
import shlex
import subprocess
import readline  # Import readline for tab completion
from typing import List

builtins = ["echo", "exit", "pwd", "cd", "type"]
# This will track the state of tab completions for a given prefix
tab_state = {}

def complete_builtin(text, state):
    # Initialize tab state for this prefix if not already present
    if text not in tab_state:
        tab_state[text] = {'count': 0, 'matches': []}
    
    # If we are still in the first TAB press, ring the bell
    if tab_state[text]['count'] == 0:
        # Bell on the first TAB press
        if state == 0:
            sys.stdout.write('\a')  # Ring the bell
            sys.stdout.flush()
            return None  # Don't return anything on first press, just ring the bell
        else:
            tab_state[text]['count'] = 1
    
    # Now check for the matching executables in PATH
    matches = tab_state[text]['matches']
    if not matches:
        # Get the directories in PATH
        path_dirs = os.environ.get('PATH', '').split(os.pathsep)
        
        # Loop through each directory in PATH and check for executables
        for path_dir in path_dirs:
            if os.path.isdir(path_dir):  # Ensure it's a valid directory
                # Get the list of files in the directory
                for filename in os.listdir(path_dir):
                    # Check if filename matches the prefix and is executable
                    if filename.startswith(text) and os.access(os.path.join(path_dir, filename), os.X_OK):
                        matches.append(filename)
    
    # If there are multiple matches, we return the list on the second TAB press
    if len(matches) > 1 and tab_state[text]['count'] == 1:
        # Print the matches on a new line, separated by 2 spaces
        print("\n" + "  ".join(matches))
        sys.stdout.write("$ ")
        sys.stdout.flush()
        return None
    
    # If we have only one match or it's the second TAB press, we return the matched command
    if state < len(matches):
        return matches[state] + " "  # Add space after autocompletion
    return None

# Enable tab completion for built-in commands and external executables
readline.parse_and_bind("tab: complete")
readline.set_completer(complete_builtin)

def type(arg) -> List[str]:
    output, error = "", ""
    if arg in builtins:
        output = f"{arg} is a shell builtin"
    else:
        path = shutil.which(arg)
        if path:
            output = f"{arg} is {path}"
        else:
            error = f"{arg}: not found"
    return [output, error]

def echo(command) -> List[str]:
    args = command[5:].strip()
    parsed_args = shlex.split(args)
    output = " ".join(parsed_args)
    return [output, ""]

def cd(arg) -> List[str]:
    try:
        if arg.startswith("~"):
            os.chdir(os.path.expanduser("~"))
        else:
            os.chdir(arg)
        return ["", ""]
    except:
        return ["", f"cd: {arg}: No such file or directory"]

def other(command) -> List[str]:
    cmd = shlex.split(command)
    path = shutil.which(cmd[0])
    if path:
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            return [res.stdout.rstrip(), res.stderr.rstrip()]
        except Exception as e:
            return ["", str(e)]
    else:
        return ["", f"{cmd[0]}: command not found"]

def execute(command) -> List[str]:
    cmd = shlex.split(command)
    if cmd[0] == "type":
        output, error = type(cmd[1])
    elif cmd[0] == "echo":
        output, error = echo(command)
    elif cmd[0] == "exit":
        output, error = "", ""
    elif cmd[0] == "pwd":
        output, error = os.getcwd(), ""
    elif cmd[0] == "cd":
        output, error = cd(cmd[1])
    else:
        output, error = other(command)
    return [output, error]

def main():
    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()
        command = input()

        # Reset tab_state for a new command
        global tab_state
        tab_state = {}

        redirect = True
        left = ""
        if '1>' in command:
            left, outputFile = command.split('1>')
        elif '2>' in command:
            left, outputFile = command.split('2>')
        elif '>' in command:
            left, outputFile = command.split('>')
        elif '1>>' in command or '>>' in command:  # Append redirection support
            left, outputFile = command.split('>>')
            append_mode = True
        else:
            redirect = False

        if redirect:
            left = left.strip()
            outputFile = outputFile.strip()
            output, error = execute(left)
        else:
            output, error = execute(command)

        if redirect:
            mode = "a" if ">>" in command else "w"  # Append mode if >> is used
            if '2>' in command:
                with open(outputFile, mode) as file:
                    file.write(error.strip())
                if output:
                    print(output.strip())
            else:
                with open(outputFile, mode) as file:
                    if output:
                        file.write(output.strip())
                    if error:
                        print(error.strip())
        else:
            if output:
                print(output)
            elif error:
                print(error)

        if command.startswith("exit"):
            return 0

if __name__ == "__main__":
    main()
