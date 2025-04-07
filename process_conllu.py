#!/usr/bin/env python3
"""
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
"""

import os
import sys
import re

def process_conllu_file(input_path, output_path):
    """
    Process a single .conllu file:
    1. Replace the form in the 2nd column with the value from "CorrectForm=" in the 10th column (if present)
    2. Update the text in "# text = " comments to reflect the corrected forms
    """
    with open(input_path, 'r', encoding='utf-8') as infile:
        lines = infile.readlines()
    
    # First pass: collect all corrections for the current sentence
    sentence_blocks = []
    current_block = []
    corrections = {}
    text_line_index = -1
    
    for i, line in enumerate(lines):
        current_block.append(line)
        
        # Track the text line index within the current block
        if line.startswith("# text = "):
            text_line_index = len(current_block) - 1
        
        # Process token lines to collect corrections
        elif line.strip() and not line.startswith("#"):
            parts = line.strip().split("\t")
            if len(parts) > 9:
                # Only process token lines (not blank lines or multiword tokens)
                if parts[0].isdigit() and "-" not in parts[0]:
                    token_id = int(parts[0])
                    original_form = parts[1]
                    misc = parts[9]
                    
                    if "CorrectForm=" in misc:
                        correct_form = misc.split("CorrectForm=")[-1].split("|")[0]
                        if correct_form != original_form:
                            corrections[token_id] = {
                                'original': original_form,
                                'corrected': correct_form
                            }
        
        # End of sentence
        elif not line.strip():
            # If we have corrections and found a text line, update the text
            if corrections and text_line_index >= 0:
                text_line = current_block[text_line_index]
                text_content = text_line.replace("# text = ", "").strip()
                
                # Apply corrections to the text
                # We need to process the tokens and build a corrected text
                tokens = []
                for j, block_line in enumerate(current_block):
                    if block_line.strip() and not block_line.startswith("#"):
                        parts = block_line.strip().split("\t")
                        if len(parts) > 1 and parts[0].isdigit() and "-" not in parts[0]:
                            token_id = int(parts[0])
                            if token_id in corrections:
                                tokens.append((token_id, corrections[token_id]['corrected']))
                            else:
                                tokens.append((token_id, parts[1]))
                
                # Sort tokens by their ID to ensure correct order
                tokens.sort(key=lambda x: x[0])
                corrected_text = " ".join(token[1] for token in tokens)
                
                # Replace the text line
                current_block[text_line_index] = f"# text = {corrected_text}\n"
            
            # Add the processed block to the sentence blocks
            sentence_blocks.append(current_block)
            
            # Reset for the next sentence
            current_block = []
            corrections = {}
            text_line_index = -1
    
    # Add the last block if there is one
    if current_block:
        sentence_blocks.append(current_block)
    
    # Second pass: apply form corrections and write to output file
    with open(output_path, 'w', encoding='utf-8') as outfile:
        for block in sentence_blocks:
            for line in block:
                if line.strip() and not line.startswith("#"):
                    parts = line.strip().split("\t")
                    if len(parts) > 9 and parts[0].isdigit() and "-" not in parts[0]:
                        token_id = int(parts[0])
                        misc = parts[9]
                        if "CorrectForm=" in misc:
                            correct_form = misc.split("CorrectForm=")[-1].split("|")[0]
                            parts[1] = correct_form
                        line = "\t".join(parts) + "\n"
                outfile.write(line)

def process_conllu_folder(input_folder):
    """
    Process all .conllu files in the given folder and save updated versions with "_updated" appended to the filenames.
    """
    for filename in os.listdir(input_folder):
        if filename.endswith(".conllu"):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(input_folder, filename.replace(".conllu", "_updated.conllu"))
            print(f"Processing {filename}...")
            process_conllu_file(input_path, output_path)
            print(f"Updated file saved as {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {os.path.basename(__file__)} <folder_path>")
        sys.exit(1)

    input_folder = sys.argv[1]
    if os.path.isdir(input_folder):
        process_conllu_folder(input_folder)
        print("All files processed successfully.")
    else:
        print(f"The folder '{input_folder}' does not exist.")
        sys.exit(1)