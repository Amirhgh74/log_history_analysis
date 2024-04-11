import csv
import subprocess
import json

# this is the second file to run in the process 

# Sample CSV file structure (replace with your CSV file)
csv_file_path = 'filtered_commits.csv'
output_json_file = 'commit_info.json'

# Initialize a list to store commit information
commit_info = []

# Read the commit IDs and commit messages from the CSV file
with open(csv_file_path, 'r', newline='') as csv_file:
    csv_reader = csv.reader(csv_file)
    next(csv_reader)  # Skip the header if there is one
    for row in csv_reader:
        commit_id = row[0]
        commit_message = row[1]  # Assuming the commit message is in the second column

        # Use subprocess to run 'git show --name-only' and capture the output
        try:
            git_diff_output = subprocess.check_output(['git', 'diff-tree', '--no-commit-id', '--name-only', '-r', commit_id], text=True)
            # Split the output by newline to get the list of changed files
            changed_files = git_diff_output.strip().split('\n')
        
        except subprocess.CalledProcessError:
            changed_files = []  # Handle errors, e.g., if the commit doesn't exist

        # Save the commit information
        commit_info.append({
            "commit_id": commit_id,
            "commit_message": commit_message,
            "changed_files": changed_files
        })

# Save the commit information to a JSON file
with open(output_json_file, 'w') as json_file:
    json.dump(commit_info, json_file, indent=4)

print(f"Commit information saved to {output_json_file}")
