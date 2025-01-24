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

        print(f"{command}: command not found")

        






if __name__ == "__main__":
    main()
    


