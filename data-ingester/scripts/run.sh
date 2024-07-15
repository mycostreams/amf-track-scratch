#!/bin/bash

DATE_STR=${1:-$(date +"%Y%m%d")}

OUPUT_DIR="/scratch-shared/$USER/images"
OUTPUT_FILE="$DATE_STR.json"

mkdir -p $OUPUT_DIR

# List files and save
rclone lsjson swift:prince-data-dev \
    --include "*/$DATE_STR*.tar" \
    --recursive \
    --files-only \
    > "$OUPUT_DIR/$DATE_STR.json"
