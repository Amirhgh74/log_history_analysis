import json
import os
import re
import sys
import subprocess
from pathlib import Path
import xml.etree.ElementTree as ET

from utils import get_element_texts

# this is the last file to be used in the process


def logging_imported(lst):
    for item in lst:
        if 'logging' in item or 'Logger' in item or 'LoggerFactory' in item or 'Logging' in item :
            return True
        return False

if __name__ == "__main__":
    # if len(sys.argv) != 2:
    #     print("Usage: python3 analysis.py <input_directory>")
    #     exit(1)



    file_address = "changed_functions.txt"
    file_list = []

    with open(file_address , 'r') as file:
        for line in file:
            parts = line.strip().split(maxsplit=1)
            if len (parts) == 2:
                file_list.append((parts[0], parts[1]))
            else:
                print ('invalid input line!')

    result = []
    
    for tuple in file_list:

        input_file = tuple[1]
        intended_function = tuple[0]
    
        # check if the file exist
        if not os.path.isfile(input_file) or not input_file.endswith('.java'):
            print ('file not exist or not supported!')
            exit(1)

    
        process = subprocess.run(['srcml', input_file], capture_output=True) # Run srcml on file
        xml = process.stdout.decode('utf-8')
        xml = re.sub('xmlns="[^"]+"', '', xml, count=1) # Remove namespace

        root = ET.fromstring(xml)
        imports = []

        for item in root.findall('.//import/name'):
            imports.append(get_element_texts(item))

        # Get root functions and loop through them
        for function in root.findall('.//function'):

            function_name = get_element_texts(function.find('name'))

            if function_name == intended_function:

                # Find the number of semi-colons in the function
                number_of_semicolons = ''.join(function.itertext()).count(';')

                loops = []
                loops.extend(function.findall('.//for') + function.findall('.//while') + function.findall('.//do'))
                number_of_nested_loops = 0
                for loop in loops:
                    nested_loops = []
                    nested_loops.extend(loop.findall('.//for') + loop.findall('.//while') + loop.findall('.//do'))
                    number_of_nested_loops += len(nested_loops)

                    if loop.find('control') is not None:
                        number_of_semicolons -= ''.join(loop.find('control').itertext()).count(';')

                number_of_loops = len(loops)

                calls_total = function.findall('.//call')
                number_of_calls = len(calls_total)

                number_of_info = 0
                number_of_trace = 0
                number_of_debug = 0
                number_of_warn = 0
                number_of_error = 0
                number_of_fatal = 0

                for call in calls_total:

                    call_name = get_element_texts(call.find('name'))
                    params = [get_element_texts(x) for x in call.findall('name/name')]

                    if logging_imported:
                        for param in params:
                            if 'info' in param:
                                number_of_info += 1
                            if 'trace' in param or 'fine' in param: 
                                number_of_trace += 1
                            if 'debug' in param:
                                number_of_debug += 1
                            if 'warn' in param or 'warning' in param:
                                number_of_warn += 1
                            if 'error' in param or 'sever' in param:
                                number_of_error += 1
                            if 'fatal' in param:
                                number_of_fatal += 1
                    
                # Find number of blocks
                number_of_blocks = len(function.findall('.//block'))

                # Check if function is recursive
                is_recursive = False
                
                if get_element_texts(call.find('name')) == function_name.split(')')[0]:
                    is_recursive = True

                # Number of statements individually
                number_of_expression_statements = len(function.findall('.//expr_stmt'))
                number_of_declaration_statements = len(function.findall('.//decl_stmt'))
                number_of_empty_statements = len(function.findall('.//empty_stmt'))


                number_of_try = len(function.findall('.//try'))


                # Number of branches
                number_of_if = len(function.findall('.//if') + function.findall('.//else'))
                number_of_switch = len(function.findall('.//switch'))

                
                result.append({
                    'function_name': function_name,
                    'file_address' : input_file,
                    'line_of_codes': number_of_semicolons + number_of_blocks - 1, # -1 because of the function entire block
                    'number_of_loops': number_of_loops,
                    'number_of_nested_loops': number_of_nested_loops,
                    'number_of_calls': number_of_calls,
                    'number_of_trys' : number_of_try,
                    'is_recursive': is_recursive,
                    'number_of_statements': {
                        'number_of_expression_statements': number_of_expression_statements,
                        'number_of_declaration_statements': number_of_declaration_statements,
                        'number_of_empty_statements': number_of_empty_statements
                    },
                    'number_of_branches': {
                        'number_of_if': number_of_if,
                        'number_of_switch': number_of_switch,
                        'number_of_branch_total': number_of_if + number_of_switch
                    },
                    'logging_info': {
                        'number_of_info' : number_of_info,
                        'number_of_trace' : number_of_trace,
                        'number_of_debug' : number_of_debug,
                        'number_of_warn' : number_of_warn,
                        'number_of_error' : number_of_error,
                        'number_of_fatal' : number_of_fatal
                    }
                })

    # Write result to file
    with open('result.json', 'w') as f:
        json.dump(result, f, indent=4)
