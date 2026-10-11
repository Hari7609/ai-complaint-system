import speech_recognition as sr
import pyttsx3
import ollama

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 180) # Speed of speech

def speak(text):
    print(f"Jarvis: {text}")
    engine.say(text)
    engine.runAndWait()

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("\nListening...")
        r.adjust_for_ambient_noise(source, duration=0.5)
        audio = r.listen(source)
    try:
        query = r.recognize_google(audio)
        print(f"User: {query}")
        return query
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        speak("Network error connecting to speech recognition service.")
        return ""

def query_ai(prompt):
    # Using a local model via Ollama (e.g., Llama 3)
    response = ollama.chat(model='llama3', messages=[
        {'role': 'system', 'content': 'You are JARVIS, a highly intelligent, sarcastic, and efficient AI assistant. Keep responses concise and conversational.'},
        {'role': 'user', 'content': prompt},
    ])
    return response['message']['content']

if __name__ == "__main__":
    speak("Systems online. At your service, sir.")
    
    while True:
        command = listen()
        if command:
            if "shutdown" in command.lower() or "exit" in command.lower():
                speak("Shutting down systems. Goodbye.")
                break
            
            # Get response from the AI model
            ai_reply = query_ai(command)
            speak(ai_reply)