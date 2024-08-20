import google.generativeai as genai
import speech_recognition as sr
import pyttsx3
from config import config

# Initialize the speech recognition engine
recognizer = sr.Recognizer()

# Initialize the TTS engine
tts_engine = pyttsx3.init()

# Configure the generative AI model with the API key from environment variables
genai.configure(api_key=config.GEMINI_API_KEY)

# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction=config.ARG_MODEL_CONFIG,
)

# Start a chat session with the generative AI model
chat = model.start_chat(history=[])

def call_gemini_api(prompt):
    response = chat.send_message(prompt)
    return response.text

def speak(text):
    tts_engine.say(text)
    tts_engine.runAndWait()
    print(text)  # Also print the output for debugging

def listen():
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Listening...")
        audio = recognizer.listen(source)

        try:
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I did not catch that.")
            return listen()
        except sr.RequestError:
            print("Could not request results from Google Speech Recognition service.")
            return ""

def start_conversation():
    session = {
        'step': 0,
        'names': [],
        'subtopics': [],
        'discussion': []
    }
    return session, "Hi, thanks for calling Dr. Jarvis AI. I'm here to mediate and guide you two through your discussion to keep it on track. May I get both of your names?"

def handle_response(session, message):
    step = session['step']
    response = ""

    if step == 0:
        session['names'] = message.split(' and ')
        session['step'] = 1
        response = f"Hi {session['names'][0]} and {session['names'][1]}, would you like to get started with the argument session? (yes or no)"

    elif step == 1:
        if 'yes' in message.lower():
            session['step'] = 2
            response = ("Okay. This will be a 9 step process, but by just starting and recognizing, "
                        "you've already accomplished 80% of the work. Let's finish the other 20%. "
                        "Go grab a writing or typing utensil, and then say 'done'.")
        else:
            response = "What would you like to do instead?"

    elif step == 2:
        if 'done' in message.lower():
            session['step'] = 3
            response = ("Great! The first step is to write down what happened, according to your own perspectives. "
                        "How do you feel? Why is this an issue? Try not to talk during this time. "
                        "Let me know when you're done.")

    elif step == 3:
        if 'done' in message.lower():
            session['step'] = 4
            response = ("Now, write down the answer to the question: What do you want from this argument? "
                        "What would happen that would make it successful? Let me know when you both are done.")

    elif step == 4:
        if 'done' in message.lower():
            session['step'] = 5
            response = ("Please share what you wrote. Based on that, I'll help create a list of subtopics "
                        "for you to discuss. Are there any additional subtopics you'd like to add?")

    elif step == 5:
        # Use AI to generate subtopics
        prompt = f"Based on the following input: '{message}', generate a list of subtopics for discussion."
        response = call_gemini_api(prompt)
        print("Let's discuss the following subtopics and figure out a solution to the argument :\n")
        session['subtopics'] = response.split('\n')
        session['step'] = 6
        response += "\nNow we're going to discuss the first subtopic. Each person alternates speaking for 30 seconds, although you can end your turn early if you want. Let's begin!"

    elif step == 6:
        if 'done' in message.lower():
            session['subtopics'].pop(0)
            if session['subtopics']:
                response = f"Let's move on to the next subtopic: {session['subtopics'][0]}. Same process."
            else:
                session['step'] = 7
                response = "Great! You've discussed all the subtopics. Now, let's talk about solutions."

    elif step == 7:
        session['step'] = 8
        response = ("Please share your solutions. I can also provide recommendations if you'd like. "
                    "Let me know when you're ready to wrap up.")

    elif step == 8:
        # Use AI to provide recommendations
        prompt = "Based on the following solutions: '{message}', provide recommendations for improvement and conflict resolution."
        response = call_gemini_api(prompt)
        session['step'] = 9
        response += "\nThanks for coming on here. I'm glad we were able to work things out. If there's anything else, I'm here to help."

    elif step == 9:
        if 'no resolution' in message.lower() or 'angry' in message.lower():
            response = ("It seems like things are still a bit tense. Let's take a moment to calm down. "
                        "I'm here to talk if you need me. If all else fails, I'll document this session "
                        "and forward it to a counselor.")
        else:
            response = "Thanks again! Have a great day."

    return session, response

# Example Usage
session, response = start_conversation()
# speak(response)
print(response)

while session['step'] < 9:
    # user_input = listen()
    user_input = input("> ")
    session, response = handle_response(session, user_input)
    # speak(response)
    print(response)

print("\n",session)
