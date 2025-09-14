import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.enhanced_products import enhanced_products

class EnhancedBeautyRecommendationEngine:
    def __init__(self):
        self.products_df = pd.DataFrame(enhanced_products)
        self.vectorizer = TfidfVectorizer()
        self.scaler = MinMaxScaler()
        self.content_similarity_matrix = None
        self._prepare_data()
    
    def _prepare_data(self):
        """Prepare data for multiple recommendation approaches"""
        # Create content-based features
        self.products_df['text_features'] = (
            self.products_df['category'] + ' ' +
            self.products_df['subcategory'] + ' ' +
            self.products_df['brand'] + ' ' +
            self.products_df['skin_types'].astype(str) + ' ' +
            self.products_df['concerns'].astype(str) + ' ' +
            self.products_df['age_groups'].astype(str) + ' ' +
            self.products_df['seasonal'].astype(str) + ' ' +
            self.products_df['finish'].astype(str) + ' ' +
            self.products_df['key_ingredients'].astype(str)
        )
        
        # Create TF-IDF matrix for content similarity
        tfidf_matrix = self.vectorizer.fit_transform(self.products_df['text_features'])
        self.content_similarity_matrix = cosine_similarity(tfidf_matrix)
        
        # Normalize numerical features for hybrid approach
        numerical_features = ['price', 'rating', 'review_count', 'spf']
        self.products_df[numerical_features] = self.scaler.fit_transform(
            self.products_df[numerical_features]
        )
    
    def get_content_based_recommendations(self, product_id, num_recommendations=3):
        """Get recommendations based on content similarity"""
        if product_id not in self.products_df['id'].values:
            return []
        
        product_idx = self.products_df[self.products_df['id'] == product_id].index[0]
        similarity_scores = list(enumerate(self.content_similarity_matrix[product_idx]))
        similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
        
        recommendations = []
        for i, score in similarity_scores[1:num_recommendations+1]:
            product = self.products_df.iloc[i]
            recommendations.append({
                'id': int(product['id']),
                'name': product['name'],
                'brand': product['brand'],
                'category': product['category'],
                'price': float(self.products_df.iloc[i]['price']) * 100 + 10,  # Denormalize price
                'rating': float(self.products_df.iloc[i]['rating']) * 5,  # Denormalize rating
                'similarity_score': float(score),
                'reason': 'Similar product features and attributes'
            })
        
        return recommendations
    
    def get_personalized_recommendations(self, user_profile, num_recommendations=3):
        """Get recommendations based on user profile"""
        user_skin_type = user_profile.get('skin_type', 'normal')
        user_concerns = user_profile.get('concerns', [])
        user_age_group = user_profile.get('age_group', '25-35')
        user_budget = user_profile.get('budget_max', 100)
        preferred_brands = user_profile.get('preferred_brands', [])
        
        # Filter products based on user preferences
        suitable_products = self.products_df[
            (self.products_df['skin_types'].astype(str).str.contains(user_skin_type, case=False, na=False)) |
            (self.products_df['skin_types'].astype(str).str.contains('all', case=False, na=False))
        ].copy()
        
        # Calculate personalization score
        suitable_products['personalization_score'] = 0
        
        # Score based on concerns match
        for concern in user_concerns:
            mask = suitable_products['concerns'].astype(str).str.contains(concern, case=False, na=False)
            suitable_products.loc[mask, 'personalization_score'] += 2
        
        # Score based on age group match
        age_mask = suitable_products['age_groups'].astype(str).str.contains(user_age_group, case=False, na=False)
        suitable_products.loc[age_mask, 'personalization_score'] += 1
        
        # Score based on preferred brands
        for brand in preferred_brands:
            brand_mask = suitable_products['brand'].str.contains(brand, case=False, na=False)
            suitable_products.loc[brand_mask, 'personalization_score'] += 1.5
        
        # Boost score based on ratings
        suitable_products['personalization_score'] += suitable_products['rating'] * 0.5
        
        # Sort by personalization score
        top_products = suitable_products.nlargest(num_recommendations, 'personalization_score')
        
        recommendations = []
        for _, product in top_products.iterrows():
            original_product = next(p for p in enhanced_products if p['id'] == product['id'])
            recommendations.append({
                'id': int(product['id']),
                'name': product['name'],
                'brand': product['brand'],
                'category': product['category'],
                'price': float(original_product['price']),
                'rating': float(original_product['rating']),
                'personalization_score': float(product['personalization_score']),
                'reason': f'Perfect match for {user_skin_type} skin and your concerns'
            })
        
        return recommendations
    
    def get_budget_friendly_recommendations(self, max_price, category=None, num_recommendations=3):
        """Get recommendations within budget"""
        # Get original prices for filtering
        budget_products = []
        for product in enhanced_products:
            if product['price'] <= max_price:
                if category is None or product['category'].lower() == category.lower():
                    budget_products.append(product)
        
        # Sort by rating and review count
        budget_products.sort(key=lambda x: (x['rating'], x['review_count']), reverse=True)
        
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
        """Get trending products based on reviews and ratings"""
        trending_products = sorted(enhanced_products, 
                                 key=lambda x: x['review_count'] * x['rating'], 
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
                'review_count': product['review_count'],
                'reason': 'Trending product with high ratings and reviews'
            })
        
        return recommendations
