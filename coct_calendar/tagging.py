def tags_for(event, keywords):
    """Return the tags whose keywords appear in the event's title or details."""
    text = f"{event['title']} {event.get('details', '')}".lower() + " "
    return [tag for tag, words in keywords.items() if any(w.lower() in text for w in words)]
