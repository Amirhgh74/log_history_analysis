import re
import csv

# this is the first file to run in the process.

# Define the list of special words to filter commits
special_words = ["fix", "solve", "resolve"]
special_words2 = ["bug", "issue", "problem", "crash"]

# Initialize lists to store filtered and non-filtered commits
filtered_commits = set()
non_filtered_commits = set()

# Open the input file containing the commit messages
with open("commit.txt", "r") as file:
    # Read the content of the file line by line
    lines = file.readlines()

# Initialize variables to store commit details
commit_id = None
author = None
date = None
message_lines = []

# Process each line in the file
for line in lines:
    line = line.strip()  # Remove leading/trailing whitespace

    # Check if the line is a commit ID line (e.g., starts with "commit")
    if line.startswith("commit "):
        # If there's already a commit message, process it
        if commit_id:
            # Check if the commit message contains any of the special words
            
            message = " ".join(message_lines).lower()
            for word1 in special_words:
                for word2 in special_words2:
                    if any( word in message for word in special_words):
                        if any (word3 in message for word3 in special_words2):
                            filtered_commits.add((commit_id, "\n".join(message_lines)))
                            continue
                        else:
                            non_filtered_commits.add((commit_id, "\n".join(message_lines)))
                            continue

        # Reset variables for the next commit
        commit_id = line[7:]
        author = None
        date = None
        message_lines = []
    # Check if the line is an author line (e.g., starts with "Author:")
    elif line.startswith("Author: "):
        author = line[8:]
    # Check if the line is a date line (e.g., starts with "Date:")
    elif line.startswith("Date: "):
        date = line[6:]
    # Otherwise, assume it's part of the commit message
    else:
        message_lines.append(line)

# Process the last commit in the file
if commit_id:
    message = " ".join(message_lines).lower()
    for word1 in special_words:
        for word2 in special_words2:
            
            if any( word in message for word in special_words):
                if any (word3 in message for word3 in special_words2):
                    filtered_commits.add((commit_id, "\n".join(message_lines)))
                else:
                    non_filtered_commits.add((commit_id, "\n".join(message_lines)))

    
with open("filtered_commits.csv" , "w") as file:
    writer = csv.writer(file)

    # Print or save the filtered and non-filtered commit messages
    for commit in filtered_commits:
        writer.writerow(commit)


with open("not_filtered_commits.csv" , "w") as file:
    writer = csv.writer(file)

    # Print or save the filtered and non-filtered commit messages
    for commit in non_filtered_commits:
        writer.writerow(commit)