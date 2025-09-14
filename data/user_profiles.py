# User profile system for personalized recommendations

sample_users = {
    "user_001": {
        "name": "Sarah",
        "age": 28,
        "skin_type": "oily",
        "concerns": ["acne", "oil_control", "coverage", "pores"],
        "age_group": "25-35",
        "budget_max": 60.00,
        "preferred_brands": ["Fenty Beauty", "The Ordinary", "Rare Beauty"],
        "seasonal_preference": "summer",
        "finish_preference": "matte",
        "coverage_preference": "full",
        "vegan_only": True,
        "cruelty_free_only": True,
        "previous_purchases": [1, 3]  # Fenty Foundation, The Ordinary Serum
    },
    
    "user_002": {
        "name": "Emily",
        "age": 35,
        "skin_type": "dry",
        "concerns": ["hydration", "anti_aging", "radiance"],
        "age_group": "30-40",
        "budget_max": 120.00,
        "preferred_brands": ["Charlotte Tilbury", "Drunk Elephant", "Tatcha"],
        "seasonal_preference": "winter",
        "finish_preference": "dewy",
        "coverage_preference": "medium",
        "vegan_only": False,
        "cruelty_free_only": True,
        "previous_purchases": [4, 6]  # Charlotte Tilbury Cream, Drunk Elephant Serum
    },
    
    "user_003": {
        "name": "Maya",
        "age": 22,
        "skin_type": "combination",
        "concerns": ["natural_glow", "budget_friendly", "easy_application"],
        "age_group": "18-25",
        "budget_max": 35.00,
        "preferred_brands": ["Glossier", "The Ordinary", "La Roche-Posay"],
        "seasonal_preference": "spring",
        "finish_preference": "natural",
        "coverage_preference": "light",
        "vegan_only": False,
        "cruelty_free_only": True,
        "previous_purchases": [5, 8]  # Glossier Cloud Paint, La Roche-Posay Moisturizer
    },
    
    "user_004": {
        "name": "Jessica",
        "age": 45,
        "skin_type": "mature",
        "concerns": ["anti_aging", "hydration", "sun_protection", "radiance"],
        "age_group": "40-50",
        "budget_max": 100.00,
        "preferred_brands": ["Charlotte Tilbury", "Supergoop!", "Tatcha"],
        "seasonal_preference": "all_seasons",
        "finish_preference": "natural",
        "coverage_preference": "medium",
        "vegan_only": False,
        "cruelty_free_only": True,
        "previous_purchases": [10, 12]  # Supergoop Sunscreen, Tatcha Water Cream
    },
    
    "user_005": {
        "name": "Alex",
        "age": 26,
        "skin_type": "sensitive",
        "concerns": ["sensitivity", "gentle_products", "hydration"],
        "age_group": "25-35",
        "budget_max": 50.00,
        "preferred_brands": ["La Roche-Posay", "Youth To The People", "Glossier"],
        "seasonal_preference": "all_seasons",
        "finish_preference": "natural",
        "coverage_preference": "light",
        "vegan_only": True,
        "cruelty_free_only": True,
        "previous_purchases": [8, 14]  # La Roche-Posay Moisturizer, YTTP Cleanser
    }
}

def get_user_profile(user_id):
    """Get user profile by ID"""
    return sample_users.get(user_id, None)

def create_custom_profile(name, age, skin_type, concerns, budget_max, preferred_brands=None):
    """Create a custom user profile"""
    if preferred_brands is None:
        preferred_brands = []
    
    # Determine age group
    if age < 25:
        age_group = "18-25"
    elif age < 35:
        age_group = "25-35"
    elif age < 45:
        age_group = "35-45"
    else:
        age_group = "45+"
    
    return {
        "name": name,
        "age": age,
        "skin_type": skin_type,
        "concerns": concerns,
        "age_group": age_group,
        "budget_max": budget_max,
        "preferred_brands": preferred_brands,
        "seasonal_preference": "all_seasons",
        "finish_preference": "natural",
        "coverage_preference": "medium",
        "vegan_only": False,
        "cruelty_free_only": True,
        "previous_purchases": []
    }

def get_all_users():
    """Get all sample users"""
    return sample_users

# Test the user profile system
if __name__ == "__main__":
    print("=== Sample User Profiles ===")
    for user_id, profile in sample_users.items():
        print(f"\n{user_id}: {profile['name']}")
        print(f"  Age: {profile['age']} | Skin Type: {profile['skin_type']}")
        print(f"  Concerns: {', '.join(profile['concerns'])}")
        print(f"  Budget: ${profile['budget_max']}")
        print(f"  Brands: {', '.join(profile['preferred_brands'])}")
    
    print("\n=== Custom Profile Example ===")
    custom = create_custom_profile(
        name="Custom User",
        age=30,
        skin_type="normal",
        concerns=["hydration", "anti_aging"],
        budget_max=75.00,
        preferred_brands=["Drunk Elephant", "Tatcha"]
    )
    print(f"Custom Profile: {custom['name']}")
    print(f"Age Group: {custom['age_group']}")
    print(f"Concerns: {', '.join(custom['concerns'])}")