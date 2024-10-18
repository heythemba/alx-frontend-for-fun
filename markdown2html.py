#!/usr/bin/python3
"""
markdown2html.py
A script that converts a Markdown file to an HTML file, supporting various Markdown syntax.
It supports:
- Headings (#, ##, etc.)
- Unordered lists (-)
- Ordered lists (*)
- Paragraphs
- Bold (**text**)
- Emphasis (__text__)
- MD5 hashing ([[text]])
- Removing 'c' or 'C' characters from text ((text))

Usage: ./markdown2html.py input_file.md output_file.html
"""

import sys
import os
import re
import hashlib


def md5_hash(content):
    """Return the MD5 hash of a string."""
    return hashlib.md5(content.encode()).hexdigest()


def remove_c(content):
    """Remove all 'c' or 'C' from the content (case insensitive)."""
    return re.sub(r'[cC]', '', content)


def markdown_to_html_line(line, in_unordered_list, in_ordered_list, in_paragraph):
    """
    Convert a single line of Markdown to HTML.
    
    Handles:
    - Heading syntax
    - Unordered and ordered list syntax
    - Paragraphs
    - Bold (**text**) and emphasis (__text__)
    - MD5 hashing ([[text]])
    - Removing 'c'/'C' from content ((text))

    Args:
        line (str): The current line of Markdown to convert.
        in_unordered_list (bool): Whether we are inside an unordered list.
        in_ordered_list (bool): Whether we are inside an ordered list.
        in_paragraph (bool): Whether we are inside a paragraph.

    Returns:
        tuple: The converted HTML line, updated list and paragraph states.
    """
    heading_levels = {
        1: "<h1>{}</h1>",
        2: "<h2>{}</h2>",
        3: "<h3>{}</h3>",
        4: "<h4>{}</h4>",
        5: "<h5>{}</h5>",
        6: "<h6>{}</h6>"
    }

    # Replace bold (**text**) with <b>text</b>
    line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)

    # Replace emphasis (__text__) with <em>text</em>
    line = re.sub(r'__(.*?)__', r'<em>\1</em>', line)

    # Replace MD5 hash ([[text]]) with the MD5 of the content
    line = re.sub(r'\[\[(.*?)\]\]', lambda match: md5_hash(match.group(1)), line)

    # Replace ((text)) by removing all 'c' or 'C'
    line = re.sub(r'\(\((.*?)\)\)', lambda match: remove_c(match.group(1)), line)

    # Check for heading syntax (up to 6 levels)
    for level in range(6, 0, -1):
        if line.startswith('#' * level + ' '):
            return heading_levels[level].format(line[level+1:].strip()), False, False, False

    # Check for unordered list syntax (-)
    if line.startswith('- '):
        list_item = f"<li>{line[2:].strip()}</li>"
        if not in_unordered_list:
            return f"<ul>\n{list_item}", True, False, False
        else:
            return list_item, True, False, False

    # Check for ordered list syntax (*)
    if line.startswith('* '):
        list_item = f"<li>{line[2:].strip()}</li>"
        if not in_ordered_list:
            return f"<ol>\n{list_item}", False, True, False
        else:
            return list_item, False, True, False

    # If the line is empty, it marks the end of a paragraph or list
    if line == "":
        if in_unordered_list:
            return "</ul>", False, False, False
        if in_ordered_list:
            return "</ol>", False, False, False
        if in_paragraph:
            return "</p>", False, False, False
        return "", False, False, False

    # Handle paragraph syntax
    if not in_paragraph:
        return f"<p>\n    {line}", False, False, True
    else:
        return f"    <br />\n    {line}", False, False, True


if __name__ == "__main__":
    # Check the number of arguments
    if len(sys.argv) < 3:
        sys.stderr.write("Usage: ./markdown2html.py README.md README.html\n")
        sys.exit(1)

    # Get the markdown input file and the output file from the arguments
    markdown_file = sys.argv[1]
    html_file = sys.argv[2]

    # Check if the markdown file exists
    if not os.path.isfile(markdown_file):
        sys.stderr.write(f"Missing {markdown_file}\n")
        sys.exit(1)

    # Read the content of the markdown file and convert it
    try:
        with open(markdown_file, 'r') as md_file:
            lines = md_file.readlines()

        # Convert markdown lines to HTML
        html_content = []
        in_unordered_list = False  # Track if we're inside an unordered list
        in_ordered_list = False    # Track if we're inside an ordered list
        in_paragraph = False       # Track if we're inside a paragraph
        for line in lines:
            html_line, in_unordered_list, in_ordered_list, in_paragraph = markdown_to_html_line(
                line.strip(), in_unordered_list, in_ordered_list, in_paragraph)
            if html_line:
                html_content.append(html_line)

        # Close any open lists or paragraphs at the end of the document
        if in_unordered_list:
            html_content.append("</ul>")
        if in_ordered_list:
            html_content.append("</ol>")
        if in_paragraph:
            html_content.append("</p>")

        # Write the converted content to the HTML file
        with open(html_file, 'w') as html_out:
            html_out.write("\n".join(html_content))

    except Exception as e:
        sys.stderr.write(str(e) + "\n")
        sys.exit(1)

    # Exit with success status
    sys.exit(0)
