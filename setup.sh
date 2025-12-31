#!/bin/bash

echo "Setting up SoundCloud Downloader..."

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Setup complete!"
echo ""
echo "To use the downloader:"
echo "  Console version: source venv/bin/activate && python main_console.py [URL]"
echo "  GUI version: source venv/bin/activate && python main_ui.py"

