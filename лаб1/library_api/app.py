from flask import Flask
from flask_restful import Api
from flasgger import Swagger

from resources.books import BookListResource, BookResource

app = Flask(__name__)
api = Api(app)

app.config["SWAGGER"] = {
    "title": "Library API",
    "uiversion": 3,
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Library API",
        "description": "API for library management using Flask, Flask-RESTful and Flasgger",
        "version": "1.0.0",
    },
    "basePath": "/",
    "schemes": [
        "http",
    ],
}

Swagger(app, template=swagger_template)

api.add_resource(BookListResource, "/books")
api.add_resource(BookResource, "/books/<string:book_id>")


@app.route("/")
def home():
    return {
        "message": "Library API is running",
        "swagger": "http://127.0.0.1:5000/apidocs/"
    }, 200


if __name__ == "__main__":
    app.run(debug=True)