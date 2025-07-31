# Business Enrichment Project

This project is designed to enrich business data by extracting contact information such as emails and phone numbers from a list of businesses stored in a CSV file. The enrichment process utilizes web scraping and free APIs to gather additional information.

## Project Structure

```
business-enrichment
├── src
│   ├── enrich_business_data.py  # Main logic for enriching business data
│   └── utils.py                 # Utility functions for data processing
├── requirements.txt             # Required libraries for the project
├── .gitignore                   # Files and directories to ignore in version control
└── README.md                    # Documentation for the project
```

## Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone https://github.com/StrikeForceAgency/business-enrichment.git
   cd business-enrichment
   ```

2. **Install the required libraries**:
   Make sure you have Python installed, then run:
   ```bash
   pip install -r requirements.txt
   ```

   > **If you get an error about missing Xcode Command Line Tools on Mac, run:**
   > ```bash
   > xcode-select --install
   > ```
   > Then re-run the `pip install` command above.

## Usage Guidelines

1. Prepare your CSV file with the necessary business data. Ensure that the file contains columns for business names and any other relevant information.

2. Run the enrichment script:
   ```bash
   python src/enrich_business_data.py <path_to_your_csv_file>
   ```

3. The enriched data will be saved to a new CSV file in the same directory.

## Enrichment Process Overview

- The script loads the CSV file and cleans the column names.
- It filters records that are missing email or phone information.
- For each business, it performs searches using SerpAPI, Bing, and DuckDuckGo.
- The script extracts contact information using regular expressions.
- Enriched data is saved to a new CSV file after every 300 successful email finds to ensure data is not lost in case of interruptions.

## Troubleshooting

- **Read-only file:**  
  If you can't edit a file, run:
  ```bash
  chmod u+w <filename>
  ```
- **Permission denied:**  
  Make sure you are in the correct directory and have write permissions.
- **Cloning asks for username/password:**  
  If the repo is private, use your GitHub username and a [personal access token](https://github.com/settings/tokens) as the password.

## Pushing Local Files to GitHub

If you have files on your Desktop you want to add to this repo:

```bash
cp -R ~/Desktop/business-enrichment/* .
git add .
git commit -m "Add local project files"
git push
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.