# Conversion Examples

This document shows examples of how different markdown elements are converted to LaTeX.

## Math Formulas

### Inline Math
**Markdown:**
```markdown
The transfer function $G(s) = \frac{K}{s+a}$ represents a first-order system.
```

**LaTeX Output:**
```latex
The transfer function $G(s) = \frac{K}{s+a}$ represents a first-order system.
```

**Rendered:** The transfer function G(s) = K/(s+a) represents a first-order system.

### Display Math
**Markdown:**
```markdown
$$\mathcal{L}\{f(t)\} = F(s) = \int_0^{\infty} f(t) e^{-st} dt$$
```

**LaTeX Output:**
```latex
\[\mathcal{L}\{f(t)\} = F(s) = \int_0^{\infty} f(t) e^{-st} dt\]
```

**Rendered:** A centered, display-style equation.

## Text Formatting

### Bold and Italic
**Markdown:**
```markdown
This is **bold** and this is *italic* text.
```

**LaTeX Output:**
```latex
This is \textbf{bold} and this is \textit{italic} text.
```

### Code
**Markdown:**
```markdown
Use the `pdflatex` command to compile.
```

**LaTeX Output:**
```latex
Use the \texttt{pdflatex} command to compile.
```

## Lists

### Unordered List
**Markdown:**
```markdown
- First item
- Second item with $\omega_n$
- Third item
```

**LaTeX Output:**
```latex
\begin{itemize}
\item First item
\item Second item with $\omega_n$
\item Third item
\end{itemize}
```

### Ordered List
**Markdown:**
```markdown
1. First step
2. Second step
3. Third step
```

**LaTeX Output:**
```latex
\begin{enumerate}
\item First step
\item Second step
\item Third step
\end{enumerate}
```

## Tables

**Markdown:**
```markdown
| Component | Impedance |
|---|---|
| Resistor | $R$ |
| Capacitor | $\frac{1}{j\omega C}$ |
| Inductor | $j\omega L$ |
```

**LaTeX Output:**
```latex
\begin{center}
\begin{tabular}{|l|l|}
\hline
Component & Impedance \\
\hline
Resistor & $R$ \\
Capacitor & $\frac{1}{j\omega C}$ \\
Inductor & $j\omega L$ \\
\hline
\end{tabular}
\end{center}
```

## Code Blocks

**Markdown:**
````markdown
```python
def transfer_function(s):
    return 1 / (s + 1)
```
````

**LaTeX Output:**
```latex
\begin{lstlisting}[language=python]
def transfer_function(s):
    return 1 / (s + 1)
\end{lstlisting}
```

## Block Quotes

**Markdown:**
```markdown
> This is a quote with important information.
```

**LaTeX Output:**
```latex
\begin{quote}
This is a quote with important information.
\end{quote}
```

## Headings

**Markdown:**
```markdown
## Section Title
### Subsection Title
#### Subsubsection Title
```

**LaTeX Output (adjusted for context):**
```latex
\section{Section Title}
\subsection{Subsection Title}
\subsubsection{Subsubsection Title}
```

Note: Heading levels are adjusted based on the document structure (chapters, sections, etc.)

## Special Cases

### Mermaid Diagrams
**Markdown:**
````markdown
```mermaid
graph TD
    A --> B
```
````

**LaTeX Output:**
```latex
\begin{comment}
graph TD
    A --> B
\end{comment}
```

Note: Mermaid diagrams are wrapped in comments since they can't be easily rendered in LaTeX.

### Links
**Markdown:**
```markdown
See [this document](path/to/doc.md) for details.
```

**LaTeX Output:**
```latex
See this document for details.
```

Note: Link text is preserved, but URLs are removed (since they're typically relative paths).

## Statistics

From the actual conversion of the control & electronics guide:

- **Total lines of LaTeX:** 6,302
- **Display math blocks:** 354
- **Inline math expressions:** 716
- **Code blocks:** ~100+
- **Tables:** ~50+
- **Estimated PDF pages:** 200-300

## Benefits

✅ **Math renders perfectly** - All LaTeX notation displays correctly
✅ **Professional formatting** - Book-style layout with proper typography
✅ **Navigable** - Hyperlinked table of contents
✅ **Printable** - High-quality output suitable for printing
✅ **Portable** - Single PDF file, no dependencies
✅ **Searchable** - Full-text search within PDF
✅ **Offline** - No internet or special viewer required
