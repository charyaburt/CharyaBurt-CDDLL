---
layout: page
title: Quality Control (QC)
parent: Technical Documentation
---

# Quality Control (QC)

## QCing Files Using Salesforce
### QC Overview
* Quality Control(QC) procedures occur in all phases of our workflow for conserving magnetic media and migrating the content to digital formats.  This document provides guidelines for the QC technician to properly assess the integrity of Transfer Technicians’ work in transferring analog media. The purpose of QC in our organization is four-fold:
    - QC will ensure that only the highest quality files and documentation are delivered to the client
    - QC will ensure that all equipment is functioning as expected
    - QC will ensure that workflows and tasks are being performed as expected
    - QC will help tell us where to focus resources

While errors will be found on a file-by-file basis, analysis of QC data can help us holistically improve the quality of our work. Keep in mind that communication between the QC Technician and the Transfer Technician is very important when discussing files for review.

* Below are a few key guidelines for performing QC:
    - QC Should be performed by someone other than the Transfer Technician
    - QC should be performing as soon as possible following transfer
    - QC should be performed before loading files to the delivery media
    - QC should be performed on the Storage Area Network (SAN)
    - QC should be performed before deleting any files from the SAN
    - Any QC fails or issues found by the QC Technician should be addressed by the Transfer Technician

### QC Software
* Salesforce
    - A web-app used for tracking our work. Each tape is represented as a Preservation Object within an Opportunity. Salesforce allows us to create reports that can give us an overview of tasks and workflows.
* QuickTime 7
    - Playback software used for QC. Other playback software exists, and can be useful for troubleshooting, but this is the main software to be used during QC.
* QCTools
    - An open-source app built specifically for performing QC on digitized a/v content. The software on its own does not perform QC, but provides the user with data visualizations and playback filters that can help them perform QC.
* MediaConch
    - An open-source app used to analyse files through a series of BAVC specific policies, ensuring file specifications are correct.

### QC Reports
* These reports can be found by clicking on the Reports tab in Salesforce, then clicking on the Preservation: Quality Control folder on the left-hand side of the screen. Each report has been designed to give the QC Technician specific overviews of their tasks and progress.
    - QC Queue
        - A list of all Preservation Objects that have been marked as Transfer Passed but not marked QC Passed
    - QC Needs Review
        - A list of all Preservation Objects that have been marked QC Needs Review
    - QC Stats
        - A list of all items transferred and QC’d within an adjustable timeframe
    - QC Review History
        - A running list of all items that have QC Notes, organized by Original Format

### QC Checklist
* Each of the following bullet points correspond to a checkbox in Salesforce in the Quality Control Elements section
    - Derivatives
        - Do the derivatives exist and playback properly in QuickTime 7?
        - Is the audio and video in sync?
    - Trimming
        - Is any content at the beginning or end cutoff?
        - Is there excessive static/snow or dead air at the beginning or end of the file?
        - If client has requested bars/slates, are they present?
    - Metadata
        - Is every required field filled?
        - Does the Video duration match the duration notated in Digital File Duration?
        - **ONLY FOR AUDIO**
            - Check the embedded metadata in the audio files:
                - Drag the WAV files into BWFMetaEdit and ensure the following fields are filled out
                    - Description: *Title; Date (if any)*
                    - Originator: *"BAVC"*
                    - OriginatorReference: *BAVC Barcode*
                    - OriginationDate: *Date of file creation*
                    - OriginationTime: *Time of file creation*
                    - TimeReference: *"0"*
                    - BextVersion: *"1"*
                    - CodingHistory: *This will be a long string of text.*
                - Drag the MP# files into iTunes and ensure the following:
                    - Title: *Title*
                    - Artist: *Creator, producer, artist, etc... (if any)*
                    - Year: *Recording year, if any*
    - Time Code **(ONLY FOR VIDEO, DO NOT CHECK BOX FOR AUDIO)**
        - Does timecode exist in the file?
        - If so, is it correct?
            - Drop Frame vs Non Drop Frame
    - Audio Sync **(ONLY FOR VIDEO, DO NOT CHECK BOX FOR AUDIO)**
        - Is the audio and video content in sync throughout the entire file?
            - Check beginning, middle, and end of file
    - Notes
        - Do notes properly describe errors, artifacts, or other salient details?
            - Transfer Notes should describe details that occur throughout the content, over large portions of content, or any extra intervention taken to complete the transfer
            - Timecode Stamped Notes should describe errors or salient details that occur at specific times in the video file, using the format
                - The format of the note should be: HH:MM:SS - Description of error;
        - Is the correct vocabulary used to describe errors?
        - Are any major errors missing from the notes?
    - QCTools Report **(ONLY FOR VIDEO, DO NOT CHECK BOX FOR AUDIO)**
        - Does the report open properly in QCTools?
        - General signal analysis:
            - Are Y levels within range?
            - Are Saturation levels within range?
            - Are MSEF spikes at expected locations?
            - Does waveform look smooth and not quantized?
    - MediaConch
        - Do files all pass associated Policies?

