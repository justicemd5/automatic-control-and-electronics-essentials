# LaTeX/PDF Documentation Build

This directory contains tools to convert the markdown documentation into a professional LaTeX document and compile it to PDF format. This ensures that all mathematical formulas are properly rendered and viewable.

## Why This Exists

The main documentation is written in Markdown with LaTeX math notation (`$...$` and `$$...$$`). While GitHub and some markdown viewers support math rendering, many text editors and viewers do not display these formulas properly. This LaTeX/PDF build system solves that problem by:

1. Converting all markdown content to LaTeX
2. Compiling it into a single, professional PDF document
3. Ensuring all math formulas are perfectly rendered

## Quick Start

### Prerequisites

You need Python 3 and a LaTeX distribution installed:

**Ubuntu/Debian:**
```bash
sudo apt-get install texlive-latex-base texlive-latex-extra python3
```

**macOS (with Homebrew):**
```bash
brew install --cask mactex
# Or for a smaller installation:
brew install --cask basictex
```

**Windows:**
- Install [MiKTeX](https://miktex.org/download) or [TeX Live](https://www.tug.org/texlive/)
- Install [Python 3](https://www.python.org/downloads/)

### Build PDF

Simply run:
```bash
cd build_latex
make
```

This will:
1. Convert all markdown files to LaTeX
2. Compile the LaTeX document to PDF (runs twice for proper TOC generation)
3. Generate `control-electronics-guide.pdf`

### Manual Build (if make is not available)

```bash
cd build_latex
python3 convert_to_latex.py
pdflatex control-electronics-guide.tex
pdflatex control-electronics-guide.tex  # Run twice for Table of Contents
```

## What Gets Included

The generated PDF includes:

- **Introduction** - From the main README
- **All numbered chapters** (01-foundations through 20-advanced-topics)
- **Appendix** - Mathematical refreshers and reference tables
- **Table of Contents** - Fully linked navigation
- **Properly rendered math** - All LaTeX formulas displayed correctly

## Files

- `convert_to_latex.py` - Python script that converts markdown to LaTeX
- `Makefile` - Automates the build process
- `control-electronics-guide.tex` - Generated LaTeX file (intermediate)
- `control-electronics-guide.pdf` - Final PDF output

## Makefile Targets

- `make` or `make pdf` - Generate the PDF
- `make clean` - Remove all generated files including PDF
- `make clean-intermediate` - Remove temporary files but keep PDF
- `make help` - Show help message

## Customization

The LaTeX document uses:
- **Document class:** `book` (11pt, A4 paper)
- **Margins:** 1 inch on all sides
- **Packages:** AMS Math, hyperref (for links), listings (for code)
- **Style:** Chapters, sections, subsections with proper hierarchy

To customize, edit the `latex_preamble` in `convert_to_latex.py`.

## Features

### Math Rendering
- Inline math: `$E = mc^2$` → $E = mc^2$
- Display math: `$$\int_0^\infty e^{-x} dx = 1$$` → Centered equation
- All math symbols and Greek letters properly rendered

### Code Blocks
```python
# Code is displayed in monospace with syntax highlighting
def control_system():
    return "properly formatted"
```

### Tables, Lists, and More
- Tables converted to LaTeX tabular
- Bullet and numbered lists
- Block quotes
- Links (text is kept, URLs in footnotes)

## Troubleshooting

**Error: "pdflatex: command not found"**
- Install a LaTeX distribution (see Prerequisites above)

**Error: Missing packages**
- Install the full TeX Live distribution: `sudo apt-get install texlive-full`

**Error: Unicode characters not displaying**
- The document uses UTF-8 encoding with T1 font encoding, which should handle most characters

**PDF has missing content**
- Check that markdown files are in the expected locations
- Mermaid diagrams are intentionally excluded (not easily convertible to LaTeX)

## Notes

- Mermaid diagrams (flowcharts) are excluded from the PDF as they require external tools
- Python/C/Verilog code examples from `.py`, `.c`, `.v` files are not auto-included, only markdown content
- The conversion handles most markdown features, but some advanced formatting may need manual adjustment

## Contributing

If you find conversion issues:
1. Check the markdown source for unusual formatting
2. Edit `convert_to_latex.py` to handle the specific case
3. Test by running `make clean && make`
4. Submit a pull request with your improvements
