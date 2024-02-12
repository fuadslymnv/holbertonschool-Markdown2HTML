#!/usr/bin/python3
"""
Script that takes 2 string arguments:
  - The name of the Markdown file.
  - The output file name.
Requirements:
  - If the number of arguments is less than 2:
    print in STDERR "Usage: ./markdown2html.py README.md README.html" and exit 1.
  - If the Markdown file doesn’t exist:
    print in STDERR "Missing <filename>" and exit 1.
  - Otherwise, print nothing and exit 0.
  - Improve the script by parsing Headings Markdown syntax for generating HTML.
    Syntax: (you can assume it will be strictly this syntax)
    Markdown     HTML generated
    # Title       <h1>Title</h1>
    ## Title      <h2>Title</h2>
    ### Title     <h3>Title</h3>
    #### Title    <h4>Title</h4>
    ##### Title   <h5>Title</h5>
    ###### Title  <h6>Title</h6>
"""

import sys
import os
import re
import hashlib

def md5_hash(content):
    """
    Convert the content to MD5 hash (lowercase).
    """
    return hashlib.md5(content.encode()).hexdigest()

def remove_character(line):
    """
    Remove all occurrences of the specified character (case insensitive).
    """

    line = re.sub(r'\[\[(.*?)\]\]', lambda m: md5_hash(m.group(1)), line)

    line = re.sub(r'\(\((.*?)\)\)', lambda m: m.group(1).replace('c', '').replace('C', ''), line)

    return line

def process_inline_formatting(text):
    """
    Process inline formatting (bold, italic) in the given text.
    """
    # Bold
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    # Underline
    text = re.sub(r'__(.*?)__', r'<em>\1</em>', text)
    return text


def list(line, in_list, list_type):
    """
    Converts a Markdown list item to an HTML list item.
    Handles both ordered and unordered lists.
    Returns the HTML line and a flag indicating if we are currently inside a list.
    """
    if line.startswith(("- ", "* ")): 
        if not in_list:
            tag = "ul" if line.startswith("- ") else "ol"
            return f"<{tag}>\n<li>" + line[2:].strip() + "</li>", True, tag
        else:
            return "<li>" + line[2:].strip() + "</li>", True, list_type
    else:
        if in_list:
            return f"</{list_type}>" + line, False, None
        else:
            return line, in_list, list_type


def heading(line):
    """
    Converts a Markdown heading to an HTML heading.
    """
    if line.startswith("#"):
        level = line.count('#')  
        line_content = line.strip('#').strip()
        return f"<h{level}>{line_content}</h{level}>"
    return line

def convert_line(lines):
    """
    Converts blocks of text to HTML paragraphs.
    """
    # Initialize variables
    in_paragraph = False
    html_lines = []

    # Iterate over each line in the input
    for line in lines:
        # Check if the line is a heading or list closing tag
        if line.startswith(("<h", "</ul>", "</ol>")):
            # If inside a paragraph, close it
            if in_paragraph:
                html_lines.append("</p>")
                in_paragraph = False
            # Add the current line to the HTML lines
            html_lines.append(line)

        # Check if the line is a list opening tag
        elif line.startswith(("<ul", "<li", "<ol")):
            # If inside a paragraph, exit it
            if in_paragraph:
                in_paragraph = False
            # Add the current line to the HTML lines
            html_lines.append(line)

        # Check if the line is empty
        elif line.strip() == "":
            # If inside a paragraph, close it
            if in_paragraph:
                html_lines.append("</p>")
                in_paragraph = False

        else:
            # If not inside a paragraph, start one
            if not in_paragraph:
                html_lines.append("<p>")
                in_paragraph = True
            # If inside a paragraph, add a line break
            elif in_paragraph:
                html_lines.append("<br />")
            # Add the current line to the HTML lines
            html_lines.append(line)

    # Check if inside a paragraph after the loop ends
    if in_paragraph:
        html_lines.append("</p>")

    # Return the HTML lines
    return html_lines


if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) < 3:
        print("Usage: ./markdown2html.py README.md README.html", file=sys.stderr)
        sys.exit(1)

    markdown_file = sys.argv[1]
    html_file = sys.argv[2]

    try:
        with open(markdown_file, 'r') as f:
            lines = [line.strip('\n') for line in f]
            processed_lines = []
            in_list = False
            list_type = None
            for line in lines:
                line = remove_character(line)
                line = process_inline_formatting(line)
                processed_line, in_list, list_type = list(heading(line), in_list, list_type)
                processed_lines.append(processed_line)
            processed_lines = convert_line(processed_lines)
            with open(html_file, 'w') as html:
                for line in processed_lines:
                    html.write(line + '\n')
                if in_list:
                    html.write(f"</{list_type}>\n")
    except FileNotFoundError:
        print(f"Missing {markdown_file}", file=sys.stderr)
        sys.exit(1)
