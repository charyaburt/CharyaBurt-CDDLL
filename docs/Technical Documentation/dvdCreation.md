---
layout: page
title: DVD Creation
parent: Technical Documentation
---

# DVD Creation

## DVD Creation From File

### Using Terminal
* **Run make_dvd_iso.sh**
    - We have a script called make_dvd_iso.sh (attached).
    - If you already have it installed on your machine, simply run the following two scripts in Terminal:
        - cd (directory)
        - make_dvd_iso.sh *
* **Install make_dvd.iso.sh
    - In order for the script to work, your computer needs to have the following installed: ffmpeg, ffprobe, dvdauthor, and cdrtools. If you don't have these, submit a ticket to get them installed (or use homebrew). If you don't have the script installed, do the following:
        - Install, update, or upgrade Homebrew
        - Download the attached make_dvd-iso.sh script
        - Move the script to the /usr/location/bin folder and change permissions
            - cd (directory that make_dvd_iso is in)
            - mv make_dvd_iso.sh /usr/local/bin
            - cd /usr/local/bin
            - chmod 777 make_dvd_iso.sh
        - Install dvdauthor & cdrtools
            - brew install dvdauthor
            - brew install cdrtools
    ***If your original files do not have a ".mov" wrapper, change that part in the command as well***


## Burning an ISO to DVD
* Put in blank disk*
* Right click on the ISO file and choose "Burn [file name] to disk"
* Keep ISO file, we give them to clients when they request DVDs

*DVD stock should be: DVD-R Inkjet Printable (also known as "hub printable). We like the Verbatim brands.


## Labeling a DVD
* As of this writing, we use the Epson Stylus Photo R2000 printer (Barcode 102181) to print CDs. We are still using a rather antiquated software to print from: Epson Print CD 2.0. The extension of Epson files is .printcd2.
