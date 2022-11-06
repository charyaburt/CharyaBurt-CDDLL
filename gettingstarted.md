---
layout: page
title: Getting Started
permalink: /gettingstarted/
nav_order: 2
---

# Getting Started

## Software and Setup

### Software (install in the following order)

* Homebrew
  - Install with the following command: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
* Python 3
  - Install with the following command: `brew install python3`
* Mediainfo
  - Install with the following command: `brew install mediainfo`
* youtube-dl
   - Install with the following command: `brew install youtube-dl`
* FFmpeg
  - Install with the following command:  `brew install ffmpeg`
* Gdrive
 - Install with the following command:  `brew install gdrive`
* Imagemagick
- Install with the following command:  `brew install imagemagick`

### Python Libraries

* Airtable:
  - Install with the following command: `pip3 install airtable-python-wrapper`
* Vimeo:
  - Install with the following command: `pip3 install PyVimeo`

### Setting up Gdrive

The `gdrive` command line app is used to upload files to the Google Drive access repository. However, there is not way to set up this application with a configuration file (as far as I can tell). Instead, `gdrive` will ask you verify the app before you can use it. At this point I'm unsure if you have to do this every time you restart your computer, or if the connection will stay open (more testing to come), so to be safe you should run the `gdrive_setup.sh` script. This is a super simple script that just runs an info query on the Google Drive ID that is specified in the `config.py` file. If the connection isn't open a browser window will open and ask you to copy in a verfification code visible in the terminal window that opens when you run the script. Again, run this script before uploading an Google Drive files.

### API Credentials

You'll need to get API logins and credentials from Airtable and Vimeo.

Rename `config_template.py` to `config.py` and then fill out the credentials from the API websites

Airtable: https://support.airtable.com/hc/en-us/articles/219046777-How-do-I-get-my-API-key-
Vimeo: https://developer.vimeo.com/apps

### Configuration File

This repository comes with a files named `config_template.py`. This is a template for a configuration files, which you'll need to fill out in order to get the Airtable and Vimeo APIs working properly. Make sure that any info you enter into the configuration file is in double quotes, and follows that formatting of the information that's already in there.

Before you can run any of the scripts you'll need to rename `config_template.py` to `config.py` then fill out the empty fields discussed below.

#### General Config Info

This section contains general configuration info.

- *DRIVE_NAME*: This is the name of the drive that the local repository lives on.
- *BACKUP_DRIVE_NAME*: If you want to run `backup_drive.sh` the backup will run from the main drive to whatever drive name you put here.

_NOTE_: If you switch out drives during backup cycles make sure you update the `DRIVE_NAME` field. This field is critical for performing drive and access maintenance.

#### Airtable Credentials and Config

- *BASE_ID This is the ID for the Base that your Airtable lives in. You can get this from XXXX
- *API_KEY*: To get an API key for Airtable you'll need to go to XXXX

#### Vimeo Credentials

- *YOUR_ACCESS_TOKEN*: Get the Vimeo Access Token from XXXX`
- *YOUR_CLIENT_ID*: Get the Vimeo Client ID token from XXXX
- *YOUR_CLIENT_SECRET*: Get the Vimeo Client Secret token from XXXX
- *VIMEO_DEFAULT_DESCRIPTION*: You can create a default description that will be appended to the Vimeo description of every file.

#### Google Drive Config

- *GDRIVE_LINK_TEXT*: This is the text that will go into the field named "Access Link" for files on the Google Drive. It's basically a manual redirect because there's not simple way to password protect a google drive file (for now)
- *GDRIVE_ROOT_ID*: This is the ID of the folder in your Google Drive that all the files will be uploaded to. To get the ID go to the folder you want and copy the string of letters after the last slash in the URL. For example, if the URL is `https://drive.google.com/drive/u/2/folders/a1b2n3m4g5v6j76liksdpe4` then the id is `a1b2n3m4g5v6j76liksdpe4`

#### Dependency Paths

This information comes pre-filled, and should match up with where homebrew installs each application. However, if these applications won't run you can open a terminal window and run the `which` command to see where the current location of each application is.

For example, to find the path of ffmpeg you can run `which ffmpeg` which will return `/usr/local/bin/ffmpeg`. You can then copy and paste `/usr/local/bin/ffmpeg` into the `FFMPEG_PATH` field in the config file.

####Various Hardcoded Values

For now the only hardcoded value is `MAX_SIZE`, which defines how large a file can be before it will have a downscaled access copy created. This is in order to get around Vimeo's size and upload limits. This field is in bytes, so 1500000000 is equal to 1.5GB.

#### Airtable Field References

This section is prefilled to work with the template version of the Airtable. If you decide you'd like to change field name in the Airtable make sure to change the field name here as well. This is how the python scripts know the names of the fields in Airtable.

## Scripts

### addRecord.py

#### Hardcoded Values Airtable Fields Used

##### Hardcoded Values:
- `BASE_ID`
- `API_KEY`
- `DRIVE_NAME`
- `MAX_SIZE`
- `FFMPEG_PATH`
- `CONVERT_PATH`
- `MEDIAINFO_PATH`

##### Airtable Field Names:
- `RECORD_NUMBER`
- `RECORD_STATUS`
- `RECORD_NUMBER`
- `FILE_PROCESS_STATUS`
- `CHECKSUM`
- `PARENT_ID`
- `FILE_COUNT`
- `FILENAME`
- `FULL_FILE_NAME`
- `DURATION`
- `FILE_SIZE_STRING`
- `FILE_SIZE`
- `FILE_FORMAT`
- `VIDEO_CODEC`
- `VIDEO_BIT_DEPTH`
- `VIDEO_SCAN_TYPE`
- `VIDEO_FRAME_RATE`
- `VIDEO_FRAME_SIZE`
- `VIDEO_ASPECT_RATIO`
- `AUDIO_SAMPLING_RATE`
- `AUDIO_CODEC`
- `COPY_VERSION`

#### Airtable Data Entries:
- `FILE_INTAKE_FLAG`

## random thoughts that need to be fleshed output

- Vimeo is very strict about weekly upload limits. If you plan to upload a huge archive to vimeo you should pay for a month of the top tier subscription, upload everything during that month, and then downgrade.
- You should be running record maintenance and access maintenance every month on a schedule
- If the drive audits and file audits return errors you need to fix these right away. It's probably something minor, but don't let it get out of hand
