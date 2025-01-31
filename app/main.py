import sys
import shutil
import os
import shlex


def main():
    

    # Wait for user input

    while True:
        sys.stdout.write("$ ")
        command = input()
        cmd = command.split()
        
        if cmd[0] == 'exit':
            
            if len(cmd) < 2:
                return 0
            
            return cmd[1]


        elif cmd[0] == 'echo':
            if len(cmd) < 2:
                print('')
            

            else:
                args = command[5:].strip()
                parsed_args = shlex.split(args)
                
                if parsed_args[1] == '1>':
                    content = ""
                    if os.path.exists(parsed_args[0]):
                        with open(parsed_args[0], "r") as file:
                            content = file.read()
                    else:
                        content = parsed_args[0]

                    with open(parsed_args[2], "w") as file:
                        file.write(content + '\n')
                    
                else:
                    print(" ".join(parsed_args))
            
        
        elif cmd[0] == 'type':
            if len(cmd) < 2:
                print('')
            elif cmd[1] == 'echo' or cmd[1] == 'exit' or cmd[1] == 'type' or cmd[1] == 'pwd' or cmd[1] == 'cd':
                print(f'{cmd[1]} is a shell builtin')

            else:
                cmd_path = shutil.which(cmd[1])
                if cmd_path:
                    print(f"{cmd[1]} is {cmd_path}")
                else:
                    print(f"{cmd[1]}: not found")

        
        elif cmd[0] == 'pwd':
            current_dir = os.getcwd()
            print(current_dir)

        elif cmd[0] == 'cd':
            
            try:
                if cmd[1] == '~':
                    home_dir = os.path.expanduser("~")
                    os.chdir(home_dir)
                else:    
                    os.chdir(cmd[1])

            except:
                print(f'cd: {cmd[1]}: No such file or directory')



        else:
            args = shlex.split(command)
            cmd_path = shutil.which(args[0])

            if cmd_path:
                os.system(command)
            else:
                print(f"{command}: command not found")

        

        



if __name__ == "__main__":
    main()
    


