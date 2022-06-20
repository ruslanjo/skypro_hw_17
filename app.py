# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from schemas import movies_schema, movie_schema, directors_schema, director_schema, genres_schema, genre_schema
from models import *
from utils import pagination

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
app.config['RESTX_JSON'] = {'ensure_ascii': False, 'indent': 3}

db = SQLAlchemy(app)
api = Api(app)

movies_ns = api.namespace('movies')
directors_ns = api.namespace('directors')
genres_ns = api.namespace('genres')


@movies_ns.route('/')
class MoviesView(Resource):
    def get(self):
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))

        movies = db.session.query(Movie)

        if 'director_id' in request.args:
            try:
                dir_id = int(request.args.get('director_id'))
            except ValueError:
                return 'director_id must be an integer', 404
            else:
                movies = movies.filter(Movie.director_id == dir_id)

        if 'genre_id' in request.args:
            try:
                genre_id = int(request.args.get('genre_id'))
            except ValueError:
                return 'genre_id must be an integer', 404
            else:
                movies = movies.filter(Movie.genre_id == genre_id)

        movies = pagination(movies, page, page_size).all()
        return movies_schema.dump(movies), 200

    def post(self):
        new_movie = request.json
        db.session.add(Movie(**new_movie))
        db.session.commit()
        return "", 204


@movies_ns.route('/<int:movie_id>')
class MovieView(Resource):
    def get(self, movie_id):
        movie = Movie.query.get(movie_id)
        if movie is not None:
            return movie_schema.dump(movie), 200
        return "there is no movie with this id", 404

    def put(self, movie_id):
        upd_movie = request.json
        movie = Movie.query.get(movie_id)

        movie.title = upd_movie.get('title')
        movie.description = upd_movie.get('description')
        movie.trailer = upd_movie.get('trailer')
        movie.year = upd_movie.get('year')
        movie.rating = upd_movie.get('rating')
        movie.genre_id = upd_movie.get('genre_id')
        movie.director_id = upd_movie.get('director_id')

        db.session.add(movie)
        db.session.commit()
        return "", 204

    def delete(self, movie_id):
        movie = Movie.query.get(movie_id)
        db.session.delete(movie)
        db.session.commit()
        return "", 204


@directors_ns.route('/')
class DirectorsView(Resource):
    def get(self):
        directors = Director.query.all()
        return directors_schema.dump(directors), 200

    def post(self):
        new_dir_req = request.json
        new_dir = Director(**new_dir_req)
        db.session.add(new_dir)
        db.session.commit()
        return "", 201


@directors_ns.route('/<int:dir_id>')
class DirectorView(Resource):
    def get(self, dir_id):
        director = Director.query.get(dir_id)
        if director is not None:
            return director_schema.dump(director), 200
        return f'there is no director with {dir_id} id', 404

    def put(self, dir_id):
        director = db.session.query(Director).get(dir_id)
        dir_req = request.json
        director.name = dir_req.get('name')
        db.session.add(director)
        db.session.commit()
        return "", 204

    def delete(self, dir_id):
        director = db.session.query(Director).get(dir_id)
        db.session.delete(director)
        db.session.commit()
        return "", 204


@genres_ns.route('/')
class GenresViews(Resource):
    def get(self):
        genres = Genre.query.all()
        return genres_schema.dump(genres), 200


@genres_ns.route('/<int:genre_id>')
class GenreViews(Resource):
    def get(self, genre_id):
        genre = Genre.query.get(genre_id)
        if genre is not None:
            return genre_schema.dump(genre), 200
        return f'there is no genre with {genre_id} id', 404


if __name__ == '__main__':
    app.run(debug=True, port=8080)
