#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MARC to OpenURL Converter

This script converts MARC records to include OpenURL links in 856 fields.
It extracts all necessary data directly from the MARC records.
"""

import os
import re
import json
import logging
from pymarc import MARCReader, Record, Field, Subfield

def read_locations_file(filename):
    """Read a JSON locations file mapping code -> name.
    Falls back to returning an empty dict if the file is missing or invalid.
    """
    locations = {}
    if not filename:
        return locations
    try:
        with open(filename, 'r', encoding='utf-8') as fh:
            data = json.load(fh)
            if isinstance(data, dict):
                locations = {str(k): str(v) for k, v in data.items()}
            else:
                print(f"Warning: locations file {filename} does not contain a mapping (code->name)")
    except FileNotFoundError:
        print(f"Warning: locations file not found: {filename}")
    except Exception as e:
        print(f"Warning: failed to read locations file {filename}: {e}")
    return locations

def read_items_file(filename):
    """Read items.txt and return a mapping of bibnum -> list of location codes.

    Expected lines are CSV-like with quoted fields, e.g.
      "b10428094","rstmp"
    Some lines contain multiple quoted location codes; we collect all quoted strings after the first as codes.
    """
    items = {}
    if not filename:
        return items
    try:
        with open(filename, 'r', encoding='utf-8') as fh:
            for line in fh:
                parts = re.findall(r'"([^"]*)"', line)
                if not parts:
                    continue
                bib = parts[0].strip()
                codes = [p.strip() for p in parts[1:]]
                if codes:
                    seen = set()
                    out = []
                    for c in codes:
                        if c and c not in seen:
                            seen.add(c)
                            out.append(c)
                    items[bib] = out
    except FileNotFoundError:
        print(f"Warning: items file not found: {filename}")
    except Exception as e:
        print(f"Warning: failed to read items file {filename}: {e}")
    return items

def sanitize_url_text(text):
    if not text:
        return ""
    # Replace special characters
    text = text.replace('&', '%26')
    text = text.replace('+', '%2b')
    # Replace spaces with plus signs
    text = text.replace(' ', '+')
    return text
def extract_bib_data_from_marc(record, locations, items_map=None):
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
    
    # Extract call number from 099 or 050 field.
    # Collect all subfield values (preserve repeatable subfields) and join them with spaces.
    callnum = ""
    # Prefer 099; fall back to 050. Use the first occurrence of the field if multiple exist.
    call_field = None
    fields_099 = record.get_fields('099')
    if fields_099:
        call_field = fields_099[0]
    else:
        fields_050 = record.get_fields('050')
        if fields_050:
            call_field = fields_050[0]

    if call_field is not None:
        # Field.subfields may be either a list of Subfield objects (pymarc newer)
        # or a flat list like ['a','value','b','value2', ...]. Handle both.
        raw = call_field.subfields
        values = []
        if raw:
            # detect Subfield objects
            if all(hasattr(x, 'value') for x in raw):
                for x in raw:
                    try:
                        v = x.value
                    except Exception:
                        v = str(x)
                    if v:
                        values.append(v)
            else:
                # assume flat list and take every second element
                values = raw[1::2]

        # Join non-empty values with a single space
        callnum = ' '.join([str(v) for v in values if v])

    callnum = sanitize_url_text(callnum)
    
    # Determine genre based on 998 subfield e
    genre_raw = ""
    if '998' in record and record['998'] is not None and 'e' in record['998']:
        genre_code = record['998']['e'].strip()
        # Map the genre code to the appropriate genre_raw value
        if genre_code == "s":  # Serial
            genre_raw = "x"
        elif genre_code in ["d", "f", "p"]:  # Manuscript 
            genre_raw = "b"
    
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
    
    # Prefer item-level locations (from items.txt) when available for this bibnum
    item_loc_codes = None
    if items_map and bibnum:
        # items.txt uses bib IDs like b10428094; bibnum is expected to match without dots
        # ensure we match the exact key
        candidate = bibnum
        if candidate in items_map:
            item_loc_codes = items_map[candidate]

    if item_loc_codes:
        # use item-level loc codes
        loc_source = 'items'
        loc_list = item_loc_codes
    else:
        loc_source = '907'
        loc_list = loc_codes

    # Map loc_list codes to human-readable names via locations mapping
    if not loc_list:
        location = ""
    elif len(loc_list) == 1:
        location = locations.get(loc_list[0], loc_list[0])
    else:
        mapped = [locations.get(code, code) for code in loc_list]
        location = ', '.join(mapped)
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
    # Configure logging for skipped records (overwrites each run)
    logging.basicConfig(
        filename='skipped_records.log',
        filemode='a',
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s'
    )
    logging.info('Beginning MARC to OpenURL conversion')
    
    # Read locations file
    locations = read_locations_file(locations_filename)
    print(f"Loaded {len(locations)} location codes from {locations_filename}")

    # Read items file (item-level locations)
    items_map = read_items_file('items.txt')
    print(f"Loaded {len(items_map)} item location entries from items.txt")
    
    # Process MARC records
    output_records = []
    record_count = 0
    modified_count = 0
    skipped_count = 0
    
    with open(marc_filename, 'rb') as marc_file:
        reader = MARCReader(marc_file)
        for record in reader:
            record_count += 1
            
            # Extract bibliographic data directly from the MARC record
            bib_data = extract_bib_data_from_marc(record, locations, items_map=items_map)
            
            if bib_data:
                # Build OpenURL
                openurl = build_openurl(bib_data)
                
                # Create a new 856 field with the OpenURL
                # ALTER LINK TEXT HERE
                subfields = [
                    Subfield('u', openurl),
                    Subfield('z', 'Special Collections Request')
                ]
                
                field_856 = Field(
                    tag='856',
                    indicators=['4', '0'],
                    subfields=subfields
                )
                
                # Remove existing 856 fields with same URL pattern
                existing_856_fields = record.get_fields('856')
                for field in existing_856_fields:
                    if field.get_subfields('u') and 'aeon.risd.edu' in field.get_subfields('u')[0]:
                        record.remove_field(field)
                
                # Add the new 856 field
                record.add_field(field_856)
                modified_count += 1
            else:
                # Log skipped records (those missing 907 $a / bibnum)
                # Prefer controlfield 001 as an identifier; fall back to leader if absent
                rec_id = None
                if record.get_fields('001'):
                    try:
                        rec_id = record['001'].value()
                    except Exception:
                        rec_id = str(record['001'])
                else:
                    rec_id = record.leader

                title_snippet = ''
                if '245' in record and record['245'] is not None and 'a' in record['245']:
                    title_snippet = record['245']['a']

                logging.info(f"Skipped record missing 907 $a - id={rec_id!s} title={title_snippet}")
                skipped_count += 1
            
            output_records.append(record)
    
    # Write output MARC file
    with open(output_filename, 'wb') as out_file:
        for record in output_records:
            out_file.write(record.as_marc())
    
    print(f"Processed {record_count} MARC records")
    print(f"Modified {modified_count} records with OpenURLs")
    print(f"Skipped {skipped_count} records (missing 907 $a). See skipped_records.log for details")
    print(f"Output written to {output_filename}")

def main():
    """Main function to run the script."""
    # Define file paths
    marc_file = "input.mrc" 
    locations_file = "locations.json"
    output_file = "output.mrc" 
    
    # Run the processing
    process_marc_file(marc_file, locations_file, output_file)

if __name__ == "__main__":
    main()
