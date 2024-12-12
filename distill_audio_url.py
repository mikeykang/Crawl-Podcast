import requests
import sqlite3
import xml.etree.ElementTree as ET
import argparse
from tqdm import tqdm

from concurrent.futures import ThreadPoolExecutor
import threading

parser = argparse.ArgumentParser()
parser.add_argument("--offset", type=int, default=0)
parser.add_argument("--limit", type=int, default=100)
parser.add_argument("--max_workers", type=int, default=1)
args = parser.parse_args()

conn = sqlite3.connect("podcastindex_feeds.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM podcasts")
print("Total feeds: ", cursor.fetchone()[0])


def process_feed(row):
    feed_url = dict(row)["url"]
    audio_urls = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        feed_response = requests.get(feed_url, headers=headers, timeout=10)
    except Exception as e:
        # print(f"Failed to fetch feed {feed_url}: {e}")
        return []

    if feed_response.status_code == 200 and feed_response.content:
        try:
            root = ET.fromstring(feed_response.content)
            for item in root.findall(".//item"):
                enclosure = item.find("enclosure")
                if enclosure is not None:
                    audio_url = enclosure.get("url")
                    if audio_url:
                        audio_urls.append(audio_url)
        except ET.ParseError as e:
            # print(f"XML parsing error for feed {feed_url}: {e}")
            return []

    return audio_urls


# Create a thread-safe list for audio tracks
audio_tracks = []
lock = threading.Lock()


def process_feed_with_lock(row):
    urls = process_feed(row)
    with lock:
        audio_tracks.extend(urls)


cursor.execute(f"SELECT * FROM podcasts LIMIT {args.limit} OFFSET {args.offset};")
rows = cursor.fetchall()

# Process feeds using thread pool
with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
    list(tqdm(executor.map(process_feed_with_lock, rows), total=len(rows)))

# Write results to file
total_audio_tracks = len(audio_tracks)
video_tracks = 0
with open(f"audio_urls_{args.offset}_{args.limit}.txt", "w") as f:
    for audio_url in audio_tracks:
        if any(
            ext in audio_url for ext in [".mp4", ".avi", ".mov", ".wmv", ".mkv", ".flv"]
        ):
            video_tracks += 1
            continue
        f.write(audio_url + "\n")

print(f"Total audio tracks: {total_audio_tracks}")
print(f"Total video tracks: {video_tracks}")
print(f"Total audio tracks without video: {total_audio_tracks - video_tracks}")
