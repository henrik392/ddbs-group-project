#!/bin/bash
# Compile LaTeX report to PDF

echo "======================================================================"
echo "Compiling Distributed Database System Report"
echo "======================================================================"
echo ""

cd "$(dirname "$0")"

# Check if pdflatex is installed
if ! command -v pdflatex &> /dev/null; then
    echo "❌ Error: pdflatex not found!"
    echo ""
    echo "Please install LaTeX:"
    echo "  macOS:   brew install --cask mactex"
    echo "  Ubuntu:  sudo apt-get install texlive-full"
    echo "  Windows: Install MiKTeX from https://miktex.org/"
    exit 1
fi

# Check if screenshots exist
if [ ! -d "screenshots" ] || [ -z "$(ls -A screenshots 2>/dev/null)" ]; then
    echo "⚠️  Warning: screenshots/ directory is empty or missing"
    echo "   The PDF will compile but images will be missing."
    echo "   See SCREENSHOT_GUIDE.md for instructions."
    echo ""
fi

echo "[1/3] First pass (resolving references)..."
pdflatex -interaction=nonstopmode report.tex > /dev/null

echo "[2/3] Second pass (building bibliography)..."
pdflatex -interaction=nonstopmode report.tex > /dev/null

echo "[3/3] Final pass (finalizing document)..."
pdflatex -interaction=nonstopmode report.tex

# Clean up auxiliary files
echo ""
echo "Cleaning up auxiliary files..."
rm -f report.aux report.log report.out report.toc

echo ""
echo "======================================================================"
if [ -f "report.pdf" ]; then
    echo "✓ Success! Report compiled: docs/report.pdf"
    echo "======================================================================"
    echo ""
    echo "File size: $(du -h report.pdf | cut -f1)"
    echo ""
    echo "To view: open report.pdf"
else
    echo "❌ Error: Compilation failed!"
    echo "======================================================================"
    echo ""
    echo "Check report.log for errors"
    exit 1
fi
