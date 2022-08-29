#!/bin/bash

GoogleID=$( cat "$(dirname "$0")/config.py" | grep "GDRIVE_ROOT_ID" | awk -F '"' '{print $2}' | awk 'NR==1{print $1}' )
gdrive info $GoogleID
