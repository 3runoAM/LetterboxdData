from .data_base import data_base

movie_genres = data_base.Table('movie_genres',
    data_base.Column('movie_id', data_base.Integer, data_base.ForeignKey('movies.id'), primary_key=True),
    data_base.Column('genre_id', data_base.Integer, data_base.ForeignKey('genres.id'), primary_key=True)
)

movie_directors = data_base.Table('movie_directors',
    data_base.Column('movie_id', data_base.Integer, data_base.ForeignKey('movies.id'), primary_key=True),
    data_base.Column('director_id', data_base.Integer, data_base.ForeignKey('directors.id'), primary_key=True)
)

class Genre(data_base.Model):
    __tablename__ = 'genres'
    id = data_base.Column(data_base.Integer, primary_key=True)
    name = data_base.Column(data_base.String(100), unique=True, nullable=False)


class Director(data_base.Model):
    __tablename__ = 'directors'
    id = data_base.Column(data_base.Integer, primary_key=True)
    name = data_base.Column(data_base.String(255), unique=True, nullable=False)


class Movie(data_base.Model):
    __tablename__ = 'movies'
    id = data_base.Column(data_base.Integer, primary_key=True)
    title = data_base.Column(data_base.String(255), nullable=False)
    release_year = data_base.Column(data_base.Integer)
    poster_url = data_base.Column(data_base.String(500))
    overview = data_base.Column(data_base.Text)
    original_language = data_base.Column(data_base.String(10))
    country = data_base.Column(data_base.String(100))
    decade = data_base.Column(data_base.String(10))

    genres = data_base.relationship('Genre', secondary=movie_genres, backref='movies')
    directors = data_base.relationship('Director', secondary=movie_directors, backref='movies')


class WatchLog(data_base.Model):
    __tablename__ = 'watch_logs'
    id = data_base.Column(data_base.Integer, primary_key=True)
    movie_id = data_base.Column(data_base.Integer, data_base.ForeignKey('movies.id'), nullable=False)
    watched_date = data_base.Column(data_base.Date, nullable=False)
    rating = data_base.Column(data_base.Float)
    is_rewatch = data_base.Column(data_base.Boolean, default=False)
    year_month = data_base.Column(data_base.String(7))
    watched_year = data_base.Column(data_base.Integer)
    day_of_week = data_base.Column(data_base.String(20))
    time_lag = data_base.Column(data_base.Integer)

    movie = data_base.relationship('Movie', backref='logs')