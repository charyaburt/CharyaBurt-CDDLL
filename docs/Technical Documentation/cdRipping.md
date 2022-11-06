---
layout: page
title: CD Ripping
parent: Technical Documentation
---

# CD Ripping

There are generally 2 types of CDs: CD-ROM and CD-DA. CD-ROMs contain an imaged volume with data, and can generally be treated like DVDs but with slightly different ripping parameters. CD-DAs contain just audio, and need to be ripped with special software.

## Ripping CD-DA discs

At BAVC we have created specific workflow for ripping CD-DAs. Our preferred method is to use XLD to rip the CD to a single WAV file. Once the file is ripped, it is possible to either create just a single MP3 access file per disc, or to split the MP3 access files according to the original tracklist on the CD.

The reason we rip the CD as a single WAV file is because it's easier to manage a single file. Our system has trouble keeping track of multiple files in a single record, especially if the number of files is variable like it often is with CDs. However, since our automation embeds the tracklist into the file, the original tracklist can always be extracted from the single WAV file.

## Required Software

* XLD
   * You can install by either:
      * Installing the DMG file from [this site](http://sourceforge.net/projects/xld/files/xld-20220917.dmg)
      * If you have homebrew install you can run the command `brew install xld`


## How To Rip
* Create folder with unique file name (BAVCbarcode_client ID)
* Open XLD, set output directory to new folder
* Under file name, set to custom and paste in folder name
* Under CD Rip, set ripping mode to CDParanoia III 10.2
* Click the following settings
   * REQUIRED
      * **Ripper Mode**: CDParanoia III 10.2
      * **Read samples offset correction value**: 0
         * ✅ Set automatically if possible.
      * **Save Log File**: Always
      * **Save Cue File**: Always
   * OPTIONAL
      * **Max retry count**: 20
         * You can set this to more or less if you’d like.
      * **Drive Speed Control**: Automatic
      * ✅ Query AccurateRip database to check integrity
      * ✅ Automatically open disc upon insertion
      * All other fields are optional, set them as you'd like
   * You can use this image for reference:
      * ![XLD Options]({{site.baseurl}}/assets/images/XLD-Options.png)
   * Insert CD
   * Second window will pop up. Make sure option in top left says *Save as a single file (+ cue)*
      * ![XLD Ripping]({{site.baseurl}}/assets/images/XLD-ripping.png)
   * Make sure you rip as a single file!


## During Rip
* Barcode Case
* Do NOT barcode CD
* Update Intake details
* Update as much of the following metadata fields as possible. Any of these fields can be left blank if they are unknown or unapplicable
   * **Embedded Metadata: Title**
      * Label on the tape
      * Or, if the title is clearly a subset of the label just put the title
   * **Embedded Metadata: Artist**
      * Music or art = Main artist or musical group
      * Oral history or interview = Interviewee’s name
   * **Embedded Metadata: Date**
      * Year only = 1/1/YYYY
      * Year and month  = MM/1/YYYY
      * Year months and day = MM/DD/YYYY
      * Unknown = leave blank
   * **Embedded Metadata: Album**
      * If it’s actually an album then use the album name
      * Otherwise, use the collection name
   * **Embedded Metadata: Institution**
      * Use the collection holder’s institutional name
   * **Embedded Metadata: Comment**
      * Optional field, but could include any errors encountered during transfer or any other salient information
      * Mention if the tracklist noted in liner notes or on the container differs from the cue file tracklist.
      * Essentially, any information from the Technicians Notes field could go here, but it is optional
   * **Embedded Metadata: Copyright**
      * If the collection holder has mention specific copyright information it should be included here. This is mostly used by California evealed
   * **Technicians Notes**
      * Any errors encountered during transfer or any other salient information
      * Mention if the tracklist noted in liner notes or on the container differs from the cue file tracklist.

## After Rip
* Rename log file to match ripped wav file name, but with .log extension
* Check log file for track number, any errors
   * If there are errors, Mark file as review in Salesforce and check the file’s spectrogram for an obvious errors
   * If no errors are audible in the file or clearly visible in the spectrogram you should note any errors mentioned in the log in the Technicians Note, mark the file as pass and move on.
* Run the [`cdEngine.py`](https://github.com/bavc/videomachine/blob/master/cdEngine.py) script on a folder containing all folders that need to be processed. Check to ensure metadata is uploaded on Salesforce
   * Run the script with the following command to create a single MP3 from the rippped WAV file:
      - `cdEngine.py -i /Path/To/Folder`
   * Run the script with the following command to create an MP3 for every track on the original CD file:
      - `cdEngine.py -i /Path/To/Folder -s`
   * Run the script with the following command to create an MP3 for every track on the original CD file, along with a single MP3 containing all of the CD content:
      - `cdEngine.py -i /Path/To/Folder -s -m`
   * It is also possible to run the `cdEngine.py` script on a single folder containing the files for a single CD if you’d like.

## Quality Control

### Bulk Quality Control
Since CDs are often transferred in large volumes, it’s best to check specifics about the metadata in bulk using BWFMetaEdit.

* Open BWFMetaEdit
* Drag the folder containing all the CD subfolders into BWFMetaEdit.
* Technical Metadata Check
   * Click on the Tech tab
   * Check that every file meets the following specs:
      * **Format**: Wave
      * **CodecID**: 0001
      * **Channels**: 2
      * **SampleRate**: 44100
      * **BitRate**: 1411200
      * **BitPerSample**: 16
      * *Note: The specifications for CDs are very strict. If any of these specs don’t match then the file wasn’t properly ripped from the CD*
* Descriptive Metadata Check
   * Click on the Core tab
   * Make sure that the embedded descriptive metadata for every file makes sense and has been properly filled out.
   * Here are the fields that are most important to check
      * **Description**
         * Should include the Title and the date. Make sure it doesn’t include the date twice by accident, which is a common way for this to fail based on how the script works.
      * **Originator**
         * Should be “BAVC”
      * **OriginationDate**
         * Should be the date the file was ripped, so within a few days of QC
      * **BextVersion**
         * Should be “1”
      * **CodingHistory**
         * Should contain the entire log file. If it’s empty there is an error
      * **ICRD**
         * Should be the original recording date of the CD (if it exists)

### File by file Quality Control
For the most part these files can be QC’d in bulk, but there are a few things that need to be checked individually.

* File playback
   * Preview the file quickly to make sure it plays. No need to check heads and tails because we do not trim these manually
   * If any files have been flagged for having a high number of errors during the rip they should be played back to ensure that these errors are not present during playback. If the errors are present then the disc should either be retransferred, or the errors should be noted according to the technician’s discretion.
* MP3 Metadata
   * Opening the MP3 in iTunes will show the file’s embedded metadata. Make sure that it looks correct compared to the metadata in the Salesforce record
   * If MP3 is split, check that the number of MP3 files matches the tracklist in the CUE and LOG files.

### Bulk QC Updates in Salesforce
Because CDs often come in large numbers, it’s easier to update the QC records for them in bulk using Views in Preservation.

* Open the Preservation Object View named !(CD QC)[https://bavc.lightning.force.com/lightning/o/Preservation_Object__c/list?filterName=00B2J000009e0vzUAA]
* This view will show any CD objects that have been marked *Digitization Status:* ***Pass***, but have not been marked *Quality Control Status:* ***Pass***
* In order for these records to be considered a QC Pass, the following fields visible in this view need to be filled out. None of these fields can be empty:
   * **Digital File Name**
      * This should reflect the file name without the extension
   * **Digital File Duration**
      * This should reflect the file duration in format HH:MM:SS:mmm
   * **Digital Audio Sampling Rate**
      * This should always be 44100
   * **Checksum**
      * This should have checksum in it.
   * **Source Deck**
      * This should reflect the disc drive used to rip the CD
      * If the drive is internal to a computer is should say “Internal”
   * **Host Computer**
      * This should reflect the computer that was used to rip the CD
* If the above fields are properly filled, you will need to update the following fields. These fields can be easily updated in bulk by clicking the checkbox on the far left side of the list for every record you want to update. Then, when you update each field make sure to click the box that says “Update X selected items” (where “X” is how many records you’ve selected)
   * **Quality Control Date**
      * The date that you are performing QC
   * **Quality Control Notes**
      * This should only be filled out if there is a problem. The format should be:
      * QC User Initials - Date - Note
   * **Quality Control User**
      * Your username
   * **Metadata**
      * “Pass”
      * This is the only “QC Checklist” record we’re updating unless you’re performing full single-file QC
   * **Quality Control Status**
      * “Pass”
      * This is the most important field, since it determines the QC status of the record.

### Ripping CDs Outside of BAVC

If you plan to rip CDs at an institution outside of BAVC you can follow most of the main steps. You'll still want to use XLD, but you won't be using Salesforce at all to handle the metadata. Instead of using `cdEngine.py`, which by design needs to be connected to salesforce, you can use [`simple_cd.py`](https://github.com/bavc/videomachine/blob/master/simple_cd.py), which works the same way, but allows the user to manually enter any embedded metadata.

* Run the script with the following command to create a single MP3 from the rippped WAV file:
   - `simple_cd.py -i /Path/To/Folder`
* Run the script with the following command to create an MP3 for every track on the original CD file:
   - `simple_cd.py -i /Path/To/Folder -s`
* Run the script with the following command to create an MP3 for every track on the original CD file, along with a single MP3 containing all of the CD content:
   - `simple_cd.py -i /Path/To/Folder -s -m`
