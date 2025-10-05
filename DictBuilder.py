import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin


def scrape_osm_primary_features():
    """
    Scrapes key-value pairs from both traditional HTML tables and div-based tables
    in the 'Primary features' section of the OSM wiki.
    """
    url = "https://wiki.openstreetmap.org/wiki/Map_features"

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the page: {e}")
        return {}

    soup = BeautifulSoup(response.content, 'html.parser')
    osm_tags_dict = {}
    primary_features_heading = soup.find('span', {'id': 'Primary_features'})
    if not primary_features_heading:
        print("Could not find the 'Primary features' section.")
        return osm_tags_dict
    additional_properties_heading = soup.find('span', {'id': 'Additional_properties'})
    stop_element = additional_properties_heading.find_parent('h2') if additional_properties_heading else None

    current_element = primary_features_heading.find_parent('h2').find_next_sibling()

    while current_element and current_element != stop_element:
        if current_element.name == 'table':
            process_standard_table(current_element, osm_tags_dict)
        elif current_element.name == 'div' and current_element.get(
                'style') and 'display: table;' in current_element.get('style'):
            process_div_table(current_element, osm_tags_dict)

        current_element = current_element.find_next_sibling()

    return osm_tags_dict


def process_standard_table(table, tags_dict):
    """Processes a standard HTML <table> element."""
    rows = table.find_all('tr')
    for row in rows:
        cells = row.find_all('td')
        if len(cells) >= 2:
            extract_key_value_pair(cells[0], cells[1], tags_dict)


def process_div_table(div_table, tags_dict):
    """
    Processes a div-based table.
    Assumes each 'display: table-row' div represents a row,
    and the cells inside are 'display: table-cell' divs.
    """
    row_divs = div_table.find_all('div', style=lambda s: s and 'display: table-row;' in s)

    for row_div in row_divs:
        cell_divs = row_div.find_all('div', style=lambda s: s and 'display: table-cell;' in s)
        if len(cell_divs) >= 2:
            extract_key_value_pair(cell_divs[0], cell_divs[1], tags_dict)


def extract_key_value_pair(key_cell, value_cell, tags_dict):
    """Extracts and cleans key-value pairs from any type of table cell."""
    key_link = key_cell.find('a')
    key = key_link.get_text(strip=True) if key_link else key_cell.get_text(strip=True)
    if key.startswith('Key:'):
        key = key[4:].strip()

    value_link = value_cell.find('a')
    value = value_link.get_text(strip=True) if value_link else value_cell.get_text(strip=True)
    if value.startswith('Tag:'):
        value = value[4:].strip()

    if key and value:
        if key not in tags_dict:
            tags_dict[key] = []
        if value not in tags_dict[key]:
            tags_dict[key].append(value)


if __name__ == "__main__":
    print("Scraping OSM Primary Features (including div tables)...")
    tags_dictionary = scrape_osm_primary_features()

    print(f"\nFound {len(tags_dictionary)} unique keys.")
    print("\nSample of extracted key-value pairs:")
    for i, (key, values) in enumerate(list(tags_dictionary.items())[:5]):
        print(f"'{key}': {values[:3]}")

    # Save to a file
    with open('osm_primary_tags_complete.json', 'w', encoding='utf-8') as f:
        json.dump(tags_dictionary, f, indent=2, ensure_ascii=False)
    print("\nFull dictionary saved to 'osm_primary_tags_complete.json'.")