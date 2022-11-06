---
layout: page
title: Cleaning Decks
parent: Services
---

# Cleaning Decks
    - Ensure deck is powered off
    - Moisten a cloth with alcohol
    - Clean entire tape path, making sure that all points of contact with tape are wiped clean
    - Hold the cloth with gentle pressure against the side of tape drum and rotate the drum, cleaning heads
    - Clean edges of tape path and area between heads (though not heads themselves) with cotton-tipped applicators moistened with alcohol
    - Clean difficult to reach areas with cotton-tipped applicators moistened with alcohol
    - Clean rubber rollers with Rubber Roller Restorer applied to cotton cloth (wear gloves and ensure room is properly ventilated when using this fluid)
    - Repeat above processes as often as necessary to remove all signs of dirt, grease, and dust from tape path
    - Clean deck before setting levels, after setting levels, and after every capture

* **Creating Digibetas**

Museums, archives, and libraries will sometimes request an additional Digibeta copy of the digital master file. Part of the Digibeta mastering process is laying down 30 seconds of black, 1 minute of bars/tone, and 30 seconds of black before the picture begins.
**Set-Up**
    - Clean heads and tape path carefully; use swab to clean the rollers.
    - Thread a BNC cable out of DIGITAL I/O Serial V/A input directly into the Blackmagic Capture Card
    - Set Remote part of patch bay from Kona to Digibeta.
    - Video Patch - Digibeta–>VDA1
    - Audio Patch - Digibeta --> RANE Mix
    - Find a blank tape of the right length. They are stored in a filing cabinet in the tape closet.
    - Open Media Express and import the file you are mastering to tape.
    - Pack the tape by fast-forwarding and rewinding.
    - Ensure the tape is wound to the beginning before laying down timecode.

**Lay Black and Timecode**
    - Switch deck to "Setup 1" by opening the control panel to reveal advance settings. Turn the deck off and back on again to activate.
    - Set the "TG Generator" to "interior" and "preset."
    - Press the "hold" button that is underneath the timecode panel.
    - Set timecode to 00:58:00
        - Press "Jog" and use the knob to move between the sections of the timecode. Set the numbers by pressing "Jog" at the same time as the knob is turned.
        - Press "Set" button under timecode.
        - Test by pressing REC
    - Pres REC + PLAY to record black and let run past 01:00:00
    - Stop

**Lay Bars and Tone**
    - Switch deck to "Setup 2" by opening the control panel to reveal advance settings. Turn the deck off and back on again to activate.  
    - Set the "TG Generator" to "interior" and "regen."
    - Rewind tape to 00:58:30
    - Under "INSERT" press "video" and all four audio channels
    - Press "Entry" and "In" at the same time
    - Forward tape to 00:59:30
    - Press "Entry" and "Out" at the same time
    - Identify Audio and Video
        - Press and hold SIF/CH1 on the Audio Input section until all audio channels light up.
        - Press and hold SIF in the Video Input section until all video channels light up.
    - Press Auto Edit

**Mastering**
    - Follow the procedures in the "Setup" section of this page.
    - Switch deck to "Setup 1"
    - On the Digibeta deck, Turn on Remote 1(9P) on
    - In Media Express–>Edit to Tape, set In Point to 1:00:00. You shouldn't have to set out point (if you do, use time code on file).
    - Click Assemble button
    - When ready to go, click the "Master" button. The tape will automatically stop when the file ends.
    - Check to make sure blacks, bars, and file all begin at the established in/out points.

**Labeling**
    tba

**Tips/Troubleshooting**
    - Do not use Media Express at the same time as you are recording blacks. You might accidentally record the file prematurely.
    - The file should be imported from the computer's local storage drive, not the presraid. Importing from the presraid will result in dropped frames.
