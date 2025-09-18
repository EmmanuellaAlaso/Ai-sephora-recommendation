from flask import Flask, jsonify, request
import json
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.enhanced_products import enhanced_products
from data.user_profiles import get_user_profile, get_all_users, create_custom_profile

app = Flask(__name__)

class SimpleRecommendationEngine:
    def __init__(self):
        self.products = enhanced_products
    
    def calculate_similarity_score(self, product, user_profile):
        """Simple similarity calculation without scikit-learn"""
        score = 0
        
        # Skin type match
        if user_profile['skin_type'] in product['skin_types'] or 'all' in product['skin_types']:
            score += 3
            
        # Concerns match
        user_concerns = set(user_profile.get('concerns', []))
        product_concerns = set(product['concerns'])
        common_concerns = user_concerns.intersection(product_concerns)
        score += len(common_concerns) * 2
        
        # Age group match
        user_age_group = user_profile.get('age_group', '25-35')
        if user_age_group in product['age_groups']:
            score += 1
            
        # Brand preference
        preferred_brands = user_profile.get('preferred_brands', [])
        for brand in preferred_brands:
            if brand.lower() in product['brand'].lower():
                score += 2
                
        # Rating boost
        score += product['rating'] * 0.5
        
        # Budget penalty if over budget
        if product['price'] > user_profile.get('budget_max', 100):
            score -= 2
            
        return score
    
    def get_personalized_recommendations(self, user_profile, num_recommendations=3):
        """Get recommendations based on user profile"""
        scored_products = []
        
        for product in self.products:
            score = self.calculate_similarity_score(product, user_profile)
            if score > 0:  # Only include products with positive scores
                scored_products.append({
                    **product,
                    'similarity_score': score
                })
        
        # Sort by score and get top recommendations
        scored_products.sort(key=lambda x: x['similarity_score'], reverse=True)
        top_products = scored_products[:num_recommendations]
        
        recommendations = []
        for product in top_products:
            recommendations.append({
                'id': product['id'],
                'name': product['name'],
                'brand': product['brand'],
                'category': product['category'],
                'price': product['price'],
                'rating': product['rating'],
                'similarity_score': product['similarity_score'],
                'reason': f"Great match for {user_profile['skin_type']} skin and your concerns"
            })
            
        return recommendations
    
    def get_content_based_recommendations(self, product_id, num_recommendations=3):
        """Simple content-based recommendations"""
        target_product = next((p for p in self.products if p['id'] == product_id), None)
        if not target_product:
            return []
            
        scored_products = []
        for product in self.products:
            if product['id'] == product_id:
                continue
                
            score = 0
            
            # Same category
            if product['category'] == target_product['category']:
                score += 3
                
            # Similar concerns
            common_concerns = set(product['concerns']).intersection(set(target_product['concerns']))
            score += len(common_concerns) * 2
            
            # Similar skin types
            common_skin_types = set(product['skin_types']).intersection(set(target_product['skin_types']))
            score += len(common_skin_types) * 1.5
            
            # Similar price range
            price_diff = abs(product['price'] - target_product['price'])
            if price_diff <= 20:
                score += 1
                
            if score > 0:
                scored_products.append({
                    **product,
                    'similarity_score': score
                })
        
        scored_products.sort(key=lambda x: x['similarity_score'], reverse=True)
        top_products = scored_products[:num_recommendations]
        
        recommendations = []
        for product in top_products:
            recommendations.append({
                'id': product['id'],
                'name': product['name'],
                'brand': product['brand'],
                'category': product['category'],
                'price': product['price'],
                'rating': product['rating'],
                'similarity_score': product['similarity_score'],
                'reason': 'Similar product features and attributes'
            })
            
        return recommendations
    
    def get_budget_friendly_recommendations(self, max_price, category=None, num_recommendations=5):
        """Get budget-friendly recommendations"""
        budget_products = []
        for product in self.products:
            if product['price'] <= max_price:
                if category is None or product['category'].lower() == category.lower():
                    budget_products.append(product)
        
        # Sort by rating and review count
        budget_products.sort(key=lambda x: (x['rating'], x.get('review_count', 0)), reverse=True)
        
        recommendations = []
        for product in budget_products[:num_recommendations]:
            recommendations.append({
                'id': product['id'],
                'name': product['name'],
                'brand': product['brand'],
                'category': product['category'],
                'price': product['price'],
                'rating': product['rating'],
                'savings': f"${max_price - product['price']:.2f} under budget",
                'reason': 'Great value within your budget'
            })
        
        return recommendations
    
    def get_trending_recommendations(self, num_recommendations=5):
        """Get trending products"""
        trending_products = sorted(self.products, 
                                 key=lambda x: x.get('review_count', 0) * x['rating'], 
                                 reverse=True)
        
        recommendations = []
        for product in trending_products[:num_recommendations]:
            recommendations.append({
                'id': product['id'],
                'name': product['name'],
                'brand': product['brand'],
                'category': product['category'],
                'price': product['price'],
                'rating': product['rating'],
                'review_count': product.get('review_count', 0),
                'reason': 'Trending product with high ratings and reviews'
            })
        
        return recommendations

# Initialize the simple recommendation engine
recommendation_engine = SimpleRecommendationEngine()

@app.route('/')
def home():
    return jsonify({
        "message": "AI Sephora Recommendation API - AWS Lambda Version",
        "version": "2.0-lambda",
        "features": [
            "Lightweight recommendations",
            "Personalized user suggestions", 
            "Budget-friendly options",
            "Trending products"
        ],
        "endpoints": {
            "get_products": "/products",
            "user_recommendations": "/recommendations/user/<user_id>",
            "custom_recommendations": "/recommendations/custom",
            "budget_recommendations": "/recommendations/budget/<max_price>",
            "trending_products": "/trending"
        }
    })

@app.route('/products')
def get_products():
    """Get all available products with filtering"""
    return jsonify({
        "products": enhanced_products,
        "total": len(enhanced_products)
    })

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

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    try:
        if filename == 'index.html':
            # Read the HTML file content
            static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
            file_path = os.path.join(static_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content, 200, {'Content-Type': 'text/html'}
        else:
            return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": "File not found", "message": str(e)}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)