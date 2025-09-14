from flask import Flask, jsonify, request
import sys
import os

# Add the parent directory to the path so we can import our recommendation engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.recommendation_engine import BeautyRecommendationEngine
from data.sample_products import products

app = Flask(__name__)

# Initialize the recommendation engine
recommendation_engine = BeautyRecommendationEngine()

@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to AI Sephora Recommendation API",
        "endpoints": {
            "get_products": "/products",
            "get_recommendations": "/recommendations/<product_id>"
        }
    })

@app.route('/products')
def get_products():
    """Get all available products"""
    return jsonify({
        "products": products,
        "total": len(products)
    })

@app.route('/recommendations/<int:product_id>')
def get_recommendations(product_id):
    """Get recommendations for a specific product"""
    try:
        recommendations = recommendation_engine.get_recommendations(product_id)
        
        if not recommendations:
            return jsonify({
                "error": "Product not found",
                "product_id": product_id
            }), 404
            
        return jsonify({
            "product_id": product_id,
            "recommendations": recommendations,
            "count": len(recommendations)
        })
        
    except Exception as e:
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    print("Starting AI Sephora Recommendation API...")
    print("API will be available at: http://127.0.0.1:5000")
    app.run(debug=True, port=5000)