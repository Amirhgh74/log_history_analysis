import re
import sys
from pathlib import Path
import os

# this is the fourth script to be used in the process

def extract_line_numbers(line):
    # Regular expression to match the @@ line in a diff file
    diff_line_pattern = re.compile(r'@@ -(\d+),\d+ \+(\d+),\d+ @@')

    match = diff_line_pattern.match(line)
    if match:
        return int(match.group(1)), int(match.group(2))
    else:
        return None, None

def detect_change_type(diff_lines):
    change_type = None  # None, 'addition', 'deletion', 'modification'
    for line in diff_lines:
        if line.startswith('-') and not line.startswith('---'):
            if change_type == 'addition':
                change_type = 'modification'
            else:
                change_type = 'deletion'
        elif line.startswith('+') and not line.startswith('+++'):
            if change_type == 'deletion':
                change_type = 'modification'
            else:
                change_type = 'addition'
        elif line.startswith(' '):
            continue  # Ignore unchanged lines
        else:
            break  # Stop checking after encountering a line that doesn't start with +, -, or space
    return change_type

def get_function_name(file_path, target_line_number):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Check if the target line is a function definition
    function_name = find_function_name(lines[target_line_number - 1])

    if function_name:
        return function_name

    # If not, search in reverse order for the nearest function definition
    for line_number in range(target_line_number - 2, -1, -1):
        function_name = find_function_name(lines[line_number])
        if function_name:
            return function_name

    # Return None if no function definition is found
    return None

def find_function_name(line):
    # Regular expression to match Java method/function declarations
    function_pattern = re.compile(r'\b(?:public|private|protected|static|final|synchronized|\w+(?:<.*?>)?)\s+(\w+)\s*\([^)]*\)\s*(?:\{|\b)')

    match = function_pattern.search(line)
    if match:
        return match.group(1)
    else:
        return None
    
def find_matching_files(file_list):
    matching_files = []

    # Iterate through the list of file names
    for diff_file_path in file_list:
        # Extract the base file name from the full path
        diff_file_name = os.path.basename(diff_file_path)
        diff_dir_path = os.path.dirname(diff_file_path)
        # print(diff_file_name)

        if diff_file_name.startswith("diff_"):
            # Extract the base file name (excluding the "diff_" prefix)
            base_file_name = diff_file_name[5:]

            # Find the corresponding "before_" and "after_" files
            before_file_name = f"{diff_dir_path}/before_{base_file_name}"
            after_file_name = f"{diff_dir_path}/after_{base_file_name}"

            # print(before_file_name, after_file_name)


            # Check if the "before_" and "after_" files exist
            if before_file_name in file_list and after_file_name in file_list:
                matching_files.append([diff_file_path, after_file_name, before_file_name])
                    
    return matching_files


if __name__ == "__main__":

    # if len(sys.argv) != 2:
    #     print("Usage: python3 analysis.py <input_directory>")
    #     exit(1)

    # input_directory = sys.argv[1]
    # if not Path(input_directory).is_dir():
    #     print("Input directory does not exist")
    #     exit(1)

    input_directory = "commit_history/"

    result = []
    files_address = []

    for subdir, dirs, files in os.walk(input_directory):
        for file in files:
            files_address.append(os.path.join(subdir, file))
           

    matching_files = find_matching_files(files_address)

    final_output = []

    # Loop through all files in the input directory
    for match in matching_files:

        diff_file = match[0]
        after_file = match[1]
        before_file = match[2]
        
        output = {}
        
        with open(diff_file, 'r', encoding='utf-8') as file:
            diff_lines = file.readlines()

        for line_number, diff_line in enumerate(diff_lines, start=1):
            negative_number, positive_number = extract_line_numbers(diff_line)

            if negative_number is not None and positive_number is not None:
            
                # Detect change type
                next_pattern_index = diff_lines.index(diff_line) + 1
                remaining_lines = diff_lines[next_pattern_index:]
                change_type = detect_change_type(remaining_lines)

                output[line_number] = [negative_number, positive_number, change_type] # a line number : line in before, line in after, change type. 

        for i in output.keys():
            value = output[i]

            if value[2] == "deletion":
                function_name = get_function_name(before_file, value[0])

                if function_name:
                    final_output.append([function_name, before_file])
                else:
                    final_output.append([value[0], before_file])
            else:
                function_name = get_function_name(after_file, value[1])
                if function_name:
                    final_output.append([function_name, after_file])
                else:
                    final_output.append([value[1], after_file])

        with open("changed_functions.txt", "w") as file:
            for row in final_output:
                file.write(str(row[0]) + "   " + row[1] + "\n")


        # print (output)

