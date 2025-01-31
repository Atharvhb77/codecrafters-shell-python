import sys
import shutil
import os
import shlex
from typing import List
import subprocess 

builtins = ["type", "echo", "exit", "pwd", "cd"]

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

        # Check for redirections
        if "1>>" in command or ">>" in command:  # Handle append
            left, outputFile = command.split("1>>") if "1>>" in command else command.split(">>")
            append = True
            redirect = True
        elif "1>" in command or ">" in command:  # Handle overwrite
            left, outputFile = command.split("1>") if "1>" in command else command.split(">")
            redirect = True
        elif "2>" in command:  # Handle error redirection
            left, outputFile = command.split("2>")
            redirect = True

        if redirect:
            left = left.strip()
            outputFile = outputFile.strip()
            output, error = execute(left)
        else:
            output, error = execute(command)

        if redirect:
            if "2>" in command:  # Redirect stderr
                with open(outputFile, "w") as file:
                    file.write(error.strip())
                if output:
                    print(output.strip())

            elif "1>>" in command or ">>" in command:  # Append output
                with open(outputFile, "a") as file:
                    if output:
                        file.write(output.strip() + "\n")  # Ensure newline after each append
                    if error:
                        print(error.strip())

            elif "1>" in command or ">" in command:  # Overwrite output
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
