#!/usr/bin/env python3
"""Add a new podcast episode to the RSS feed."""
import sys
import os
import subprocess
import hashlib
from datetime import datetime
import xml.etree.ElementTree as ET

def main():
    if len(sys.argv) < 3:
        print("Usage: python add_episode.py <mp3-file> \"<title>\" \"<description>\"")
        sys.exit(1)
    
    mp3_file = sys.argv[1]
    title = sys.argv[2]
    description = sys.argv[3] if len(sys.argv) > 3 else title
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    feed_file = os.path.join(script_dir, "feed.xml")
    episodes_dir = os.path.join(script_dir, "episodes")
    
    # Create episodes directory
    os.makedirs(episodes_dir, exist_ok=True)
    
    # Generate safe filename
    safe_title = title.lower()
    safe_title = ''.join(c if c.isalnum() else '-' for c in safe_title)
    safe_title = '-'.join(filter(None, safe_title.split('-')))
    episode_file = os.path.join(episodes_dir, f"{safe_title}.mp3")
    
    # Copy MP3
    import shutil
    shutil.copy(mp3_file, episode_file)
    print(f"Copied: {episode_file}")
    
    # Get file size
    file_size = os.path.getsize(episode_file)
    
    # Get duration with ffprobe
    duration = ""
    try:
        result = subprocess.run(
            ["ffprobe", "-i", episode_file, "-show_entries", "format=duration", 
             "-v", "quiet", "-of", "csv=p=0"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            duration_sec = int(float(result.stdout.strip()))
            duration = f"<itunes:duration>{duration_sec}</itunes:duration>"
    except:
        pass
    
    # Generate episode URL
    episode_url = f"https://sable1991.github.io/sable-podcasts/episodes/{safe_title}.mp3"
    
    # Generate GUID and date
    guid = f"sable-podcast-{int(datetime.now().timestamp())}"
    pub_date = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")
    
    # Read and parse feed
    with open(feed_file, 'r') as f:
        content = f.read()
    
    # Create episode XML
    episode_xml = f'''
    <item>
      <title>{title}</title>
      <description>{description}</description>
      <enclosure url="{episode_url}" length="{file_size}" type="audio/mpeg"/>
      <guid isPermaLink="false">{guid}</guid>
      <pubDate>{pub_date}</pubDate>
      {duration}
    </item>'''
    
    # Insert before closing </channel>
    content = content.replace("  </channel>", episode_xml + "\n  </channel>")
    
    with open(feed_file, 'w') as f:
        f.write(content)
    
    print(f"Episode added: {title}")
    print(f"Feed URL: https://sable1991.github.io/sable-podcasts/feed.xml")

if __name__ == "__main__":
    main()
