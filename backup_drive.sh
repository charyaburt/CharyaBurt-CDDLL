#!/bin/bash

source_drive=/Volumes/$(cat "$(dirname "$0")/config.py" | grep "DRIVE_NAME" | awk -F '"' '{print $2}' | awk 'NR==1{print $1}')
backup_drive=/Volumes/$(cat "$(dirname "$0")/config.py" | grep "BACKUP_DRIVE_NAME" | awk -F '"' '{print $2}')

find "$source_drive" -not -path '*/.*' -mindepth 1 -maxdepth 1 -exec rsync -avv --progress {} "$backup_drive" \;
