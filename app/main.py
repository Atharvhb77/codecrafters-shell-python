import sys
import shutil
import os
import shlex
import subprocess
import readline  # Import readline for tab completion
from typing import List, Final, Dict
import pathlib

# List of built-in commands
SHELL_BUILTINS: Final[List[str]] = ["echo", "exit", "pwd", "cd", "type"]

# Dictionary to store programs in PATH
PROGRAMS_IN_PATH: Dict[str, pathlib.Path] = {}

def parse_programs_in_path(path: str, programs: Dict[str, pathlib.Path]) -> None:
    """Parse executables in the given PATH directory and add them to the programs dictionary."""
    if os.path.isdir(path):
        try:
            for filename in os.listdir(path):
                filepath = os.path.join(path, filename)
                if os.access(filepath, os.X_OK) and not os.path.isdir(filepath):
                    programs[filename] = pathlib.Path(filepath)
        except PermissionError:
            pass

# Populate PROGRAMS_IN_PATH with executables from PATH
for path_dir in os.environ.get("PATH", "").split(os.pathsep):
    parse_programs_in_path(path_dir, PROGRAMS_IN_PATH)

# List of all completions (built-ins + programs in PATH)
COMPLETIONS: Final[List[str]] = [*SHELL_BUILTINS, *PROGRAMS_IN_PATH.keys()]

def display_matches(substitution, matches, longest_match_length):
    """Display matches for tab completion."""
    print()
    if matches:
        print(" ".join(matches))
    print("$ " + substitution, end="")

def complete(text: str, state: int) -> str | None:
    """Handle tab completion for commands."""
    matches = [s for s in COMPLETIONS if s.startswith(text)]
    if state < len(matches):
        return matches[state] + " "  # Append space after autocompletion
    return None

# Enable tab completion for built-in commands and external executables
readline.set_completion_display_matches_hook(display_matches)
readline.parse_and_bind("tab: complete")
readline.set_completer(complete)

def type(arg: str) -> List[str]:
    """Handle the 'type' built-in command."""
    output, error = "", ""
    if arg in SHELL_BUILTINS:
        output = f"{arg} is a shell builtin"
    else:
        path = shutil.which(arg)
        if path:
            output = f"{arg} is {path}"
        else:
            error = f"{arg}: not found"
    return [output, error]

def echo(command: str) -> List[str]:
    """Handle the 'echo' built-in command."""
    args = command[5:].strip()
    parsed_args = shlex.split(args)
    output = " ".join(parsed_args)
    return [output, ""]

def cd(arg: str) -> List[str]:
    """Handle the 'cd' built-in command."""
    try:
        if arg.startswith("~"):
            os.chdir(os.path.expanduser("~"))
        else:
            os.chdir(arg)
        return ["", ""]
    except:
        return ["", f"cd: {arg}: No such file or directory"]

def other(command: str) -> List[str]:
    """Handle external commands."""
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

def execute(command: str) -> List[str]:
    """Execute a command and return the output and error."""
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
    """Main loop of the shell."""
    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()
        command = input()

        # Handle redirection
        redirect = False
        left = command
        outputFile = ""
        append_mode = False
        error_redirect = False

        if '2>>' in command:
            left, outputFile = command.split('2>>', 1)  # Split on first occurrence of '2>>'
            redirect = True
            append_mode = True
            error_redirect = True
        elif '1>>' in command:
            left, outputFile = command.split('1>>', 1)  # Split on first occurrence of '>>'
            redirect = True
            append_mode = True
        elif '>>' in command:
            left, outputFile = command.split('>>', 1)  # Split on first occurrence of '>>'
            redirect = True
            append_mode = True
        elif '2>' in command:
            left, outputFile = command.split('2>', 1)  # Split on first occurrence of '2>'
            redirect = True
            error_redirect = True
            append_mode = False
        elif '1>' in command:
            left, outputFile = command.split('1>', 1)  # Split on first occurrence of '2>'
            redirect = True
            error_redirect = False
            append_mode = False
        elif '>' in command:
            left, outputFile = command.split('>', 1)  # Split on first occurrence of '>'
            redirect = True
            append_mode = False

        if redirect:
            left = left.strip()
            outputFile = outputFile.strip()

            # Execute the command
            output, error = execute(left)

            # Write output or error to the file
            mode = "a" if append_mode else "w"
            if error_redirect:
                with open(outputFile, mode) as file:
                    if error:
                        file.write(error.strip() + "\n")  # Add newline after the error message
                if output:
                    print(output.strip())
            else:
                with open(outputFile, mode) as file:
                
                    if output:
                        file.write(output.strip() + "\n")
                    
                if error:
                    print(error.strip())
        else:
            # Execute the command without redirection
            output, error = execute(command)
            if output:
                print(output)
            if error:
                print(error)

        if command.startswith("exit"):
            return 0

if __name__ == "__main__":
    main()