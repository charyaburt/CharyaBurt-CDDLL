---
layout: page
title: Bash Helper Scripts
parent: Scripts
---
# Bash Helper Scripts

There are currently a number of small helper scripts that help the user complete simple tasks. There scripts all end in `.sh` and if configured properly can be run simply by doubleing clicking.

## add_record_single.sh

This very simply just runs the `addRecord.py` script. It's made to be run by someone who isn't comfortable running a terminal command. This is all it does:

```
cd "$(dirname "$0")"
python3 addRecord.py
```

## add_record_batch.sh

Similar to the above script, but it runs `addRecord.py` with the `-b` flag for batch mode. 

```
cd "$(dirname "$0")"
python3 addRecord.py -b
```

## backup_drive.sh

This script is used to automatically backup files from the main drive to a backup drive. The name of each drive is defined in the config file.

This is the command it runs:

```
find "$source_drive" -not -path '*/.*' -mindepth 1 -maxdepth 1 -exec rsync -avv --progress {} "$backup_drive" \;
```

`$source_drive` and `$backup_drive` come from `DRIVE_NAME` and `BACKUP_DRIVE_NAME` respectively in `config.py`, but have `Volumes/` added to the beginning.

## gdrive_setup.sh

This script only needs to be run once, the first time a computer is used to upload a file to GDrive. It allows the user to verify that the computer being used can upload and edit files on the Google Drive folder defined in the config file

The command it runs is quite simple, it's just this:

```
gdrive info $GoogleID
```

where `$GoogleID` is the `GDRIVE_ROOT_ID` variable stored in `config.py`

## mediainfo_to_csv.sh

This script was initially used to harvest metadata from media files on the hard drive. This script is no longer used and should be deleted once it is safe to do so
