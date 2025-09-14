import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sys
import os

# Add the parent directory to the path so we can import from data folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.sample_products import products

class BeautyRecommendationEngine:
    def __init__(self):
        self.products_df = pd.DataFrame(products)
        self.vectorizer = TfidfVectorizer()
        self.similarity_matrix = None
        self._prepare_data()
    
    def _prepare_data(self):
        # Combine text features for similarity calculation
        self.products_df['features'] = (
            self.products_df['category'] + ' ' +
            self.products_df['brand'] + ' ' +
            self.products_df['skin_types'].astype(str) + ' ' +
            self.products_df['concerns'].astype(str)
        )
        
        # Create similarity matrix
        feature_vectors = self.vectorizer.fit_transform(self.products_df['features'])
        self.similarity_matrix = cosine_similarity(feature_vectors)
    
    def get_recommendations(self, product_id, num_recommendations=2):
        """Get product recommendations based on similarity"""
        if product_id not in self.products_df['id'].values:
            return []
        
        # Find product index
        product_idx = self.products_df[self.products_df['id'] == product_id].index[0]
        
        # Get similarity scores
        similarity_scores = list(enumerate(self.similarity_matrix[product_idx]))
        similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
        
        # Get top recommendations (excluding the product itself)
        recommendations = []
        for i, score in similarity_scores[1:num_recommendations+1]:
            product = self.products_df.iloc[i]
            recommendations.append({
                'id': product['id'],
                'name': product['name'],
                'brand': product['brand'],
                'price': product['price'],
                'similarity_score': score
            })
        
        return recommendations

# Test the recommendation engine
if __name__ == "__main__":
    engine = BeautyRecommendationEngine()
    recommendations = engine.get_recommendations(1)
    print("Recommendations for Fenty Foundation:")
    for rec in recommendations:
        print(f"- {rec['name']} by {rec['brand']} (${rec['price']})")