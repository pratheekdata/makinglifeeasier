import os
import re

def search_files_with_regex(string_text, directory_path):
     # Normalize the directory path to handle slashes correctly
    directory_path = os.path.normpath(directory_path)
    
    # Escape the string to safely use it in a regex pattern
    escaped_string = re.escape(string_text)
    
    # Compile the regex pattern to find the string in any part of the filename
    pattern = re.compile(escaped_string)
    
    # List to store the paths of files containing the string
    matching_files = []

    # Walk through the directory
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if pattern.search(file):
                # Append the full path of the matching file
                matching_files.append(os.path.join(root, file))

    return matching_files


# Example usage
directory_path = input("Enter the directory path to search: ")
string_text = input("Enter the pattern to search: ")
files_with_string = search_files_with_regex(string_text, directory_path)

if files_with_string:
    print(f"Files containing {string_text} in their name:")
    for file_path in files_with_string:
        print(file_path)
else:
    print(f"No files containing  {string_text} found in the specified directory.")
