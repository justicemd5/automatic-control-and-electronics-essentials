#!/usr/bin/env python3
"""
Convert Markdown files with LaTeX math to LaTeX document
"""

import os
import re
import sys
from pathlib import Path


def escape_latex(text):
    """Escape special LaTeX characters in regular text"""
    # Don't escape content that's already in math mode or code blocks
    replacements = {
        '&': r'\&',
        '%': r'\%',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
    }
    
    result = text
    for char, replacement in replacements.items():
        result = result.replace(char, replacement)
    return result


def convert_markdown_to_latex(md_content, title="", level=0):
    """Convert markdown content to LaTeX"""
    lines = md_content.split('\n')
    latex_lines = []
    in_code_block = False
    in_math_block = False
    in_table = False
    code_language = ""
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Skip mermaid diagrams (not supported in LaTeX easily)
        if line.strip().startswith('```mermaid'):
            in_code_block = True
            code_language = 'mermaid'
            latex_lines.append(r'\begin{comment}')
            i += 1
            continue
        
        # Code blocks
        if line.strip().startswith('```'):
            if in_code_block:
                if code_language == 'mermaid':
                    latex_lines.append(r'\end{comment}')
                else:
                    latex_lines.append(r'\end{lstlisting}')
                in_code_block = False
                code_language = ""
            else:
                in_code_block = True
                code_language = line.strip()[3:].strip()
                if code_language == 'mermaid':
                    latex_lines.append(r'\begin{comment}')
                else:
                    lang_option = f'[language={code_language}]' if code_language else ''
                    latex_lines.append(r'\begin{lstlisting}' + lang_option)
            i += 1
            continue
        
        if in_code_block:
            latex_lines.append(line)
            i += 1
            continue
        
        # Block math ($$...$$)
        if line.strip().startswith('$$') and line.strip().endswith('$$') and len(line.strip()) > 4:
            # Single line math
            math_content = line.strip()[2:-2]
            latex_lines.append(r'\[' + math_content + r'\]')
            i += 1
            continue
        elif line.strip() == '$$':
            if in_math_block:
                latex_lines.append(r'\]')
                in_math_block = False
            else:
                latex_lines.append(r'\[')
                in_math_block = True
            i += 1
            continue
        
        if in_math_block:
            latex_lines.append(line)
            i += 1
            continue
        
        # Headings
        heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if heading_match:
            level_str = heading_match.group(1)
            heading_text = heading_match.group(2)
            heading_level = len(level_str)
            
            # Remove markdown formatting from heading
            heading_text = re.sub(r'\*\*(.+?)\*\*', r'\1', heading_text)
            heading_text = re.sub(r'\*(.+?)\*', r'\1', heading_text)
            heading_text = re.sub(r'`(.+?)`', r'\1', heading_text)
            
            # Adjust heading level based on section depth
            adjusted_level = heading_level + level
            
            if adjusted_level <= 1:
                latex_lines.append(r'\section{' + heading_text + '}')
            elif adjusted_level == 2:
                latex_lines.append(r'\subsection{' + heading_text + '}')
            elif adjusted_level == 3:
                latex_lines.append(r'\subsubsection{' + heading_text + '}')
            else:
                latex_lines.append(r'\paragraph{' + heading_text + '}')
            i += 1
            continue
        
        # Horizontal rules
        if line.strip() in ['---', '***', '___']:
            latex_lines.append(r'\medskip\noindent\hrulefill\medskip')
            i += 1
            continue
        
        # Tables (simple conversion)
        if '|' in line and not line.strip().startswith('#'):
            if not in_table:
                # Start table - count columns
                cols = len([c for c in line.split('|') if c.strip()])
                latex_lines.append(r'\begin{center}')
                latex_lines.append(r'\begin{tabular}{|' + 'l|' * cols + '}')
                latex_lines.append(r'\hline')
                in_table = True
            
            # Check if it's a separator line
            if re.match(r'^\|[\s\-:|]+\|$', line):
                latex_lines.append(r'\hline')
                i += 1
                continue
            
            # Convert table row
            cells = [c.strip() for c in line.split('|') if c.strip()]
            # Process inline formatting in cells
            processed_cells = []
            for cell in cells:
                cell = process_inline_formatting(cell)
                processed_cells.append(cell)
            latex_lines.append(' & '.join(processed_cells) + r' \\')
            i += 1
            continue
        elif in_table:
            latex_lines.append(r'\hline')
            latex_lines.append(r'\end{tabular}')
            latex_lines.append(r'\end{center}')
            in_table = False
        
        # Block quotes
        if line.strip().startswith('>'):
            quote_text = line.strip()[1:].strip()
            quote_text = process_inline_formatting(quote_text)
            latex_lines.append(r'\begin{quote}')
            latex_lines.append(quote_text)
            latex_lines.append(r'\end{quote}')
            i += 1
            continue
        
        # Lists
        if re.match(r'^\s*[-*+]\s+', line):
            # Unordered list
            indent = len(line) - len(line.lstrip())
            item_text = re.sub(r'^\s*[-*+]\s+', '', line)
            item_text = process_inline_formatting(item_text)
            
            if i == 0 or not re.match(r'^\s*[-*+]\s+', lines[i-1]):
                latex_lines.append(r'\begin{itemize}')
            
            latex_lines.append(r'\item ' + item_text)
            
            if i == len(lines) - 1 or not re.match(r'^\s*[-*+]\s+', lines[i+1]):
                latex_lines.append(r'\end{itemize}')
            i += 1
            continue
        
        if re.match(r'^\s*\d+\.\s+', line):
            # Ordered list
            item_text = re.sub(r'^\s*\d+\.\s+', '', line)
            item_text = process_inline_formatting(item_text)
            
            if i == 0 or not re.match(r'^\s*\d+\.\s+', lines[i-1]):
                latex_lines.append(r'\begin{enumerate}')
            
            latex_lines.append(r'\item ' + item_text)
            
            if i == len(lines) - 1 or not re.match(r'^\s*\d+\.\s+', lines[i+1]):
                latex_lines.append(r'\end{enumerate}')
            i += 1
            continue
        
        # Empty lines
        if not line.strip():
            latex_lines.append('')
            i += 1
            continue
        
        # Regular paragraph
        processed_line = process_inline_formatting(line)
        latex_lines.append(processed_line)
        i += 1
    
    # Close any open environments
    if in_table:
        latex_lines.append(r'\hline')
        latex_lines.append(r'\end{tabular}')
        latex_lines.append(r'\end{center}')
    
    return '\n'.join(latex_lines)


