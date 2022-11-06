---
layout: page
title: Preservation Objects
parent: Salesforce
---

# Preservation Objects

## Preservation Object Detail

### Intake/Inspection
*Complete during intake*

* Intake/Inspection covers all inventorying and condition information gathered upon (you guessed it) initial intake and inspection!

    - **Media Type:** Almost always Video or Audio
    - **Opportunity:** Should auto fill with collection name
    - **Barcode:** Enter BAVC barcode number you apply to tape
    - **Intake Date:** Current date
    - **Intake Contact:** Your name
    - **Label on Original:** Any label or information on tape or case. Please be as correct as possible, but if there is a lot of information on the tape, you should be succinct rather than comprehensive.
    - **Client Identifier:** Any identifying number appearing consistently within the collection
    - **Box:** Only relevant if collection comprises of multiple boxes
    - **Tape Series:** Rarely used, as generally covered by client identifier
    - **Format of Original:** Choose from drop down menu. If format is missing, please inform staff member.
    - **Manufacturer Length of Tape:** Often printed on base of tape, or printed on tape or case label. If length on tape differs from length on label, defer to tape, as it may have been rehoused at some point.
    - **Manufacturer on Tape:** Choose from drop down menu if manufacturer known
    - **Model of Tape:** If not printed on label, may be printed on base of tape, ex. KCA-60
    - **Magnetic Pigment Formulation:** Choose from drop down menu. Generally Oxide, but DV tapes will be MP (metal particle) or ME (metal evaporate)
    - **Back Matting:** Check box if back matting present on tape
    - **Inspection/Condition Notes:** Note any physical issues related to the tape or it’s housing here. Examples of notes you may make are popped strands, stepping, no case, dirty, removed record tape etc. If mold is found, please note in inspection/condition notes AND technician notes. Also, alert a staff member immediately.

## Transfer Environment
*Complete before capture*
*
    - **Transfer Suite:** Choose the preservation room you are working in from drop down menu
    - **Transfer Technician:** Begin typing your own name. It should appear quickly and you can chose it from the list that appears
    - **Transfer Date:** Current date
    - **Host Computer:** The computer you are using to capture. Type in computer’s inventory number and search, then choose from search list
    - **Operating System Name:** Mac OS
    - **Source Deck:** The deck you are using for this capture. Type in deck’s inventory number and search, then choose from search list
    - **SDI Converter:** Most transfers utilize an SDI converter before being captured on the computer disk. Type in the inventory number and search, then choose from search list
    - **Operating System Version:** Choose computer’s current OS from drop down menu. If not present, please alert a staff member
    - **Capture Hardware:** Choose from drop down menu. Black Magic 4K Extreme currently in use at all stations.
    - **Capture Software:** Choose from drop down menu
    - **Trim Software:** Choose from drop down menu. We currently use QuickTime7 almost exclusively to trim files.

## Video Transfer Elements
*Complete before capture - Video*

    - **Analog Video Transmission:** Choose the transmission method from the drop down menu
    - **Color:** Choose from drop down menu
    - **Audio Source Channels:** Choose from drop down menu. While the majority of formats have two channels (CH1, CH2), ½ inch and occasionally Umatic have one channel, and Betacam can have more than two.
    - **Audio Source Channel Layout:** Choose from drop down menu
    - **Audio Source Recording Method:** Choose from drop down menu. Particularly relevant for VHS transfer, as cabling must be adjusted for HiFi
    - **TBC/Frame Sync:** The time base corrector(TBC) you are using to capture. Type in TBC’s inventory number and search, then choose from search list. If using internal TBC, note this in **Proc Amp Notes**
    - **Proc Amp Notes:** Note all adjustments you made to TBC (Black, Luma; Chroma, Hue, H Position)
    - **Bars/Tone:** Choose from drop down menu
    - **Timecode:** Choose from drop down menu if capturing timecode. Timecode is almost always dropped frame.
    - **Alternate Modes:** Choose relevant headings, or leave blank if none apply
    - **Video Transfer Notes:** Notes about the transfer you would like your colleagues and QC technician to see, ex. *File captured twice on two different TBCs. Please review both.*

## Audio Transfer Elements
*Complete before capture - Audio*

    - **Audio Material Type:** Choose from drop down menu
    - **Audio Speed:** Choose from drop down menu
    - **Audio Reel Size:** Choose from drop down menu
    - **Audio Track Configuration:** Choose from drop down menu
    - **Audio Size Configuration:** Choose from drop down menu
    - **Audio Transfer Notes:** Notes about the transfer you would like your colleagues and QC technician to see

## Supervised Transfer Notes
*Complete after capture*

* **Technician's Notes**
    - Technician’s Notes should contain *general* information about the overall condition of the tape content, ex. regularity of drop outs (occasional, regular, heavy), presence of double headswitching, regular instances of sync loss.
    - Video notes should come before audio notes, ex. Regular drop outs. Numerous sync errors, audio buzz present throughout. Intermittent audio drop outs.

