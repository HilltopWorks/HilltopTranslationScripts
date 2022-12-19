"""
XML Generator for SRT video translations on the PSX

Takes in a folder containing translated frames and writes out an XML import document
for the SRT tool

Usage: <frame_filepath> <output_filepath>

"""

import sys
import re
import os
import xml.etree.ElementTree as ET
from pathlib import Path

frames_to_export = {}

FRAME_OFFSET = 0

# Return a usage message if not enough arguments were supplied
if len(sys.argv) < 3:
    print("Usage: <folder_of_translated_frames> <output_dir>")
    exit()

frame_filepath = sys.argv[1]
output_filepath = sys.argv[2]

frame_number_regex = re.compile(r"\[\d*\]\[(\d*)\]")


def read_directory(directory):
    """
    Scans the given directory recursively and parses any files within
    for their frame number and file path

    Frame number is in the format of [0][xyz], where xyz is the frame number
    :param directory: Current directory to scan
    """
    for path in Path(directory).rglob("*"):
        # If this is a directory, ignore it
        if path.is_dir():
            continue

        # Check that the given image is in the right format
        # This could be made more sophisticated
        if "[" not in path.name:
            print("Image was not in the right format, ignoring: " + str(path))
            continue

        video_name = path.name.split("[")[0]
        frame_number = int(re.search(frame_number_regex, path.name).group(1))

        # If a frame number could not be parsed, return an error and ignore it
        if frame_number < 0:
            print("Could not parse image from " + path.name)
            continue

        # If this is the first time we've seen this video, add a new entry for it
        if video_name not in frames_to_export:
            frames_to_export[video_name] = []

        frame_entry = {"frame_number": frame_number, "frame_filepath": str(path)}
        frames_to_export[video_name].append(frame_entry)


def write_xml(video_name, frame, output):
    """
    Generates XML from a video entry
    :param video_name: Name of the video, derived from the frame's filename
    :param frame: Frame data, which includes the frame number and file name
    :param output: Folder to write resulting XML to
    """
    # Make the output directory if it doesn't exist
    if not os.path.exists(output):
        os.makedirs(output)

    root = ET.Element("str-replace")
    root.set("version", "0.3")
    for entry in frame:
        replace = ET.SubElement(root, "replace")
        replace.set("frame", '#' + str( entry["frame_number"] + FRAME_OFFSET))
        replace.text = entry["frame_filepath"]

    xml_data = ET.tostring(root).decode()
    output_file = open(output + os.path.sep + video_name + ".xml", "w")
    output_file.write(xml_data)


def export_frames(output):
    """
    Exports over the parsed video information and writes out XML
    :param output: Folder to output XML to
    """
    for video_name in frames_to_export:
        write_xml(video_name, frames_to_export[video_name], output_filepath)


print("\nSearching for all images in " + frame_filepath )
read_directory(frame_filepath)

print("Parsing complete!\n")
print("Writing XML...")
export_frames(output_filepath)

print("Complete!")