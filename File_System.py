import json , os
import sys
class FileSystem:
    def __init__(self):
        self.current_directory = '/'
        self.directories = {'/': {}}
        self.files = {}

    def save_state(self, file_path):
        state_data = {
            'current_directory': self.current_directory,
            'directories': self.directories,
            'files': self.files
        }
        with open(file_path, 'w') as file:
            json.dump(state_data, file)
        print(f"File system state saved to {file_path}.")

    def load_state(self, file_path):
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                state_data = json.load(file)
            self.current_directory = state_data.get('current_directory', '/')
            self.directories = state_data.get('directories', {'/': {}})
            self.files = state_data.get('files', {})
            print(f"File system state loaded from {file_path}.")
        else:
            print(f"Error: File system state file '{file_path}' not found.")


    def mkdir(self, newdir_name):
        path = f'{self.current_directory}/{newdir_name}'
        path = self.normalize_path(path)
        if path not in self.directories:
            self.directories[path] = {}
            self.directories[self.current_directory][newdir_name] = True
            return f"Directory '{newdir_name}' created successfully."
        else:
            return f"Error: Directory '{newdir_name}' already exists."

    def ls(self, path=None):
        if path is not None:
            path = self.normalize_path(path)
            entries = list(self.directories.get(path, {}).keys())
            entries.extend(self.files.get(path, {}).keys())
            return entries
        else:
            entries = list(self.directories[self.current_directory].keys())
            entries.extend(self.files.get(self.current_directory, {}).keys())
            print("Files and Directories:-")
            print("- "*10)
            for entry in entries:
                print(entry)

    def cd(self, path):
        if path == '/':
            self.current_directory = '/'
        elif path == '..':
            self.current_directory = self.normalize_path('/'.join(self.current_directory.split('/')[:-1]))
        elif path.startswith('/'):
            self.current_directory = self.normalize_path(path)
        else:
            new_path = self.normalize_path(f'{self.current_directory}/{path}')
            if new_path in self.directories:
                self.current_directory = new_path
            else:
                print('Invalid path')

    def touch(self, file_name):
        path = f'{self.current_directory}/{file_name}'
        path = self.normalize_path(path)
        if path not in self.files:
            self.files[path] = ''
            self.directories[self.current_directory][file_name] = True
            return f"File '{file_name}' created successfully."
        else:
            return f"Error: File '{file_name}' already exists."

    def cat(self, file_name):
        path = f'{self.current_directory}/{file_name}'
        file_path = self.normalize_path(path)
        if file_path in self.files:
            return self.files[file_path]
        else:
            return f"Error: File '{file_path}' not found."

    def echo(self, content, file_name):
        path = f'{self.current_directory}/{file_name}'
        path = self.normalize_path(path)
        if path in self.files:
            self.files[path] = content
            return f"Content written to file '{file_name}' successfully."
        else:
            return f"Error: File '{file_name}' not found."

    def mv(self, source_path, destination_path):
        source_path = self.normalize_path(source_path)
        destination_path = self.normalize_path(destination_path)
        self.cp(source_path,destination_path)
        temp = self.current_directory
        self.current_directory =  source_path.rsplit('/', 1)[0]
        file_name = source_path.split('/')[-1]
        self.rm(file_name)
        self.current_directory = temp



    def cp(self, source_path,destination_path):
        source_path = self.normalize_path(source_path)
        destination_path = self.normalize_path(destination_path)
        if destination_path in self.files:
            return "cannot copy file or folder to another file.mention the path of a directory"
        if source_path in self.files:
            if destination_path not in self.directories:
                return f"Error: Destination path '{destination_path}' doesnt exists."
            else:
                if source_path in self.files:
                    file_name=source_path.split('/')[-1]
                    new_path = f'{destination_path}/{file_name}'
                    self.files[new_path] = self.files[source_path]
                    self.directories[destination_path][file_name] = True
        elif source_path in self.directories:
            if destination_path not in self.directories:
                return f"Error: Destination path '{destination_path}' doesnt exists."
            else:
                dir_name = source_path.split('/')[-1]
                new_path = f'{destination_path}/{dir_name}'
                self.directories[new_path] = {}
                self.directories[destination_path][dir_name] = True
                self.recur_cp(source_path,new_path)




        else:
            return f"Error: Source path '{source_path}' not found."

    def recur_cp(self, source_path,dest_path):
        entries = list(self.directories[source_path].keys())
        for entry in entries:
            entry_path = f'{source_path}/{entry}'
            if entry_path in self.files:
                new_path = f'{dest_path}/{entry}'
                self.files[new_path] = self.files[entry_path]
                self.directories[dest_path][entry] = True
            elif entry_path in self.directories:
                new_path = f'{dest_path}/{entry}'
                self.directories[new_path] = {}
                self.directories[dest_path][entry] = True
                self.recur_cp(entry_path,new_path)

    def grep(self, pattern, file_name):
        path = f'{self.current_directory}/{file_name}'
        path = self.normalize_path(path)
        if path in self.files:
            content = self.files[path]
            lines = content.split('\n')
            for line in lines:
                if pattern in line:
                    # Highlight the matched pattern in red
                    highlighted_line = line.replace(pattern, f"\033[91m{pattern}\033[0m")
                    print(highlighted_line)
                else:
                    print(line)
        else:
            print(f"Error: File '{file_name}' not found.")

    def rm(self, name):
        name = self.normalize_path(f'{self.current_directory}/{name}')
        if name in self.files:
            file_name = name.split('/')[-1]
            del self.directories[self.current_directory][file_name]
            del self.files[name]
            return f"File '{file_name}' removed successfully."
        elif name in self.directories:
            self._remove_directory_recursive(name)
            return f"Directory '{name}' and its contents removed successfully."
        else:
            return f"Error: File or directory '{name}' not found."



    def _remove_directory_recursive(self, dir_path):
        # Recursively remove the directory and its contents
        entries = list(self.directories[dir_path].keys())  # Copy the keys
        for entry in entries:
            entry_path = f'{dir_path}/{entry}'
            if entry_path in self.files:
                # Remove file
                del self.files[entry_path]
            elif entry_path in self.directories:
                # Recursively remove child directory
                self._remove_directory_recursive(entry_path)

        # Remove the directory itself
        parent_directory = dir_path.rsplit('/', 1)[0]
        if len(parent_directory)==0:
            parent_directory = '/'
        if parent_directory in self.directories:
            del self.directories[parent_directory][dir_path.rsplit('/',1)[1]]
        if dir_path in self.directories:
            del self.directories[dir_path]
    def normalize_path(self, path):
        return '/' + '/'.join(filter(bool, path.split('/')))

    def execute_command(self,command):
        if command.startswith('mkdir '):
            _, directory_name = command.split(' ', 1)
            print(self.mkdir(directory_name))

        elif command.startswith('ls '):
            _, directory_path = command.split(' ', 1)
            print(self.ls(directory_path))

        elif command.startswith('cd '):
            _, path = command.split(' ', 1)
            self.cd(path)

        elif command.startswith('touch '):
            (_, file_name) = command.split(' ', 1)
            print(self.touch(file_name))

        elif command.startswith('cat '):
            (_, file_path) = command.split(' ', 1)
            print(self.cat(file_path))

        elif command.startswith('echo '):
            (_, echo_command) = command.split(' ', 1)
            parts = echo_command.split(' > ')
            if len(parts) == 2:
                content, file_name = parts
                print(self.echo(content, file_name))
            else:
                print("Invalid echo command. Example: echo 'content' > file.txt")

        elif command.startswith('mv '):
            (_, paths) = command.split(' ', 1)
            source_path, destination_path = paths.split(' ')
            self.mv(source_path, destination_path)

        elif command.startswith('cp '):
            (_, paths) = command.split(' ', 1)
            source_path, destination_path = paths.split(' ')
            self.cp(source_path, destination_path)

        elif command == 'ls':
            self.ls()

        elif command.startswith('rm '):
            _, name = command.split(' ', 1)
            print(self.rm(name))

        elif command.startswith('grep '):
            _, grep_command = command.split(' ', 1)
            pattern, file_name = "", ""
            parts = grep_command.split('"')
            if len(parts) == 3:
                # Ensure the command has the correct format
                pattern = parts[1]
                file_name = parts[2].strip()
                self.grep(pattern, file_name)
            else:
                print("Invalid grep command. Example: grep \"pattern\" file_name")

        elif command.startswith('save '):
            _, file = command.split(' ', 1)
            self.save_state(file)
        elif command.startswith('load '):
            _, file = command.split(' ', 1)
            self.load_state(file)
        else:
            print("\033[91m",
                  "The term is not recognized as the name of a cmdlet, function, script file, or operable program\n. Check the spelling of the name, or if a path was included, verify that the path is correct and try again.\033[0m")