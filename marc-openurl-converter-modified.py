#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MARC to OpenURL Converter

This script converts MARC records to include OpenURL links in 856 fields.
It extracts all necessary data directly from the MARC records without requiring a separate bibliographic data file.
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
def extract_bib_data_from_marc(record, locations):
    """Extract bibliographic data directly from a MARC record."""
    # Extract record ID from 907 field
    bibnum = None
    if '907' in record and record['907'] is not None:
        if 'a' in record['907']:
            bibnum = record['907']['a'].replace('.', '')
    
    if not bibnum:
        return None
    
    blink = re.sub(r'[0-9a-z]$', '', bibnum)
    
    # Extract author from 100 or 110 field
    author = ""
    if '100' in record and record['100'] is not None and 'a' in record['100']:
        author = record['100']['a']
    elif '110' in record and record['110'] is not None and 'a' in record['110']:
        author = record['110']['a']
    author = sanitize_url_text(author)
    
    # Extract title information from 245 field
    title_a = ""
    title_b = ""
    if '245' in record and record['245'] is not None:
        if 'a' in record['245']:
            title_a = record['245']['a']
        if 'b' in record['245']:
            title_b = record['245']['b']
    
    title_a = sanitize_url_text(title_a)
    title_b = sanitize_url_text(title_b)
    
    # Extract call number from 099 or 050 field
    callnum = ""
    if '099' in record and record['099'] is not None:
        if 'a' in record['099']:
            callnum = record['099']['a']
            if 'b' in record['099']:
                callnum += " " + record['099']['b']
    elif '050' in record and record['050'] is not None:
        if 'a' in record['050']:
            callnum = record['050']['a']
            if 'b' in record['050']:
                callnum += " " + record['050']['b']
    callnum = sanitize_url_text(callnum)
    
    # Determine genre based on 998 subfield e
    genre_raw = ""
    if '998' in record and record['998'] is not None and 'e' in record['998']:
        genre_code = record['998']['e'].strip()
        # Map the genre code to the appropriate genre_raw value
        # Adjust these mappings based on your catalog's conventions
        if genre_code == "s":  # Serial
            genre_raw = "x"
        elif genre_code in ["d", "f", "p"]:  # Manuscript 
            genre_raw = "b"
        # You can add more mappings as needed
    
    # Extract location codes from 907 fields
    loc_codes = []
    for field in record.get_fields('907'):
        if 'b' in field:
            loc_code = field['b'].strip()
            if loc_code and loc_code not in loc_codes:
                loc_codes.append(loc_code)
    
    # Join multiple location codes with commas
    joined_loc_code = ",".join(loc_codes)
    
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
    if len(loc_codes) > 1:
        location = "Multiple"
    else:
        location = locations.get(joined_loc_code, "")
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
        'permalink': permalink,
        'loc_code': joined_loc_code  # Added this to keep track of the original location codes
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

def process_marc_file(marc_filename, locations_filename, output_filename):
    """
    Process MARC records to create new MARC records with OpenURLs.
    All data is extracted directly from the MARC records.
    
    Args:
        marc_filename: Path to the input MARC file (.mrc)
        locations_filename: Path to the locations mapping file (.txt)
        output_filename: Path to the output MARC file (.mrc)
    """
    print(f"Starting MARC to OpenURL conversion process...")
    
    # Read locations file
    locations = read_locations_file(locations_filename)
    print(f"Loaded {len(locations)} location codes from {locations_filename}")
    
    # Process MARC records
    output_records = []
    record_count = 0
    modified_count = 0
    
    with open(marc_filename, 'rb') as marc_file:
        reader = MARCReader(marc_file)
        for record in reader:
            record_count += 1
            
            # Extract bibliographic data directly from the MARC record
            bib_data = extract_bib_data_from_marc(record, locations)
            
            if bib_data:
                # Build OpenURL
                openurl = build_openurl(bib_data)
                
                # Create a new 856 field with the OpenURL
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
    marc_file = "input.mrc"     # Your input MARC file
    locations_file = "locations.txt"  # Your locations mapping file
    output_file = "output.mrc"  # Output MARC file with added OpenURLs
    
    # Run the processing
    process_marc_file(marc_file, locations_file, output_file)

if __name__ == "__main__":
    main()
