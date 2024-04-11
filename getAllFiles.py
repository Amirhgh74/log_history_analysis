import os
import json
import subprocess

#  this is the third file to be used in the process

def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_commit_diff(commit_id, parent_commit_id, file_path, output_path):
    command = f"git diff {parent_commit_id}...{commit_id} -- {file_path}"
    diff_output = subprocess.check_output(command, shell=True, text=True)
    
    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.write(diff_output)

def get_file_at_commit(commit_id, file_path, output_path):
    command = f"git show {commit_id}:{file_path}"
    try:
        file_content = subprocess.check_output(command, shell=True, text=True)

        with open(output_path, 'w', encoding='utf-8') as output_file:
            output_file.write(file_content)
    except subprocess.CalledProcessError as e:
        pass


def process_commit(commit_data):
    commit_id = commit_data['commit_id']
    files_changed = commit_data['changed_files']

    # Create a directory for the commit
    commit_directory = os.path.join("commit_history", commit_id)
    create_directory(commit_directory)

    # Process each changed file in the commit
    for file_path in files_changed:
        # Create a directory for the changed file

        if file_path.endswith(".java"):

            last_slash = file_path.rfind("/")
            second_to_last_slash_index = file_path.rfind("/", 0, last_slash)

            try:
                file_directory = os.path.join(commit_directory, os.path.dirname(file_path[second_to_last_slash_index + 1: ]))
                create_directory(file_directory)

                # Get the diff for the file
                diff_output_path = os.path.join(file_directory, "diff_"+ file_path[last_slash + 1 :])
                get_commit_diff(commit_id, commit_id + "^", file_path, diff_output_path)

            
                # Get the file content after the commit
                after_output_path = os.path.join(file_directory, "after_" + file_path[last_slash + 1 :])
                get_file_at_commit(commit_id, file_path, after_output_path)

                # Get the file content before the commit
                before_output_path = os.path.join(file_directory, "before_" + file_path[last_slash + 1 :])
                get_file_at_commit(commit_id + "^", file_path, before_output_path)
            except():
                continue

if __name__ == "__main__":
    json_file_path = 'commit_info.json'  # Replace with the actual path to your JSON file

    # Read commit data from JSON
    with open(json_file_path, 'r', encoding='utf-8') as json_file:
        commit_data_list = json.load(json_file)

    # Create a directory for commit history
    create_directory("commit_history")

    # Process each commit
    for commit_data in commit_data_list:
        process_commit(commit_data)
