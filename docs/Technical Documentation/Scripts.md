---
layout: page
title: Scripts
parent: Technical Documentation
---

# Scripts

## Basic Unix Commands

* Change directories: `cd [path]`
* Remove a directory: `rmdir [file]`
* Run commands in presraid: `ssh presraid@presraid`
* Change permissions (read, write, execute by everyone): `chmod 777 [file]`

***

## Homebrew

Homebrew is a program that allows for the easy install and updating of a variety of applications that we use, including ffmpeg, qctools, vrecord, and micromediaservices.
* Install Homebrew [http://brew.sh](http://brew.sh)
* Brew Cheatsheet [http://ricostacruz.com/cheatsheets/homebrew.html](http://ricostacruz.com/cheatsheets/homebrew.html)
* FFmpeg Cookbook for Archivists [https://avpres.net/FFmpeg/](https://avpres.net/FFmpeg/)


* Upgrade/Update Homebrew
```
brew update&&upgrade
```
* Dave's Mediamicroservices
```
brew tap mediamicroservices/mm
```
* AMIA Open Source
```
brew tap amiaopensource/amiaos
```
***

## Bagging Drives

Bagging a drive is a way to prove to provide a digital shipping manifest to the client, as well as ensure that all the files that were loaded onto the drive were loaded properly.

When we bag drives, we do so on the client's drive after all files have been reviewed. The "data" folder of the bag will include: files, transfer log, codec, readme.txt, qctools report

There are two tools that can be used: Bagit and Bagit.py.

Bagit is outdated, and the library of congress is now just supporting Bagit.py.

You can install bagit.py with homebrew:
```
brew install bagit
```

### Bagit.py

Before running the command you'll want to remove hidden files:
```
sudo find [Path to Directory] -name ".*" -exec rm -vR {} \;
```
Now you can run the basic bagging command for BAVC:
```
bagit.py --md5  --contact-name 'Bay Area Video Coalition' --contact-email 'preservation@bavc.org' --contact-phone '415-558-2158' [Path to Directory]
```
It is generating checksums so it will take a while to run, an overnight process for big projects.

If you want to run this on a bunch of sub-directories within a directory, the easiest way to do that is to use the find command with a clever query. In this case [Path to Directory] refers to the path to the directory that contains the sub-directories you want bagged:
```
find [Path to Directory]  -type d -maxdepth 1 -mindepth 1 -exec bagit.py --md5  --contact-name 'Bay Area Video Coalition' --contact-email 'preservation@bavc.org' --contact-phone '415-558-2158' {} \;
```
***
## FFmpeg
FFmpeg is the command line tool for digital media manipulations that drives vRecord, QCtools, and most of our automated script processes.

### Install/update
Once Homebrew is installed, you can install or update ffmpeg by running:
```
brew install ffmpeg --HEAD
brew reinstall ffmpeg --HEAD
```
Reto Kromer's FFmpeg Cookbook for Archivists (great resource for installation and manipulations) [https://avpres.net/FFmpeg/#ch1](https://avpres.net/FFmpeg/#ch1)

### Transcode
The default specs for our access files are based on CAVPP's target specifications: [http://calpreservation.org/wp-content/uploads/2014/12/CAVPP-file-specs-2014.11.20.pdf](http://calpreservation.org/wp-content/uploads/2014/12/CAVPP-file-specs-2014.11.20.pdf)

**For all Transcoding strings you need to cd into the working directory before running the string.**

#### FFv1
* Creating an MKV Master File from 10-Bit Uncompressed:
```
for file in *.mov ; do ffmpeg -i "$file" -c:v ffv1 -level 3 -g 1 -slices 16 -slicecrc 1 -color_primaries smpte170m -color_trc bt709 -colorspace smpte170m -color_range mpeg -metadata:s:v:0 "encoder= FFV1 version 3" -c:a copy -vf setfield=bff,setsar=40/27,setdar=4/3 -metadata creation_time=now -f matroska "${file%.*}.mkv" ; done
```
* Creating a 10-but Uncompressed File from an FFV1/MKV files:
```
for file in *.mkv ; do ffmpeg -i "$file" -movflags write_colr -c:v v210 -color_primaries smpte170m -color_trc bt709 -colorspace smpte170m -color_range mpeg -metadata:s:v:0 "encoder=Uncompressed 10-bit 4:2:2" -c:a copy -vf setfield=bff,setsar=40/27,setdar=4/3 -f mov "${file%.*}.mov" ; done
```

#### Access files

* Analog Master: 640 x 480 Access Files (De-Interlaced), Audio Channels Same as Original:
```
for file in *.mov ; do ffmpeg -i "$file" -c:v libx264 -pix_fmt yuv420p -movflags faststart -crf 18 -b:a 160000 -ar 48000 -s 640x480 -vf crop=720:480:0:4,yadif,setdar=4/3 "${file%.*}_access.mp4" ; done
```
* Analog Master: 640 x 480 Access Files (De-Interlaced), Audio Channels Same as Original (FROM PAL ORIGINAL):
```
for file in *.mov ; do ffmpeg -i "$file" -c:v libx264 -pix_fmt yuv420p -movflags faststart -crf 18 -b:a 160000 -ar 48000 -s 640x480 -vf crop=720:570:0:4,yadif,setdar=4/3 "${file%.*}_access.mp4" ; done
```
* Analog Master: 640 x 480 Access Files (De-Interlaced), Left Channel Panned to Center:
```
for file in *.mov ; do ffmpeg -i "$file" -c:v libx264 -pix_fmt yuv420p -movflags faststart -crf 18 -b:a 160000 -ar 48000 -s 640x480 -vf crop=720:480:0:4,yadif,setdar=4/3 -af "pan=stereo|c0=c0|c1=c0" "${file%.*}_access.mp4" ; done
```
* Analog Master: 640 x 480 Access Files (De-Interlaced), Right Channel Panned to Center:
```
for file in *.mov ; do ffmpeg -i "$file" -c:v libx264 -pix_fmt yuv420p -movflags faststart -crf 18 -b:a 160000 -ar 48000 -s 640x480 -vf crop=720:480:0:4,yadif,setdar=4/3 -af "pan=stereo|c0=c1|c1=c1" "${file%.*}_access.mp4" ; done
```
* Analog Master: 640 x 480 Access Files (De-Interlaced), Stereo Channels Summed to Mono:
```
for file in *.mov ; do ffmpeg -i "$file" -c:v libx264 -pix_fmt yuv420p -movflags faststart -crf 18 -b:a 160000 -ar 48000 -s 640x480 -vf crop=720:480:0:4,yadif,setdar=4/3 -af "pan=stereo|c0=c0+c1|c1=c0+c1" "${file%.*}_access.mp4" ; done
```
* Analog Master: 640 x 480 Access Files (De-Interlaced), 4 Channels summed to 2 Channel Mono:
```
for file in *.mov ; do ffmpeg -i "$file" -c:v libx264 -pix_fmt yuv420p -movflags faststart -crf 18 -b:a 160000 -ar 48000 -ac 2 -s 640x480 -vf crop=720:480:0:4,yadif,setdar=4/3 -af "pan=stereo|c0=c0+c1+c2+c3|c1=c0+c1+c2+c3" "${file%.*}_access.mp4" ; done
```
* DV Master: 640 x 480 Access Files (De-Interlaced), Audio Channels Same as Original, 4:3 aspect ratio:
```
for file in *.mov ; do ffmpeg -i "$file" -c:v libx264 -pix_fmt yuv420p -movflags faststart -crf 18 -b:a 160000 -ar 48000 -s 640x480 -vf yadif,setdar=4/3 "${file%.*}_access.mp4" ; done
```
* DV Master: 640 x 480 Access Files (De-Interlaced), Audio Channels Same as Original, 16:9 aspect ratio:
```
for file in *.mov ; do ffmpeg -i "$file" -c:v libx264 -pix_fmt yuv420p -movflags faststart -crf 18 -b:a 160000 -ar 48000 -s 640x480 -vf yadif,setdar=16/9 "${file%.*}_access.mp4" ; done
```
* 1920 x 1080 Access Files from Upscaled Mezzanine Files
```
for file in *_mezzanine.mov ; do ffmpeg -i "$file" -c:v libx264 -pix_fmt yuv420p -movflags faststart -crf 17 -b:a 160000 -ar 48000 -s 1920x1080 -ac 2 -af "channelmap=map=FL|FR:channel_layout=stereo" -y  "${file%_mezzanine.*}_access.mp4" ; done
```
* 1920 x 1080 Access Files from Upscaled Mezzanine Files High Quality version (crf 12 instead of 17)
```
for file in *_mezzanine.mov ; do ffmpeg -i "$file" -c:v libx264 -pix_fmt yuv420p -movflags faststart -crf 12 -b:a 160000 -ar 48000 -s 1920x1080 -ac 2 -af "channelmap=map=FL|FR:channel_layout=stereo" -y "${file%_mezzanine.*}_access_HQ.mp4" ; done
```
* 1920 x 1080 Access Files from HDV .m2t files
```
for file in *.m2t ; do ffmpeg -i "$file" -c:v libx264 -pix_fmt yuv420p -movflags faststart -crf 17 -b:a 160000 -ar 48000 -s 1920x1080 -ac 2 -vf yadif -filter_complex "[0:a:0]aresample=async=1:min_hard_comp=0.01" -y  "${file%.*}_access.mp4" ; done
```
#### Mezzanine files

* For Prores HQ, De-Interlaced, 24-bit PCM Audio [Note: Prores version determined by profile #: 0=Proxy; 1=LT, 2=422 Normal, 3=HQ)
```
for file in *.mov ; do ffmpeg  -i "$file" -c:v prores -profile:v 3 -vf yadif -c:a pcm_s24le "${file%.*}_mezzanine.mov" ; done
```
* For Prores HQ, De-Interlaced, 24-bit PCM Audio Channels Same as Original [Note: Prores version determined by profile #: 0=Proxy; 1=LT, 2=422 Normal, 3=HQ)
```
for file in *.mov ; do ffmpeg -vsync 0 -i "$file" -c:v prores -profile:v 3 -vf yadif -c:a pcm_s24le "${file%.*}_mezzanine.mov" ; done
```
* For Prores HQ, De-Interlaced, 24-bit PCM Audio Left Channel Panned to Center [Note: Prores version determined by profile #: 0=Proxy; 1=LT, 2=422 Normal, 3=HQ)
```
for file in *.mov ; do ffmpeg -i "$file" -c:v prores -profile:v 3 -vf yadif -c:a pcm_s24le -af "pan=stereo|c0=c0|c1=c0" "${file%.*}_mezzanine.mov" ; done
```
* For Prores HQ, De-Interlaced, 24-bit PCM Audio Right Channel Panned to Center [Note: Prores version determined by profile #: 0=Proxy; 1=LT, 2=422 Normal, 3=HQ)
```
for file in *.mov ; do ffmpeg -i "$file" -c:v prores -profile:v 3 -vf yadif -c:a pcm_s24le -af "pan=stereo|c0=c1|c1=c1" "${file%.*}_mezzanine.mov" ; done
```
* For Prores HQ, De-Interlaced, 24-bit PCM Audio Stereo Channels Summed to Mono [Note: Prores version determined by profile #: 0=Proxy; 1=LT, 2=422 Normal, 3=HQ)
```
for file in *.mov ; do ffmpeg -i "$file" -c:v prores -profile:v 3 -vf yadif -c:a pcm_s24le -af "pan=stereo|c0=c0+c1|c1=c0+c1" "${file%.*}_mezzanine.mov" ; done
```
* For Prores HQ, De-Interlaced, 24-bit PCM Audio 4 Channels Channels Summed to 2 Channel Mono [Note: Prores version determined by profile #: 0=Proxy; 1=LT, 2=422 Normal, 3=HQ)
```
for file in *.mov ; do ffmpeg -i "$file" -c:v prores -profile:v 3 -vf yadif -c:a pcm_s24le -ac 2 -af "pan=stereo|c0=c0+c1+c2+c3|c1=c0+c1+c2+c3" "${file%.*}_mezzanine.mov" ; done
```
* For Prores HQ, Interlaced, 24-bit PCM Audio Channels Same as Original [Note: Prores version determined by profile #: 0=Proxy; 1=LT, 2=422 Normal, 3=HQ)
```
for file in *.mov ; do ffmpeg -i "$file" -c:v prores -profile:v 3 -c:a pcm_s24le "${file%.*}_mezzanine.mov" ; done
```
* For Prores HQ, Interlaced, 24-bit PCM Audio Left Channel Panned to Center [Note: Prores version determined by profile #: 0=Proxy; 1=LT, 2=422 Normal, 3=HQ)
```
for file in *.mov ; do ffmpeg -i "$file" -c:v prores -profile:v 3 -c:a pcm_s24le -af "pan=stereo|c0=c0|c1=c0" "${file%.*}_mezzanine.mov" ; done
```
* For Prores HQ, Interlaced, 24-bit PCM Audio Right Channel Panned to Center [Note: Prores version determined by profile #: 0=Proxy; 1=LT, 2=422 Normal, 3=HQ)
```
for file in *.mov ; do ffmpeg -i "$file" -c:v prores -profile:v 3 -c:a pcm_s24le -af "pan=stereo|c0=c1|c1=c1" "${file%.*}_mezzanine.mov" ; done
```
* For Prores HQ, Interlaced, 24-bit PCM Audio Stereo Channels Summed to Mono [Note: Prores version determined by profile #: 0=Proxy; 1=LT, 2=422 Normal, 3=HQ)
```
for file in *.mov ; do ffmpeg -i "$file" -c:v prores -profile:v 3 -c:a pcm_s24le -af "pan=stereo|c0=c0+c1|c1=c0+c1" "${file%.*}_mezzanine.mov" ; done
```
* For Prores HQ, Interlaced, 24-bit PCM Audio 4 Channels Summed to 2 Channel Mono [Note: Prores version determined by profile #: 0=Proxy; 1=LT, 2=422 Normal, 3=HQ)
```
for file in *.mov ; do ffmpeg -i "$file" -c:v prores -profile:v 3 -c:a pcm_s24le -ac 2-af "pan=stereo|c0=c0+c1+c2+c3|c1=c0+c1+c2+c3" "${file%.*}_mezzanine.mov" ; done
```
* For CAVPP Standards (2015) Production files:
```
for file in *.mov ; do ffmbc -i "$file" -target dvcpro50 -pix_fmt yuv422p -r ntsc -acodec copy "${file%.*}_dv50.mov" ; done
```
* 1920 x 1080 ProRes HQ Files from HDV .m2t files
```
for file in *.m2t ; do ffmpeg -i "$file" -c:v prores -profile:v 3 -vf yadif -filter_complex "[0:a:0]aresample=async=1:min_hard_comp=0.01" -c:a pcm_s24le -y  "${file%.*}_access.mp4" ; done
```

#### Upres SD Files to HD
* For HD Prores HQ, De-Interlaced, 24-bit PCM Audio, Pillarboxed 16:9 1080 Files
```
for file in *.mov ; do ffmpeg -i "$file" -c:v prores -profile:v 3 -aspect 16:9 -vf yadif,scale=w=1440:h=1080:flags=lanczos,pad=1920:1080:240:0 -c:a pcm_s24le -s 1920x1080 "${file%.*}_mezzanineHD.mov" ; done
```
* For HD Prores HQ, De-Interlaced, 24-bit PCM Audio, Full Frame 16:9 1080 Files
```
for file in *.mov ; do ffmpeg -i "$file" -c:v prores -profile:v 3 -vf yadif,scale=w=1920:h=1080:flags=lanczos -aspect 16:9 -c:a pcm_s24le "${file%.*}_mezzanineHD.mov" ; done
```
* For HD Access HQ, De-Interlaced, Pillarboxed 16:9 1080 Files
```
for file in *.mov ; do ffmpeg -i "$file"  -c:v libx264 -pix_fmt yuv420p -movflags faststart -b:v 3500000 -b:a 160000 -ar 48000 -aspect 16:9 -vf yadif,scale=w=1440:h=1080:flags=lanczos,pad=1920:1080:240:0 -s 1920x1080 "${file%.*}_accesHD.mp4" ; done
```
* For HD Access HQ, De-Interlaced, Full Frame 16:9 1080 Files
```
for file in *.mov ; do ffmpeg -i "$file" -c:v libx264 -pix_fmt yuv420p -movflags faststart -b:v 3500000 -b:a 160000 -ar 48000 -vf yadif,scale=w=1920:h=1080:flags=lanczos -aspect 16:9 "${file%.*}_accessHD.mp4" ; done
```

#### Trimming
* Trim the end of a file. In this case you can either use the HH:MM:SS format or just put the number of seconds for [output duration]
```
ffmpeg -i [/Path/To/OriginalFile.mov] -c copy -movflags write_colr -t [output duration] [/Path/To/TrimmedFile.mov]
```
* Trim the beginning of a file. In this case you must use the HH:MM:SS format to specify the start time
```
ffmpeg -ss [start time] -i [/Path/To/OriginalFile.mov] -c copy -movflags write_colr [/Path/To/TrimmedFile.mov]
```

#### Other
* Turn a 16:9 Pillarboxed video with 4:3 content into full-screen 16:9 content by cropping the pillars and resizing the content:
```
ffmpeg -i [input.mov] -movflags write_colr -color_range mpeg -color_primaries smpte170m -color_trc bt709 -colorspace smpte170m -aspect 16:9 -s 1920x1080 -c:v prores -profile:v 3 -vf crop=1440:1080:240:0,setdar=16/9 -c:a pcm_s24le [output.mov]
```
```
-movflags write_colr -color_range mpeg -color_primaries smpte170m -color_trc bt709 -colorspace smpte170m -aspect 16:9  -c:v prores -profile:v 3 -vf crop=1440:1080:240:0,yadif,setdar=16/9
```
* If accidentally captured a file with 2 stereo audio tracks (4 channels total) instead of 1 stereo audio track (2 channels total) this is a quick fix for removing the extra audio track
```
ffmpeg -i [input.mov] -movflags write_colr -map 0 -map -0:a:1 -c copy [output.mov]
```
* If you export a file from Premiere this command MUST be run on the output file before running it through the Transcode Engine
```
ffmpeg -i [input.mov] -dn -map_metadata "-1" -movflags write_colr -c:v v210 -color_range mpeg -color_primaries smpte170m -color_trc bt709 -colorspace smpte170m -vf "setfield=bff,setsar=40/27,setdar=4/3" -c:a copy [output.mov]
```
* Basic command for re-wrapping a file while maintaining the codec streams
```
ffmpeg -i input.ext -c:v copy -c:a copy -map 0 output.ext
```
* Creating FrameMD5 Manifests for video streams in all files in a folder:
```
for file in *; do ffmpeg -i "$file" -an -f framemd5 -y "${file%}.fd5" ; done
```
* Extract DV stream from a .MOV wrapped DV file
```
ffmpeg -i BAVC1004511_2385M_1.mov -c:v copy -f rawvideo BAVC1004511_2385M_1.dv
```
* Create 5 seconds of SMPTE Bars with 1kHz Tone
```
ffmpeg -f lavfi -i smptebars=s=720x486:r=30000/1001 -f lavfi -i "sine=frequency=1000:sample_rate=48000" -movflags write_colr+faststart -color_primaries smpte170m -color_trc bt709 -colorspace smpte170m -color_range mpeg -vf "setfield=bff,setdar=4/3" -c:v v210 -c:a pcm_s24le -t 5 -y tn2162_v210.mov
```
* Create 5 seconds of Black Bars with Silent Audio
```
ffmpeg -f lavfi -i color=c=black:s=720x486:r=30000/1001 -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=48000 -movflags write_colr+faststart -color_primaries smpte170m -color_trc bt709 -colorspace smpte170m -color_range mpeg -vf "setfield=bff,setdar=4/3" -c:v v210 -c:a pcm_s24le -t 5 -y tn2162_v210_black_silent.mov
```
***
## QCTools/vRecord  

* How to install QCLI
```
brew install qcli
```
* For running QCLI on a single file:
```
qcli -i [file name]
```
* For running QCLI on a whole directory:
```
for file in *.mov; do qcli -i "$file" ; done
```
***
## Audio
* See the max peak of the audio of a file (you can use this to check for digital clipping. If the Max Volume is 0dB it has clipped
```
ffmpeg -i input.wav -filter:a volumedetect -f null /dev/null
```
* For creating an MP3 from a folder of WAV files, maintaining channels
```
for file in *.wav ; do ffmpeg -i "$file" -c:a libmp3lame -b:a 320k -write_xing 0 -ac 2 "${file%.*}_access.mp3" ; done
```
* For creating an MP3 from a folder of WAV files, Left Channel Panned to Center
```
for file in *.wav ; do ffmpeg -i "$file" -c:a libmp3lame -b:a 320k -write_xing 0 -ac 2 -af "pan=stereo|c0=c0|c1=c0" "${file%.*}_access.mp3" ; done
```
* For creating an MP3 from a folder of WAV files, Right Channel Panned to Center
```
for file in *.wav ; do ffmpeg -i "$file" -c:a libmp3lame -b:a 320k -write_xing 0 -ac 2 -af "pan=stereo|c0=c1|c1=c1" "${file%.*}_access.mp3" ; done
```
* For creating an MP3 from a folder of WAV files, Stereo Channels Summed to Mono
```
for file in *.wav ; do ffmpeg -i "$file" -c:a libmp3lame -b:a 320k -write_xing 0 -ac 2 -af "pan=stereo|c0=c0+c1|c1=c0+c1" "${file%.*}_access.mp3" ; done
```
* Convert an .mov file to a .wav file
```
ffmpeg -i input.mov -map 0:a -c:a pcm_s16le -ar 48000 output.wav
```
* Convert an .mov DV file to a .wav file
```
ffmpeg -i input.mov -map 0:a:0 -c:a pcm_s16le -ar 48000 output.wav
```
***
## Mediainfo
* Salesforce syntax for Filename, Duration, and FileSize
```
mediainfo --Inform="General;\n%FileName%\n%Duration/String4%\n%FileSize/String4%\n"  [FILE NAME or DIRECTORY]
```
***
## Checksums

A checksum is a string of letters and numbers that acts like a fingerprint for a file. If two files have the same sum, it is safe to assume the files are the same.

To obtain a file's Md5 checksum:
* Open Terminal app, type “md5 “ (without quotes, with space after)
* Drop file(s) from finder window into terminal window, and press enter, and wait...
* Copy md5 checksum codes from terminal window and paste into MD5 field in Salesforce

    More on MD5's here: [http://www.codejacked.com/using-md5sum-to-validate-the-integrity-of-downloaded-files/](http://www.codejacked.com/using-md5sum-to-validate-the-integrity-of-downloaded-files/)

* Create an MD5 Checksum Sidecar file for each file in the working directory
```
for file in *.* ; do md5 -q "$file">"${file}.md5" ; done
```
***
## Rsync
* rsync to presraid
```
rsync -avv --progress [FILE OR DIRECTORY] presraid@presraid.bavc-int.org:/presraid
```
* rsync to client drive
```
rsync -avv --progress [FILE OR DIRECTORY] [DESTINATION FOLDER]
```
***
## DVRescue
DVRescue is a suite of tools that allow you to fix and re-wrap dv diles.

DVPackager is a part of the suite that slipts up dv streams with different attributes contained in a single file. The input is always a DV file. You can use it to package a .dv file as 1 or many .mov files with the following command:
```
dvpackager -e mov [path/to/file.dv]
```
You can also run in a folder using this command:
```
find [path/to/folder] -name "*.dv" -not -name ".*" -exec dvpackager -e mov {} \;
```
It's possible to merge multiple transfers of a tape into a single file to remove errors. You can input as many files as you'd like, as long as they have an overlap in content. You can use this with .dv or .mov files:
```
dvrescue [path/to/file1.dv] [path/to/file2.dv] [path/to/file3.dv] -m [path/to/OutputFile.dv]
```
Like with QCTools, it's possible to generate DVRescue reports using the command line. This string will create an .xml report for every .mov file in the current directory. This will make it so that the DVRescue GUI opens instantly. To run this command you first need to change the current directory of terminal to the target folder using `cd /path/to/directory/`
```
for i in *.mov ; do dvrescue "$i" -x "$i.dvrescue.xml" -c "$i.dvrescue.scc" -s "$i.dvrescue.vtt" ; done ; cowsay "done"
```
***

## Transcode Engine
Transcode Engine is a python script that lives on the SAN. The path is:
```
/Volumes/SymplyUltra/Scripts/transcodeEngine.py
```
_Be sure to use this instance and not the script on your desktop - The script on the SAN will be the most up to date._

You can run the script with the -h flag for help, you'll see the following information:
```
/Volumes/SymplyUltra/Scripts/transcodeEngine.py  -h
usage: transcodeEngine.py [-h] [-i I] [-o O] [-c C] [-mkv] [-dv] [-nsf]

Harvests Mediainfo of input file or files in input directory

options:
  -h,   --help          show this help message and exit
  -i I, --input I       the path to the input directory or files
  -o O, --output O      the output file path (optional)
  -c C, --csvname C     the name of the csv file (optional)
  -mkv, --Matroska      Allows input file type to be mkv rather than default
                        mov
  -dv, --DV             Allows input file type to be dv rather than default mov. Processes as 720x480 rather than 720x486
  -nsf, --NoSalesForce  Turns off 'No SalesForce' flag, which will avoid syncing the CSV to SF automatically. By default this script will sync CSV files to SalesForce
  ```
  Other than -h for help, there are three other input flag: -i, -o, and -c

  * -i is used to specify the file or directory being processed. If you choose a file, only that file will be processed. If you choose a directory, all files with the extension ".mov" will be processed. This includes V210 files and ProRes files. No other codecs are fully supported at the moment.

    Example:
    ```
    /Volumes/SymplyUltra/Scripts/transcodeEngine.py -i [Path/To/Input/Folder]
    ```
  * -o is used to specify the output path of the resulting CSV file. If not specified, the output path will be the same directory as the input file (if processing a file), or the input directory (if processing a directory).

    Example:
    ```
    /Volumes/SymplyUltra/Scripts/transcodeEngine.py -i [Path/To/Input/Folder] -o [Path/To/Output/Folder]
    ```
  * -c is used to specify the filename for the resulting CSV file. If not specified, the output filename will be the same as the input file in the format inputfile.mov.csv (if processing a file), or mediainfo.csv (if processing a directory)

    Example:
    ```
    /Volumes/SymplyUltra/Scripts/transcodeEngine.py -i [Path/To/Input/Folder] -o [Path/To/Output/Folder] -c OutputFilename.csv
    ```
***

## Salesforce Metadata Python (out of date)
Salesforce records can be updated using the CSV created by the transcode engine and a python script. Here is how you do it!
### Setup
* make sure you have python3 installed. run the following command `brew install python3`
* Install the simple salesforce python library with the following command: `sudo pip3 install simple-salesforce`
  * You will need to type in the password after running this command
* Download sfsync.py and config.py from the preservation Team Drive (Inventory -> Software -> Scripts)
* Drop these scripts into the  ~/Documents/FFMPEG folder on your computer.
  * These scripts can live anywhere, but they must be in the same folder. These instructions will assume that the files are in ~/Documents/FFMPEG
* Note: config.py has private user/password data in it. DO NOT SHARE this file with people online

### Running
* You can run the script with the following command: `python3 ~/Documents/FFMPEG/sfsync.py [path/to/mediainfo.csv]`
* You can actually run as many CSV files as you want in a single command!
 `python3 ~/Documents/FFMPEG/sfsync.py [path/to/01mediainfo.csv path/to/02mediainfo.csv path/to/03mediainfo.csv path/to/04mediainfo.csv]`

Note: Anything in brackets is a placeholder for the folder or file - [path/to/example]

***

## Salesforce Metadata CSV Update
*With the new updates that use Python, the skyvia method is now out of date. This portion is still here in case the Skyvia portion needs to be used, but it’s deprecated.*

The Transcode Engine script creates a file named mediainfo.csv when it's finished running. This CSV file contains the Digital Object Elements metadata for each .mov file that was processed. There is a script that runs in the background that will update the Digital Object Elements in a Salesforce Preservation Objects with the information contained in these CSV files, and it uses the Barcode Number to match the data up with the correct record.

It reads the CSV files from a Shared Google Drive folder. That folder lives in the preservation@bavc.org account's google drive. This folder is accessible from every Capture Station using the Backup and Sync from Google application. Each computer should have the folder accessible via finder, like this:

![Google Drive Salesforce]({{site.baseurl}}/assets/images/Google_Drive_SalesForce.png)

Every file in this folder will be synced daily to SalesForce at exactly 11:45 a.m. In order to sync up the CSV file you just created, you must rename it to match the following naming convention: XXmediainfo.csv (where XX is a number 01 thru - 09). Each staff member should have one or two filenames reserved for their individual use, in order to keep people from overwriting each other's files.  If you don't remember which numbers are yours ask your coworkers!

Drag the renamed CSV file into the SalesForceCSV folder to overwrite the existing file; When prompted, select "Replace".

Wait until 11:45 a.m. rolls around again to ensure that the record has updated, or...

### Manually Run The Update

It's possible to run the update manually, rather than wait for the automatic sync at 11:45 a.m.  Go the Skyvia web app at https://app.skyvia.com/ (login information available in the Accounts and Login page) and to the following

* Click on the Integration tab on the left
* Click on the Digital Object Elements Update item
* Click the Run button on the top-right side of the page
* Be patient! It can take a few minutes to run

### Known Issues!

There is a major known issue that can cause problems. If a single tape has multiple parts, and there is a file for each part, you'll need to edit the CSV file to remove all but one part. We typically fill the Salesforce record with Digital Object Elements fields with the data from Part01 of a tape. So, you'll need to go into the CSV file and remove the rows that correspond to the other parts. You can edit the CSV files in TextEdit .

***

## SAN
If the SAN gets unmounted you can mount it with the following command:
```
sudo xsanctl mount SymplyUltra
```
you'll be prompted for a password, it's preservation

***

## Github
We use GitHub to develop all of our open source projects such as QCTools, SignalServer, and AVAA.

### Getting Started

If you have Homebrew, then you already have git installed on your local machine. You can also install git by itself from here: http://git-scm.com/download/mac.

Next, you should create your GitHub account here: https://github.com/.

### Basic Use

Here are some very basic CLI steps for updating GitHub projects via Terminal.

  1. Login to GitHub and fork the original repository (of the application you want to make changes too) to your remote repository
  ![GitHub Fork]({{site.baseurl}}/assets/images/GitHubFork.png)
  2. Clone your remote repository to your local computer. You can do this in GitHub, or you can use a command line:
  ```
  git clone [remote repository url]
  ```
  3. In your local repo, open the .md file you would like to edit in Atom [Atom](https://atom.io/) or another text editor
  4. Make you edits, save and close the file
  5. In Terminal, cd into your local repository
  ```
  cd [path/to/repository]
  ```
  6. Now add the the change to a temporary staging area
  ```
  git add [filename]
  ```
  7. Commit the change to your local repository and add a message - the more specific the better
  ```
  git commit -m "changed the title from preservation to av preservation"  
  ```
  8. Now you are ready to send the change and the commit to your remote repository (the one on GitHub).
  ```
  git push origin master
  ```
  9. Finally, it's time to send the proposed changes to administrators of the original repository. In GitHub, go to the Pull Request tab and click the New Pull Request button
  ![GitHub Pull Request]({{site.baseurl}}/assets/images/GitHubFork.png)
  10. Follow the steps of the Pull Request and make sure your comments are descriptive and specific. It will be sent to the GitHub community. If an administrator approves, they will merge the changes into the repository. If they do not immediately approve, they will begin a dialogue about the change.
#### Resources
Here is a great guide with more explanatory notes about checkouts, branches, and other features: http://rogerdudler.github.io/git-guide/.
***
## Rename
### General Use
Rename is a super useful tool for renaming files and folders in bulk. It's pretty tricky to use, but here's a quick explanation of a simple use case

  * Installation is simple, just run `brew install rename`
  * In this example we will rename all files with the     extension .jpeg to have the extension .jpg instead.
  * First you need to `cd` into a the folder you want to rename.
  * Then run this command
  ```
  rename -n 's/\.jpeg/\.jpg/' *
  ```
  * The `-n` flag will run in dry-run mode,  meaning it will tell you what it will do before doing it.
  * `s/\.jpeg/\.jpg/` tells rename to look at the standard in, and replace ".jpeg" with ".jpg" in any file it finds
  * the `*` tells rename to look at every file in the working directory.
  * Once you run the command in dry-run mode it'll show you what changes it will make. If you're happy with that run the command again without the -n flag and it'll actually rename the files:
  ```
  rename 's/\.jpeg/\.jpg/' *
  ```
The above example just runs on files in a single folder. If you want to run the command on a bunch of recursive directories you'll need to use a more complex command:
  * First you need to `cd` into a the folder you want to rename.
  * Then run this command
  ```
  find . -type f -name '*.jpeg' -print0 | xargs -0 rename -n 's/\.jpeg/\.jpg/
  ```
  * This part: `find . -type f -name '*.jpeg' -print0 | xargs -0` performs a find in the working directory for any file ending with ".jpeg". Then it passes the file path to rename, which runs in dry-run mode
  * If you're happy with what dry-run mode comes up with, you can run it for real without the -n flag
  ```
  find . -type f -name '*.jpeg' -print0 | xargs -0 rename 's/\.jpeg/\.jpg/
  ```
In both examples we're just replacing .jpeg with .jpeg with this command: `s/\.jpeg/\.jpg/`

Keep in mind you can replace any string with any other string. It's very useful!

### Removing Barcodes

Rename can very easily remove barcodes from files names. However, it's **very dangerous** because you can easily mangle files names with this command.

  * First, you need to make sure you remove all hidden files from the working directory.
  * `cd` into whatever directory you want to rename the files in
  * Run this command to see every hidden file in the directory `find . -name ".*"`
  * If what you see looks like just hidden files, then run this command to remove hidden files. BE SUPER CAREFUL DON'T MESS THIS UP OR YOU CAN REMOVE EVERY FILE IN THE DIRECTORY.
  ```
  find . -name ".*" -exec rm  -vR {} \;
  ```
  * From here you can run the following command to remove the barcodes (first 12 characters) from every file in the folder
  ```
  rename -n 's/.{12}(.*)/$1/' *
  ```
  * That command actually runs in dry-run mode. Remove the -n to run it for real if you're happy with the projected results of the dry-run

  You can read the manual [here](http://plasmasturm.org/code/rename/)
