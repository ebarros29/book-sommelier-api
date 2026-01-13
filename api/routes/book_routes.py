from flask import Blueprint, request, jsonify
from api.repositories.book_repository import BookRepository

book_bp = Blueprint('books', __name__, url_prefix='/api/v1')

@book_bp.route('/books', methods=['GET'])
def get_books():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)
    
    repository = BookRepository()
    pagination = repository.get_all_paginated(page, per_page)
    
    return jsonify({
        "books": [
            {
                "id": b.id,
                "title": b.title,
                "price": b.price / 100,
                "currency": b.currency,
                "rating": b.rating,
                "category": b.category,
                "img_url": b.img_url,
                "url": b.url
            } for b in pagination.items
        ],
        "meta": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total_pages": pagination.pages,
            "total_items": pagination.total,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev
        }
    }), 200