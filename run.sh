#!/bin/bash

# Your initial git commands
echo "Fetching all branches..."
# git fetch --all

echo "Saving commits to file"
# git log --all > commit.txt

# Sequentially run your Python scripts
echo "Running filterCommits.py"
python3 filterCommits.py

echo "Running getAllCommitFiles.py"
python3 getAllCommitFiles.py

echo "Running getAllFiles.py"
python3 getAllFiles.py

echo "Running parsCommitHistory.py"
python3 parsCommitHistory.py

echo "Running parsFunctions.py"
python3 parsFunctions.py

echo "Process completed!"
