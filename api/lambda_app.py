from flask import Flask, jsonify, request
import json

app = Flask(__name__)

# Embedded product data (no external imports needed)
PRODUCTS = [
    {
        "id": 1, "name": "Fenty Beauty Pro Filt'r Foundation", "brand": "Fenty Beauty",
        "category": "Foundation", "price": 38.00, "rating": 4.2,
        "skin_types": ["oily", "combination"], "concerns": ["coverage", "oil_control"]
    },
    {
        "id": 2, "name": "Rare Beauty Liquid Blush", "brand": "Rare Beauty",
        "category": "Makeup", "price": 22.00, "rating": 4.5,
        "skin_types": ["all"], "concerns": ["natural_glow"]
    },
    {
        "id": 3, "name": "The Ordinary Niacinamide Serum", "brand": "The Ordinary",
        "category": "Skincare", "price": 7.90, "rating": 4.1,
        "skin_types": ["oily", "combination"], "concerns": ["pores", "oil_control"]
    },
    {
        "id": 4, "name": "Charlotte Tilbury Magic Cream", "brand": "Charlotte Tilbury",
        "category": "Skincare", "price": 100.00, "rating": 4.3,
        "skin_types": ["dry", "mature"], "concerns": ["hydration", "anti_aging"]
    },
    {
        "id": 5, "name": "Tarte Shape Tape Concealer", "brand": "Tarte",
        "category": "Makeup", "price": 29.00, "rating": 4.6,
        "skin_types": ["all"], "concerns": ["coverage", "under_eyes"]
    }
]

SAMPLE_USERS = {
    "user_001": {
        "name": "Sarah", "skin_type": "oily", "concerns": ["acne", "oil_control"],
        "budget_max": 60.0, "preferred_brands": ["Fenty Beauty", "The Ordinary"]
    },
    "user_002": {
        "name": "Emily", "skin_type": "dry", "concerns": ["hydration", "anti_aging"],
        "budget_max": 120.0, "preferred_brands": ["Charlotte Tilbury"]
    },
    "user_003": {
        "name": "Maya", "skin_type": "combination", "concerns": ["natural_glow"],
        "budget_max": 35.0, "preferred_brands": ["Rare Beauty"]
    }
}

def calculate_match_score(product, user_profile):
    """Calculate how well a product matches a user profile"""
    score = 0
    
    # Skin type match
    if user_profile['skin_type'] in product['skin_types'] or 'all' in product['skin_types']:
        score += 3
        
    # Concerns match
    user_concerns = set(user_profile.get('concerns', []))
    product_concerns = set(product['concerns'])
    score += len(user_concerns.intersection(product_concerns)) * 2
    
    # Brand preference
    preferred_brands = user_profile.get('preferred_brands', [])
    for brand in preferred_brands:
        if brand.lower() in product['brand'].lower():
            score += 2
            
    # Rating boost
    score += product['rating'] * 0.5
    
    # Budget penalty
    if product['price'] > user_profile.get('budget_max', 100):
        score -= 2
        
    return max(0, score)  # Don't return negative scores

def get_recommendations_for_user(user_profile, num_recs=3):
    """Get personalized recommendations for a user"""
    scored_products = []
    
    for product in PRODUCTS:
        score = calculate_match_score(product, user_profile)
        if score > 0:
            scored_products.append({
                'id': product['id'],
                'name': product['name'],
                'brand': product['brand'],
                'price': product['price'],
                'rating': product['rating'],
                'score': score,
                'reason': f"Perfect match for {user_profile['skin_type']} skin and your concerns"
            })
    
    # Sort by score and return top recommendations
    scored_products.sort(key=lambda x: x['score'], reverse=True)
    return scored_products[:num_recs]

@app.route('/')
def home():
    return jsonify({
        "message": "🚀 AI Beauty Recommendations - AWS Lambda",
        "status": "live",
        "endpoints": {
            "products": "/products",
            "user_recommendations": "/recommendations/user/<user_id>",
            "custom_recommendations": "/recommendations/custom",
            "web_interface": "/web"
        }
    })

@app.route('/products')
def get_products():
    """Get all products"""
    return jsonify({
        "products": PRODUCTS,
        "total": len(PRODUCTS)
    })

@app.route('/recommendations/user/<user_id>')
def get_user_recommendations(user_id):
    """Get recommendations for a sample user"""
    if user_id not in SAMPLE_USERS:
        return jsonify({"error": "User not found"}), 404
    
    user_profile = SAMPLE_USERS[user_id]
    recommendations = get_recommendations_for_user(user_profile)
    
    return jsonify({
        "user_id": user_id,
        "user_name": user_profile['name'],
        "user_profile": {
            "skin_type": user_profile['skin_type'],
            "concerns": user_profile['concerns'],
            "budget_max": user_profile['budget_max']
        },
        "recommendations": recommendations,
        "count": len(recommendations)
    })

@app.route('/recommendations/custom', methods=['POST'])
def get_custom_recommendations():
    """Get recommendations for custom user input"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Create user profile from request data
        user_profile = {
            "skin_type": data.get('skin_type', 'normal'),
            "concerns": data.get('concerns', []),
            "budget_max": float(data.get('budget_max', 100)),
            "preferred_brands": data.get('preferred_brands', [])
        }
        
        recommendations = get_recommendations_for_user(user_profile)
        
        return jsonify({
            "recommendations": recommendations,
            "count": len(recommendations),
            "user_profile": user_profile
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/web')
def web_interface():
    """Simple web interface"""
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Beauty Recommendations</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            .card { background: #f9f9f9; padding: 20px; margin: 10px 0; border-radius: 8px; }
            button { background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin: 5px; }
            button:hover { background: #0056b3; }
            .result { background: white; padding: 15px; margin: 10px 0; border-left: 4px solid #007bff; }
        </style>
    </head>
    <body>
        <h1>🚀 AI Beauty Recommendations</h1>
        <div class="card">
            <h3>Try Sample Users:</h3>
            <button onclick="getRecommendations('user_001')">Sarah (Oily Skin)</button>
            <button onclick="getRecommendations('user_002')">Emily (Dry Skin)</button>
            <button onclick="getRecommendations('user_003')">Maya (Combination)</button>
        </div>
        <div id="results"></div>
        
        <script>
        async function getRecommendations(userId) {
            try {
                const response = await fetch('/recommendations/user/' + userId);
                const data = await response.json();
                
                let html = '<div class="card"><h3>Recommendations for ' + data.user_name + '</h3>';
                html += '<p>Skin Type: ' + data.user_profile.skin_type + ' | Budget: $' + data.user_profile.budget_max + '</p>';
                
                data.recommendations.forEach(rec => {
                    html += '<div class="result">';
                    html += '<strong>' + rec.name + '</strong> by ' + rec.brand + '<br>';
                    html += 'Price: $' + rec.price + ' | Rating: ' + rec.rating + '/5<br>';
                    html += '<em>' + rec.reason + '</em>';
                    html += '</div>';
                });
                
                html += '</div>';
                document.getElementById('results').innerHTML = html;
            } catch (error) {
                document.getElementById('results').innerHTML = '<div class="card"><h3>Error: ' + error.message + '</h3></div>';
            }
        }
        </script>
    </body>
    </html>
    '''
    return html

if __name__ == '__main__':
    app.run(debug=True)