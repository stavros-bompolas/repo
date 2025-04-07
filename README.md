CoNLL-U Correction Script

This script processes CoNLL-U files by:
1. Replacing the form in column 2 with the value from "CorrectForm=" in column 10 (if present)
2. Updating the sentence text in "# text = " comment lines to reflect all corrections

Usage:
    python process_conllu.py /path/to/folder

Where:
    /path/to/folder - Directory containing .conllu files to process

Example:
    python process_conllu.py "C:/Users/Username/Desktop/conllu_files"

Note:
    - All .conllu files in the specified folder will be processed
    - For each input file, a new file with "_updated" appended to the name will be created
    - The original files remain unchanged
