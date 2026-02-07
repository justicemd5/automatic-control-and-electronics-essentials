# Makefile for generating PDF from markdown documentation
# This converts all markdown files to LaTeX and compiles to PDF

.PHONY: all pdf clean help

# Main target
all: pdf

# Generate LaTeX and compile to PDF
pdf: control-electronics-guide.pdf

# Convert markdown to LaTeX
control-electronics-guide.tex: convert_to_latex.py
	python3 convert_to_latex.py

# Compile LaTeX to PDF (run twice for TOC and references)
control-electronics-guide.pdf: control-electronics-guide.tex
	pdflatex -interaction=nonstopmode control-electronics-guide.tex
	pdflatex -interaction=nonstopmode control-electronics-guide.tex

# Clean generated files
clean:
	rm -f *.aux *.log *.out *.toc *.pdf *.tex

# Clean only intermediate files, keep PDF
clean-intermediate:
	rm -f *.aux *.log *.out *.toc *.tex

# Help target
help:
	@echo "Makefile for Control & Electronics Guide PDF generation"
	@echo ""
	@echo "Usage:"
	@echo "  make          - Generate PDF from markdown files"
	@echo "  make pdf      - Same as 'make'"
	@echo "  make clean    - Remove all generated files including PDF"
	@echo "  make clean-intermediate - Remove temporary files but keep PDF"
	@echo "  make help     - Show this help message"
	@echo ""
	@echo "Requirements:"
	@echo "  - Python 3"
	@echo "  - pdflatex (from TeX Live or MiKTeX)"
	@echo ""
	@echo "Installation (Ubuntu/Debian):"
	@echo "  sudo apt-get install texlive-latex-base texlive-latex-extra"
