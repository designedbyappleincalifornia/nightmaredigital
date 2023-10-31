import json
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import requests

# Initialize your system prompt here
base_system_prompt = "You are a powerful AI called Urgo"
dynamic_system_prompt = base_system_prompt
past_system_prompts = ""

# Your OpenAI API key here
OPENAI_KEY = "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"


@csrf_exempt
def chat_handler(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))

        user_message = data.get('message', '')

        messages = [
            {"role": "system", "content": dynamic_system_prompt},
            {"role": "user", "content": user_message}
        ]

        print(f"Sending these messages to OpenAI: {messages}") #Debug print 1

        # Make API call here
        response_data = make_openai_request(messages)

        print(f"Received this from OpenAI: {response_data}")  # Debug print 2

        bot_message = response_data["choices"][0]["message"]["content"]

        return JsonResponse({'message': bot_message})

    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=400)


def home(request):
    return render(request, 'home.html')


def make_openai_request(messages):
    headers = {
        "Authorization": f"Bearer {OPENAI_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "gpt-3.5-turbo",
        "messages": messages,
        "temperature": 0.9,
        "stream": False
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)

    print(f"API response: {response.json()}")  # Debug print 3

    if response.status_code != 200:
        raise Exception(f"OpenAI request failed: {response.json()['error']['message']}")

    return response.json()


# Update the dynamic system prompt
def update_system_prompt(user_history):
    global dynamic_system_prompt, past_system_prompts

    messages = [
        {"role": "system", "content": dynamic_system_prompt},
        {"role": "user",
         "content": f'Based on the user\'s history of saying "{user_history}", tell me how to subtly update my system prompt.'}
    ]

    advice_data = make_openai_request(messages)
    advice = advice_data["choices"][0]["message"]["content"]

    # Update past and dynamic prompts
    past_system_prompts += advice
    dynamic_system_prompt = base_system_prompt + past_system_prompts
