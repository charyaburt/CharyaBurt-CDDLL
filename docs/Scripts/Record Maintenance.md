---
layout: page
title: Record Maintenance
parent: Scripts
---

# Record maintenance

This is run using the script named `recordMaintenance.py`

This script is used to update records and perform the regular maintenance required for long-term preservation. It can be run with different flags in order to run specific subprocesses. No matter which flags are used the script will perform three audits before any extra subprocesses can be run:

- *Drive Audit*: This checks every record/folder on the drive and makes sure that it has a corresponding active (non-deaccessioned) Airtable record.
- *Airtable Audit*: This checks every active record on the Airtable and makes sure that it has a corresponding folder on the drive.
- *File Audit*: This checks every file record related to an active record on the Airtable and makes sure that it appears on the drive in the location that Airtable thinks it should be.

## Record Maintenance Subprocesses

- *Get Checksums*: This is run by using the `-gc` flag. This will run through Airtable to see if any `File` type records (excluding albums) are missing a checksum. If it finds a missing checksum the checksum will be harvested from the file and put into Airtable. This isn't really necessary anymore because checksums are harvested at the time of ingest, but we decided to keep the script around in case a checksum gets lost or falls out of date.
- *Validate Checksums*: This is run by using the `-vc` flag. This will validate the Airtable checkum against the file on the drive's checksum for every `File` type record in Airtable. It will throw an error if the checksum fails.
- *Deaccession*: This is run by using the `-da` flag. This will go through the airtable and find any records marked with the status `Deaccessioned Record`. If a record has this status it will be moved to the `_Trash` folder on the drive, and any associated `File` type records will deleted from the Airtable. This subprocess actually runs before the audits because deaccessioned records need to be handled properly before the audits can be properly passed.

If any of these three audits fail, the script will ask you to fix the problems before you continue. It it possible to skip the audits, but it is HIGHLY recommended that you not do so, since updating an out of sync drive or Airtable can cause more problems in the future.

## Hardcoded Values Airtable Fields Used
The following entries from `config.py` are used in this script. you'll need to update the config file if you've made

### Hardcoded Values:

- `BASE_ID`
- `API_KEY`
- `DRIVE_NAME`
- `VIMEO_DEFAULT_DESCRIPTION`

### Airtable Field Names:
- `RECORD_NUMBER`
- `RECORD_STATUS`
- `RECORD_STATUS_LOOKUP`
- `FILE_FORMAT`
- `FILE_COUNT`
- `FULL_FILE_NAME`
- `CHECKSUM`
- `CHECKSUM_VALID`
- `CHECKSUM_VALID_DATE`
- `FILES_IN_RECORD`

### Airtable Data Entries:
- `RECORD_DEACCESS_FLAG`
