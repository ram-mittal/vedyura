import json
import random

# --- Load Food Database ---
try:
    with open('data/food_database.json', 'r', encoding='utf-8') as f:
        FOOD_DATA = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    FOOD_DATA = []

def generate_health_profile(form_data, ppg_data, plan_type='daily'):
    """
    Analyzes user data to determine dosha, caloric needs, and generate a
    personalized diet chart with advice. This is the "Intelligent Backend Engine".
    """
    # --- 1. Rule-Based Engine: Determine Dosha & Caloric Needs ---
    # UPDATED: This function is now compatible with the new form
    dominant_dosha = determine_dominant_dosha(form_data)

    # This function remains compatible
    caloric_needs = calculate_caloric_needs(form_data)

    # --- 2. Rule-Based Engine: Filter Food Database ---
    approved_foods = [
        food['food_name'] for food in FOOD_DATA
        if food.get('ayurvedic_properties', {}).get(dominant_dosha.lower()) in ['Decrease', 'Neutral']
    ]

    # --- 3. Generate Health Profile Summary for the LLM ---
    # UPDATED: This function now creates a richer summary
    summary = generate_profile_summary(form_data, ppg_data, dominant_dosha)

    # --- 4. Construct the Upgraded LLM Prompt (Simulated) ---
    simulated_llm_output = generate_simulated_llm_response(dominant_dosha, caloric_needs, summary, approved_foods, plan_type)

    return {
        'dominant_dosha': dominant_dosha,
        'caloric_target': caloric_needs,
        'health_profile_summary': summary,
        'diet_chart_text': simulated_llm_output
    }

def determine_dominant_dosha(form_data):
    """
    UPDATED: Determines dominant dosha based on a weighted scoring of the NEW form data.
    """
    scores = {'Vata': 0, 'Pitta': 0, 'Kapha': 0}

    # Physical Nature (Deha Prakriti)
    if form_data.get('body_frame') == 'light_lean': scores['Vata'] += 2
    if form_data.get('body_frame') == 'moderate_athletic': scores['Pitta'] += 2
    if form_data.get('body_frame') == 'solid_sturdy': scores['Kapha'] += 2

    if form_data.get('skin_texture') == 'dry_cool': scores['Vata'] += 1
    if form_data.get('skin_texture') == 'warm_sensitive': scores['Pitta'] += 1
    if form_data.get('skin_texture') == 'thick_smooth': scores['Kapha'] += 1

    if form_data.get('hair_type') == 'dry_brittle': scores['Vata'] += 1
    if form_data.get('hair_type') == 'fine_oily': scores['Pitta'] += 1
    if form_data.get('hair_type') == 'thick_lustrous': scores['Kapha'] += 1

    # Metabolism & Digestion (Agni)
    if form_data.get('appetite') == 'unpredictable': scores['Vata'] += 2
    if form_data.get('appetite') == 'strong_urgent': scores['Pitta'] += 2
    if form_data.get('appetite') == 'slow_steady': scores['Kapha'] += 2

    if form_data.get('digestion') == 'dry_gas': scores['Vata'] += 1
    if form_data.get('digestion') == 'acidity_urgency': scores['Pitta'] += 1
    if form_data.get('digestion') == 'slow_heaviness': scores['Kapha'] += 1

    # Energy & Mind (Manas Prakriti)
    if form_data.get('energy_levels') == 'bursts_of_energy': scores['Vata'] += 1
    if form_data.get('energy_levels') == 'focused_driven': scores['Pitta'] += 1
    if form_data.get('energy_levels') == 'steady_enduring': scores['Kapha'] += 1

    if form_data.get('stress_reaction') == 'anxiety_worry': scores['Vata'] += 1
    if form_data.get('stress_reaction') == 'irritability_impatience': scores['Pitta'] += 1
    if form_data.get('stress_reaction') == 'withdrawal_lethargy': scores['Kapha'] += 1

    if form_data.get('sleep_pattern') == 'light_interrupted': scores['Vata'] += 1
    if form_data.get('sleep_pattern') == 'sound_short': scores['Pitta'] += 1
    if form_data.get('sleep_pattern') == 'deep_long': scores['Kapha'] += 1

    # Subtle Indicators
    if form_data.get('speaking_style') == 'fast_talkative': scores['Vata'] += 1
    if form_data.get('speaking_style') == 'clear_purposeful': scores['Pitta'] += 1
    if form_data.get('speaking_style') == 'slow_calm': scores['Kapha'] += 1

    if form_data.get('body_temperature') == 'tend_to_be_cold': scores['Vata'] += 1
    if form_data.get('body_temperature') == 'tend_to_be_warm': scores['Pitta'] += 1
    if form_data.get('body_temperature') == 'adaptable': scores['Kapha'] += 1


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
    """
    UPDATED: Generates a more detailed health profile summary using the NEW form data.
    """
    # Helper to format the descriptive answers
    def format_answer(key):
        raw_answer = form_data.get(key, 'N/A')
        return raw_answer.replace('_', ' ').replace(' and ', ' & ')

    summary = (
        f"The user is a {form_data.get('age', 'N/A')}-year-old {form_data.get('gender', 'N/A')} "
        f"with a dominant {dosha} dosha. Their primary health goal is {format_answer('health_goal')}. "
        f"Their self-reported physical traits include a '{format_answer('body_frame')}' frame and skin that is '{format_answer('skin_texture')}'. "
        f"Metabolically, they report a '{format_answer('appetite')}' appetite and their digestion tends towards '{format_answer('digestion')}'. "
        f"Under stress, they tend towards '{format_answer('stress_reaction')}'. "
        f"Reported allergies: {form_data.get('allergies', 'none') or 'none'}. "
        f"Pre-existing conditions: {form_data.get('medical_conditions', 'none') or 'none'}."
    )
    if 'heart_rate' in ppg_data and 'error' not in ppg_data:
        summary += f" An objective biometric scan shows a resting heart rate of {int(ppg_data['heart_rate'])} BPM."
    
    summary += f" Their yoga experience is at a '{format_answer('yoga_experience')}' level."
    
    return summary

