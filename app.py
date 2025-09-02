from flask import Flask, render_template, request, jsonify, session
import mysql.connector
import openai
import json
from datetime import timedelta
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config['SECRET_KEY']
app.permanent_session_lifetime = timedelta(days=7)

# Initialize OpenAI
openai.api_key = app.config['OPENAI_API_KEY']

def get_db_connection():
    return mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB']
    )

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create recipes table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recipes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            ingredients TEXT,
            instructions TEXT,
            prep_time VARCHAR(50),
            difficulty VARCHAR(50),
            user_id INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Create a demo user if not exists
    cursor.execute("SELECT id FROM users WHERE email = 'demo@recipeapp.com'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (username, email) VALUES (%s, %s)",
            ('Demo User', 'demo@recipeapp.com')
        )
    
    conn.commit()
    cursor.close()
    conn.close()

@app.route('/')
def index():
    # Set a demo user session for the app
    session.permanent = True
    if 'user_id' not in session:
        # Get the demo user ID
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = 'demo@recipeapp.com'")
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user:
            session['user_id'] = user[0]
            session['username'] = 'Demo User'
    
    return render_template('index.html')

@app.route('/get_recipes', methods=['POST'])
def get_recipes():
    try:
        data = request.get_json()
        ingredients = data.get('ingredients', [])
        
        if not ingredients:
            return jsonify({'error': 'No ingredients provided'}), 400
        
        # Generate recipe suggestions using OpenAI
        prompt = f"""
        Suggest 3 simple recipes using these ingredients: {', '.join(ingredients)}.
        For each recipe, provide:
        1. A creative name
        2. A brief description (1-2 sentences)
        3. Preparation time (e.g., "20 minutes")
        4. Difficulty level (Easy, Medium, or Hard)
        
        Format the response as a JSON array with objects containing:
        name, description, prep_time, difficulty
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful recipe assistant. Provide responses in valid JSON format."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )
        
        # Parse the response
        recipes_text = response.choices[0].message.content.strip()
        recipes = json.loads(recipes_text)
        
        # Save to database
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'User not authenticated'}), 401
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Save each recipe to the database
        for recipe in recipes:
            cursor.execute(
                """INSERT INTO recipes 
                (name, description, ingredients, prep_time, difficulty, user_id) 
                VALUES (%s, %s, %s, %s, %s, %s)""",
                (recipe['name'], recipe['description'], ', '.join(ingredients), 
                 recipe['prep_time'], recipe['difficulty'], user_id)
            )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'recipes': recipes})
        
    except Exception as e:
        print(f"Error: {str(e)}")
        # Fallback to mock data if OpenAI fails
        mock_recipes = [
            {
                'name': f"Delicious {ingredients[0] if ingredients else 'Ingredient'} Bowl",
                'description': f"A flavorful dish combining {', '.join(ingredients)} with fresh herbs and spices.",
                'prep_time': '20 minutes',
                'difficulty': 'Easy'
            },
            {
                'name': f"{ingredients[0] if ingredients else 'Ingredient'} & Veggie Stir Fry",
                'description': f"An Asian-inspired stir fry featuring {', '.join(ingredients[:2])} with fresh vegetables.",
                'prep_time': '25 minutes',
                'difficulty': 'Medium'
            },
            {
                'name': f"Oven-Roasted {ingredients[0] if ingredients else 'Ingredients'} Medley",
                'description': f"Oven-roasted {', '.join(ingredients)} with garlic and herbs. Simple yet delicious!",
                'prep_time': '35 minutes',
                'difficulty': 'Easy'
            }
        ]
        return jsonify({'recipes': mock_recipes})

@app.route('/recipe_history')
def recipe_history():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User not authenticated'}), 401
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute(
        "SELECT name, description, ingredients, prep_time, difficulty, created_at FROM recipes WHERE user_id = %s ORDER BY created_at DESC LIMIT 10",
        (user_id,)
    )
    
    recipes = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return jsonify({'recipes': recipes})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)