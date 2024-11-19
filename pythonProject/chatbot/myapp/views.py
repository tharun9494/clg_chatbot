from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import os

# Load chatbot responses from JSON
json_path = os.path.join(settings.BASE_DIR, 'static', 'data.json')

# Try to load the JSON file, with proper error handling
try:
    with open(json_path, 'r') as file:
        responses = json.load(file)
except FileNotFoundError:
    responses = {"faqs": []}  # Fallback if the file doesn't exist
except json.JSONDecodeError:
    responses = {"faqs": []}  # Fallback if there's an issue with the JSON structure


@csrf_exempt
def chatbot_response(request):
    if request.method == 'POST':
        try:
            user_input = json.loads(request.body).get('message', '').lower()

            if not user_input:
                return JsonResponse({"response": "Please ask a valid question."}, status=400)

            # Search the JSON for a partially matching question or tag
            matched_response = "Sorry, I don't understand that."
            for faq in responses.get('faqs', []):
                if user_input in faq['question'].lower() or any(
                        tag.lower() in user_input for tag in faq.get('tags', [])):
                    matched_response = f"Category: {faq['category']}\nAnswer: {faq['answer']}"
                    if 'link' in faq:
                        matched_response += f"\nMore info: {faq['link']}"
                    break

            # Return response with \n line breaks
            return JsonResponse({"response": matched_response})

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid input format. Please send a valid JSON request."}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)