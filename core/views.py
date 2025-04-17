from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from .forms import StudentForm
from .models import Student
import requests
import os
import openai
import json

# Function to handle chat with DeepSeek
def chat_with_deepseek(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message')

        # Replace this with your DeepSeek API call logic
        response = openai.ChatCompletion.create(
            model="gpt-4",  # or "deepseek-chat" based on your model
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message},
            ]
        )

        bot_reply = response['choices'][0]['message']['content']
        return JsonResponse({'reply': bot_reply})

# Home page view to handle form submissions and chat requests
def index(request):
    form = StudentForm()
    response = None
    error = None

    if request.method == 'POST':
        if 'submit_form' in request.POST:
            form = StudentForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('index')

        elif 'submit_chat' in request.POST:
            message = request.POST.get('message', '').strip()
            if message:
                api_response = query_deepseek(message)
                if api_response.get("error"):
                    error = api_response["error"]
                else:
                    response = api_response["reply"]
            else:
                error = "Prompt is empty"

    students = Student.objects.all()
    return render(request, 'index.html', {
        'form': form,
        'students': students,
        'response': response,
        'error': error,
    })

@csrf_exempt
def chat_api(request):
    """
    Chat API endpoint for frontend JavaScript: handles POST requests and returns a response from DeepSeek.
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        message = data.get('message', '').strip()

        if not message:
            return JsonResponse({'error': 'Prompt is empty'}, status=400)

        api_response = query_deepseek(message)
        if api_response.get("error"):
            return JsonResponse({'error': api_response["error"]}, status=400)
        return JsonResponse({'response': api_response["reply"]})

    return JsonResponse({'error': 'Invalid request method. Use POST.'}, status=405)

# Function to interact with the DeepSeek API and return a reply or error
def query_deepseek(prompt):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return {"error": "API key not found. Please set DEEPSEEK_API_KEY in environment variables."}

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    data = {
        "model": "deepseek-chat",  # or any other model required by DeepSeek
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        res_json = response.json()

        choices = res_json.get("choices")
        if choices and isinstance(choices, list) and "message" in choices[0]:
            return {"reply": choices[0]["message"]["content"]}
        else:
            return {"error": "Unexpected response format from DeepSeek API."}

    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}

    except Exception as e:
        return {"error": f"Internal error: {str(e)}"}
