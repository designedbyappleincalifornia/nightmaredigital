import json
import os

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import requests

# Initialize your system prompt here
base_system_prompt = "You are a powerful AI called Urgo"
dynamic_system_prompt = base_system_prompt

# Initialize the conversation history
conversation_history = []

# Your OpenAI API key here
OPENAI_KEY = os.environ.get('OPENAI_KEY', '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')


@csrf_exempt
def chat_handler(request):
    global conversation_history  # Make sure to use the global variable

    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        user_message = data.get('message', '')

        # Add user's message to conversation history
        conversation_history.append({"role": "user", "content": user_message})

        messages = [
            {"role": "system", "content": dynamic_system_prompt},
            {"role": "user", "content": user_message}
        ]

        # Make API call here
        response_data = make_openai_request(messages)
        bot_message = response_data["choices"][0]["message"]["content"]

        # Add bot's message to conversation history
        conversation_history.append({"role": "assistant", "content": bot_message})

        # Update the system prompt
        update_system_prompt()

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
        "messages": messages
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)

    if response.status_code != 200:
        raise Exception(f"OpenAI request failed: {response.json()['error']['message']}")

    return response.json()


# Update the dynamic system prompt
def update_system_prompt():
    global dynamic_system_prompt, conversation_history

    # Ask the model for advice based on the entire conversation
    conversation_history.append({"role": "user",
                                 "content": f'Tell me how to subtly update my system prompt based on the entire conversation so far.'})

    advice_data = make_openai_request(conversation_history)
    advice = advice_data["choices"][0]["message"]["content"]

    # Extract the new system prompt suggestion from the advice
    start_idx = advice.find('"') + 1
    end_idx = advice.rfind('"')
    new_system_prompt = advice[start_idx:end_idx]

    # Combine base and new prompts
    dynamic_system_prompt = base_system_prompt + " " + new_system_prompt

    print(f"\033[91mUpdated system prompt: {dynamic_system_prompt}\033[0m")  # Print in red

    # Remove the last user's message asking for advice, to avoid confusion in future interactions
    conversation_history.pop()