def process_inline_formatting(text):
    """Process inline markdown formatting"""
    # Preserve inline math
    parts = []
    current = 0
    
    # Find all inline math segments
    math_segments = []
    for match in re.finditer(r'\$([^\$]+)\$', text):
        math_segments.append((match.start(), match.end(), match.group(0)))
    
    if not math_segments:
        # No math, process normally
        return process_text_formatting(text)
    
    # Process text between math segments
    result = ""
    for i, (start, end, math) in enumerate(math_segments):
        # Process text before this math segment
        if i == 0:
            result += process_text_formatting(text[current:start])
        else:
            result += process_text_formatting(text[current:start])
        
        # Add math segment as-is
        result += math
        current = end
    
    # Process remaining text
    result += process_text_formatting(text[current:])
    
    return result


def process_text_formatting(text):
    """Process text formatting (bold, italic, code) outside of math"""
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', text)
    text = re.sub(r'__(.+?)__', r'\\textbf{\1}', text)
    
    # Italic
    text = re.sub(r'\*(.+?)\*', r'\\textit{\1}', text)
    text = re.sub(r'_(.+?)_', r'\\textit{\1}', text)
    
    # Inline code
    text = re.sub(r'`(.+?)`', r'\\texttt{\1}', text)
    
    # Links [text](url) - just keep the text
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
    
    # Emoji or special markers - keep as-is for now
    
    return text


