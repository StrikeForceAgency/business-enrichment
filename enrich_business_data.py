import pandas as pd
import re
import time
import requests
from serpapi import GoogleSearch

# -------------------- Config --------------------
SERPAPI_KEYS = [
    "5efe1436193f76d932f7af5d2ba7bf4ab754b7cb8d52a83cc4c6a9cb99fd5034",
    "52d618127eb70c4941599878cb2079908e466794137f202f64b4358d638dc07e",
    "62060e899777a0a5a83064f4e4e4ebdcb4499f5e3a9718e31b5516251da09e2e",
    "945d7450dc430addc1430abcb70ab1c8d35bd919f80d0a1a7724707f1a89d49e",
    "129ed34d84b00bc9582138c0ba1b3bd8f7f5e0a673c540de485b9ade7e1b3a3e",
    "c645b316db9f4f1a374988c2fd0b5ea165efe7514c098969bfba89bd9bdd150a"
]
APOLLO_API_KEY = "JQkCq0GrscAt9Wg9rNBTgQ"
INPUT_CSV = "Filtered_CA_Domestic_Entities.csv"
SLEEP_SECONDS = 2

# -------------------- Regex Patterns --------------------
EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
PHONE_REGEX = r"\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}"

# -------------------- Load CSV --------------------
df = pd.read_csv(INPUT_CSV)
df.columns = df.columns.str.strip().str.replace(" ", "_")
for col in ["Email", "Phone", "Website"]:
    if col not in df.columns:
        df[col] = ""

df = df[(df["Email"] == "") | (df["Phone"] == "")]
print(f"🧠 Processing {len(df)} rows")

# -------------------- API Rotation --------------------
key_index = 0
def rotate_serpapi_key():
    global key_index
    key = SERPAPI_KEYS[key_index]
    key_index = (key_index + 1) % len(SERPAPI_KEYS)
    return key

# -------------------- Enrichment Functions --------------------
def search_google(name, city):
    key = rotate_serpapi_key()
    params = {
        "engine": "google",
        "q": f"{name} {city} contact",
        "api_key": key,
        "num": 5
    }
    try:
        return GoogleSearch(params).get_dict().get("organic_results", [])
    except Exception as e:
        print(f"❌ SerpAPI error: {e}")
        return []

def search_apollo(name, city):
    try:
        url = "https://api.apollo.io/v1/mixed_people/search"
        headers = {"Cache-Control": "no-cache"}
        payload = {
            "api_key": APOLLO_API_KEY,
            "q_organization_names": name,
            "person_locations": city,
            "page": 1
        }
        r = requests.post(url, json=payload, headers=headers)
        data = r.json()
        if data.get("people"):
            person = data["people"][0]
            return person.get("email"), person.get("phone_numbers", [None])[0]
    except Exception as e:
        print(f"❌ Apollo error: {e}")
    return None, None

# -------------------- Loop & Enrich --------------------
successful_count = 0
failed_rows = []

for i, row in df.iterrows():
    name, city = row["Business_Name"], row["City"]
    print(f"[{i+1}/{len(df)}] 🔍 {name}, {city}")

    enriched = False
    results = search_google(name, city)

    for result in results:
        snippet = result.get("snippet", "")
        link = result.get("link", "")
        email_match = re.search(EMAIL_REGEX, snippet)
        phone_match = re.search(PHONE_REGEX, snippet)

        if not df.at[i, "Website"] and "http" in link:
            df.at[i, "Website"] = link
        if not df.at[i, "Email"] and email_match:
            df.at[i, "Email"] = email_match.group()
            enriched = True
        if not df.at[i, "Phone"] and phone_match:
            df.at[i, "Phone"] = phone_match.group()
            enriched = True

    if not enriched:
        email, phone = search_apollo(name, city)
        if email:
            df.at[i, "Email"] = email
            enriched = True
        if phone:
            df.at[i, "Phone"] = phone
            enriched = True

    if df.at[i, "Email"]:
        successful_count += 1
        if successful_count % 300 == 0:
            batch_file = f"Enriched_Emails_Batch_{successful_count // 300}.csv"
            df.to_csv(batch_file, index=False)
            print(f"💾 Batch saved: {batch_file}")

    if not enriched:
        failed_rows.append(i)

    time.sleep(SLEEP_SECONDS)

# -------------------- Final Save --------------------
df.to_csv("Enriched_Business_Data_Final.csv", index=False)
print("✅ Final file saved: Enriched_Business_Data_Final.csv")

if failed_rows:
    df.loc[failed_rows].to_csv("Failed_Enrichment.csv", index=False)
    print(f"❗ Failed lookups saved: Failed_Enrichment.csv")
