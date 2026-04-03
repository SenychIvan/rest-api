import uuid
from flask import request
from flask_restful import Resource

from storage import BOOKS


def validate_book_data(data):
    required_fields = ["title", "author", "status", "year"]

    for field in required_fields:
        if field not in data:
            return {"message": f"Field '{field}' is required"}, 400

    if not isinstance(data["title"], str) or not data["title"].strip():
        return {"message": "Field 'title' must be a non-empty string"}, 400

    if not isinstance(data["author"], str) or not data["author"].strip():
        return {"message": "Field 'author' must be a non-empty string"}, 400

    if "description" in data and data["description"] is not None and not isinstance(data["description"], str):
        return {"message": "Field 'description' must be a string"}, 400

    if data["status"] not in ["available", "issued"]:
        return {"message": "Field 'status' must be 'available' or 'issued'"}, 400

    if not isinstance(data["year"], int):
        return {"message": "Field 'year' must be an integer"}, 400

    return None


class BookListResource(Resource):
    def get(self):
        """
        Get all books
        ---
        tags:
          - Books
        parameters:
          - name: status
            in: query
            type: string
            required: false
            enum: [available, issued]
            description: Filter books by status
          - name: author
            in: query
            type: string
            required: false
            description: Filter books by author
          - name: sort_by
            in: query
            type: string
            required: false
            enum: [title, year]
            description: Sort books by title or year
          - name: order
            in: query
            type: string
            required: false
            enum: [asc, desc]
            default: asc
            description: Sort order
        responses:
          200:
            description: List of books
            schema:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: string
                  title:
                    type: string
                  author:
                    type: string
                  description:
                    type: string
                  status:
                    type: string
                  year:
                    type: integer
        """
        status_filter = request.args.get("status")
        author_filter = request.args.get("author")
        sort_by = request.args.get("sort_by")
        order = request.args.get("order", "asc")

        result = BOOKS.copy()

        if status_filter:
            result = [book for book in result if book["status"] == status_filter]

        if author_filter:
            result = [
                book for book in result
                if book["author"].lower() == author_filter.lower()
            ]

        if sort_by in ["title", "year"]:
            reverse = order == "desc"
            if sort_by == "title":
                result.sort(key=lambda x: x["title"].lower(), reverse=reverse)
            else:
                result.sort(key=lambda x: x["year"], reverse=reverse)

        return result, 200

    def post(self):
        """
        Create a new book
        ---
        tags:
          - Books
        parameters:
          - in: body
            name: body
            required: true
            schema:
              type: object
              required:
                - title
                - author
                - status
                - year
              properties:
                title:
                  type: string
                  example: Dune
                author:
                  type: string
                  example: Frank Herbert
                description:
                  type: string
                  example: Science fiction novel
                status:
                  type: string
                  enum: [available, issued]
                  example: available
                year:
                  type: integer
                  example: 1965
        responses:
          201:
            description: Book created successfully
            schema:
              type: object
              properties:
                id:
                  type: string
                title:
                  type: string
                author:
                  type: string
                description:
                  type: string
                status:
                  type: string
                year:
                  type: integer
          400:
            description: Validation error
        """
        data = request.get_json()

        if not data:
            return {"message": "Request body must be JSON"}, 400

        validation_error = validate_book_data(data)
        if validation_error:
            return validation_error

        book = {
            "id": str(uuid.uuid4()),
            "title": data["title"].strip(),
            "author": data["author"].strip(),
            "description": data.get("description", ""),
            "status": data["status"],
            "year": data["year"],
        }

        BOOKS.append(book)
        return book, 201


class BookResource(Resource):
    def get(self, book_id):
        """
        Get book by ID
        ---
        tags:
          - Books
        parameters:
          - name: book_id
            in: path
            type: string
            required: true
            description: UUID of the book
        responses:
          200:
            description: Book found
            schema:
              type: object
              properties:
                id:
                  type: string
                title:
                  type: string
                author:
                  type: string
                description:
                  type: string
                status:
                  type: string
                year:
                  type: integer
          404:
            description: Book not found
        """
        for book in BOOKS:
            if book["id"] == book_id:
                return book, 200
        return {"message": "Book not found"}, 404

    def delete(self, book_id):
        """
        Delete book by ID
        ---
        tags:
          - Books
        parameters:
          - name: book_id
            in: path
            type: string
            required: true
            description: UUID of the book
        responses:
          204:
            description: Book deleted or already absent
        """
        initial_len = len(BOOKS)
        BOOKS[:] = [book for book in BOOKS if book["id"] != book_id]

        # idempotent delete
        if len(BOOKS) == initial_len:
            return "", 204

        return "", 204