def generate_main_latex(guide_dir):
    """Generate main LaTeX document"""
    
    latex_preamble = r'''\documentclass[11pt,a4paper]{book}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{amsmath,amssymb,amsfonts}
\usepackage{graphicx}
\usepackage{listings}
\usepackage{xcolor}
\usepackage{hyperref}
\usepackage{geometry}
\usepackage{fancyhdr}
\usepackage{comment}

\geometry{margin=1in}

\hypersetup{
    colorlinks=true,
    linkcolor=blue,
    filecolor=magenta,      
    urlcolor=cyan,
    pdftitle={Automatic Control Systems \& Electronics Guide},
    pdfpagemode=FullScreen,
}

\lstset{
    basicstyle=\ttfamily\small,
    breaklines=true,
    frame=single,
    backgroundcolor=\color{gray!10},
    keywordstyle=\color{blue},
    commentstyle=\color{green!60!black},
    stringstyle=\color{red},
}

\pagestyle{fancy}
\fancyhf{}
\fancyhead[LE,RO]{\thepage}
\fancyhead[RE]{\leftmark}
\fancyhead[LO]{\rightmark}

\title{Automatic Control Systems \& Electronics\\
\large Complete Learning Guide}
\author{Control Systems Learning Repository}
\date{\today}

\begin{document}

\maketitle

\tableofcontents
\newpage

'''
    
    latex_ending = r'''
\end{document}
'''
    
    # Start building the main document
    full_latex = latex_preamble
    
    # Read the main README
    main_readme = os.path.join(guide_dir, 'README.md')
    if os.path.exists(main_readme):
        with open(main_readme, 'r', encoding='utf-8') as f:
            content = f.read()
        
        full_latex += r'\chapter*{Introduction}' + '\n'
        full_latex += r'\addcontentsline{toc}{chapter}{Introduction}' + '\n'
        full_latex += convert_markdown_to_latex(content, level=1)
        full_latex += '\n\n'
    
    # Process each numbered section
    sections = sorted([d for d in os.listdir(guide_dir) 
                      if os.path.isdir(os.path.join(guide_dir, d)) 
                      and d[0].isdigit()])
    
    for section_dir in sections:
        section_path = os.path.join(guide_dir, section_dir)
        readme_path = os.path.join(section_path, 'README.md')
        
        if os.path.exists(readme_path):
            # Extract chapter number and title
            match = re.match(r'(\d+)-(.+)', section_dir)
            if match:
                chapter_num = match.group(1)
                chapter_title = match.group(2).replace('-', ' ').title()
                
                with open(readme_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract the title from the markdown if present
                title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                if title_match:
                    chapter_title = title_match.group(1)
                
                full_latex += f'\\chapter{{{chapter_title}}}' + '\n'
                full_latex += convert_markdown_to_latex(content, level=0)
                full_latex += '\n\n'
    
    # Add appendix
    appendix_dir = os.path.join(guide_dir, 'appendix')
    if os.path.exists(appendix_dir):
        full_latex += r'\appendix' + '\n'
        
        appendix_readme = os.path.join(appendix_dir, 'README.md')
        if os.path.exists(appendix_readme):
            with open(appendix_readme, 'r', encoding='utf-8') as f:
                content = f.read()
            
            full_latex += r'\chapter{Appendix}' + '\n'
            full_latex += convert_markdown_to_latex(content, level=0)
            full_latex += '\n\n'
        
        # Add individual appendix files
        appendix_files = sorted([f for f in os.listdir(appendix_dir) 
                                if f.endswith('.md') and f != 'README.md'])
        
        for appendix_file in appendix_files:
            file_path = os.path.join(appendix_dir, appendix_file)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            title = appendix_file.replace('-', ' ').replace('.md', '').title()
            full_latex += f'\\section{{{title}}}' + '\n'
            full_latex += convert_markdown_to_latex(content, level=1)
            full_latex += '\n\n'
    
    full_latex += latex_ending
    
    return full_latex


def main():
    # Determine paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    guide_dir = os.path.join(repo_root, 'control-and-electronics-guide')
    output_dir = script_dir
    
    if not os.path.exists(guide_dir):
        print(f"Error: Guide directory not found: {guide_dir}")
        sys.exit(1)
    
    print("Generating LaTeX document...")
    latex_content = generate_main_latex(guide_dir)
    
    output_file = os.path.join(output_dir, 'control-electronics-guide.tex')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(latex_content)
    
    print(f"LaTeX document generated: {output_file}")
    print("\nTo generate PDF, run:")
    print(f"  cd {output_dir}")
    print("  pdflatex control-electronics-guide.tex")
    print("  pdflatex control-electronics-guide.tex  # Run twice for ToC")


if __name__ == '__main__':
    main()
