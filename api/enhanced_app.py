from flask import Flask, jsonify, request
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.enhanced_recommendation_engine import EnhancedBeautyRecommendationEngine
from data.enhanced_products import enhanced_products
from data.user_profiles import get_user_profile, get_all_users, create_custom_profile

app = Flask(__name__)

# Initialize the enhanced recommendation engine
recommendation_engine = EnhancedBeautyRecommendationEngine()

@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to Enhanced AI Sephora Recommendation API",
        "version": "2.0",
        "features": [
            "Content-based recommendations",
            "Personalized user recommendations", 
            "Budget-friendly suggestions",
            "Trending products",
            "User profile management"
        ],
        "endpoints": {
            "get_products": "/products",
            "get_product_details": "/products/<product_id>",
            "content_recommendations": "/recommendations/content/<product_id>",
            "user_recommendations": "/recommendations/user/<user_id>",
            "custom_recommendations": "/recommendations/custom",
            "budget_recommendations": "/recommendations/budget/<max_price>",
            "trending_products": "/trending",
            "user_profiles": "/users",
            "specific_user": "/users/<user_id>"
        }
    })

@app.route('/products')
def get_products():
    """Get all available products with filtering options"""
    category = request.args.get('category')
    brand = request.args.get('brand')
    max_price = request.args.get('max_price', type=float)
    skin_type = request.args.get('skin_type')
    
    filtered_products = enhanced_products.copy()
    
    # Apply filters
    if category:
        filtered_products = [p for p in filtered_products 
                           if p['category'].lower() == category.lower()]
    
    if brand:
        filtered_products = [p for p in filtered_products 
                           if brand.lower() in p['brand'].lower()]
    
    if max_price:
        filtered_products = [p for p in filtered_products 
                           if p['price'] <= max_price]
    
    if skin_type:
        filtered_products = [p for p in filtered_products 
                           if skin_type in p['skin_types'] or 'all' in p['skin_types']]
    
    return jsonify({
        "products": filtered_products,
        "total": len(filtered_products),
        "filters_applied": {
            "category": category,
            "brand": brand,
            "max_price": max_price,
            "skin_type": skin_type
        }
    })

@app.route('/products/<int:product_id>')
def get_product_details(product_id):
    """Get detailed information about a specific product"""
    product = next((p for p in enhanced_products if p['id'] == product_id), None)
    
    if not product:
        return jsonify({"error": "Product not found"}), 404
    
    return jsonify({
        "product": product,
        "similar_products": recommendation_engine.get_content_based_recommendations(product_id, 3)
    })

@app.route('/recommendations/content/<int:product_id>')
def get_content_recommendations(product_id):
    """Get content-based recommendations for a product"""
    num_recs = request.args.get('count', 3, type=int)
    
    try:
        recommendations = recommendation_engine.get_content_based_recommendations(
            product_id, num_recs
        )
        
        if not recommendations:
            return jsonify({
                "error": "Product not found",
                "product_id": product_id
            }), 404
            
        return jsonify({
            "product_id": product_id,
            "recommendations": recommendations,
            "count": len(recommendations),
            "recommendation_type": "content_based"
        })
        
    except Exception as e:
        return jsonify({"error": "Internal server error", "message": str(e)}), 500

@app.route('/recommendations/user/<user_id>')
def get_user_recommendations(user_id):
    """Get personalized recommendations for a user"""
    num_recs = request.args.get('count', 3, type=int)
    
    user_profile = get_user_profile(user_id)
    if not user_profile:
        return jsonify({"error": "User not found"}), 404
    
    try:
        recommendations = recommendation_engine.get_personalized_recommendations(
            user_profile, num_recs
        )
        
        return jsonify({
            "user_id": user_id,
            "user_name": user_profile.get('name', 'Unknown'),
            "user_profile": {
                "skin_type": user_profile['skin_type'],
                "concerns": user_profile['concerns'],
                "budget_max": user_profile['budget_max']
            },
            "recommendations": recommendations,
            "count": len(recommendations),
            "recommendation_type": "personalized"
        })
        
    except Exception as e:
        return jsonify({"error": "Internal server error", "message": str(e)}), 500

