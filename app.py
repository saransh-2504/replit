import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import check_password_hash
import database
from api_helper import get_user_intent, get_intent_from_text

app = Flask(__name__)

app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

database.init_db()

@app.route('/')
def index():
    """Main marketing landing page."""
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        user_id = database.create_user(username, password)
        
        if user_id is None:
            return jsonify({'error': 'Username already exists'}), 400
        
        database.create_website_entry(user_id)
        
        session['user_id'] = user_id
        session['username'] = username
        
        return redirect(url_for('dashboard'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login route."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        user = database.get_user_by_username(username)
        
        if user and database.verify_password(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        else:
            return jsonify({'error': 'Invalid username or password'}), 401
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout route."""
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """Protected dashboard route - YouTube Studio style."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    website_data = database.get_website_content(user_id)
    
    return render_template('dashboard.html', 
                         username=session['username'],
                         website=website_data)

@app.route('/process-audio', methods=['POST'])
def process_audio():
    """Protected API route for voice command processing."""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        
        if audio_file.filename == '':
            return jsonify({'error': 'No audio file selected'}), 400
        
        result = get_user_intent(audio_file)
        
        if result.get('success') and result.get('action') == 'update':
            user_id = session['user_id']
            field = result.get('field')
            value = result.get('value')
            
            current_data = database.get_website_content(user_id)
            
            update_data = {
                'shop_name': current_data.get('shop_name', ''),
                'description': current_data.get('description', ''),
                'announcement': current_data.get('announcement', ''),
                'image_url': current_data.get('image_url', '')
            }
            
            if field in update_data:
                update_data[field] = value
                
                success = database.save_website_content(
                    user_id=user_id,
                    shop_name=update_data['shop_name'],
                    description=update_data['description'],
                    announcement=update_data['announcement'],
                    image_url=update_data['image_url']
                )
                
                if success:
                    updated_website = database.get_website_content(user_id)
                    result['website'] = updated_website
                    result['message'] = f'Successfully updated {field}'
                else:
                    result['error'] = 'Failed to save changes to database'
            else:
                result['error'] = f'Invalid field: {field}'
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/process-text', methods=['POST'])
def process_text():
    """Protected API route for text command processing (backup for voice)."""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        print(f"\n=== /process-text DEBUG ===")
        print(f"Received text: '{text}'")
        
        if not text:
            print("ERROR: No text provided")
            return jsonify({'error': 'No text provided'}), 400
        
        print("Calling get_intent_from_text()...")
        intent_data = get_intent_from_text(text)
        print(f"Intent data received: {intent_data}")
        
        intent = intent_data.get('intent')
        content = intent_data.get('content')
        
        if intent in ['shop_name', 'description', 'announcement']:
            action = "update"
            field = intent
            value = content
        else:
            action = "unknown"
            field = ""
            value = ""
        
        result = {
            'success': True,
            'action': action,
            'field': field,
            'value': value
        }
        
        print(f"Result prepared: {result}")
        
        if result.get('action') == 'update':
            user_id = session['user_id']
            field = result.get('field')
            value = result.get('value')
            
            print(f"Updating database - user_id: {user_id}, field: {field}, value: {value}")
            
            current_data = database.get_website_content(user_id)
            
            update_data = {
                'shop_name': current_data.get('shop_name', ''),
                'description': current_data.get('description', ''),
                'announcement': current_data.get('announcement', ''),
                'image_url': current_data.get('image_url', '')
            }
            
            if field in update_data:
                update_data[field] = value
                
                success = database.save_website_content(
                    user_id=user_id,
                    shop_name=update_data['shop_name'],
                    description=update_data['description'],
                    announcement=update_data['announcement'],
                    image_url=update_data['image_url']
                )
                
                if success:
                    print("Database update successful!")
                    updated_website = database.get_website_content(user_id)
                    result['website'] = updated_website
                    result['message'] = f'Successfully updated {field}'
                else:
                    print("ERROR: Database update failed")
                    result['error'] = 'Failed to save changes to database'
            else:
                print(f"ERROR: Invalid field: {field}")
                result['error'] = f'Invalid field: {field}'
        
        print(f"Returning result: {result}")
        print("=== END DEBUG ===\n")
        return jsonify(result), 200
        
    except Exception as e:
        print(f"\n!!! CRITICAL ERROR in /process-text !!!")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        import traceback
        print(f"Full traceback:\n{traceback.format_exc()}")
        print("!!! END ERROR !!!\n")
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/save-data', methods=['POST'])
def save_data():
    """Protected API route for saving website content."""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        user_id = session['user_id']
        data = request.get_json()
        
        shop_name = data.get('shop_name')
        description = data.get('description')
        announcement = data.get('announcement')
        image_url = data.get('image_url')
        
        success = database.save_website_content(
            user_id=user_id,
            shop_name=shop_name,
            description=description,
            announcement=announcement,
            image_url=image_url
        )
        
        if success:
            return jsonify({'message': 'Website content saved successfully'}), 200
        else:
            return jsonify({'error': 'Failed to save website content'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/public/<username>')
def public_website(username):
    """Public website route for displaying user's live website."""
    user = database.get_user_by_username(username)
    
    if not user:
        return render_template('404.html'), 404
    
    user_id = user['id']
    website_data = database.get_website_content(user_id)
    
    database.increment_website_view(user_id)
    
    if not website_data:
        website_data = {
            'shop_name': f"{username}'s Website",
            'description': 'Welcome to my website!',
            'announcement': '',
            'image_url': '',
            'views': 0
        }
    
    return render_template('public_template.html', 
                         username=username,
                         website=website_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
