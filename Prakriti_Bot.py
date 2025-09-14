# This dictionary will act as a simple in-memory database to store the 
# state of the conversation for each user.
conversation_state = {}

# This is the list of questions the bot will ask to determine Prakriti.
QUESTIONS = [
    "How would you describe your body frame? (e.g., Slim, Medium, Large)",
    "What is your appetite usually like? (e.g., Irregular, Strong, Slow but steady)",
    "How is your skin type? (e.g., Dry, Sensitive/Oily, Thick/Cool)",
    "What is your typical energy level? (e.g., Comes in bursts, High and intense, Steady and calm)",
    "How do you typically react to stress? (e.g., Become anxious, Get irritable, Withdraw)"
]

def get_response(user_id, msg):
    """
    Manages the conversation flow and generates a response based on the user's input.
    """
    # Get the current state for this user, or create a new one if it doesn't exist.
    state = conversation_state.get(user_id, {"question_index": -1, "answers": []})

    # If the user says hello or wants to start, begin the quiz.
    if msg.lower() in ['hi', 'hello', 'start', 'begin']:
        state = {"question_index": 0, "answers": []}
        conversation_state[user_id] = state
        # Ask the first question.
        return f"Hello! I will ask you {len(QUESTIONS)} questions to help determine your Prakriti. Let's begin. Question 1: {QUESTIONS[0]}"

    # If the quiz hasn't started yet, prompt the user to start.
    if state["question_index"] == -1:
        return "Please say 'start' to begin the Prakriti assessment."

    # --- Process the user's answer and ask the next question ---

    # Save the user's answer to the previous question.
    state["answers"].append(msg)
    
    # Move to the next question index.
    state["question_index"] += 1
    
    # Check if there are more questions to ask.
    if state["question_index"] < len(QUESTIONS):
        next_question_number = state["question_index"] + 1
        response = f"Thank you. Question {next_question_number}: {QUESTIONS[state['question_index']]}"
    else:
        # --- The quiz is over. Calculate and return the result. ---
        
        # This is a simplified analysis for demonstration. 
        # It looks for keywords in the user's answers.
        vata_score = 0
        pitta_score = 0
        kapha_score = 0
        
        for answer in state["answers"]:
            ans_lower = answer.lower()
            if any(word in ans_lower for word in ['slim', 'irregular', 'dry', 'bursts', 'anxious']):
                vata_score += 1
            if any(word in ans_lower for word in ['medium', 'strong', 'sensitive', 'oily', 'intense', 'irritable']):
                pitta_score += 1
            if any(word in ans_lower for word in ['large', 'slow', 'steady', 'thick', 'cool', 'calm', 'withdraw']):
                kapha_score += 1

        scores = {"Vata": vata_score, "Pitta": pitta_score, "Kapha": kapha_score}
        # Find the Prakriti with the highest score.
        dominant_prakriti = max(scores, key=scores.get)

        response = (f"Thank you for your answers! Based on your responses, your dominant Prakriti "
                    f"appears to be **{dominant_prakriti}**. This is a preliminary assessment. For a "
                    f"complete diagnosis, please consult a registered Ayurvedic practitioner. "
                    f"You can say 'start' to begin again.")
        
        # The quiz is over, so we reset the conversation state for this user.
        if user_id in conversation_state:
            del conversation_state[user_id]

    return response

