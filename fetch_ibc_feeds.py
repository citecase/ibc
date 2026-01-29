import feedparser
import json
import os
import sys
from datetime import datetime

# Configuration for IBC specific feeds and keywords
FEEDS = [
    "https://ibclaw.in/feed",
    "https://www.livelawbiz.com/ibc/feed",
    "https://caseciter.com/rss",
    "https://verdictum.in/feed",
    "https://www.barandbench.com/feed"
]
KEYWORDS = ["ibc", "insolvency", "cirp", "bankruptcy", "nclt", "nclat"]
JSON_FILE = "ibc.json"
MD_FILE = "ibc.md"

def fetch_and_filter():
    print(f"Starting IBC feed sync at {datetime.now()}")
    
    # 1. Load existing data to avoid duplicates
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            try:
                content = f.read()
                all_entries = json.loads(content) if content.strip() else []
            except Exception as e:
                print(f"Error loading existing JSON: {e}")
                all_entries = []
    else:
        all_entries = []

    existing_links = {item['link'] for item in all_entries}
    new_found = False
    new_items_count = 0

    # 2. Fetch and filter
    for url in FEEDS:
        try:
            print(f"Fetching: {url}")
            feed = feedparser.parse(url)
            
            if feed.bozo:
                print(f"Warning: Non-critical issue parsing {url}")

            for entry in feed.entries:
                title = entry.title
                summary = entry.get('summary', '')
                link = entry.link
                
                # Search keywords in title or summary
                text_to_search = (title + " " + summary).lower()
                
                if any(kw in text_to_search for kw in KEYWORDS) and link not in existing_links:
                    all_entries.insert(0, {
                        "title": title,
                        "link": link,
                        "published": entry.get('published', datetime.now().strftime("%d %b %Y")),
                        "source_url": url,
                        "timestamp": datetime.now().isoformat()
                    })
                    existing_links.add(link)
                    new_found = True
                    new_items_count += 1
        except Exception as e:
            print(f"Error processing feed {url}: {e}")

    if not new_found:
        print("No new IBC updates found.")
        return

    print(f"Found {new_items_count} new articles.")

    # 3. Save updated JSON
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(all_entries, f, indent=4)

    # 4. Rewrite Markdown file
    with open(MD_FILE, "w", encoding="utf-8") as f:
        f.write("# IBC & Insolvency Updates\n\n")
        f.write(f"*Last synced: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
        
        if not all_entries:
            f.write("No articles found yet.\n")
        else:
            for item in all_entries:
                f.write(f"### [{item['title']}]({item['link']})\n")
                f.write(f"- **Published:** {item['published']}\n")
                f.write(f"- **Source:** {item['source_url']}\n\n")

if __name__ == "__main__":
    fetch_and_filter()
