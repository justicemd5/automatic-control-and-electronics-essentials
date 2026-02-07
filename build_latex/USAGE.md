# Usage Guide: Building PDF Documentation

This guide walks you through generating the PDF documentation from the markdown files.

## Prerequisites Check

Before you begin, verify you have the required tools:

### 1. Check Python
```bash
python3 --version
```
Should show Python 3.x or higher.

### 2. Check LaTeX (pdflatex)
```bash
pdflatex --version
```
Should show pdfTeX version information.

If pdflatex is not found, install a LaTeX distribution:

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install texlive-latex-base texlive-latex-extra
```

**Fedora/RHEL:**
```bash
sudo dnf install texlive-scheme-basic texlive-collection-latexextra
```

**macOS:**
```bash
brew install --cask mactex
# or for minimal installation:
brew install --cask basictex
sudo tlmgr update --self
sudo tlmgr install collection-latexextra
```

**Windows:**
- Download and install [MiKTeX](https://miktex.org/download)
- Or download [TeX Live](https://www.tug.org/texlive/)

## Building the PDF

### Method 1: Using Make (Recommended)

```bash
cd build_latex
make
```

This will:
1. Run `convert_to_latex.py` to generate `.tex` file
2. Run `pdflatex` twice to create the PDF with proper table of contents
3. Output: `control-electronics-guide.pdf`

### Method 2: Manual Steps

If you don't have `make` or want to run steps individually:

```bash
cd build_latex

# Step 1: Generate LaTeX from markdown
python3 convert_to_latex.py

# Step 2: Compile to PDF (first pass)
pdflatex control-electronics-guide.tex

# Step 3: Compile to PDF (second pass for TOC)
pdflatex control-electronics-guide.tex
```

**Why run pdflatex twice?**
- First run: Generates content and saves TOC information
- Second run: Uses saved TOC information to build complete table of contents

## Output Files

After building, you'll see these files:

```
build_latex/
├── control-electronics-guide.tex    # Generated LaTeX source
├── control-electronics-guide.pdf    # Final PDF (this is what you want!)
├── control-electronics-guide.aux    # Auxiliary file (can be deleted)
├── control-electronics-guide.log    # Build log (for debugging)
├── control-electronics-guide.toc    # Table of contents data
└── control-electronics-guide.out    # Hyperlink data
```

The important file is **`control-electronics-guide.pdf`** - open this to view the documentation.

## Cleaning Up

### Remove all generated files including PDF:
```bash
make clean
```

### Remove only intermediate files (keep PDF):
```bash
make clean-intermediate
```

### Manual cleanup:
```bash
rm -f *.aux *.log *.out *.toc
```

## Troubleshooting

### Problem: "python3: command not found"
**Solution:** Install Python 3 for your operating system.

### Problem: "pdflatex: command not found"
**Solution:** Install a LaTeX distribution (see Prerequisites above).

### Problem: Missing LaTeX packages
**Error message:** `! LaTeX Error: File 'xyz.sty' not found.`

**Solution:** Install additional LaTeX packages:
```bash
# Ubuntu/Debian
sudo apt-get install texlive-latex-extra texlive-fonts-extra

# macOS
sudo tlmgr install <package-name>

# Windows (MiKTeX will prompt automatically)
```

### Problem: Unicode errors or missing characters
**Solution:** The document uses UTF-8 encoding. Ensure your LaTeX distribution is up to date:
```bash
# Ubuntu/Debian
sudo apt-get install texlive-fonts-recommended

# macOS
sudo tlmgr update --all
```

### Problem: Build fails with errors
**Solution:** Check the log file:
```bash
cat control-electronics-guide.log | grep -A 5 "!"
```

Common issues:
- Special characters in markdown that need escaping
- Complex markdown formatting not yet handled by converter
- Missing LaTeX packages

### Problem: Math formulas still don't look right
**Solution:** The converter handles most standard LaTeX math. If specific formulas aren't rendering:
1. Check the source markdown file
2. Verify math delimiters (`$...$` for inline, `$$...$$` for display)
3. Look at the generated `.tex` file to see how it was converted

## Customizing the PDF

To customize the PDF appearance, edit `convert_to_latex.py`:

### Change paper size:
Find `\documentclass[11pt,a4paper]{book}` and change to:
- `letterpaper` - US Letter size
- `a4paper` - A4 size (default)

### Change margins:
Find `\geometry{margin=1in}` and adjust as needed.

### Change fonts:
Add font packages in the preamble, e.g.:
```latex
\usepackage{lmodern}  % Latin Modern fonts
\usepackage{palatino} % Palatino font
```

### Change color scheme:
Modify the hyperref setup:
```latex
\hypersetup{
    colorlinks=true,
    linkcolor=red,     % Change from blue
    urlcolor=magenta,  % Change from cyan
}
```

## Viewing the PDF

Once generated, open `control-electronics-guide.pdf` with any PDF viewer:

**Linux:**
```bash
xdg-open control-electronics-guide.pdf
# or
evince control-electronics-guide.pdf
```

**macOS:**
```bash
open control-electronics-guide.pdf
```

**Windows:**
```bash
start control-electronics-guide.pdf
```

## What's Included in the PDF

The generated PDF includes:

✅ All 20 chapters from the guide
✅ Introduction from main README
✅ Appendix with math refreshers
✅ Complete table of contents with hyperlinks
✅ All math formulas properly rendered
✅ Code examples with syntax highlighting
✅ Tables and lists
✅ Block quotes and emphasis

❌ Mermaid flowchart diagrams (not easily convertible)
❌ External code files (.py, .c, .v) - only markdown content

## Performance Notes

- **Conversion time:** Usually completes in under 10 seconds
- **Compilation time:** First pdflatex run takes 30-60 seconds, second run is faster
- **PDF size:** Expect 500KB-2MB depending on content
- **Page count:** Approximately 200-300 pages

## Next Steps

After generating the PDF:

1. **Share it:** The PDF is self-contained and can be shared with others
2. **Print it:** Professional formatting makes it suitable for printing
3. **Study offline:** No need for markdown viewer or internet connection
4. **Annotate:** Use PDF annotation tools to take notes

---

**Happy learning!** If you encounter issues not covered here, please open an issue on GitHub.
