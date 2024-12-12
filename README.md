# Crawl Podcast
Repository for crawling audio files from [Podcast Index](https://podcastindex.org/).

## Downloading Podcast Feeds
The feed Database is updated every week. (4,369,929 feeds on 2024-12-11)
```bash
wget https://public.podcastindex.org/podcastindex_feeds.db.tgz
tar -xvf podcastindex_feeds.db.tgz
rm podcastindex_feeds.db.tgz
```

## Extracting Audio URLs
Use the following command to parse audio URLs from a subset of feeds.  
Offset sets the starting position, and limit specifies the number of feeds to process.
```bash
python distill_audio_url.py --offset 0 --limit 1000
```

## Download Audio
```bash
aria2c --download-result hide summary-interval 0 --console-log-level error -c -s 16 -x 16 -k 1M -j 16 -d /data/podcast -i audio_urls_0_100.txt
```

## Use WhisperX for Transcription and Diarization
[WhisperX](https://github.com/m-bain/whisperX)
