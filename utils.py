import csv
import feedparser
import datetime
import dateutil.parser

from dateutil.tz import gettz


def read_feed(link, tags=True, summary=True, published=True, updated=False):
    feed = feedparser.parse(link)
    events = set()
    to_time = datetime.datetime.timestamp(datetime.datetime.now())
    from_time = to_time - 86400
    for event in feed.entries:
        if updated:
            event["time"] = event["updated"]
        elif published:
            event["time"] = event["published"]
        event_time = datetime.datetime.timestamp(dateutil.parser.parse(event["time"], tzinfos={"PDT": gettz("America/Los_Angeles")}))
        if from_time < event_time < to_time:
            events.add(event)
            if tags:
                event["tags"] = format_tags(event["tags"])
            else:
                event["tags"] = None
        return events
    else:
        return None


def fetch_feed_metadata(filename):
    with open(filename, 'r') as f:
        feeds_in_dict = [line for line in csv.DictReader(f)]
    return feeds_in_dict


def fetch_from_feeds(feeds_dict):
    post_data = list()
    for feed in feeds_dict:
        if feed["source"].startswith("#"):
            continue
        else:
            events = read_feed(feed["source"], **{key: eval(value) for key, value in feed.items() if (key != "source" and key != "title")})
            if events is not None:
                for event in events:
                    event["org"] = feed["title"]
                    post_data.append(event)
    return post_data


def format_tags(tags_list):
    formatted_tags = ' '.join(["#" + tag["term"].replace(" ", "_") for tag in tags_list[:3]])
    return formatted_tags


def create_post(events):
    if not events:
        return None
    text = ""
    for event in events:
        if event["title"] not in text:
            text += event["title"] + ' | <a href="{0}">{1}</a>'.format(event["link"], event["org"])
            text += "\n\n"
    return text


def workflow():
    feeds = fetch_feed_metadata('feeds.csv')
    posts = fetch_from_feeds(feeds)
    post = create_post(posts)
    return post


if __name__ == '__main__':
    print(workflow())
