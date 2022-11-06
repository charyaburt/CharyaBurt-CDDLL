---
layout: page
title: Video Transfer Workflow
parent: Services
---

# General Tape Transfer Workflow

## Start of Day

* Check that the previous day's transcodes and scripts have completed processing
* Restart every computer that ran overnight
* Patch the Audio and Video for the format you are using at your station
* Power on all equipment, allowing it to warm up (monitor, TBC, scopes, blackburst, audio mixer, etc)
* Empty the dehumidifier located in the Tape Closet if necessary
* Pack and/or clean tapes prior to transfer
* Bring only the tapes you intend on capturing for the day to your Capture Station

## Capturing with vrecord

* Follow **Start of Day** steps above to ensure that your station is ready to run
* Clean deck thoroughly, ensuring the entire tape path and heads are free of dirt
* Open **Terminal** and type in **vrecord -p** (passthrough mode)
* Ensure that your video settings in **vrecord** are correct. If not, type **vrecord -e** and select the appropriate configuration for that specific client and/or format. Return to vrecord's passthrough mode
* Insert a Bars & Tone tape to adjust waveform/vectorscope and audio within Broadcast range (or -18dB)
    - In some case, audio levels may need to be adjusted on a TBC
* Eject the Bars & Tone tape and insert or thread the client tape to be captured
* Observe the threading and press Play (if necessary)
    - Watch and listen to the tape movement in the deck. If there is ever any sign of struggling or loud squeaking; if you have any concerns whatsoever - **STOP THE TAPE**
* Set the levels to the program utilizing the scopes or **vrecord** to guide you
    - If Bars & Tone is present on the client tape, set to these levels first. If those levels are off, make subjective adjustments to the content
    - If you feel your eyes have adjusted and hue or saturation is still off, look away for 30 seconds and come back to it
* Set the audio levels during the loudest moments of the content.  Do not allow the dB to drift into single digits. -10 dB should be the threshold
* Center the Horizontal framing by locating Input H-Position or H-Pos in a TBC
* If you are pleased with the settings, rewind and eject the tape, and re-clean the tape path
* Open **Salesforce** and locate the Preservation Object by typing in the tape's 7-digit barcode
* Copy the entire *Digital File Name*
* Exit and reopen vrecord, this time typing in **vrecord -e**
* Double check that the configuration is correct
* Follow the prompts and paste the digital file name where it asks for the *Client Identifier*
    - Type **_take01** to the file name
* Press *Enter* to activate the capture. Start/play the tape from head at the same moment

## Capturing with Media Express (only do this if you need to capture timecode or an upscaled video from the Teranex)

* Open **BlackMagic Media Express**
* Open **Log and Capture** window
* Save Media Express project as the same name as the project folder, and save to folder
* In the top right-hand corner, go to **Preferences** and set **Capture Audio and Video To:** and **Capture Still Frames To:** to your project folder on the storage raid
* While in **Preferences**, ensure that **Project Video Format** is set to the correct settings:
    - For analog tape captures:
        - **Framerate:** 29.97 NTSC
        - **Capture File Format:** 10 bit Uncompressed
        - **Use Dropped Frame Timecode** should be checked
    - For upscale HD captures:
        - **Framerate:** Make sure to set this according to the client’s specifications
        - **Capture File Format:** ProRes 422 HQ
        - **Use Dropped Frame Timecode** should be checked
* Navigate to **Blackmagic Desktop Video Setup** (should be in the dock) and ensure that your settings are correct for both video and audio set up
* Use bars and tone tape to set levels
* Ensure your capture station is set up correctly for the selected format AND the video input you are using

## During the Capture

* Keep your eyes and ears on the transfer, taking notes on any artifacts or errors
    - Notate these artifacts using the following timecode formula *HH:MM:SS* (Hours, Minutes, Seconds)
        - Example: *01:13:42 - Crash record;*
    - Regularly check the waveform monitor and vectorscope as you capture, being watchful for signal variances outside of broadcast range
    - Watch the audio meters, ensuring that the audio is not peaking
* Once the recorded content has ended, press *Esc*
* Ensure no more content exists on tape. If complete, rewind the tape fully
* Eject or remove the tape and return it to it's case
* Wrap a green elastic band around the tape/case if the capture was successful.  If unsuccessful, wrap an orange elastic band
* Clean the tape path

## File Trimming

* There is now a script that can help with file trimming, located on the SAN
    - /Volumes/SymplyUltra/Scripts/trimmer.sh
* Open a terminal window
* Drag in the script or type in the path to the script above
* Drag in the file you want to trim
* Enter the timecode you want the trimmed file to start and end in the format HH:MM:SS
* Optional: enter how many hours you want the script to wait before running
* This script only works on uncompressed .mov files. DV files (even .movs created from DV) will need to be trimmed manually using this ffmpeg command:
    - **ffmpeg -i [input file] -ss HH:MM:SS -to HH:MM:SS -c copy [output file]**

## Transcoding

* Generally, transcoding should take place EOD as to not interfere with other processing
* If the file was captured to a local RAID, it will first need to be rsync'd to the **SAN**
* Regular BAVC clients and archives (such as the Walt Disney Archives**) have variable requests pertaining to their deliverables. Check the project's **Salesforce Opportunity** for those specifications prior to creating the derivatives
* For the most commonly used script, open **Terminal**
    - Drag in the file from the SAN scripts folder called **transcodeEngine.py**
    - Add one space and type *-i*
    - Drag the folder containing similar .mov files to be transcoded alike (i.e. all files with left channel audio only - do not mix)
    - Hit *Enter* and follow each step
         1. creates the Access file or H.264/MP4
            - De-interlace (unless otherwise specified)
            - Choose how to map the audio (Usually choosing from “Keep Original” or “Sum Stereo to Mono”)
            - 640x480 unless otherwise specified
         2. creates the Mezzanine file or ProRes/MOV
            - De-interlace (unless otherwise specified)
            - Choose how to map the audio (typically “same as original” unless otherwise specified)
        - Move the files to the PresRaid
            - When prompted, enter the folder name on the PresRaid, i.e. *PV22_ClientName*
                - Note: you do not need to type in the full path to the project folder, the script will automatically assume it goes in the *InProgress* folder
        - Create a QCTools file and Checksum
            - We typically create MD5 checksums without sidecar files

## Update Salesforce

* **Transfer Details**
    - Fill out the ***Transfer Environment*** section
    - Fill out the ***Video Transfer Elements*** section
* **Signal Notes**
    - There are two Salesforce fields where we put information about the tape quality. Each has a slightly different format:
        - Technicians Notes
            - This field contains information about the tape's quality in general
            - Here are some common notes:
                - Intermittent dropouts
                - Flagging
                - Headswitch error in underscan
                - Audio buzz
                - Audio hiss
        - Timecode Stamped Notes
            - This field contains information for mandatory errors, or any content of note specific to a certain time
            - Use the following format for each instance:
                - HH:MM:SS - This is a timecode stamped note;
                - HH:MM:SS - Every note but the last ends with a semicolon;
                - HH:MM:SS - The last note does not have a semicolon
* **Digital File Metadata**
    - The **transcodeEngine.py** script will create a mediainfo.py file and automatically sync this file to Salesforce. If you want to do the sync manually you can run the **sfsync.py** script in the Scripts folder on the SAN
    - If you want to refresh the metadata in Salesforce, you can recreate it from any file or a folder of files using the **metaharvest** script

## End of Day

* Power off all decks, monitors, and power conditioners
* Clean the deck(s) and replace the tops
* Return tapes to the tape closet
* Empty the dehumidifier
* Turn off lights and lock door(s)
