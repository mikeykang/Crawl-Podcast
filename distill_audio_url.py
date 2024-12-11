import requests
import sqlite3
import xml.etree.ElementTree as ET
import argparse
from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument("--offset", type=int, default=0)
parser.add_argument("--limit", type=int, default=100)
args = parser.parse_args()

conn = sqlite3.connect("podcastindex_feeds.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM podcasts")
print("Total feeds: ", cursor.fetchone()[0])

audio_tracks = []

cursor.execute(f"SELECT * FROM podcasts LIMIT {args.limit} OFFSET {args.offset};")
for i, row in tqdm(enumerate(cursor.fetchall()), total=args.limit):
    feed_url = dict(row)["url"]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        feed_response = requests.get(feed_url, headers=headers, timeout=10)
    except Exception as e:
        print(f"Failed to fetch feed {i} {feed_url}: {e}")

    if feed_response.status_code == 200 and feed_response.content:
        try:
            root = ET.fromstring(feed_response.content)
            for item in root.findall(".//item"):
                enclosure = item.find("enclosure")
                if enclosure is not None:
                    audio_url = enclosure.get("url")
                    if audio_url:
                        audio_tracks.append(audio_url)
        except ET.ParseError as e:
            print(f"XML parsing error for feed {i} {feed_url}: {e}")
    else:
        print(f"Failed to fetch feed {i} {feed_url}")

for audio_url in audio_tracks:
    with open(f"audio_urls_{args.offset}_{args.limit}.txt", "a") as f:
        f.write(audio_url + "\n")
