import time
import speech_recognition as sr
import os
import requests
import pyttsx3

# Remplacez ceci par votre clé API Perplexity
API_KEY = "votre_clé_API"

# Fonction pour transcrire l'audio, envoyer à l'API Perplexity, et répondre par la parole
def listen_and_respond(after_prompt=True):
    """
    Transcrit l'audio, envoie à l'API Perplexity, et répond par la parole
    
    Args:
        after_prompt: bool, si la réponse vient directement après que l'utilisateur dit "Hey, Jarvis!" ou non
    """
    start_listening = False

    with microphone as source:
        if after_prompt:
            recognizer.adjust_for_ambient_noise(source)
            print("Say 'Hey, Jarvis!' to start")
            audio = recognizer.listen(source, phrase_time_limit=5)
            try:
                transcription = recognizer.recognize_google(audio)
                if transcription.lower() == "hey jarvis":
                    start_listening = True
                else:
                    start_listening = False
            except sr.UnknownValueError:
                start_listening = False
        else:
            start_listening = True

        if start_listening:
            try:
                print("Listening for question...")
                audio = recognizer.record(source, duration=5)
                transcription = recognizer.recognize_google(audio)
                print(f"Input text: {transcription}")

                # Envoyer le texte transcrit à l'API Perplexity
                url = "https://api.perplexity.ai/chat/completions"
                payload = {
                    "model": "llama-3.1-sonar-large-128k-chat",
                    "messages": [
                        {
                            "role": "system",
                            "content": "Be precise and concise."
                        },
                        {
                            "role": "user",
                            "content": transcription
                        }
                    ],
                    "max_tokens": 150,
                    "temperature": 0.2,
                    "top_p": 0.9,
                    "return_citations": True,
                    "search_domain_filter": ["perplexity.ai"],
                    "return_images": False,
                    "return_related_questions": False,
                    "search_recency_filter": "month",
                    "top_k": 0,
                    "stream": False,
                    "presence_penalty": 0,
                    "frequency_penalty": 1
                }
                headers = {
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                }

                # Effectuer la requête POST
                response = requests.post(url, json=payload, headers=headers)

                # Vérifier la réponse de l'API
                if response.status_code == 200:
                    response_json = response.json()
                    response_text = response_json.get('choices', [{}])[0].get('message', {}).get('content', 'Pas de réponse.')
                else:
                    response_text = f"Erreur {response.status_code} : {response.text}"

                # Imprimer la réponse de l'API
                print(f"Response text: {response_text}")

                # Dire la réponse
                engine.say(response_text)
                engine.runAndWait()

            except sr.UnknownValueError:
                print("Unable to transcribe audio")

# Paramètres du moteur pyttsx3
engine = pyttsx3.init()
engine.setProperty('rate', 150) 
engine.setProperty('voice', 'english_north')

recognizer = sr.Recognizer()
microphone = sr.Microphone()

# Première question
first_question = True

# Initialiser last_question_time à l'heure actuelle
last_question_time = time.time()

# Définir le seuil pour le temps écoulé avant de nécessiter "Hey, Jarvis!" à nouveau
threshold = 60  # 1 minute

while True:
    if (first_question == True) or (time.time() - last_question_time > threshold):
        listen_and_respond(after_prompt=True)
        first_question = False
    else:
        listen_and_respond(after_prompt=False)

# Peut être exécuté dans le terminal avec la commande suivante pour supprimer les avertissements :
# python jarvis.py 2>/dev/null
