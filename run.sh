#!/bin/bash
# WTQ Utility Bill Decoder - Run Script

set -e

# Activate venv
source venv/Scripts/activate

# Move to source
cd source

# Run main
python src/main.py "$@"
