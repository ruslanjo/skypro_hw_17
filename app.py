# app.py

from flask import Flask, request, jsonify
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from schemas import movies_schema, movie_schema, director_schema, directors_schema

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
app.config['RESTX_JSON'] = {'ensure_ascii': False, 'indent': 3}


db = SQLAlchemy(app)

api = Api(app)

movies_ns = api.namespace('movies')
directors_ns = api.namespace('directors')


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


@movies_ns.route('/')
class MoviesView(Resource):
    def get(self, page=1, page_size=10):

        if 'page' in request.args:
            try:
                page = int(request.args.get('page'))
            except ValueError:
                return 'page must be an integer', 404

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

        movies = movies.limit(page_size).offset((page - 1) * page_size).all()
        return movies_schema.dump(movies), 200



@movies_ns.route('/<int:movie_id>')
class MovieView(Resource):
    def get(self, movie_id):
        movie = Movie.query.get(movie_id)
        if movie:
            return movie_schema.dump(movie), 200
        return "there is no movie with this id", 404


@directors_ns.route('/')
class DirectorsView(Resource):
    def post(self):
        new_dir_req = request.json
        new_dir = Director(**new_dir_req)
        db.session.add(new_dir)
        db.session.commit()
        return "", 201


@directors_ns.route('/<int:dir_id>')
class DirectorView(Resource):
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



if __name__ == '__main__':
    app.run(debug=True, port=8080)
