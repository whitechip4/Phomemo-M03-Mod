#!/bin/bash
# Python formatter script using black
# Usage: ./format_python.sh <target_file_or_directory>

if [ $# -lt 1 ]; then
    echo "Usage: $0 <target_file_or_directory>"
    exit 1
fi
TARGET="$1"
if [ ! -e "$TARGET" ]; then
    echo "Target '$TARGET' does not exist."
    exit 1
fi

# Run black formatter
black "$TARGET"
RESULT=$?
if [ $RESULT -eq 0 ]; then
    echo "Formatted: $TARGET"
else
    echo "Formatting failed."
    exit $RESULT
fi
