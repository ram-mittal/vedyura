import json

# --- Load Food Database ---
try:
    with open('data/foods.json', 'r') as f:
        FOOD_DATA = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    FOOD_DATA = []

# --- Conversation State & Questions (Based on the GitHub Project) ---
conversation_state = {}

# This is the full, detailed questionnaire adapted from the GitHub project.
QUESTIONS = [
    {"key": "Body Size", "question": "Let's start with your physical build. How would you describe your body size?", "options": ["Small", "Medium", "Large"]},
    {"key": "Bone Structure", "question": "What about your bone structure?", "options": ["Light, small bones", "Medium bone structure", "Large, heavy bones"]},
    {"key": "Complexion", "question": "How would you describe your skin's complexion?", "options": ["Dark, tans easily", "Fair, burns easily", "White, pale"]},
    {"key": "General Feel Of Skin", "question": "What is the general feel of your skin?", "options": ["Dry, rough", "Soft, oily", "Thick, cold"]},
    {"key": "Skin Texture", "question": "And the texture of your skin?", "options": ["Thin", "Delicate", "Thick"]},
    {"key": "Appearance of Hair", "question": "How would you describe the appearance of your hair?", "options": ["Dry, black, knotted", "Straight, oily", "Thick, wavy"]},
    {"key": "Shape of the Face", "question": "What is the shape of your face?", "options": ["Long, angular", "Heart-shaped, pointed chin", "Large, round, full"]},
    {"key": "Cheeks", "question": "How would you describe your cheeks?", "options": ["Wrinkled, sunken", "Smooth, flat", "Rounded, plump"]},
    {"key": "Nose", "question": "And your nose?", "options": ["Crooked, narrow", "Pointed, average size", "Rounded, large open nostrils"]},
    {"key": "Eyes", "question": "What are your eyes like?", "options": ["Small, active, darting", "Medium, sharp, penetrating", "Big, round, beautiful"]},
    {"key": "Nails", "question": "How would you describe your nails?", "options": ["Dry, rough, brittle", "Soft, pink, tender", "Thick, oily, smooth, polished"]},
    {"key": "Appetite", "question": "Finally, let's talk about your appetite. How would you describe it?", "options": ["Irregular, variable", "Strong, unbearable", "Slow but steady"]}
]

def format_question_with_buttons(question_dict):
    """Formats a question string with embedded button syntax."""
    question_text = question_dict['question']
    options = question_dict['options']
    buttons_html = " ".join([f"[button:{opt}]" for opt in options])
    return f"{question_text}<br>{buttons_html}"

def get_response(user_id, msg):
    """ Manages the entire conversation, from Prakriti quiz to food recommendations. """
    state = conversation_state.get(user_id, {"mode": "start"})
    msg_lower = msg.lower()

    if state["mode"] == "quiz" or (state["mode"] == "start" and msg_lower in ['hi', 'hello', 'start', 'begin']):
        return handle_quiz(user_id, msg_lower)
    
    elif state["mode"] == "food_recommendation":
        return handle_food_query(user_id, msg_lower)

    else:
        state["mode"] = "quiz"
        conversation_state[user_id] = state
        return handle_quiz(user_id, "start")

def handle_quiz(user_id, msg_lower):
    """ Handles the logic for the detailed Prakriti determination quiz. """
    state = conversation_state.get(user_id, {"question_index": -1, "answers": {}})

    if msg_lower in ['hi', 'hello', 'start', 'begin']:
        state = {"mode": "quiz", "question_index": 0, "answers": {}}
        conversation_state[user_id] = state
        current_question = QUESTIONS[0]
        return f"Hello! I will ask you a series of questions to help determine your Prakriti. Please choose the option that best describes you.<br><br>Question 1: {format_question_with_buttons(current_question)}"

    if state["question_index"] == -1:
        return "Please say 'start' to begin the assessment."

    # --- Process Answer ---
    current_question_index = state["question_index"]
    current_question = QUESTIONS[current_question_index]
    
    # Simple logic to find which option was chosen
    chosen_option = None
    option_index = -1
    for i, option in enumerate(current_question['options']):
        # We now check if the user's message EXACTLY matches an option.
        if option.lower() == msg_lower:
            chosen_option = option
            option_index = i
            break
    
    if chosen_option is None:
        return f"I'm sorry, I didn't understand that. Please click one of the buttons for the question: '{current_question['question']}'"

    # Store the index of the chosen option (0 for Vata, 1 for Pitta, 2 for Kapha)
    state["answers"][current_question["key"]] = option_index
    state["question_index"] += 1
    
    if state["question_index"] < len(QUESTIONS):
        next_q_num = state["question_index"] + 1
        next_question = QUESTIONS[state["question_index"]]
        conversation_state[user_id] = state
        return f"Thank you. Question {next_q_num}: {format_question_with_buttons(next_question)}"
    else:
        # --- End of Quiz: Calculate Result ---
        vata_score = sum(1 for ans_index in state["answers"].values() if ans_index == 0)
        pitta_score = sum(1 for ans_index in state["answers"].values() if ans_index == 1)
        kapha_score = sum(1 for ans_index in state["answers"].values() if ans_index == 2)

        scores = {"Vata": vata_score, "Pitta": pitta_score, "Kapha": kapha_score}
        dominant_prakriti = max(scores, key=scores.get)

        conversation_state[user_id] = {"mode": "food_recommendation", "prakriti": dominant_prakriti}
        
        good_foods = [food['name'].capitalize() for food in FOOD_DATA if dominant_prakriti in food.get('good_for', [])]
        
        score_breakdown = f"Score Breakdown -> Vata: {vata_score}, Pitta: {pitta_score}, Kapha: {kapha_score}."
        
        response = (f"Thank you for completing the assessment! Based on your answers, your dominant Prakriti appears to be **{dominant_prakriti}**. "
                    f"{score_breakdown}<br><br>"
                    f"Foods generally good for you include: **{', '.join(good_foods[:3])}**. "
                    f"You can now ask me about a specific food (e.g., 'What about banana?'), or say 'restart' to take the quiz again.")
        return response

def handle_food_query(user_id, msg_lower):
    """ Handles user questions about specific foods after Prakriti is known. """
    state = conversation_state.get(user_id)
    prakriti = state.get("prakriti")

    if 'restart' in msg_lower:
        conversation_state[user_id] = {"mode": "start"}
        return "Let's start over. Say 'start' to begin the assessment."

    for food_item in FOOD_DATA:
        if food_item["name"] in msg_lower:
            food_name = food_item["name"].capitalize()
            
            if not prakriti: # Should not happen, but a safeguard
                return "I need to determine your Prakriti first. Please say 'start'."

            effect = food_item["effects"][prakriti.lower()]
            
            if prakriti in food_item.get("good_for", []):
                judgment = "is generally considered **good** for you"
            elif prakriti in food_item.get("bad_for", []):
                judgment = "should be consumed in **moderation** as it can aggravate your dosha"
            else:
                judgment = "is generally **neutral** for you"

            return f"{food_name} {judgment}. It tends to **{effect}** your {prakriti} dosha."

    return "I'm not familiar with that food, but you can ask me about another. I know about apple, banana, rice, etc. You can also say 'restart'."

