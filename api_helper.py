import os
import requests
import json
import google.generativeai as genai

def transcribe_audio_file(audio_file):
    """
    Transcribe audio file using Hugging Face Whisper API.
    
    Args:
        audio_file: Flask FileStorage object containing the audio file
        
    Returns:
        str: Transcribed text from the audio
        
    Raises:
        Exception: If transcription fails or API key is missing
    """
    hf_token = os.environ.get('HF_TOKEN')
    if not hf_token:
        raise Exception('HF_TOKEN environment variable not set')
    
    audio_data = audio_file.read()
    
    if len(audio_data) > 25 * 1024 * 1024:
        raise Exception('Audio file too large (max 25MB)')
    
    content_type = audio_file.mimetype or 'application/octet-stream'
    
    api_url = "https://api-inference.huggingface.co/models/openai/whisper-base"
    headers = {
        "Authorization": f"Bearer {hf_token}",
        "Content-Type": content_type
    }
    
    try:
        response = requests.post(api_url, headers=headers, data=audio_data)
        response.raise_for_status()
        
        result = response.json()
        
        if isinstance(result, dict) and 'text' in result:
            return result['text']
        elif isinstance(result, dict) and 'error' in result:
            raise Exception(f"Hugging Face API error: {result['error']}")
        else:
            raise Exception(f"Unexpected API response format: {result}")
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to transcribe audio: {str(e)}")


def get_intent_from_text(text):
    """
    Extract structured intent from transcribed text using Google Gemini API.
    
    Args:
        text: Transcribed text from audio
        
    Returns:
        dict: Parsed intent with 'intent' and 'content' fields
        Example: {"intent": "shop_name", "content": "Meera's Flowers"}
        
    Raises:
        Exception: If intent extraction fails or API key is missing
    """
    print(f"\n=== get_intent_from_text DEBUG ===")
    print(f"Input text: '{text}'")
    
    try:
        gemini_api_key = os.environ.get('GEMINI_API_KEY')
        if not gemini_api_key:
            print("ERROR: GEMINI_API_KEY not found in environment")
            raise Exception('GEMINI_API_KEY environment variable not set')
        
        print("GEMINI_API_KEY found, configuring API...")
        genai.configure(api_key=gemini_api_key)
        
        prompt = f"""You are an AI assistant helping users update their website content through voice commands.

The user can update three fields:
1. "shop_name" - The name of their business/shop
2. "description" - A description of their business
3. "announcement" - A special announcement or message

Analyze the following voice command and determine what the user wants to update.

User's voice command: "{text}"

Respond ONLY with a JSON object in this exact format (no additional text):
{{"intent": "field_name", "content": "the value to set"}}

Examples:
- If user says "Change my shop name to Meera's Flowers", respond: {{"intent": "shop_name", "content": "Meera's Flowers"}}
- If user says "Update my description to We sell fresh organic vegetables", respond: {{"intent": "description", "content": "We sell fresh organic vegetables"}}
- If user says "Add an announcement that we're open on weekends", respond: {{"intent": "announcement", "content": "We're open on weekends"}}

If you cannot determine the intent, respond: {{"intent": "unknown", "content": ""}}"""
        
        print("Calling Gemini API...")
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        
        response_text = response.text.strip()
        print(f"Raw Gemini response: '{response_text}'")
        
        if response_text.startswith('```json'):
            response_text = response_text.replace('```json', '').replace('```', '').strip()
        elif response_text.startswith('```'):
            response_text = response_text.replace('```', '').strip()
        
        print(f"Cleaned response: '{response_text}'")
        
        try:
            parsed_response = json.loads(response_text)
            print(f"Parsed JSON: {parsed_response}")
            
            if 'intent' not in parsed_response or 'content' not in parsed_response:
                print("ERROR: Response missing required fields")
                raise ValueError("Response missing required fields")
            
            valid_intents = ['shop_name', 'description', 'announcement', 'unknown']
            if parsed_response['intent'] not in valid_intents:
                print(f"WARNING: Invalid intent '{parsed_response['intent']}', setting to 'unknown'")
                parsed_response['intent'] = 'unknown'
            
            print(f"Returning parsed response: {parsed_response}")
            print("=== END get_intent_from_text DEBUG ===\n")
            return parsed_response
            
        except json.JSONDecodeError as json_err:
            print(f"ERROR: JSON decode failed - {str(json_err)}")
            print("Returning unknown intent")
            print("=== END get_intent_from_text DEBUG ===\n")
            return {
                "intent": "unknown",
                "content": ""
            }
            
    except Exception as e:
        print(f"\n!!! CRITICAL ERROR in get_intent_from_text !!!")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        import traceback
        print(f"Full traceback:\n{traceback.format_exc()}")
        print("!!! END ERROR !!!\n")
        raise Exception(f"Failed to get intent from Gemini: {str(e)}")


def get_user_intent(audio_file):
    """
    Main function to process audio file and extract user intent.
    This combines transcription and intent extraction.
    
    Args:
        audio_file: Flask FileStorage object containing the audio file
        
    Returns:
        dict: Complete response with transcription and intent
        Example: {
            "transcription": "Change my shop name to Meera's Flowers",
            "action": "update",
            "field": "shop_name",
            "value": "Meera's Flowers",
            "success": True
        }
    """
    try:
        transcription = transcribe_audio_file(audio_file)
        
        intent_data = get_intent_from_text(transcription)
        
        intent = intent_data.get("intent")
        content = intent_data.get("content")
        
        if intent in ['shop_name', 'description', 'announcement']:
            action = "update"
            field = intent
            value = content
        else:
            action = "unknown"
            field = ""
            value = ""
        
        return {
            "transcription": transcription,
            "action": action,
            "field": field,
            "value": value,
            "success": True
        }
        
    except Exception as e:
        return {
            "transcription": "",
            "action": "error",
            "field": "",
            "value": "",
            "success": False,
            "error": str(e)
        }
