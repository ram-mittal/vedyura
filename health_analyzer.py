import json

def load_food_database():
    """Loads the food database from the JSON file."""
    try:
        with open('data/food_database.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def analyze_user_data(form_data, ppg_data):
    """
    This is the core of the Rule-Based Engine.
    It processes form and PPG data to generate a user health profile.
    """
    # 1. Determine Dominant Dosha (simplified logic based on form)
    # In a real system, this would be a more complex scoring of all form answers.
    physical_build = form_data.get('body_type', 'Medium')
    dominant_dosha = "Pitta" # Default
    if physical_build == 'Slim':
        dominant_dosha = "Vata"
    elif physical_build == 'Large':
        dominant_dosha = "Kapha"
    
    # Override with PPG data if available and conclusive
    if ppg_data and 'dosha' in ppg_data:
        # A more advanced system might weigh form vs. PPG, but for now PPG takes precedence
        dominant_dosha = ppg_data['dosha'].capitalize()

    # 2. Calculate Caloric Needs (using Harris-Benedict Equation - simplified)
    # This is a placeholder. A real implementation needs weight, height, activity level.
    caloric_needs = 1800 # Default

    # 3. Filter Food Database (The Scientist)
    food_db = load_food_database()
    safe_palette = []
    for food in food_db:
        props = food.get('ayurvedic_properties', {})
        dosha_effect = props.get(dominant_dosha.lower(), "Neutral")
        
        # Simple filter: avoid foods that strongly increase the dominant dosha
        if dosha_effect not in ["Increase"]:
             safe_palette.append(food['food_name'])

    # 4. Generate a Health Profile Summary
    summary = (f"User is a {form_data.get('age', 'N/A')}-year-old {form_data.get('gender', 'N/A')} "
               f"with a dominant {dominant_dosha} dosha. Stated goal is {form_data.get('health_goal', 'general wellness')}. "
               f"Biometric data suggests a heart rate around {ppg_data.get('heart_rate', 'N/A')} BPM. "
               f"User has indicated a preference for {form_data.get('diet_preference', 'any')} meals.")

    return {
        "caloric_target": caloric_needs,
        "dominant_dosha": dominant_dosha,
        "approved_foods": safe_palette[:100], # Limit for prompt size
        "health_profile_summary": summary
    }


def generate_diet_chart_prompt(health_profile):
    """Creates the detailed prompt for the LLM."""
    
    prompt = f"""
    You are an expert Ayurvedic chef and holistic health advisor creating a personalized, recipe-based diet chart.
    The user's dominant dosha is {health_profile['dominant_dosha']} and their daily calorie target is {health_profile['caloric_target']} kcal.
    You must only use ingredients from the following list: {", ".join(health_profile['approved_foods'])}.

    User Health Profile: {health_profile['health_profile_summary']}

    Your Task:
    1. Create a one-day vegetarian meal plan (Breakfast, Lunch, Dinner) using only the approved ingredients, targeting {health_profile['caloric_target']} kcal. For each meal, provide a simple recipe.
    2. After the meal plan, create a section called "Personalized Recommendations". Based on the user's health profile, provide 3-5 actionable suggestions. These should be a mix of dietary advice (e.g., "Favor cooling foods like cucumber and coconut to balance your Pitta") and lifestyle advice (e.g., "To manage stress, consider a short, calming walk after dinner").
    """
    return prompt

def get_llm_diet_chart(health_profile):
    """
    Simulates the LLM call and returns a complete diet chart.
    In a real application, this function would make an API call to a Large Language Model.
    """
    
    # --- This is where the actual API call to the LLM would go ---
    # prompt = generate_diet_chart_prompt(health_profile)
    # llm_response = your_llm_api.generate(prompt)
    # return llm_response
    
    # --- Placeholder LLM Response ---
    dosha = health_profile['dominant_dosha']
    
    # Simple logic to make the placeholder feel personalized
    if dosha == "Pitta":
        breakfast = "Cooling Coconut and Rice Flake Porridge"
        lunch = "Quinoa Salad with Cucumber and Mint"
        dinner = "Mung Dal Kitchari with Steamed Asparagus"
        rec1 = f"Favor cooling foods like cucumber, coconut, and cilantro to balance your {dosha}."
        rec2 = "Avoid spicy, oily, and excessively sour foods as they can aggravate your system."
    elif dosha == "Vata":
        breakfast = "Warm Spiced Oatmeal with Ghee and Cinnamon"
        lunch = "Root Vegetable Stew with Basmati Rice"
        dinner = "Nourishing Lentil Soup with Ginger"
        rec1 = f"Emphasize warm, moist, and grounding foods to balance your airy {dosha} nature."
        rec2 = "Maintain a regular meal schedule to support stable digestion."
    else: # Kapha
        breakfast = "Light and Spiced Millet Porridge"
        lunch = "Steamed Vegetables with Chickpea Flour (Besan) Roti"
        dinner = "Spicy Black Bean Soup with a side of steamed Kale"
        rec1 = f"Focus on light, dry, and warm foods to invigorate your {dosha} constitution."
        rec2 = "Incorporate pungent spices like ginger, black pepper, and turmeric to stimulate digestion."

    llm_output = f"""
    =================================
    Your Personalized Ayurvedic Diet Chart
    =================================
    Dominant Dosha: {dosha}
    Daily Calorie Target: {health_profile['caloric_target']} kcal

    --- MEAL PLAN ---

    **Breakfast: {breakfast}**
    Recipe: Gently cook 1/2 cup of the main grain (e.g., rice flakes, oats, millet) with 1 cup of water or almond milk. Add a teaspoon of ghee (for Vata/Pitta) or a pinch of warming spice (for Kapha) like cinnamon or cardamom. Cook until tender.

    **Lunch: {lunch}**
    Recipe: Combine 1 cup of cooked grains (like quinoa or rice) with 1.5 cups of steamed or fresh, dosha-appropriate vegetables. Create a simple dressing with lemon juice, a touch of olive oil, and herbs like cilantro or mint.

    **Dinner: {dinner}**
    Recipe: A simple kitchari or soup is ideal. Cook 1/2 cup of split mung beans with 1/4 cup of basmati rice in 3-4 cups of water until soft. Season with ginger, turmeric, and cumin. This is balancing for all doshas.

    --- PERSONALIZED RECOMMENDATIONS ---

    1. {rec1}
    2. {rec2}
    3. **Mindful Eating:** Regardless of your dosha, eating in a calm and settled environment is crucial for proper digestion. Avoid distractions like TV or phones during meals.
    4. **Hydration:** Sip warm water throughout the day. For Pitta, room temperature is fine. Vata and Kapha benefit most from warm or hot water.
    """
    
    return llm_output
