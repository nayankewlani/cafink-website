#!/bin/bash
# CAFLink Website - Start Script

echo "======================================"
echo "  CAFLink Full-Stack Website"
echo "======================================"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required. Please install it."
    exit 1
fi

# Check Flask
python3 -c "import flask" 2>/dev/null || {
    echo "📦 Installing Flask..."
    pip install flask
}

# Run
echo "🚀 Starting CAFLink server..."
echo "🌐 Open: http://localhost:5000"
echo "======================================
"
python3 app.py
