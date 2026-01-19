from flask import Blueprint, jsonify, request
import pandas as pd

api_bp = Blueprint('insights_api', __name__)
CSV_PATH = './data/books.csv'

def load_data():
    try:        
        df = pd.read_csv(CSV_PATH)  
        df['price_decimal'] = df['price'] / 100
        return df
    except Exception:
        return None

@api_bp.route('/api/v1/stats/overview', methods=['GET'])
def get_stats_overview():
    df = load_data()
    if df is None: return jsonify({"error": "Data not found"}), 404
    
    stats = {
        "total_books": len(df),
        "average_price": round(df['price_decimal'].mean(), 2),
        "rating_distribution": df['rating'].value_counts().to_dict()
    }
    return jsonify(stats)

@api_bp.route('/api/v1/stats/categories', methods=['GET'])
def get_stats_categories():
    df = load_data()
    if df is None: return jsonify({"error": "Data not found"}), 404
    
    cat_stats = df.groupby('category').agg(
        count=('title', 'count'),
        avg_price=('price_decimal', 'mean')
    ).round(2).to_dict(orient='index')
    
    return jsonify(cat_stats)

@api_bp.route('/api/v1/books/top-rated', methods=['GET'])
def get_top_rated():
    df = load_data()
    if df is None: return jsonify({"error": "Data not found"}), 404
    
    top_books = df[df['rating'] == 5]
    return jsonify(top_books.to_dict(orient='records'))

@api_bp.route('/api/v1/books/price-range', methods=['GET'])
def get_price_range():
    df = load_data()
    if df is None: return jsonify({"error": "Data not found"}), 404
    
    min_p = request.args.get('min', type=float)
    max_p = request.args.get('max', type=float)
    
    if min_p is None or max_p is None:
        return jsonify({"error": "Provide min and max price"}), 400
        
    filtered = df[(df['price_decimal'] >= min_p) & (df['price_decimal'] <= max_p)]
    return jsonify(filtered.to_dict(orient='records'))