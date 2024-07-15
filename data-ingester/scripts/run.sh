#!/bin/bash

while getopts "d:" opt; do
   case "$opt" in
       d) DATE_STR=${OPTARG};;
   esac
done

OUPUT_DIR="/scratch-shared/$USER/images"
mkdir -p $OUPUT_DIR

OUTPUT_FILE="$DATE_STR.json"

# List files and save
rclone lsjson swift:prince-data-dev \
    --include "*/$DATE_STR*.tar" \
    --recursive \
    --files-only \
    > "$OUPUT_DIR/$DATE_STR.json"
