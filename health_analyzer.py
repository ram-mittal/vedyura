import json
import random

# --- Load Food Database ---
try:
    with open('data/food_database.json', 'r', encoding='utf-8') as f:
        FOOD_DATA = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    FOOD_DATA = []

def generate_health_profile(form_data, ppg_data, plan_type='daily'): # NEW: Added plan_type
    """
    Analyzes user data to determine dosha, caloric needs, and generate a
    personalized diet chart with advice. This is the "Intelligent Backend Engine".
    """
    # --- 1. Rule-Based Engine: Determine Dosha & Caloric Needs ---
    
    # More scientific and nuanced Dosha determination
    dominant_dosha = determine_dominant_dosha(form_data)

    # Scientific Caloric needs calculation using Mifflin-St Jeor Equation
    caloric_needs = calculate_caloric_needs(form_data)

    # --- 2. Rule-Based Engine: Filter Food Database ---
    approved_foods = [
        food['food_name'] for food in FOOD_DATA 
        if food.get('ayurvedic_properties', {}).get(dominant_dosha.lower()) in ['Decrease', 'Neutral']
    ]
    
    # --- 3. Generate Health Profile Summary for the LLM ---
    summary = generate_profile_summary(form_data, ppg_data, dominant_dosha)
    
    # --- 4. Construct the Upgraded LLM Prompt (Simulated) ---
    # NEW: Pass plan_type to the response generator
    simulated_llm_output = generate_simulated_llm_response(dominant_dosha, caloric_needs, summary, approved_foods, plan_type)

    return {
        'dominant_dosha': dominant_dosha,
        'caloric_target': caloric_needs,
        'health_profile_summary': summary,
        'diet_chart_text': simulated_llm_output
    }

def determine_dominant_dosha(form_data):
    """Determines dominant dosha based on a weighted scoring of form data."""
    scores = {'Vata': 0, 'Pitta': 0, 'Kapha': 0}
    
    # Physical Traits
    if form_data.get('body_frame') == 'slim': scores['Vata'] += 2
    if form_data.get('body_frame') == 'medium': scores['Pitta'] += 2
    if form_data.get('body_frame') == 'large': scores['Kapha'] += 2
    
    if form_data.get('skin_texture') == 'dry_rough': scores['Vata'] += 1
    if form_data.get('skin_texture') == 'oily_sensitive': scores['Pitta'] += 1
    if form_data.get('skin_texture') == 'thick_cool': scores['Kapha'] += 1

    if form_data.get('hair_type') == 'dry_thin': scores['Vata'] += 1
    if form_data.get('hair_type') == 'oily_fine': scores['Pitta'] += 1
    if form_data.get('hair_type') == 'thick_wavy': scores['Kapha'] += 1

    # Metabolic Traits
    if form_data.get('appetite') == 'irregular': scores['Vata'] += 2
    if form_data.get('appetite') == 'strong': scores['Pitta'] += 2
    if form_data.get('appetite') == 'slow': scores['Kapha'] += 2

    if form_data.get('energy_levels') == 'variable': scores['Vata'] += 1
    if form_data.get('energy_levels') == 'moderate_focused': scores['Pitta'] += 1
    if form_data.get('energy_levels') == 'steady_endurance': scores['Kapha'] += 1

    if form_data.get('sleep_pattern') == 'light_interrupted': scores['Vata'] += 1
    if form_data.get('sleep_pattern') == 'moderate_sound': scores['Pitta'] += 1
    if form_data.get('sleep_pattern') == 'deep_long': scores['Kapha'] += 1

    dominant_dosha = max(scores, key=scores.get) if any(scores.values()) else "Tridoshic"
    return dominant_dosha

def calculate_caloric_needs(form_data):
    """Calculates daily caloric needs using Mifflin-St Jeor equation."""
    try:
        weight = float(form_data.get('weight', 70))
        height = float(form_data.get('height', 175))
        age = int(form_data.get('age', 30))
        gender = form_data.get('gender', 'male')
        activity = form_data.get('activity_level', 'sedentary')

        # BMR calculation
        if gender == 'male':
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else: # female
            bmr = 10 * weight + 6.25 * height - 5 * age - 161

        # Activity multiplier
        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'very_active': 1.725
        }
        multiplier = activity_multipliers.get(activity, 1.2)
        
        caloric_needs = bmr * multiplier

        # Adjust for health goal
        goal = form_data.get('health_goal')
        if goal == 'weight_loss':
            caloric_needs -= 400 # Caloric deficit
        elif goal == 'weight_gain':
            caloric_needs += 400 # Caloric surplus
            
        return int(caloric_needs)

    except (ValueError, TypeError):
        return 2000 # Return a default value if form data is invalid