### QC Status
* There are five possible entries for QC Status
    - Blank
        - QC has not been performed at all on the Object
    - Pass
        - QC has been performed and the Object passes all checks
    - Review
        - QC has been performed and one or more of the checks has failed or has a questionable status
        - When marking an Object as Review, make sure to always enter a description of the issue into Quality Control Notes. Upon saving the Salesforce record, a bot will send the QC Tech and Transfer Tech an email containing the Barcode and Quality Control Notes.
    - Review Addressed
        - Transfer Technician has addressed the reviews flagged by the QC Technician, by either correcting errors or by ensuring the errors are inherent to the tape
        - Transfer Technician will enter a description of tasks performed to address errors in Quality Control Notes
    - Not Captured
        - If the Object has not been transferred for any reason, often because it is a duplicate or is beyond intervention. In any case where an Object has not been transferred the Digitization Status and QC Status should both be marked Not Captured, and there should be a Technicians Notes describing why it was not captured.

## QC Workflow
 - Navigate to QC Queue report
 - Find the Opportunity you will be performing QC on
    - Priorities will most commonly be decided by the Preservation Manager
    - If no priorities are clear, navigate to the opportunity with the fewest number of Preservation Items that are ready for QC. This makes it easier to close any existing gaps.
    - Every Preservation Object associated with the selected Opportunity should be visible in the report. If they are not visible, press the Show Details button.
- Navigate to the QCReady folder of the OPportunity you will be QCing
    - SymplyUltra (SAN)
        - TransferProjects
            - Opportunity Name
                - 03_QCReady
    - NOTE: All files in the QCReady folder should be marked ready for QC according to Salesforce. Do not QC anything that isn’t ready according to Salesforce. Additionally, make sure to clear up any discrepancies about the status of an Object with the transfer technician.
- Run MediaConch on all Preservation files in the QCReady folder
    - The most common Policy used on Preservation files is CAVPP Preservation Master, which is used for 10-Bit Uncompressed MOV files
        - If the Preservation file being delivered to the client is not a typical 10-Bit Uncompressed file, work with the Preservation Manager to find or create a profile that works for the Opportunity
    - If any fails occur, investigate the failure to determine whether the Object should be marked for review
        - Not all MediaConch failures are grounds for an overall fail, but they must all be investigated
- Navigate to the Preservation Object you will be QCing by right-clicking the Barcode number and opening a new tab or new window
    - DO NOT QC the object if it has not been loaded to the PresRaid
- Step through the checkboxes in the Quality Control Elements section of the Salesforce page
    - Stepping through the checkboxes in order will ensure that you are following the workflow in the prescribed manner
        - The exception to this is the MediaConch box, which will be checked in bulk at the beginning of the QC Workflow. If you know that the files associated with this object have passed the MediaConch check you may check off this box at any time.
    - Check off each box once you have ensured that the associated details pass QC
    - Upon encountering any fail, describe the problem in Quality Control Notes, mark the QC Status of the record Review, and save the record. Move onto the next record.
- Once all of the check boxes are ticked, enter the Quality Control Date with today’s date, and mark the Quality Control Status as Pass
- Close the Object window and navigate back to the QC Queue report
- Move onto the next Object in the Opportunity

## Drive Load Workflow
* Drive loads should generally be started at the end of the day. Too many drive loads on a single station can slow the station’s SAN connection, and QCing during a drive load can be very slow.
    - Drive Formatting
        - Attach labels to all important parts of the drive
            - Box
            - Drive
            - Power Brick
            - Computer end of USB Cable
        - Mark drive as received in Salesforce Opportunity, and include notes on make/model/capacity
        - Plug Drive into computer
        - Format the Drive

        - ***ONLY PERFORM THE FOLLOW STEPS IF THE CLIENT DOES NOT HAVE MATERIALS ON THE DRIVE ALREADY***

            - Open Disk Utility
            - Click on the corresponding drive under External on the left-hand side of the window
            - Click the Erase button at the top of the window
                - ***WARNING: THIS WILL DEFINITELY ERASE THE DRIVE
            - Enter the name of the Drive. You can only use 10 characters, so make them count!
            - Set the format to ExFAT
            - Set the Scheme to GUID Partition Map
            - Click Erase. This process should run quickly
        - Drag the BAVC_Preservation folder from the desktop of your computer to the root level of the hard drive
        - Once finished, you can either start loading to the drive, or place it on the PresSuite shelf if it will not be used immediately.
    - Drive Loading
        - Plug the drive into the load station
        - Open a Terminal Window
        - Type in the following command
            - rsync -rlgtvD --progress
            - Press the space bar
            - Drag in the contents on 05_Loading from the opportunity folder on the SAN
            - Drag in the BAVC_Preservation folder on the Drive
            - The resulting string should look something like this:

            rsync -avv --progress /Volumes/SymplyUltra/TransferProjects/OpportinityName/05_Loading/Files_Access /Volumes/SymplyUltra/TransferProjects/OpportinityName/05_Loading/test/Files_Preservation /Volumes/ClientDriveName/BAVC_Preservation

            - Press Return and watch the files start to load!
            - When complete, move files into appropriate (Pres or Access) folders.
    - Click the "Loaded to Drive" box on each record in Salesforce.