@app.route('/recommendations/custom', methods=['POST'])
def get_custom_recommendations():
    """Get recommendations for custom user input"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Create temporary user profile
        custom_profile = create_custom_profile(
            name=data.get('name', 'Custom User'),
            age=data.get('age', 25),
            skin_type=data.get('skin_type', 'normal'),
            concerns=data.get('concerns', []),
            budget_max=data.get('budget_max', 100.0),
            preferred_brands=data.get('preferred_brands', [])
        )
        
        num_recs = data.get('count', 3)
        recommendations = recommendation_engine.get_personalized_recommendations(
            custom_profile, num_recs
        )
        
        return jsonify({
            "custom_profile": custom_profile,
            "recommendations": recommendations,
            "count": len(recommendations),
            "recommendation_type": "custom_personalized"
        })
        
    except Exception as e:
        return jsonify({"error": "Internal server error", "message": str(e)}), 500

@app.route('/recommendations/budget/<float:max_price>')
def get_budget_recommendations(max_price):
    """Get budget-friendly recommendations"""
    category = request.args.get('category')
    num_recs = request.args.get('count', 5, type=int)
    
    try:
        recommendations = recommendation_engine.get_budget_friendly_recommendations(
            max_price, category, num_recs
        )
        
        return jsonify({
            "max_price": max_price,
            "category": category,
            "recommendations": recommendations,
            "count": len(recommendations),
            "recommendation_type": "budget_friendly"
        })
        
    except Exception as e:
        return jsonify({"error": "Internal server error", "message": str(e)}), 500

@app.route('/trending')
def get_trending_products():
    """Get trending products"""
    num_products = request.args.get('count', 5, type=int)
    
    try:
        trending = recommendation_engine.get_trending_recommendations(num_products)
        
        return jsonify({
            "trending_products": trending,
            "count": len(trending),
            "based_on": "review_count_and_ratings"
        })
        
    except Exception as e:
        return jsonify({"error": "Internal server error", "message": str(e)}), 500

@app.route('/users')
def get_users():
    """Get all sample users"""
    users = get_all_users()
    
    # Return simplified user info (without sensitive details)
    simplified_users = {}
    for user_id, profile in users.items():
        simplified_users[user_id] = {
            "name": profile['name'],
            "age": profile['age'],
            "skin_type": profile['skin_type'],
            "concerns": profile['concerns'][:3],  # Show only first 3 concerns
            "budget_max": profile['budget_max']
        }
    
    return jsonify({
        "users": simplified_users,
        "total_users": len(simplified_users)
    })

@app.route('/users/<user_id>')
def get_user_details(user_id):
    """Get detailed user profile"""
    user_profile = get_user_profile(user_id)
    
    if not user_profile:
        return jsonify({"error": "User not found"}), 404
    
    # Get some quick recommendations for this user
    quick_recs = recommendation_engine.get_personalized_recommendations(user_profile, 2)
    
    return jsonify({
        "user_profile": user_profile,
        "quick_recommendations": quick_recs
    })

@app.route('/search')
def search_products():
    """Search products by name or description"""
    query = request.args.get('q', '').lower()
    
    if not query:
        return jsonify({"error": "Search query required"}), 400
    
    matching_products = []
    for product in enhanced_products:
        if (query in product['name'].lower() or 
            query in product['brand'].lower() or
            query in product['category'].lower() or
            any(query in concern for concern in product['concerns'])):
            matching_products.append(product)
    
    return jsonify({
        "search_query": query,
        "results": matching_products,
        "count": len(matching_products)
    })

if __name__ == '__main__':
    print("🚀 Starting Enhanced AI Sephora Recommendation API...")
    print("✨ Features: Personalized recommendations, user profiles, budget filtering")
    print("🌐 API available at: http://127.0.0.1:5000")
    print("📖 Try: http://127.0.0.1:5000 for all endpoints")
    app.run(debug=True, port=5000)