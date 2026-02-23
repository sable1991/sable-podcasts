#!/bin/bash
# add-episode.sh - Add a new podcast episode to the feed
# Usage: ./add-episode.sh <mp3-file> "<title>" "<description>"

set -e

MP3_FILE="$1"
TITLE="$2"
DESCRIPTION="$3"
FEED_DIR="$(dirname "$0")"
FEED_FILE="$FEED_DIR/feed.xml"
EPISODES_DIR="$FEED_DIR/episodes"

if [ -z "$MP3_FILE" ] || [ -z "$TITLE" ]; then
    echo "Usage: $0 <mp3-file> \"<title>\" \"<description>\""
    exit 1
fi

# Create episodes directory
mkdir -p "$EPISODES_DIR"

# Generate episode filename
SAFE_TITLE=$(echo "$TITLE" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-\|-$//g')
EPISODE_FILE="$EPISODES_DIR/${SAFE_TITLE}.mp3"

# Copy MP3 to episodes folder
cp "$MP3_FILE" "$EPISODE_FILE"
echo "Copied: $EPISODE_FILE"

# Get file size in bytes
FILE_SIZE=$(stat -f%z "$EPISODE_FILE")

# Get duration using ffprobe (if available)
if command -v ffprobe &> /dev/null; then
    DURATION=$(ffprobe -i "$EPISODE_FILE" -show_entries format=duration -v quiet -of csv="p=0" | cut -d. -f1)
    DURATION_TAG="<itunes:duration>${DURATION}</itunes:duration>"
else
    DURATION_TAG=""
fi

# Generate episode URL (GitHub Pages)
EPISODE_URL="https://sable1991.github.io/sable-podcasts/episodes/${SAFE_TITLE}.mp3"

# Generate GUID
GUID="sable-podcast-$(date +%s)"

# Generate RFC 2822 date
PUB_DATE=$(date -R)

# Create episode XML
EPISODE_XML="
    <item>
      <title>${TITLE}</title>
      <description>${DESCRIPTION}</description>
      <enclosure url=\"${EPISODE_URL}\" length=\"${FILE_SIZE}\" type=\"audio/mpeg\"/>
      <guid isPermaLink=\"false\">${GUID}</guid>
      <pubDate>${PUB_DATE}</pubDate>
      ${DURATION_TAG}
    </item>"

# Insert episode before the closing </channel> tag
sed -i '' "s|  </channel>|${EPISODE_XML}
  </channel>|" "$FEED_FILE"

echo "Episode added to feed: $TITLE"
echo "Feed URL: https://sable1991.github.io/sable-podcasts/feed.xml"
