# -*- coding: utf-8 -*-
"""
Created with Copilot
"""

import requests
import json
import pandas as pd
import os
import re
from datetime import datetime

# Load commander list from CSV
commanders_file = "Commanders.csv"
output_file = "card_data.csv"

try:
    commanders_df = pd.read_csv(commanders_file)
except FileNotFoundError:
    print(f"Error: {commanders_file} not found.")
    exit()

# Ensure expected columns exist
if "Commander" not in commanders_df.columns or "url" not in commanders_df.columns:
    print(f"Error: {commanders_file} must contain 'Commander' and 'url' columns.")
    exit()

# Get current date
current_date = datetime.today().strftime("%Y-%m-%d")

# List to store results
all_cards = []

for _, row in commanders_df.iterrows():
    commander_name = row["Commander"]
    url = row["url"]

    print(f"Processing data for {commander_name}...")

    # Fetch webpage content
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve webpage for {commander_name}. Status code: {response.status_code}")
        continue

    # Extract JSON data from the page source
    page_content = response.text
    json_start = page_content.find('"json_dict":')

    if json_start == -1:
        print(f"No JSON data found for {commander_name}. Skipping...")
        continue

    # Extract JSON until '],"card":'
    json_data_str = page_content[json_start + len('"json_dict":'):]
    json_data_str = json_data_str.split('],"card":', 1)[0] + "]}"  # Close JSON properly

    try:
        json_data = json.loads(json_data_str)
    except json.JSONDecodeError:
        print(f"Failed to parse JSON for {commander_name}. Skipping...")
        continue

    # Extract card data
    for cardlist in json_data.get("cardlists", []):
        header = cardlist.get("header", "Unknown")
        for card in cardlist.get("cardviews", []):
            raw_label = card.get("label", "N/A")

            # Extract percentage using regex
            match = re.search(r"\d+%", raw_label)
            label_cleaned = match.group(0) if match else "N/A"

            all_cards.append([
                commander_name,
                current_date,
                card.get("name", "N/A"),
                card.get("inclusion", "N/A"),
                label_cleaned,  # Only the percentage
                "https://edhrec.com" + card.get("url", ""),
                header
            ])

# Convert to DataFrame
df = pd.DataFrame(all_cards, columns=["Commander", "Date", "Name", "Inclusion", "Label", "URL", "Header"])

# Save or append to CSV
if os.path.exists(output_file):
    df.to_csv(output_file, mode="a", header=False, index=False)  # Append without headers
else:
    df.to_csv(output_file, index=False)  # Create new file

print(f"Data saved successfully to {output_file}!")