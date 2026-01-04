def default_reactions():
    return {
        "emoji_reactions": {
            "love": {"emoji": "😍", "count": 0},
            "happy": {"emoji": "😄", "count": 0},
            "sad": {"emoji": "😢", "count": 0},
            "angry": {"emoji": "😡", "count": 0},
            "surprised": {"emoji": "😲", "count": 0}
        },
        "preferences": {
            "like": {"count": 0},
            "dislike": {"count": 0}
        }
    }
