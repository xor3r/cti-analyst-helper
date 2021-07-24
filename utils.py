import csv
import feedparser
import datetime


def read_feed(link, tags=True, summary=True, published=True, updated=False):
    feed = feedparser.parse(link)
    feed_data = dict()
    feed_data["link"] = feed.entries[0]["link"]
    feed_data["title"] = feed.entries[0]["title"]
    if updated:
        feed_data["time"] = feed.entries[0]["updated"]
    elif published:
        feed_data["time"] = feed.entries[0]["published"]
    if tags:
        feed_data["tags"] = format_tags(feed.entries[0]["tags"])
    else:
        feed_data["tags"] = None
    today = datetime.datetime.today()
    today_format_1 = today.strftime("%d %b %Y")
    today_format_2 = today.strftime("%Y-%m-%d")
    if today_format_1 in feed_data["time"] or today_format_2 in feed_data["time"]:
        return feed_data
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
            post_raw = read_feed(feed["source"], **{key: eval(value) for key, value in feed.items() if (key != "source" and key != "title")})
            if post_raw is not None:
                post_raw["org"] = feed["title"]
                post_data.append(post_raw)
    return post_data


def format_tags(tags_list):
    formatted_tags = ' '.join(["#" + tag["term"].replace(" ", "_") for tag in tags_list[:3]])
    return formatted_tags


def create_post(events):
    if not events:
        return None
    text = ""
    for event in events:
        text += event["title"] + ' | <a href="{0}">{1}</a>'.format(event["link"], event["org"])
        # No need of tags for now
        # text += ("\n" + event["tags"] if event["tags"] else "")
        text += "\n\n"
    return text


def workflow():
    feeds = fetch_feed_metadata('feeds.csv')
    posts = fetch_from_feeds(feeds)
    post = create_post(posts)
    return post


if __name__ == '__main__':
    print(workflow())
