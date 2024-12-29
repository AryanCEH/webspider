import requests
from bs4 import BeautifulSoup
import datetime
import csv
import re

# Function to scrape important information from a website
def scrape_website(url, target_elements):
    """Scrape information from the given website.

    Args:
        url (str): The URL of the website to scrape.
        target_elements (dict): A dictionary with keys as element names (e.g., 'title')
                               and values as CSS selectors to extract them.

    Returns:
        dict: Extracted information.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        extracted_data = {}
        for key, selector in target_elements.items():
            element = soup.select_one(selector)
            extracted_data[key] = element.text.strip() if element else None

        return extracted_data

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return {}
    except Exception as e:
        print(f"An error occurred: {e}")
        return {}

# Function to extract keywords from meta tags
def extract_keywords(url):
    """Extract keywords from the meta tag of a webpage.

    Args:
        url (str): The URL of the webpage.

    Returns:
        list: A list of keywords.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        keywords_meta = soup.find("meta", attrs={"name": "keywords"})

        if keywords_meta and keywords_meta.get("content"):
            return [keyword.strip() for keyword in keywords_meta["content"].split(",")]
        else:
            return []
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL for keywords: {e}")
        return []

# Function to check robots.txt for crawling rules
def check_robots_txt(url):
    """Check the robots.txt file of a website for crawling rules.

    Args:
        url (str): The base URL of the website.

    Returns:
        dict: A dictionary with rules extracted from robots.txt.
    """
    robots_url = f"{url.rstrip('/')}/robots.txt"
    try:
        response = requests.get(robots_url)
        if response.status_code == 200:
            rules = {}
            for line in response.text.splitlines():
                line = line.strip()
                if line.startswith("User-agent") or line.startswith("Disallow") or line.startswith("Allow"):
                    key, _, value = line.partition(":")
                    rules.setdefault(key.strip(), []).append(value.strip())
            return rules
        else:
            print(f"robots.txt not found at {robots_url}")
            return {}
    except requests.exceptions.RequestException as e:
        print(f"Error fetching robots.txt: {e}")
        return {}

# Function to extract web technologies used
def detect_web_technologies(url):
    """Detect web technologies used by analyzing response headers.

    Args:
        url (str): The URL of the website.

    Returns:
        list: A list of detected technologies.
    """
    try:
        response = requests.get(url)
        headers = response.headers
        technologies = []

        # Simple detection based on headers
        if "X-Powered-By" in headers:
            technologies.append(headers["X-Powered-By"])
        if "Server" in headers:
            technologies.append(headers["Server"])
        return technologies
    except requests.exceptions.RequestException as e:
        print(f"Error detecting technologies: {e}")
        return []

# Function to filter scraped data by date
def filter_by_date(data, date_key, date_format="%Y-%m-%d", date_threshold=None):
    """Filter data based on a date key.

    Args:
        data (list): A list of dictionaries containing scraped data.
        date_key (str): The key containing the date in each dictionary.
        date_format (str): The format of the date in the data.
        date_threshold (datetime.date): The threshold date for filtering.

    Returns:
        list: Filtered data.
    """
    if not date_threshold:
        date_threshold = datetime.date.today()

    filtered_data = []
    for item in data:
        try:
            if not item.get(date_key):
                print(f"Warning: Missing date for item {item}. Skipping.")
                continue

            item_date = datetime.datetime.strptime(item[date_key], date_format).date()
            if item_date >= date_threshold:
                filtered_data.append(item)
        except (ValueError, KeyError) as e:
            print(f"Error processing date for item {item}: {e}. Skipping.")
            continue

    return filtered_data

# Function to save data to a CSV file
def save_to_csv(data, filename):
    """Save data to a CSV file.

    Args:
        data (list): A list of dictionaries to save.
        filename (str): The name of the CSV file.
    """
    if not data:
        print("No data to save.")
        return

    keys = data[0].keys()
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)

    print(f"Data saved to {filename}")

if __name__ == "__main__":
    # Example usage
    website_url = "https://internshala.com/"
    elements_to_scrape = {
        "title": "title",
        "date": "meta[property='article:published_time'], meta[name='date'], time[datetime]",  # Updated to include multiple date selectors
        "description": "meta[name='description']"
    }

    print(f"Scraping website: {website_url}\n")
    scraped_data = [scrape_website(website_url, elements_to_scrape)]

    # Filter data by a threshold date (e.g., today)
    filtered_data = filter_by_date(scraped_data, date_key="date", date_format="%Y-%m-%d")

    if filtered_data:
        print("Filtered Data:")
        for item in filtered_data:
            print(item)

        # Save to CSV
        save_to_csv(filtered_data, "scraped_data.csv")
    else:
        print("No data matching the date criteria.")

    # Extract keywords
    print("\nExtracting keywords...")
    keywords = extract_keywords(website_url)
    print("Keywords:", keywords)

    # Check robots.txt
    print("\nChecking robots.txt...")
    robots_rules = check_robots_txt(website_url)
    print("Robots.txt Rules:", robots_rules)

    # Detect web technologies
    print("\nDetecting web technologies...")
    technologies = detect_web_technologies(website_url)
    print("Detected Technologies:", technologies)
