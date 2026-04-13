import os

# -----------------------------------------------------------------------------------------------------------------------

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

# -----------------------------------------------------------------------------------------------------------------------

EXPECTED_DATA = {
    'diary.csv': ['Date', 'Name', 'Year', 'Letterboxd URI', 'Rating', 'Rewatch', 'Tags', 'Watched Date'],
    'ratings.csv': ['Date', 'Name', 'Year', 'Letterboxd URI', 'Rating'],
    'watched.csv': ['Date', 'Name', 'Year', 'Letterboxd URI']
}

# -----------------------------------------------------------------------------------------------------------------------

TMDB_GENRES = {
    28: "Ação", 12: "Aventura", 16: "Animação", 35: "Comédia", 80: "Crime", 99: "Documentário", 18: "Drama",
    10751: "Família", 14: "Fantasia", 36: "História", 27: "Terror", 10402: "Música", 9648: "Mistério", 10749: "Romance",
    878: "Ficção Científica", 10770: "Cinema TV", 53: "Suspense", 10752: "Guerra", 37: "Faroeste"
}

# -----------------------------------------------------------------------------------------------------------------------

STOPWORDS_OVERVIEW = {
    "although", "another", "anyone", "anything", "attempt", "attempted", "attempting", "attempts",
    "back", "based", "became", "become", "becomes", "becoming", "began", "begin", "beginning", "begins",
    "behind", "book", "boy", "boys", "bring", "bringing", "brings", "brought", "call", "called", "came",
    "cast", "character", "characters", "city", "come", "comes", "coming", "confront", "day", "days",
    "decide", "decided", "decides", "deciding", "despite", "determined", "different", "directed",
    "director", "discover", "discovered", "discovering", "discovers", "documentary", "embark",
    "embarking", "embarks", "end", "episode", "escape", "event", "events", "everyone", "everything",
    "face", "faced", "faces", "facing", "fall", "falling", "falls", "family", "feature", "fell", "fight",
    "fighting", "fights", "film", "films", "find", "finding", "finds", "first", "follow", "following",
    "follows", "force", "forced", "forces", "forcing", "fought", "found", "friend", "friends", "get",
    "gets", "getting", "girl", "girls", "go", "goes", "going", "gone", "got", "gotten", "group", "guy",
    "happen", "happened", "happens", "help", "helped", "helping", "helps", "home", "however", "inside",
    "instead", "job", "journey", "journeys", "kid", "known", "late", "later", "lead", "leading", "leads",
    "leave", "leaves", "leaving", "led", "left", "life", "live", "lived", "lives", "living", "local",
    "long", "made", "make", "makes", "making", "man", "meanwhile", "meet", "meeting", "meets", "men",
    "met", "mission", "movie", "movies", "must", "name", "named", "new", "night", "nobody", "nothing",
    "novel", "now", "old", "one", "order", "own", "people", "person", "place", "play", "plays", "plot",
    "quest", "realize", "realized", "realizes", "realizing", "return", "returned", "returning", "returns",
    "role", "s", "save", "saved", "saves", "saving", "second", "see", "seem", "seemed", "seeming",
    "seems", "send", "sent", "series", "set", "sets", "setting", "short", "show", "showed", "showing",
    "shown", "shows", "small", "someone", "something", "soon", "starring", "stars", "start", "stories",
    "story", "suddenly", "survive", "survived", "survives", "surviving", "take", "takes", "taking",
    "task", "team", "tell", "telling", "tells", "thing", "things", "third", "three", "time", "together",
    "told", "took", "town", "true", "try", "tried", "tries", "trying", "turn", "turned", "turning",
    "turns", "two", "use", "used", "uses", "using", "way", "went", "will", "woman", "women", "world",
    "year", "years", "york", "young", "future", "past", "travel", "last", "century", "learn", "search", "stop",
    "struggle", "land", "join", "best", 
}
