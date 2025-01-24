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
                print(command.split(' ')[1])
            
        else:


            print(f"{command}: command not found")

        






if __name__ == "__main__":
    main()
    


