---
layout: page
title: Digital Deliverables
parent: Information for Collection Holders
---

# Digital File Deliverables

## Preservation Formats for Analog Video

### V210
Often referred to as 10-Bit Uncompressed YUV, this format can be thought of as the “vanilla” flavor of preservation formats for its ubiquity, simplicity, and wide appeal. With the correct codec installed,V210 files play in most video playback software and NLE workstations, making it an easy format to work with. The wide adoption of the format makes it a strong contender for long-term viability and support.This file doesn’t generally work well with embedded metadata, and has a small range of preservation-specific features.The largest drawback is the size; Clocking in at 100GB/Hr, V210 files can easily take up multiple terabytes of space for even medium-sized collections.

### FFV1
This is an open source, losslessly compressed preservation format. Open source means all the documentation about the format is freely available to read, and the format specification is reviewed and updated transparently by the Internet Engineering Task Force. Lossless means that while the file is compressed, no information is lost during this process, and you’ll be able to store more information with smaller file sizes. The trade-off is that the format is not supported across the board by some playback or NLE software. However, this is changing rapidly and the format is supported by VLC, a free and cross-platform video player. Another advantage of FFV1 is that it supports many preservation-friendly features, such as checksums of video and audio frames and embedded metadata. These files are often around 40GB per hour

## Preservation Formats for Digital Video

### DV wrapped in mov

When capturing born digital video tapes like MiniDV, DVCAM, and DVCPRO we use a purely digital signal chain to avoid transcoding from digital, to analog, and back to digital. Using the DVRescue software we're able to create nearly perfect trasnfers of tapes, even in cases where the tape is problemtic or damaged. After capture, the files are packaged in the MOV wrapper to provide a superior preservation format to the otherwise naked DV wrapper. We do not suggest that any other format be used to deliver DV-style tape transfers. These files are about 12GB per hour

## Preservation Formats for Analog Audio

### Broadcast WAVE (BWAV)
This format is an uncompressed Linear PCM audio file. It is similar to an uncompressed WAV file, except that it has an extra bit of embedded metadata referred to as the “bext chunk”. This bext chunk allows users to embed metadata such as a description, a unique identifier, information about the digitization signal chain, and when the file was created. BAVC embeds metadata into your BWAV files according to the Federal Agencies Digital Guidelines Initiative (FADGI) specification, which can be found [here](https://www.digitizationguidelines.gov/audio-visual/documents/BWF_Embed_Guideline_v3_2021.pdf). Preservation files for analog materials are always transferred at 96kHz / 24 bit. However, born digital materials like DAT are transferred at their original resolution. These files are about 2GB per hour

## Preservation Formats for Digital Audio

Similarly to Analog Audio, we cpature Digital Audio tapes like DAT and MiniDisc as uncompressed Linear PCM audio file. However, for digital tapes we capture the audio in its native digital resolution using an all-digital signal chain to avoid any unecessary transcoding. These tapes are often 16 Bits at a 44.1 kHz sampling rate, which amounts to about 635MB per hour.  

### DV wrapped in mov

When capturing born digital video tapes like MiniDV, DVCAM, and DVCPRO we use a purely digital signal chain to avoid transcoding from digital, to analog, and back to digital. Using the DVRescue software we're able to create nearly perfect trasnfers of tapes, even in cases where the tape is problemtic or damaged. After capture, the files are packaged in the MOV wrapper to provide a superior preservation format to the otherwise naked DV wrapper. We do not suggest that any other format be used to deliver DV-style tape transfers.

## Mezzanine files

These deliverables are optimized for editting and production. The files are similar to the preservation file, but are lightly compressed and optimized for use in a Non-Linear Editing platform (NLE). If you don't plan to edit your files or use them in a production these files can be omitted.

### ProRes 422 HQ
ProRes is a high-quality lossy proprietary Apple video format designed to be used in post-production workflows. 422 HQ is a high-bitrate version, which sacrifices a slightly larger file size for a higher quality image. The quality of this format is very good, making it difficult for the regular user to tell the difference between a ProRes Mezzanine file and its accompanying preservation file. We recommend this format for Mezzanine files because of its wide support and higher-quality image. These files are about 30GB per hour

### DV25
DV is a lossy video format. The DV25 version is the most common version of DV, with a bitrate of 25 Mbps.The file size is very small and it works well with NLE software. Unfortunately, the quality is generally worse than ProRes due to a smaller bitrate and the fact that the color space is 4:1:1 or 4:2:0, meaning that there is less color data per pixel. These files are about 12GB per hour

### DV50
Naturally, DV50 has twice the data rate of DV25 at 50 Mbps.Therefore, the quality is greater than DV25, is well-supported, and is still smaller than ProRes. These files are about 25GB per hour

## Access Files For Video

These deliverables are optimized for sharing, screening, and playback. The files are deinterlaced and any missing audio chanels are removed for an improved viewing experience. Bars and tone can be removed upon request for a small fee.

### Advanced Video Codec (AVC)
Also known as H.264 or MPEG-4, this is a compressed video format that creates a small file with excellent quality. At BAVC, we typically construct AVC files with a bitrate of 3 Mbps, which results in a file that is just over 1GB per hour and can be indistinguishable from the preservation file.This file is primarily meant to be viewed and performs well in most video playback software. However, it does not work well in NLE software and is not recommended in post-production workflows. These files are generally about 1GB per hour

### DVD Image
As optical media reaches the end of its life, BAVC has moved away from the delivery of DVDs. We are able to provide DVD Image files upon request, which can be burned onto a playable DVD. We do not recommended DVDs as an access medium because of its low image quality and larger file size. These files are about 4GB per hour

## Access Files For Audio

### MPEG Audio Layer-3 (MP3)
This is a common format for creating small and accessible audio files. MP3s allows users to embed metadata like "Title","Artist", and "Album", which makes them easy to view and search for in audio playback software. By default, BAVC creates MP3 files at 320 Kbps, which maintains a great deal of quality while still being small enough to send via email. BAVC automatically embeds metadata into the MP3s according to information provided by you and the information on the tape label. These files are about 150MB per hour
