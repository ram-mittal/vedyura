import json

# --- Load Food Database ---
try:
    with open('data/food_database.json', 'r', encoding='utf-8') as f:
        FOOD_DATA = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    FOOD_DATA = []

def get_tool_response(user_id, msg, session_data):
    """
    Manages the logic for the Personal Diet Tool, providing intelligent responses
    based on the user's profile and query.
    """
    msg_lower = msg.lower()

    # --- Function 1: Intelligent Food Search (Placeholder) ---
    if "food" in msg_lower or "eat" in msg_lower or "vegetable" in msg_lower or "fruit" in msg_lower:
        return handle_food_search(msg_lower, session_data)

    # --- Function 2: Diet Chart Explanation (Placeholder) ---
    elif "why" in msg_lower and ("recommend" in msg_lower or "chart" in msg_lower):
        return handle_chart_explanation(msg_lower, session_data)

    # --- Function 3: Personalized Timetable (Placeholder) ---
    elif "routine" in msg_lower or "schedule" in msg_lower or "timetable" in msg_lower:
        return handle_timetable_request(session_data)
        
    # --- Default Greeting ---
    else:
        return "Hello! I am your Personal Diet Tool. You can ask me for food recommendations, explanations about your diet chart, or for a personalized daily routine."

def handle_food_search(msg, session_data):
    """
    Provides personalized food recommendations.
    This is a placeholder and would be replaced with a sophisticated search.
    """
    # In a real implementation, this would use the user's dosha, goals, and region
    # from session_data to filter FOOD_DATA.
    
    # Simple keyword matching for this placeholder:
    if "breakfast" in msg:
        return "For a high-protein breakfast, consider Moong Dal Chilla or a Spinach and Paneer Omelette."
    elif "lunch" in msg:
        return "For lunch, a balanced meal of Roti, a seasonal Sabzi, and a bowl of Dal is a great option for you."
    else:
        # Example of a filtered search (simplified)
        pitta_friendly_foods = [food['food_name'] for food in FOOD_DATA if food.get('ayurvedic_properties', {}).get('pitta') == 'Decrease'][:3]
        return f"Based on your profile, here are some good food options for you: {', '.join(pitta_friendly_foods)}."

def handle_chart_explanation(msg, session_data):
    """
    Explains the reasoning behind a food recommendation in the diet chart.
    This is a placeholder.
    """
    # Simple keyword matching for this placeholder:
    if "cucumber" in msg:
        return "Cucumber was recommended because it is very hydrating and low in calories. From an Ayurvedic perspective, it is a cooling food, which is excellent for balancing a Pitta dosha."
    elif "rice" in msg:
        return "Boiled rice is recommended as it's easy to digest and provides sustained energy. Ayurvedically, its sweet taste helps to ground Vata and cool Pitta."
    else:
        return "Please ask about a specific food in your chart, for example: 'Why was cucumber recommended?'"

def handle_timetable_request(session_data):
    """
    Generates and formats a personalized daily routine.
    This is a placeholder.
    """
    # In a real implementation, this timetable would be dynamically generated
    # based on the user's dosha and lifestyle from session_data.
    
    # We will format the response as a simple table for chatbot.js to parse.
    response = (
        "Here is a sample daily routine tailored to your profile:\n"
        "[table]\n"
        "Time | Activity\n"
        "---|---\n"
        "6:00 AM | Wake up, drink warm water\n"
        "7:00 AM | Light exercise (Yoga/Walking)\n"
        "8:30 AM | Breakfast\n"
        "1:00 PM | Lunch\n"
        "4:30 PM | Light snack (Fruit)\n"
        "7:00 PM | Dinner\n"
        "10:00 PM | Wind down, prepare for sleep\n"
        "[/table]"
    )
    return response
