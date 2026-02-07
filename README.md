# Automatic Control Systems & Electronics Essentials

A comprehensive, rigorous learning repository for mastering control theory, analog & digital electronics, signal processing, and embedded systems.

## 📖 Documentation

The main documentation is located in the [`control-and-electronics-guide/`](control-and-electronics-guide/) directory.

**Start here:** [control-and-electronics-guide/README.md](control-and-electronics-guide/README.md)

## 📄 PDF Version Available

**Math formulas not displaying correctly?** 

We provide a LaTeX/PDF build system that converts all documentation into a professionally formatted PDF with perfectly rendered mathematical formulas.

```bash
cd build_latex
make
```

This generates `control-electronics-guide.pdf` containing all chapters with proper math rendering.

**Requirements:**
- Python 3
- LaTeX distribution (TeX Live, MiKTeX, or MacTeX)

See [build_latex/README.md](build_latex/README.md) for detailed instructions.

## 🎯 What's Inside

- **20 Comprehensive Chapters** covering everything from foundations to advanced topics
- **Mathematical Modeling** with differential equations, Laplace transforms, and state-space
- **Control Theory** including PID, root locus, Bode plots, modern control, and robust control
- **Electronics** covering analog, digital, and power electronics
- **Embedded Systems** with real-time control and microcontroller implementation
- **Industrial Applications** including PLCs, SCADA, robotics, and automation
- **Worked Examples** with code in Python, C, and Verilog

## 🚀 Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/justicemd5/automatic-control-and-electronics-essentials.git
   cd automatic-control-and-electronics-essentials
   ```

2. **Start learning:**
   ```bash
   cd control-and-electronics-guide
   # Read README.md and begin with 01-foundations/
   ```

3. **Generate PDF (optional):**
   ```bash
   cd build_latex
   make
   ```

## 📚 Repository Structure

```
.
├── control-and-electronics-guide/    # Main documentation
│   ├── 01-foundations/
│   ├── 02-mathematical-modeling/
│   ├── 03-signals-and-systems/
│   ├── ...
│   └── 20-advanced-topics/
│
└── build_latex/                      # PDF generation tools
    ├── convert_to_latex.py
    ├── Makefile
    └── README.md
```

## 🎓 Who This Is For

- Engineering students (EE, ME, CS) learning control systems
- Self-taught engineers wanting to master controls and electronics
- Software engineers transitioning to embedded/controls
- Practicing engineers broadening their knowledge

**Prerequisites:** Calculus, linear algebra, basic physics, and programming

## 📖 Learning Path

### For Beginners
Start at [01-foundations](control-and-electronics-guide/01-foundations/) and work sequentially through each numbered chapter.

### For Experienced Engineers
Jump directly to the topics you need - each section is self-contained with cross-references.

## 🛠️ Tools & Dependencies

- **Python 3.8+** with NumPy, SciPy, Matplotlib, python-control
- **GCC/ARM-GCC** for embedded examples (optional)
- **LaTeX** for PDF generation (optional)

See [control-and-electronics-guide/README.md](control-and-electronics-guide/README.md) for complete installation instructions.

## 💡 Philosophy

1. **Mathematics is the language** - but always explained with physical intuition
2. **No oversimplification** - every "why" is answered alongside every "how"
3. **Hands-on learning** - runnable code examples for every concept
4. **Trade-offs are explicit** - real engineering is about choosing among imperfect options

## 📝 License

This guide is provided for educational purposes. All examples are original or based on standard textbook formulations with proper attribution where applicable.

## 🤝 Contributing

Found an issue or want to improve the content? Contributions are welcome!

---

**Begin your journey:** [control-and-electronics-guide/README.md](control-and-electronics-guide/README.md)

*"The best way to understand control systems is to close the loop between theory and practice."*
