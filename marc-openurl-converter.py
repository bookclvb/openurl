#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MARC to OpenURL Converter

This script converts MARC records to include OpenURL links in 856 fields.
It replaces the multi-step bash process with a single Python script.
"""

import os
import re
from pymarc import MARCReader, Record, Field, Subfield

def read_locations_file(filename):
    """Read the locations.txt file and return a dictionary of location codes and names."""
    locations = {}
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            if '|' in line:
                parts = line.strip().split('|')
                if len(parts) >= 2:
                    locations[parts[0]] = parts[1]
    return locations

def sanitize_url_text(text):
    """Sanitize text for URL usage by replacing spaces and special characters."""
    if not text:
        return ""
    # Replace special characters
    text = text.replace('&', '%26')
    text = text.replace('+', '%2b')
    # Replace spaces with plus signs
    text = text.replace(' ', '+')
    return text

def process_bib_data(bib_line, locations):
    """Process a bibliographic data line and return a dictionary of values."""
    parts = bib_line.strip().split('|')
    
    # Handle case where line doesn't have enough parts
    if len(parts) < 7:
        print(f"Warning: Line does not have enough fields: {bib_line}")
        return None
    
    bibnum = parts[0]
    blink = re.sub(r'[0-9a-z]$', '', bibnum)
    author = sanitize_url_text(parts[1])
    title_a = sanitize_url_text(parts[2])
    title_b = sanitize_url_text(parts[3])
    callnum = sanitize_url_text(parts[4])
    genre_raw = parts[5].strip()
    loc_code = parts[6].strip()
    
    # Concatenate titles
    x_title = f"{title_a} {title_b}".strip()
    
    # Set default values
    author = author if author else "BLANK"
    callnum = callnum if callnum else "n/a"
    
    # Initialize default values
    genre = "monograph"
    volume = "BLANK"
    i_title = "BLANK"
    s_title = "BLANK"
    
    # Determine genre and related fields
    if genre_raw == "x":
        genre = "serial"
        volume = "n/a"
    elif genre_raw == "b":
        genre = "manuscript"
        volume = "n/a"
        i_title = x_title
        x_title = "BLANK"
    
    # Determine location
    if ',' in loc_code:
        location = "Multiple"
    else:
        location = locations.get(loc_code, "")
        location = sanitize_url_text(location)
    
    # Create the permalink
    permalink = f"https://librarycat.risd.edu/record={blink}"
    
    return {
        'bibnum': bibnum,
        'genre': genre,
        'x_title': x_title,
        'i_title': i_title,
        's_title': s_title,
        'author': author,
        'callnum': callnum,
        'volume': volume,
        'location': location,
        'permalink': permalink
    }

def build_openurl(bib_data):
    """Build an OpenURL from the bibliographic data."""
    baseurl = "https://aeon.risd.edu/logon?Action=10&Form=30&"
    
    # Construct the raw URL with all parameters
    url_raw = (
        f"{baseurl}Genre={bib_data['genre']}"
        f"&Title={bib_data['x_title']}"
        f"&ItemTitle={bib_data['i_title']}"
        f"&ItemSubTitle={bib_data['s_title']}"
        f"&Author={bib_data['author']}"
        f"&CallNumber={bib_data['callnum']}"
        f"&ItemVolume={bib_data['volume']}"
        f"&Location={bib_data['location']}"
        f"&ItemInfo1={bib_data['permalink']}"
    )
    
    # Remove any BLANK parameters and ensure proper spacing
    finalurl = url_raw
    for blank_param in ["&Title=BLANK", "&ItemTitle=BLANK", "&ItemSubTitle=BLANK", 
                        "&Author=BLANK", "&ItemVolume=BLANK", "&Location=BLANK"]:
        finalurl = finalurl.replace(blank_param, "")
    
    finalurl = finalurl.replace(' ', '+')
    
    return finalurl

def process_marc_file(marc_filename, bib_filename, locations_filename, output_filename):
    """
    Process MARC records and bibliographic data to create new MARC records with OpenURLs.
    
    Args:
        marc_filename: Path to the input MARC file (.mrc)
        bib_filename: Path to the bibliographic data file (.txt)
        locations_filename: Path to the locations mapping file (.txt)
        output_filename: Path to the output MARC file (.mrc)
    """
    print(f"Starting MARC to OpenURL conversion process...")
    
    # Read locations file
    locations = read_locations_file(locations_filename)
    print(f"Loaded {len(locations)} location codes from {locations_filename}")
    
    # Read bibliographic data
    bib_data_by_id = {}
    with open(bib_filename, 'r', encoding='utf-8') as bib_file:
        # Skip header line if present
        first_line = bib_file.readline()
        if "RECORD #(BIBLIO)" in first_line:
            print("Skipping header line in bibliographic data file")
        else:
            # Process the first line if it wasn't a header
            bib_line_data = process_bib_data(first_line, locations)
            if bib_line_data:
                bib_data_by_id[bib_line_data['bibnum']] = bib_line_data
        
        # Process remaining lines
        for line in bib_file:
            bib_line_data = process_bib_data(line, locations)
            if bib_line_data:
                bib_data_by_id[bib_line_data['bibnum']] = bib_line_data
    
    print(f"Loaded bibliographic data for {len(bib_data_by_id)} records")
    
    # Process MARC records
    output_records = []
    record_count = 0
    modified_count = 0
    
    with open(marc_filename, 'rb') as marc_file:
        reader = MARCReader(marc_file)
        for record in reader:
            record_count += 1
            
            # Extract record ID from 907 field
            record_id = None
            if record['907'] and record['907']['a']:
                record_id = record['907']['a'].replace('.', '')
            
            if record_id and record_id in bib_data_by_id:
                # Build OpenURL
                openurl = build_openurl(bib_data_by_id[record_id])
                
                # Create a new 856 field with the OpenURL using the new Subfield approach
                subfields = [
                    Subfield('u', openurl),
                    Subfield('z', 'Special Collections Request')
                ]
                
                field_856 = Field(
                    tag='856',
                    indicators=['4', '0'],
                    subfields=subfields
                )
                
                # Remove existing 856 fields with same URL pattern (optional)
                existing_856_fields = record.get_fields('856')
                for field in existing_856_fields:
                    if field.get_subfields('u') and 'aeon.risd.edu' in field.get_subfields('u')[0]:
                        record.remove_field(field)
                
                # Add the new 856 field
                record.add_field(field_856)
                modified_count += 1
            
            output_records.append(record)
    
    # Write output MARC file
    with open(output_filename, 'wb') as out_file:
        for record in output_records:
            out_file.write(record.as_marc())
    
    print(f"Processed {record_count} MARC records")
    print(f"Modified {modified_count} records with OpenURLs")
    print(f"Output written to {output_filename}")

def main():
    """Main function to run the script."""
    # Define file paths
    marc_file = "input.mrc"  # Your input MARC file
    bib_file = "bib.txt"     # Your bibliographic data file
    locations_file = "locations.txt"  # Your locations mapping file
    output_file = "output.mrc"  # Output MARC file with added OpenURLs
    
    # Run the processing
    process_marc_file(marc_file, bib_file, locations_file, output_file)

if __name__ == "__main__":
    main()