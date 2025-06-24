import vertexai
from vertexai.generative_models import GenerativeModel, HarmCategory, HarmBlockThreshold
import json
import os
from typing import Optional, Dict, Any

def query_chat_endpoint(prompt: str, model_name: str = "gemini-2.0-flash") -> str:
    """
    Query the Gemini model endpoint with improved error handling and safety settings.
    
    Args:
        prompt (str): The prompt to send to the model
        model_name (str): The name of the Gemini model to use
        
    Returns:
        str: The model's response text or empty string if an error occurs
    """
    try:
        PROJECT_ID = ""
        vertexai.init(project=PROJECT_ID, location="europe-west1")

        # Initialize the model with safety settings
        model = GenerativeModel(model_name)
        
        # Configure safety settings
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }

        # Generate content with safety settings
        response = model.generate_content(
            prompt,
            safety_settings=safety_settings,
            generation_config={
                "temperature": 0.2,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 512,
            }
        )
        
        if response.candidates:
            return response.text
        else:
            print(f"No response generated for prompt: {prompt[:100]}...")
            return ''
            
    except Exception as e:
        print(f"Error in query_chat_endpoint: {str(e)}")
        print(f"Prompt that caused error: {prompt[:100]}...")
        return ''

def get_field_label(field_name: str, model_name: str = "gemini-2.0-flash") -> Optional[str]:
    """
    Get a label for a field using the Gemini model.
    
    Args:
        field_name (str): The name of the field to label
        model_name (str): The name of the Gemini model to use
        
    Returns:
        Optional[str]: The generated label or None if an error occurs
    """
    prompt = f"""
        Generate a short human readable label for the field '{field_name}' meant to be used in a Looker Explore.
        Only return the label text without any additional formatting or explanation.
        The label should be concise, descriptive, and suitable for a data exploration context.
        Avoid using technical jargon or abbreviations.

        If a field starts with m_, it is a metric, but that should not be included in the label.
        If a field starts with d_, it is a derived field but that should not be included in the label.
        if a field starts with is_ or has_ it is a boolean field, and that should be included in the label.
    """
    response = query_chat_endpoint(prompt, model_name)
    
    if response:
        return response.strip()
    else:
        return None