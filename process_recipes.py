import csv
import json
import re
import os # NEW: Import the 'os' module to handle file paths

def get_ayurvedic_properties(ingredients_str):
    """Analyzes ingredients to determine their likely effect on doshas."""
    properties = {'vata': 'Neutral', 'pitta': 'Neutral', 'kapha': 'Neutral'}
    ingredients_lower = ingredients_str.lower()
    
    # Define keywords that increase doshas
    pitta_increase_keywords = ['chilli', 'pepper', 'mustard', 'asafoetida', 'hing', 'sour', 'tamarind', 'tomato', 'onion', 'garlic', 'pickle', 'fermented', 'vinegar', 'spicy']
    kapha_increase_keywords = ['cheese', 'cream', 'yogurt', 'milk', 'sugar', 'jaggery', 'sweet', 'potato', 'wheat flour', 'maida', 'butter', 'ghee', 'oil', 'banana']
    vata_increase_keywords = ['beans', 'chickpeas', 'lentils', 'dal', 'sprouts', 'cabbage', 'cauliflower', 'raw vegetables', 'salad', 'bitter gourd', 'karela', 'dry']
    
    # Define keywords that decrease doshas
    vata_decrease_keywords = ['ghee', 'sesame oil', 'sweet potato', 'pumpkin', 'rice', 'warm milk']
    pitta_decrease_keywords = ['coconut', 'cilantro', 'coriander', 'mint', 'cucumber', 'sunflower oil', 'rose']
    kapha_decrease_keywords = ['honey', 'ginger', 'turmeric', 'mustard seeds', 'spinach', 'millet', 'ragi']

    # Assign properties based on keywords
    if any(k in ingredients_lower for k in pitta_increase_keywords): properties['pitta'] = 'Increase'
    if any(k in ingredients_lower for k in kapha_increase_keywords): properties['kapha'] = 'Increase'
    if any(k in ingredients_lower for k in vata_increase_keywords): properties['vata'] = 'Increase'
        
    if any(k in ingredients_lower for k in vata_decrease_keywords): properties['vata'] = 'Decrease' if properties['vata'] != 'Increase' else 'Neutral'
    if any(k in ingredients_lower for k in pitta_decrease_keywords): properties['pitta'] = 'Decrease' if properties['pitta'] != 'Increase' else 'Neutral'
    if any(k in ingredients_lower for k in kapha_decrease_keywords): properties['kapha'] = 'Decrease' if properties['kapha'] != 'Increase' else 'Neutral'
            
    # Specific overrides for balancing dishes
    if 'khichdi' in ingredients_lower:
        properties.update({'vata': 'Decrease', 'pitta': 'Decrease', 'kapha': 'Decrease'})
        
    return properties

def create_recipe_database():
    """Reads the CSV and creates an enriched recipes.json file."""
    
    # --- UPDATED SECTION ---
    # This makes the script find files relative to its own location
    script_dir = os.path.dirname(__file__) # Gets the directory where the script is: Vedyura/
    csv_file_path = os.path.join(script_dir, 'IndianFoodDatasetCSV.csv') # Joins it with the CSV filename
    json_file_path = os.path.join(script_dir, 'data', 'recipes.json') # Joins it with the output path
    # --- END UPDATED SECTION ---

    recipe_list = []
    
    try:
        with open(csv_file_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                recipe_name = row.get('RecipeName', '').strip()
                clean_name = re.sub(r'\s*Recipe.*', '', recipe_name, flags=re.IGNORECASE).strip()
                ingredients = row.get('TranslatedIngredients', '').strip()
                instructions = row.get('TranslatedInstructions', '').strip()

                if not clean_name or not ingredients or not instructions:
                    continue

                properties = get_ayurvedic_properties(ingredients)
                
                recipe_list.append({
                    "name": clean_name,
                    "ingredients": ingredients,
                    "instructions": instructions,
                    "properties": properties
                })

        with open(json_file_path, 'w', encoding='utf-8') as outfile:
            json.dump(recipe_list, outfile, indent=4)
        print(f"✅ Success! Created recipe database with {len(recipe_list)} recipes at: {json_file_path}")

    except FileNotFoundError:
        print(f"❌ Error: The file {csv_file_path} was not found.")
        print("👉 Please make sure 'IndianFoodDatasetCSV.csv' is in the same folder as this script.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    create_recipe_database()