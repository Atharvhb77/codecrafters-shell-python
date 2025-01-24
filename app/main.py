import sys


def main():
    

    # Wait for user input

    while True:
        sys.stdout.write("$ ")
        command = input()
        

        if command.split(' ')[0] == 'exit':
            
            if len(command.split(' ')) < 2:
                return 0
            
            return command.split(' ')[1]


        elif command.split(' ')[0] == 'echo':
            if len(command.split(' ')) < 2:
                print('')
            else:
                print(' '.join(command.split(' ')[1:]))
            
        
        elif command.split(' ')[0] == 'type':
            if len(command.split(' ')) < 2:
                print('')
            elif command.split(' ')[1] == 'echo' or command.split(' ')[1] == 'exit' or command.split(' ')[1] == 'type':
                print(f'{command.split(' ')[1]} is a shell builtin')
            else:
                print(f"{command.split(' ')[1]}: not found")



        else:


            print(f"{command}: command not found")

        






if __name__ == "__main__":
    main()
    


