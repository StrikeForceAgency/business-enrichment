import pandas as pd
import requests
import re
import time
from serpapi import GoogleSearch
from utils import validate_email, extract_phone_numbers

# Load the CSV file
df = pd.read_csv("business_data.csv")
df.columns = df.columns.str.strip()  # removes accidental leading/trailing spaces
df.columns = df.columns.str.replace(" ", "_")  # Replaces spaces with underscores

# Filter records with missing email or phone
df = df[(df["Email"] == "") | (df["Phone"] == "")]
print("Columns available:", df.columns.tolist())

# Add new columns for enriched data
df["Website"] = ""

# SerpAPI key setup
API_KEY = "YOUR_SERPAPI_KEY"

def search_google(query):
    params = {
        "engine": "google",
        "q": query,
        "api_key": API_KEY,
        "num": 5
    }
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        return results.get("organic_results", [])
    except Exception as e:
        print(f"Error searching for '{query}': {e}")
        return []

# Loop through entries
for i, row in df.iterrows():
    name = row["Business_Name"]
    city = row["City"]
    query = f"{name} {city} contact"

    print(f"[{i+1}/{len(df)}] Searching: {query}")
    results = search_google(query)

    for result in results:
        link = result.get("link", "")
        snippet = result.get("snippet", "")

        # Save the first relevant website
        if df.at[i, "Website"] == "" and "http" in link:
            df.at[i, "Website"] = link

        # Extract email if missing
        if df.at[i, "Email"] == "" and "@" in snippet:
            email_candidates = [word for word in snippet.split() if validate_email(word)]
            if email_candidates:
                df.at[i, "Email"] = email_candidates[0]

        # Extract phone if missing
        if df.at[i, "Phone"] == "":
            phone_candidates = extract_phone_numbers(snippet)
            if phone_candidates:
                df.at[i, "Phone"] = phone_candidates[0]

    # Save enriched data every 300 successful finds
    if (i + 1) % 300 == 0:
        df.to_csv("Enriched_Business_Data.csv", index=False)
        print(f"Saved enriched data after processing {i + 1} entries.")

    # Respect rate limits
    time.sleep(2)

# Final save to new file
df.to_csv("Enriched_Business_Data.csv", index=False)
print("✅ Enrichment complete. File saved as 'Enriched_Business_Data.csv'")