"""Build Metricool createScheduledPost payloads from a plan file.
Usage: python3 metricool_payloads.py PLAN.json RAW_BASE_URL [ITEM_ID ...]
RAW_BASE_URL e.g. https://raw.githubusercontent.com/<owner>/hethspices-media/main
Prints one JSON object per line: {"id", "date", "info"} where info is the JSON string Metricool expects.
"""
import json, sys
from urllib.parse import quote

plan = json.load(open(sys.argv[1]))
base = sys.argv[2].rstrip('/')
only = set(sys.argv[3:])
tz = plan['timezone']
for it in plan['items']:
    if only and it['id'] not in only:
        continue
    urls = [f"{base}/media/{plan['batch']}/{quote(m)}" for m in it['media']]
    info = {
        "autoPublish": it.get('autoPublish', True),
        "draft": False,
        "descendants": [],
        "firstCommentText": "",
        "hasNotReadNotes": False,
        "media": urls,
        "mediaAltText": it.get('alt', []),
        "providers": [{"network": "instagram"}],
        "publicationDate": {"dateTime": it['date'], "timezone": tz},
        "shortener": False,
        "smartLinkData": {"ids": []},
        "instagramData": {"type": it['type'], "isAiGenerated": False},
    }
    if it['type'] != 'STORY':
        info["text"] = it['text']
    offset = "+05:30" if tz == "Asia/Calcutta" else ""
    print(json.dumps({"id": it['id'], "date": it['date'] + offset, "info": json.dumps(info, ensure_ascii=False)}, ensure_ascii=False))
