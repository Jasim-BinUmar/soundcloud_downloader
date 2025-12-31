#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: ./download.sh [SOUNDCLOUD_URL]"
    exit 1
fi

cd "$(dirname "$0")"
source venv/bin/activate
python main_console.py "$1"