def generate_one_day_meal_plan(safe_foods):
    """
    Generates a single day's meal plan. This function is created to be reusable.
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
    This contains the professional, 10-step Yoga sequence.
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
    yoga_recommendations = "" 

    if dosha == 'Vata':
        recommendations = (
            "1. Favor warm, moist, and grounding foods. Your constitution benefits from routine and nourishment.\n"
            "2. Incorporate healthy fats like ghee and sesame oil to combat dryness.\n"
            "3. Manage a tendency towards anxiety by practicing calming activities like meditation or a gentle walk in nature."
        )
        yoga_recommendations = (
            "**Focus:** A grounding and stabilizing practice to calm the nervous system.\n"
            "**Pace:** Slow, mindful, and deliberate. Hold each pose for 5 deep breaths.\n\n"
            "**Your 10-Step Vata-Balancing Yoga Sequence:**\n"
            "1.  **Centering (Sukhasana / Easy Pose):** Sit comfortably, close your eyes, and take 10 slow, deep belly breaths.\n"
            "2.  **Warm-up (Marjaryasana-Bitilasana / Cat-Cow):** Gently move through 10 rounds to warm up the spine.\n"
            "3.  **Standing Pose 1 (Tadasana / Mountain Pose):** Stand firm, feel your connection to the ground, and hold for 1 minute.\n"
            "4.  **Standing Pose 2 (Virabhadrasana II / Warrior II):** Hold for 30 seconds on each side, feeling your strength and stability.\n"
            "5.  **Seated Bend (Paschimottanasana / Seated Forward Bend):** Gently stretch the back of your body. Do not force.\n"
            "6.  **Seated Twist (Ardha Matsyendrasana / Half Lord of the Fishes):** Gently twist to aid digestion and release spinal tension.\n"
            "7.  **Gentle Backbend (Setu Bandhasana / Bridge Pose):** Lift your hips to open the chest gently.\n"
            "8.  **Gentle Inversion (Viparita Karani / Legs-Up-the-Wall):** A highly restorative pose. Rest with your legs up a wall for 3-5 minutes.\n"
            "9.  **Cool-down (Balasana / Child's Pose):** Rest your forehead on the mat and relax completely for 1 minute.\n"
            "10. **Final Relaxation (Savasana / Corpse Pose):** Lie flat on your back for 5-10 minutes, allowing your body to integrate the practice."
        )
    elif dosha == 'Pitta':
        recommendations = (
            "1. Favor cooling, fresh, and non-spicy foods to balance your natural heat. Avoid overly sour or salty tastes.\n"
            "2. Stay well-hydrated with water and cooling herbal teas like mint or fennel.\n"
            "3. Channel your focused energy, but avoid overheating. Engage in relaxing activities like swimming or evening strolls."
        )
        yoga_recommendations = (
            "**Focus:** A cooling and calming practice to release intensity and heat.\n"
            "**Pace:** Relaxed and non-competitive. Breathe smoothly and avoid strain.\n\n"
            "**Your 10-Step Pitta-Balancing Yoga Sequence:**\n"
            "1.  **Centering (Sukhasana with Sheetali Breath):** Sit comfortably. Inhale through a curled tongue to cool the body. 10 breaths.\n"
            "2.  **Warm-up (Chandra Namaskar / Moon Salutations):** Flow through 3-5 rounds at a relaxed, graceful pace.\n"
            "3.  **Standing Pose (Trikonasana / Triangle Pose):** Hold for 30 seconds each side to open the side body.\n"
            "4.  **Seated Bend (Janu Sirsasana / Head-to-Knee Bend):** A cooling forward bend to calm the mind.\n"
            "5.  **Gentle Backbend (Bhujangasana / Cobra Pose):** Open the heart without creating excessive heat. Hold for 5 breaths.\n"
            "6.  **Deeper Backbend (Ustrasana / Camel Pose):** A powerful heart-opener. Keep your head neutral to avoid strain.\n"
            "7.  **Shoulder Stand (Salamba Sarvangasana):** A cooling and restorative inversion. Hold for 1-3 minutes.\n"
            "8.  **Plow Pose (Halasana):** Transition from shoulder stand to deepen the stretch in the spine.\n"
            "9.  **Counterpose (Matsyasana / Fish Pose):** The perfect release after shoulder stand and plow.\n"
            "10. **Final Relaxation (Savasana / Corpse Pose):** Lie flat for 5-10 minutes, focusing on releasing all heat and effort."
        )
    elif dosha == 'Kapha':
        recommendations = (
            "1. Favor warm, light, and stimulating foods with pungent, bitter, and astringent tastes.\n"
            "2. Engage in regular, vigorous exercise to boost your metabolism and prevent stagnation.\n"
            "3. Keep your mind active and stimulated with new hobbies and challenges to prevent feelings of lethargy."
        )
        yoga_recommendations = (
            "**Focus:** An energizing and stimulating practice to invigorate the body and mind.\n"
            "**Pace:** Dynamic and flowing (Vinyasa style). Move with your breath to build heat.\n\n"
            "**Your 10-Step Kapha-Balancing Yoga Sequence:**\n"
            "1.  **Centering (Virasana with Bhastrika Breath):** Sit tall and practice 3 rounds of Bellows Breath to build energy.\n"
            "2.  **Warm-up (Surya Namaskar / Sun Salutations):** Flow through 5-8 rounds at a brisk, steady pace.\n"
            "3.  **Standing Pose (Utkatasana / Chair Pose):** Build heat and strength in the legs. Hold for 5-8 breaths.\n"
            "4.  **Standing Balance (Virabhadrasana III / Warrior III):** Challenge your focus and build core strength.\n"
            "5.  **Peak Backbend (Dhanurasana / Bow Pose):** A powerful pose to stimulate the entire front of the body.\n"
            "6.  **Core Strength (Navasana / Boat Pose):** Engage your core to stimulate digestive fire (Agni).\n"
            "7.  **Inversion (Sirsasana / Headstand or Dolphin Pose):** Change your perspective and improve circulation. Hold as long as comfortable.\n"
            "8.  **Reclining Twist (Jathara Parivartanasana):** A deep twist to cleanse and detoxify.\n"
            "9.  **Cool-down (Setu Bandhasana / Bridge Pose):** A gentler backbend to begin the cool-down process.\n"
            "10. **Final Relaxation (Savasana / Corpse Pose):** Despite the active practice, do not skip this. Relax for 5-10 minutes."
        )
    else: # Tridoshic
        recommendations = ("1. Your constitution is relatively balanced. Focus on a varied diet with fresh, seasonal foods.\n"
                           "2. Listen to your body's signals of hunger and fullness to maintain equilibrium.\n"
                           "3. Adapt your routine to the seasons: favor warming foods in winter and cooling foods in summer.")
        yoga_recommendations = (
            "**Focus:** A balanced and varied practice to maintain your natural equilibrium.\n"
            "**Pace:** Moderate and intuitive. On energetic days, practice faster; on tired days, practice slower.\n\n"
            "**A Balanced 10-Step Yoga Sequence:**\n"
            "1.  **Centering (Sukhasana):** 10 deep breaths.\n"
            "2.  **Warm-up (Cat-Cow):** 10 rounds.\n"
            "3.  **Flow (Sun Salutation A):** 3-5 rounds.\n"
            "4.  **Standing Pose (Warrior II):** 30 seconds each side.\n"
            "5.  **Balance (Vrksasana / Tree Pose):** 30 seconds each side.\n"
            "6.  **Seated Bend (Paschimottanasana):** 1 minute.\n"
            "7.  **Backbend (Bridge Pose):** 30 seconds.\n"
            "8.  **Twist (Ardha Matsyendrasana):** 30 seconds each side.\n"
            "9.  **Cool-down (Child's Pose):** 1 minute.\n"
            "10. **Final Relaxation (Savasana):** 5-10 minutes."
        )

    diet_chart_text = f"""
Vedyura Personalized Health Plan
=================================

User Health Profile Summary:
----------------------------
{profile}

Your Meal Plan (Approx. Target: {calories} kcal per day):
------------------------------------------------
{meal_plan_text}

Personalized Lifestyle Recommendations:
------------------------------------
{recommendations}

Your Daily Yoga & Movement Sequence:
------------------------------------
{yoga_recommendations}

Disclaimer: This diet chart is a preliminary suggestion based on the provided data. It is not a substitute for professional medical advice. Please consult with a qualified healthcare professional or a certified yoga instructor before making significant changes to your diet or lifestyle, especially if you have pre-existing health conditions.
"""
    return diet_chart_text