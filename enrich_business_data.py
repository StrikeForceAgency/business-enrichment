import pandas as pd
import requests
import re
import time
from serpapi import GoogleSearch
from utils import validate_email, extract_phone_numbers


# Load the CSV file (update filename to match your actual CSV)
CSV_FILENAME = "Filtered_CA_Domestic_Entities.csv"
try:
    df = pd.read_csv(CSV_FILENAME)
except FileNotFoundError:
    print(f"❌ CSV file '{CSV_FILENAME}' not found. Please place it in the project folder.")
    exit(1)

# Clean column names
df.columns = df.columns.str.strip()
df.columns = df.columns.str.replace(" ", "_")

# Ensure required columns exist
for col in ["Email", "Phone", "Business_Name", "City"]:
    if col not in df.columns:
        df[col] = ""

# Filter records with missing email or phone
df = df[(df["Email"] == "") | (df["Phone"] == "")]
print("Columns available:", df.columns.tolist())

# Add new columns for enriched data
if "Website" not in df.columns:
    df["Website"] = ""

# SerpAPI key setup
API_KEY = "YOUR_SERPAPI_KEY"  # Replace with your actual key or use an environment variable

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