def generate_profile_summary(form_data, ppg_data, dosha):
    """Generates a concise health profile summary for the LLM."""
    summary = (
        f"User is a {form_data.get('age', 'N/A')}-year-old {form_data.get('gender', 'N/A')} "
        f"with a dominant {dosha} dosha. "
        f"Their primary health goal is {form_data.get('health_goal', 'general_wellness').replace('_', ' ')}. "
        f"Reported allergies: {form_data.get('allergies', 'none')}. "
        f"Pre-existing conditions: {form_data.get('medical_conditions', 'none')}."
    )
    if 'heart_rate' in ppg_data and 'error' not in ppg_data:
        summary += f" Objective biometric scan shows a resting heart rate of {int(ppg_data['heart_rate'])} BPM."
    # Future improvement: Add HRV analysis for stress here
    return summary

def generate_one_day_meal_plan(safe_foods):
    """
    NEW: Generates a single day's meal plan. This function is created to be reusable.
    """
    breakfast_options = [f for f in safe_foods if any(k in f.lower() for k in ['poha', 'upma', 'idli', 'dosa', 'oats'])]
    lunch_options = [f for f in safe_foods if any(k in f.lower() for k in ['roti', 'chapati', 'rice', 'dal', 'sabzi', 'curry'])]
    dinner_options = [f for f in safe_foods if any(k in f.lower() for k in ['khichdi', 'soup', 'dal'])]

    breakfast = random.choice(breakfast_options) if breakfast_options else "a light and suitable breakfast"
    lunch = random.choice(lunch_options) if lunch_options else "a balanced lunch"
    dinner = random.choice(dinner_options) if dinner_options else "a light dinner"

    return f"""
**Breakfast:**
- Meal: {breakfast}
- Rationale: [A real AI would explain why this is a good choice for your dosha.]

**Lunch:**
- Meal: {lunch} with a side of seasonal greens.
- Rationale: [A real AI would provide a reason for this choice.]

**Dinner:**
- Meal: {dinner}
- Rationale: [A real AI would provide a reason for this choice.]
"""

def generate_simulated_llm_response(dosha, calories, profile, safe_foods, plan_type='daily'):
    """
    This function simulates the output of a Large Language Model to generate
    the diet chart and personalized recommendations.
    UPDATED: Now generates either a daily or weekly plan.
    """
    
    meal_plan_text = ""
    if plan_type == 'weekly':
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for day in days:
            meal_plan_text += f"\n--- {day} ---\n"
            meal_plan_text += generate_one_day_meal_plan(safe_foods)
    else: # Default to daily
        meal_plan_text = generate_one_day_meal_plan(safe_foods)

    recommendations = ""
    if dosha == 'Vata':
        recommendations = (
            "1. Favor warm, moist, and grounding foods. Your constitution benefits from routine and nourishment.\n"
            "2. Incorporate healthy fats like ghee and sesame oil to combat dryness.\n"
            "3. Manage a tendency towards anxiety by practicing calming activities like meditation or a gentle walk in nature."
        )
    elif dosha == 'Pitta':
        recommendations = (
            "1. Favor cooling, fresh, and non-spicy foods to balance your natural heat. Avoid overly sour or salty tastes.\n"
            "2. Stay well-hydrated with water and cooling herbal teas like mint or fennel.\n"
            "3. Channel your focused energy, but avoid overheating. Engage in relaxing activities like swimming or evening strolls."
        )
    elif dosha == 'Kapha':
        recommendations = (
            "1. Favor warm, light, and stimulating foods with pungent, bitter, and astringent tastes.\n"
            "2. Engage in regular, vigorous exercise to boost your metabolism and prevent stagnation.\n"
            "3. Keep your mind active and stimulated with new hobbies and challenges to prevent feelings of lethargy."
        )
    else: # Tridoshic
        recommendations = ("1. Your constitution is relatively balanced. Focus on a varied diet with fresh, seasonal foods.\n"
                           "2. Listen to your body's signals of hunger and fullness to maintain equilibrium.\n"
                           "3. Adapt your routine to the seasons: favor warming foods in winter and cooling foods in summer.")

    diet_chart_text = f"""
Vedyura Personalized Health Plan
=================================

User Health Profile Summary:
----------------------------
{profile}

Your Meal Plan (Approx. Target: {calories} kcal per day):
------------------------------------------------
{meal_plan_text}

Personalized Recommendations:
-----------------------------
{recommendations}

Disclaimer: This diet chart is a preliminary suggestion based on the provided data. It is not a substitute for professional medical advice. Please consult with a qualified healthcare professional before making significant changes to your diet or lifestyle.
"""
    return diet_chart_text