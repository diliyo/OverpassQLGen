import requests
from bs4 import BeautifulSoup
import json


def scrape_osm_primary_features():
    """
    Scrapes key-value pairs from the 'Primary features' tables on the OSM wiki page,
    stopping at the 'Additional properties' section.
    """
    url = "https://wiki.openstreetmap.org/wiki/Map_features"

    try:
        # Send a request to the website
        response = requests.get(url)
        response.raise_for_status()  # Raises an exception for bad status codes (4xx or 5xx)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the page: {e}")
        return {}

    soup = BeautifulSoup(response.content, 'html.parser')
    osm_tags_dict = {}

    # 1. Find the "Primary_features" section
    primary_features_heading = soup.find('span', {'id': 'Primary_features'})
    if not primary_features_heading:
        print("Could not find the 'Primary features' section.")
        return osm_tags_dict

    # 2. Find the "Additional_properties" section to know where to stop
    additional_properties_heading = soup.find('span', {'id': 'Additional_properties'})

    # 3. Navigate through the DOM until the additional properties section is found
    current_element = primary_features_heading.find_parent('h2').find_next_sibling()
    stop_element = additional_properties_heading.find_parent('h2') if additional_properties_heading else None

    while current_element and current_element != stop_element:
        # Look for tables within the current section
        if current_element.name == 'table':
            # Process the table
            process_table(current_element, osm_tags_dict)

        # Move to the next sibling element
        current_element = current_element.find_next_sibling()

    return osm_tags_dict


def process_table(table, tags_dict):
    """Processes a single table to extract keys and values from the first two columns."""
    # Find all rows in the table body. Using tbody is more precise.
    table_body = table.find('tbody')
    if not table_body:
        return

    rows = table_body.find_all('tr')

    for row in rows:
        # Find all data cells in the row
        cells = row.find_all('td')

        # Ensure there are at least two columns
        if len(cells) >= 2:
            # --- Key Extraction: Check for a hyperlink first ---
            key_cell = cells[0]
            key_link = key_cell.find('a')
            # Use the text from the <a> tag if it exists, otherwise use the cell's text
            key = key_link.get_text(strip=True) if key_link else key_cell.get_text(strip=True)

            # --- Value Extraction: Check for a hyperlink first ---
            value_cell = cells[1]
            value_link = value_cell.find('a')
            # Use the text from the <a> tag if it exists, otherwise use the cell's text
            value = value_link.get_text(strip=True) if value_link else value_cell.get_text(strip=True)

            # Remove the "Key:" and "Tag:" prefixes if present, based on the wiki's format.
            if key.startswith('Key:'):
                key = key[4:].strip()
            if value.startswith('Tag:'):
                value = value[4:].strip()

            # Only add if both key and value are non-empty
            if key and value:
                # If the key is already in the dictionary, append the value to its list.
                if key in tags_dict:
                    if value not in tags_dict[key]:
                        tags_dict[key].append(value)
                else:
                    # Create a new list for the key with the first value.
                    tags_dict[key] = [value]


# Execute the scraper and print results
if __name__ == "__main__":
    print("Scraping OSM Primary Features... This may take a moment.")
    tags_dictionary = scrape_osm_primary_features()

    print(f"\nFound {len(tags_dictionary)} unique keys.")
    print("\nSample of extracted key-value pairs:")

    # Print the first 5 items as a sample
    for i, (key, values) in enumerate(list(tags_dictionary.items())[:5]):
        print(f"'{key}': {values}")

    # Save to a file for your project
    with open('osm_primary_tags.json', 'w', encoding='utf-8') as f:
        json.dump(tags_dictionary, f, indent=2, ensure_ascii=False)
    print("\nFull dictionary saved to 'osm_primary_tags.json'.")