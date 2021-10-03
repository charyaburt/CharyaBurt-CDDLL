#!/bin/bash

FormatFile="/tmp/inform.txt"
FolderRoot="$1"
CSVFile="$2"
ExtList=".*\.\(mp4\|m4v\|m4p\|mkv\|avi\|asf\|wmv\|flv\|vob\|ts\|mpg\|mpeg\|mts\|m2ts\|webm\|ogv\|mov\|3gp\|3g2\|mp3\|m4a\|ogg\|flac\)"

function cleanup ()
{
   rm "$FormatFile"
}
trap "cleanup"  EXIT

mi=$(which mediainfo)
if [ $? -eq 1 ]; then
		echo "Failed to locate mediainfo on this system. This script won't work without it."
      exit;
fi

# Create the Format file used by mediainfo
echo 'General;%FileName%, ""%CompleteName%"", %Format/String%, %FileExtension%, %FileSize/String4%, %Duration/String3%, ' > "$FormatFile"
echo 'Video;%Format/String%, %Width%x%Height%, %FrameRate%, %DisplayAspectRatio/String%, %ScanType% ' >> "$FormatFile"

# Create CSV file with headers
echo "filename, path, format, ext, size, duration, codec, size, fps, aspect, scan type" > "$CSVFile"

find "$FolderRoot" -type f -not -name ".*" -exec "$mi" --Inform="file://$FormatFile" {} \; >> "$CSVFile"
#find "$FolderRoot" -type f -exec "$mi" --Inform="file://$FormatFile" {} \; >> "$CSVFile"

exit;
