# Crawl Podcast

## Download Podcast Feeds
Feed Database is updated every week. (4,369,929 feeds on 2024-12-11)
```bash
wget https://public.podcastindex.org/podcastindex_feeds.db.tgz
tar -xvf podcastindex_feeds.db.tgz
```

## Distill Audio URL
```bash
python distill_audio_url.py --offset 0 --limit 1000
```
