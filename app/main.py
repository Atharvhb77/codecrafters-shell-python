import sys
import shutil
import os
import shlex
from typing import List
import subprocess 
import readline  # Import readline for tab completion

builtins = ["type", "echo", "exit", "pwd", "cd"]
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
                    if filename.startswith(text) and os.access(os.path.join(path_dir, filename), os.X_OK):
                        matches.append(filename)
    
    # If there are multiple matches, we return the list on the second TAB press
    if len(matches) > 1 and tab_state[text]['count'] == 1:
        # Print the matches on a new line, separated by 2 spaces
        sys.stdout.write("\n" + "  ".join(matches) + "\n$ ")
        sys.stdout.flush()
        return None
    
    # If we have only one match or it's the second TAB press, we return the matched command
    if state < len(matches):
        return matches[state] + " "  # Add space after autocompletion
    return None

# Enable tab completion for built-in commands
readline.parse_and_bind("tab: complete")
readline.set_completer(complete_builtin)


def type(arg) -> List[str]:  # str[0] -> output, str[1] -> error
    output = ""
    error = ""
    if arg in builtins:
        output = f"{arg} is a shell builtin"
    else:
        path = shutil.which(arg)
        if path:
            output = f"{arg} is {path}"
        else:
            error = f"{arg}: not found"
    return [output, error]

def echo(command) -> List[str]:  # str[0] -> output, str[1] -> error
    args = command[5:].strip()
    parsed_args = shlex.split(args)
    output = " ".join(parsed_args)
    return [output, ""]

def cd(arg) -> List[str]:  # str[0] -> output, str[1] -> error
    try:
        if arg.startswith("~"):
            home = os.path.expanduser("~")
            os.chdir(home)
        else:
            os.chdir(arg)
        return ["", ""]
    except:
        return ["", f"cd: {arg}: No such file or directory"]

def other(command) -> List[str]:  # str[0] -> output, str[1] -> error
    cmd = shlex.split(command)
    path = shutil.which(cmd[0])
    if path:
        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
            )
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
        command = input().strip()

        redirect = False
        append = False  # Track if we need to append output
        left = ""
        outputFile = ""
        errorFile = ""
        stderr_redirect = False

        # Check for error redirection (2>)
        if "2>>" in command:
            left, errorFile = command.split("2>>")
            stderr_redirect = True
            append = True
            redirect = True
        elif "2>" in command:
            left, errorFile = command.split("2>")
            stderr_redirect = True
            redirect = True

        # Check for stdout redirection (>> or >)
        elif "1>>" in command or ">>" in command:  # Append output
            left, outputFile = command.split("1>>") if "1>>" in command else command.split(">>")
            append = True
            redirect = True
        elif "1>" in command or ">" in command:  # Overwrite output
            left, outputFile = command.split("1>") if "1>" in command else command.split(">")
            redirect = True

        if redirect:
            left = left.strip()
            if stderr_redirect:
                errorFile = errorFile.strip()
            else:
                outputFile = outputFile.strip()
            output, error = execute(left)
        else:
            output, error = execute(command)

        # Handle redirections
        if redirect:
            if stderr_redirect:  # Redirect stderr
                mode = "a" if append else "w"
                with open(errorFile, mode) as file:
                    if error:
                        file.write(error.strip() + "\n")  # Ensure newline
                if output:
                    print(output.strip())

            elif append:  # Append stdout
                with open(outputFile, "a") as file:
                    if output:
                        file.write(output.strip() + "\n")  # Ensure newline
                    if error:
                        print(error.strip())

            else:  # Overwrite stdout
                with open(outputFile, "w") as file:
                    if output:
                        file.write(output.strip() + "\n")
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
