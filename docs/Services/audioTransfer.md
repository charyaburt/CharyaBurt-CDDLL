---
layout: page
title: Audio Transfer Workflow
parent: Services
---

# Audio Transfer Workflow

# Baking
* Test the tape to see if it's sticky
    - If the tape is from the 80's or later and has black backing, it's likely sticky
    - Test the tape by slowly unreeling the tape off the reel. If it's sticky, the tape will not easily fall off the reel.
    - If you are already playing back the tape and it's squaling, it will need to be baked.
    - Only bake tapes that are polyester, NEVER bake acetate tapes. An easy way to remember this is "if it's opaque, you can bake!" Acetate tapes are translucent when held up to bright lights, and will melt if you bake them.
* If sticky, bake the tape using Program 3
    - 50 degrees C
    - 4.0 degrees C/min
    - 48 hour cycle
    - Fan speed 60%
* Salesforce
    - Notate any baking you do as a Preservation Activity in Salesforce
        - Click "New Preservation Activity" from the Preservation Object page
        - Select the date
        - Select "Baking"
        - Make sure the correct Preservation Object is associated
        - Make sure a note about which program was used, or any extra info

# Audio Transfer Station Setup
* Here is the typical signal chain for an analog audio transfer
    - Tape Deck (Otari for Reel to Reel, Tascam for cassettes)
    - A/D converter (MOTU Ultralite Mk4)
    - Computer (Mac laptop running REAPER)
* Set up the signal chain
    - Connect the Left and Right outputs of the Tape Deck to Inputs 1 and 2 respectively of the MOTU.
    - Connect the MOTU to the Mac laptop via USB
    - Open REAPER, create a new project
        - Press *File -> Open* in *New Project* tab
        - Select a template by pressing *File -> Project Template*
            - Select the appropriate template for the tape type you're using
            - Analog tapes: ***96k_24b_Analog***
            - DAT tapes: ***48k_16b_DAT***
            - MiniDisc: ***48k_16b_DAT***
        - Name the project after the BAVC Barcode Number. Save it in a folder named after the Opportunity on the Scratch RAID
        - Make sure the project settings are correct. You can see them at the top of the screen.
    - Project Templates should have the inputs already set up. However, you can click on the audio meters per track to set the inputs accordingly.
* You can monitor the audio being recorded on the studio monitors. Make sure they are on and click the "Main Volume" encoder on the MOTU until Main 1-2 appears. Adjust the levels appropriately.

# Salesforce
* Fill out the ***Transfer Environment*** section
    - Transfer Suite (Preservtion Grotto)
    - Transfer Technician (User)
    - Transfer Date
    - Source Deck
    - TBC/Frame Sync 1 (will always be None)
    - SDI Converter (will always be None)
    - Host Computer
    - Operating System Name
    - Operating System Version
    - Capture Hardware
    - Capture Software
* Fill out the ***Audio Metdata*** sections. This metadata gets embedded directly into the audio files, so make sure it is correct and has no typos! You can get this info either from the metadata provided by the client, or from the content on the tape.
    - Audio Metadata: Title
         - You can just use the label if it is descriptive. If not, just give it a good title according to the metadata. If that doesn't work, just enter the barcode.
    - Audio metadata: Artist
        - If there is an interviewee, artist, or musician and you have their full name, use that. If you can't get that then use the Archive or Collection Holder's name.
    - Audio metadata: Date
        - Enter the original recording date if you have it. If not, leave blank.
    - Audio Metadata: Album
        - Use the collection name if you have it. If not, use the Archive or Collection Holder's name.

# Prep
* Track Configuration
    - Determine what the track configuration is
* Leader
    - When auditioning, test to see if the audio goes right to the beginning and end of the tape. If so, add leader to either side before transferring.
* Levels
    - The Otari decks are calibrated against test tones. However, if the levels are way too low or clipping, you can turn off SRL (Standard Record Level) and adjust the levels manually.
* Cleaning
    - Clean the entire signal path of the tape deck with cotton swabs, texwipes, and isopropyl alcohol before transferring.
* Salesforce
    - Fill out the ***Audio Transfer Elements*** section
        - Audio Material Type
        - Audio Speed
        - Audio Reel Size
        - Audio Track Configuration
        - Audio Sound Configuration
        - Audio Transfer Notes (This is just to be used for internal notes, this does not go to the client)
    - ***BUG REPORT***
        - *You'll also need to fill out all of the Video Transfer Elements, or Salesforce won't let you save the record. This will be fixed.*

# Transferring
* During the transfer process, monitor the audio and make notes about any momentary or constant errors. Make sure to pass on as much information about the audio to the client.
* There are two Salesforce fields where we put information about the audio quality. Each has a slightly different format:
    - Technicians Notes
        - This field contains info about the audio quality in general
        - Here are some common notes
            - Audio Buzz
            - Audio Hiss
            - Native Clipping
            - Wow and flutter
            - Low recording levels
    - Timecode Stamped Notes
        - This field contains info for momentary errors, or any content of note specific to a certain time.
        - Use the following format for each instance:
            - HH:MM:SS - This is a timecode stamped note;
            - HH:MM:SS - Every note but the last ends with a semicolon;
            - HH:MM:SS - The last note does not have a semicolon

# Post-Digitization
* Exporting the file
    - Trim the audio to the appropriate length and according to project/client specs
        - Default is 5 seconds or less of silence at the tail or head
    - Press *File -> Render*
    - Select the proper Sample Rate and Bit Depth, according to the recording specs
    - Name the output files appropriately
        - BAVC#######_ClientID_Face##
    - Press *Render 1 File*
* Updating Metadata
    - The transcode engine will automatically insert metadata into the files. This needs to come from the following fields in Salesforce:
        - Audio Metadata: Title
            - *No apostrophes or quotes!*
        - Audio Metadata: Artist
            - *Use artist or interviewee name is possible*
        - Audio Metadata: Date
            - *Must be in format YYYY-MM-DD*
        - Audio Metadata: Album
            - *Use collection name if possible*
    * Creating Derivatives
        - transcodeEngine.py can process audio files
            - Select 1 derivative
            - Select MP3
            - Select bitrate (default is 320kbps)
    * Moving to the SAN for QC
        - If not mounted, mount the SAN
            - Select Finder
            - Go -> Connect to Server... (or ⌘K)
            - Server address is *smb://presfsan*
        - Make sure there is a folder on the SAN for the Opportunity
        - rsync -av --progress [path to sounce file/folder] [path to destination folder]
    * Backup file on PresRaid
        - If not mounted, mount the PresRaid
            - Select Finder
            - Go -> Connect to Server... (or ⌘K)
            - Server address is *smb://presraid*
        - Make sure there is a folder on the PresRaid for the project
        - rsync -av --progress [path to sounce file/folder] [path to destination folder]
    * Salesforce
        - Once this is all complete, fill out the following fields:
            - Loaded to PresRaid
            - Digitization Status (Pass)
