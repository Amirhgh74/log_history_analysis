import re
import os

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


def extract_function_name(function_definition):
    """
    Extracts and returns the function name from a given Java method definition line.
    """
    # Regex pattern to match the function name
    pattern = re.compile(r'\s+(\w+)\s*\(')
    match = pattern.search(function_definition)
    
    if match:
        # If a match is found, the function name is in the first capturing group
        return match.group(1)
    else:
        return "Function name not found"

def parse_diff(diff_file_path):
    """
    Parses the diff file to extract chunks, changes, and the unchanged lines immediately 
    preceding the first change line for each change set within a chunk.
    Returns a list of tuples: (line_number, change_type, [changed_lines], [context_lines])
    """
    changes = []
    with open(diff_file_path, 'r') as file:
        lines = file.readlines()

    current_chunk_start = None
    current_changes = []
    current_change_type = None
    context_lines = []  # To capture unchanged lines right before the changes
    collecting_context = True  # Flag to start collecting context lines
    current_chunk_start_add = None
    current_chunk_start_del = None

    for line in lines:
        if line.startswith('@@'):
            # Process previous chunk
            if current_changes:
                # Include context lines only if there are changes
                changes.append((current_chunk_start, current_change_type, current_changes, context_lines))
                current_changes = []
                context_lines = []
            # Extract the start line number for the 'after' file from the chunk header
            match = re.search(r'\+(\d+)', line)
            if match:
                current_chunk_start_add = int(match.group(1))
                current_chunk_start_del = int(match.group(0))

            collecting_context = True  # Reset context collecting for the new chunk
        elif line.startswith(('+', '-')):
            if line.startswith(('---', '+++')):
                continue
            if collecting_context:
                # We have reached the first change in the chunk, stop collecting context
                collecting_context = False
                # Determine change type at the start of a new set
                if line.startswith('+'):
                    current_change_type = 'addition'
                    current_chunk_start = current_chunk_start_add
                else:
                    current_change_type = 'deletion'
                    current_chunk_start = current_chunk_start_del
                
            else:
                # If current line's prefix is different from the current change set's type, it's a modification
                if (line.startswith('+') and current_change_type == 'deletion') or \
                   (line.startswith('-') and current_change_type == 'addition'):
                    current_change_type = 'modification'
                    current_chunk_start = current_chunk_start_add

            current_changes.append(line)
        else:
            # This line is an unchanged context line
            if collecting_context:
                # Collect unchanged lines only before the first change
                context_lines.append(line)
            else:
                # Reset context for potential next change set within the same chunk
                if current_changes:
                    changes.append((current_chunk_start, current_change_type, current_changes, context_lines))
                    current_changes = []
                    context_lines = [line]  # Start new context collecting
                    current_change_type = None
                    collecting_context = True

    # Process any remaining changes at the end of the file
    if current_changes:
        changes.append((current_chunk_start, current_change_type, current_changes, context_lines))

    return changes



def find_function_in_changes(java_file_path, changes):
    """
    Searches for function definitions within the provided changes.
    If not found, searches backward from the start of the change for the closest function definition.
    """

    function_names = []

    # \s*(public|protected|private|static|final|synchronized)\s+[\w<>\[\]]+\s+\w+\s*\([^)]*\)\s*\{?
    # \b(public|protected|private|static)?\s+[\w<>\[\]]+\s+\w+\s*\(
    # \s*(public|protected|private|static|\s)+[\w<>\[\]]+\s+\w+\s*\([^)]*\)\s*{?\s*$

    function_pattern = re.compile(r'\s*(public|protected|private|static|final|synchronized)\s+[\w<>\[\]]+\s+\w+\s*\([^)]*')
    with open(java_file_path, 'r') as file:
        lines = file.readlines()

    for start_line, change_type, changed_lines, context_lines in changes:

        function_found = False
        # Check each line in the change set for a function definition

        # search in the changed lines
        for changed_line in changed_lines:
            if function_pattern.match(changed_line[1:]):  # Skip the first character (+/-)
                # print(f"Function found in changes at line {start_line}: {changed_line[1:].strip()}")
                if changed_line.strip()[0] == "+":
                    function_decl = changed_line[1:].strip()
                    function_name = extract_function_name(function_decl)
                    function_names.append(function_name)
                function_found = True

        # search in the line between changed lines and start line in chunk
        if not function_found and context_lines:

            # for i in reversed(context_lines):
            #     print (i)
            for context_line in reversed(context_lines):
                if function_pattern.match(context_line.strip()):
                    # print(f"Function found in context lines at line {start_line}: {context_line.strip()}")
                    function_decl = context_line.strip()
                    function_name = extract_function_name(function_decl)
                    function_names.append(function_name)
                    function_found = True
                    break

        # search from the start line backwards until a function definition is found 
        if not function_found:
            # If no function definition is found in the change set, search backward
            for i in range(int (start_line) - 1, 0, -1):
                if function_pattern.match(lines[i]):
                    # print(f"Nearest function found backward at line {i}: {lines[i].strip()}")
                    function_decl = lines[i].strip()
                    function_name = extract_function_name(function_decl)
                    function_names.append(function_name)
                    break
    return function_names


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
        
        changes = parse_diff(diff_file)

        detected_functions_add = find_function_in_changes(after_file, [(ln, ct, cl, cx) for ln, ct, cl, cx in changes if ct in ['addition', 'modification']])

        detected_functions_del = find_function_in_changes(before_file, [(ln, ct, cl) for ln, ct, cl in changes if ct == 'deletion'])

        if detected_functions_add:
            for item in detected_functions_add:
                final_output.append([item, after_file])
        if detected_functions_del:
            for item in detected_functions_del:
                final_output.append([item, before_file])

        with open("changed_functions.txt", "w") as file:
            for row in final_output:
                file.write(str(row[0]) + "   " + row[1] + "\n")
