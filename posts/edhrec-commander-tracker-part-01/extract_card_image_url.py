# -*- coding: utf-8 -*-
"""
Created on Sat Apr 26 18:17:30 2025

@author: Derek with Copilot
"""

import pandas as pd
import requests
import time
import re

# Load card_data.csv and keep only 'Name' and 'URL' columns
df = pd.read_csv('card_data.csv', usecols=['Name', 'URL'])
df = df.drop_duplicates(subset=['Name'])

# Load card_images.csv
card_images = pd.read_csv('card_images.csv')

# Regex pattern to match the last occurrence of the image URL
pattern = r'"image_uris":\[\{"normal":"(https://[^"]+)"'

# Iterate over df and check if the name exists in card_images
for index, row in df.iterrows():
    name = row['Name']
    url = row['URL']

    # Skip if name already exists in card_images
    if name in card_images['Name'].values:
        continue

    print(f"Requesting data for: {name}")

    try:
        response = requests.get(url)
        time.sleep(0.1)  # delay to avoid timeouts

        # Search for the last occurrence of the image URL in the page source
        if response.status_code == 200:
            matches = re.findall(pattern, response.text)
            if matches:
                image_url = matches[-1]  # Take the last match

                # Append the new row to card_images.csv
                new_row = pd.DataFrame({'Name': [name], 'Image': [image_url]})
                card_images = pd.concat([card_images, new_row], ignore_index=True)
    except Exception as e:
        print(f"Error retrieving data for {name}: {e}")

# Save updated card_images.csv
card_images.to_csv('card_images.csv', index=False)
print("Updated card_images.csv successfully!")