* **Timecode Stamped Notes**
    - Timecode Stamped Notes indicate particular instances of damage or image/audio variation of which you wish to alert the client.
    - Timecode Stamped Notes should appear as follows:
        - 00:00:00(space)-(space)Capitalized note; ex. 01:02:03 - Drop out;
    - Each note (barring the final note you make) should have it’s own line and end in a semi-colon. This is to ensure that the information displaces legibly in the Excel transfer log we provide to clients.

## Digitization Status
* **In Progress** - The transfer process has been started and is proceeding as normal, but has not yet been completed.
* **Pass** - You are satisfied with your captured file and notes.
* **Review** - There is an issue with your file that you would like to review, either by yourself or with colleagues.
* **Fail** - Your capture was not successful.
* **Not Captured** - The tape has not and will not be captured.
* **Sent to Sub** - The tape is not at BAVC, and has been sent to a subcontractor like Specs Brothers.

## Digital Object Elements
* The information for Digital Object Elements are auto-populated into the Salesforce record via a script appended to the transcodeEngine. The majority of the fields in Digital Object Elements will remain the same from record to record. For 10-bit uncompressed capture, your fields should read as follows:

    - **Digital File Format:** MOV
    - **Digital Video Codec:** Uncompressed 10-bit (v210)
    - **Digital Video Bit Depth:** 10 bit
    - **Digital Compression Mode:** Lossless
    - **Digital Video Scan Type:** Interlaced
    - **Digital Video Frame Rate:** 29.97
    - **Digital Video Frame Size:** 720 x 486
    - **Digital Video Aspect Ratio:** 4:3
    - **Digital Video Data Rate:** 224 Mbps
    - **Digital Video Color Matrix:** BT.601
    - **Digital Video Color Space:** YUV
    - **Digital Video Chroma Subsampling:** 4:2:2
    - **Digital Video Audio Data Rate:** 2 304 Kbps
    - **Digital Audio Bit Depth:** 24 bit
    - **Digital Audio Sampling Rate:** 48 kHz
    - **Digital Audio Codec:** Linear PCM
    - **Digital Audio Channel Positions:** L R
    - **Digital Audio Channel(s):** 2 Channels
    - **Checksum Generator:** MD5

* The only contantly variable fields are:
    - **Digital File Name**
    - **Digital File Duration**
    - **Digital File Size**
    - **Checksum**

### Non 10-bit Captures
* While we largely capture files as 10 bit uncompressed (v210), there are occasions when we will capture to other codecs. These situations require some changes to the normally static Digital Object Elements fields.
    - **ProRes 422 HQ**
        - **Digital Video Codec:** Prores 422 HQ
        - **Digital Compression Mode:** Lossy
        - **Digital Video Scan Type:** Progressive
        - **Digital Video Frame Size:** 648 x 486
        - **Digital Video Data Rate:** Variable
    - **DV (DVCAM, MiniDV)**
        - **Digital Video Codec:** DV
        - **Digital Video Bit Depth:** 8 bit
        - **Digital Compression Mode:** Lossy
        - **Digital Video Frame Size:** 720 x 480
        - **Digital Video Data Rate:** 24.4 Mbps
        - **Digital Video Chroma Subsampling:** 4:1:1
        - **Digital Audio Data Rate:** 1 536 Kbps
        - **Digital Audio Bit Depth:** 16 bit
        - **Digital Audio Sampling Rate:** 48 kHz OR 32 kHz

## Quality Control Elements
* Checklist
    - **Trimming:**
        - Is any content at the beginning or end cutoff?
        - Is there excessive static/snow or dead air at the beginning or end of the file?
        - Are client requested bars/slates present?
    - **Metadata:** Is every required field filled out?
    - **Time Code:**
        - Does timecode exist in the file?
        - If so, is it correct?
    - **Audio Sync:** Is the audio and video content in sync throughout the entire file?
    - **Notes:**
        - Do notes properly describe errors, artifacts, or other salient details?
        - Is the correct vocabulary used to describe errors?
        - Are any major errors missing from the notes?
    - **QCTools Report:** Does the report open properly in QCTools?
    - **MediaConch:** Do all files pass associated Policies?
    - **Quality Control Notes:** Note any issues, errors or oversights that need to be addressed by digitization technician
    - **Quality Control User:** Autofills when QC Technician is assigned at outset of project
    - **Quality Control Date:** Today's date
    - **Quality Control Status:** Select Pass, Review or Not Captured, dependent on outcome of QC process
    - **Loaded to Drive:** Check box when all files associated with record have been successfully loaded to client drive

## Preservation Activities
* Any interventionist actions taken on a tape must be recorded in Preservation Activities. The most common activities are cleaning and baking, but actions such as splicing or rehousing should also be recorded here.
    - Select **New Preservation Activities**
    - **Activity Type:** Select option from drop down menu. If Other selected, please specify which activity was taken in the Note field
    - **Activity Date:** Date activity was undertaken
    - **Preservation Object:** Should already contain object barcode number
    - **Note:** space for short, relevant notes, such as the type of action taken (if not listed in Activity Type drop down menu) or number of cleaning passes if tape required repeated cleaning

## Google Docs, Notes, and Attachments
* This field is rarely used at the object level.

## Notes
* This field is rarely used at the object level.
