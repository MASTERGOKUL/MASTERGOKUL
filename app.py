from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import speech_recognition as sr
import time
from time import ctime
from gtts import gTTS
import playsound
import os
import io
import json
import random
import secrets
import base64
import wave

r = sr.Recognizer()  # initializing the recognizer
# def to_gsheet(file_name, char_array,changed_text):
#     # Load Google Sheets API credentials from the JSON file
#     scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
#     creds = ServiceAccountCredentials.from_json_keyfile_name('./palm-leaf-data-34f660ec63e1.json', scope)
#     client = gspread.authorize(creds)
#
#     # Open the Google Sheet by title
#     sheet = client.open('palm leaf predicted datas').sheet1
#
#     # Append the first row of the data
#     first = [ctime(),file_name,char_array[0],changed_text[0]]
#     sheet.append_row(first)
#     for i in range(1,len(char_array)):
#         remaining = ['','',char_array[i],changed_text[i]]
#         sheet.append_row(remaining)


def record_audio(audio_file):
    # if we can give the
    # there is a common exception it will through to us , it will show when it doesnot understand the input , like noise
    voice_data = None
    with sr.AudioFile(audio_file) as source:
        try:
            voice_data = r.recognize_google(source)  # it will give the audio to recognize_google -> there are more like this
        except sr.UnknownValueError:
            # assistant_speak("sorry, I did not get that,could you say it again")
            voice_data = "cant able to recognize"  # go to voice assistant in below
        except sr.RequestError:
            # assistant_speak("Sorry , my speech is down now")
            voice_data = None
    # os.remove(audio_file_path)
    return voice_data


def assistant_speak(audio_string):  # 🤔🤔if it is predefined and wont change for a while we can use recorded audio
    # time.sleep(1)
    tts = gTTS(text=audio_string, lang='en')  # gtts is used to convert the string to audio
    r = random.randint(1, 1000000)  # just picking up some random name here to make a name for the file
    audio_file = 'audio-' + str(r) + '.mp3'
    tts.save(
        'static/' + audio_file)  # it just return an audio we can only able to save that it does not have any speaker modules
    # playing sonund will play only in the server speaker so need to send it to the client

    # os.remove(audio_file) # it is not necessary to have the file so we can delete the saved audio
    return audio_file


app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # 🤔 Replace with a secure secret key

# responses = {"A1": "", "A2": "","A3": ""} # one bug 🐞🪲🪳 --> removed using session 🍳
@app.route('/')
def index():
    session['responses'] = {"Q1": "", "Q2": "", "Q3": ""}
    print(session['responses'])
    return render_template('index.html')


@app.route('/question/<int:question_number>', methods=['GET', 'POST'])
def question(question_number):
    if request.method == 'POST' and 'recognizedText' in request.form:
        print(request.form['recognizedText'])
    if request.method == 'POST' and 'answer' in request.form:
        answer = request.form['answer']
        played_audio_file_name = request.form['played_audio_file']
        # Retrieve responses from the session
        responses = session.get('responses', {})
        responses[f"Q{question_number}"] = answer
        os.remove('static/' + played_audio_file_name)

        # Save updated responses in the session
        session['responses'] = responses

        if question_number == 3:  # Assuming there are 3 questions # 👶👶 improve this
            return redirect(url_for('summary'))

        return redirect(url_for('question', question_number=question_number + 1))

    question_text = pre_defined_questions[f"Q{question_number}"]
    audio_file_name = assistant_speak(question_text)
    # # Check if speech recognition is requested
    # if 'speech_recognition' in request.form:
    #     voice_data = record_audio() #recognize speech
    #     if voice_data is not None:
    #         return redirect(url_for('question', question_number=question_number + 1))
    #     else:
    #         return render_template('question.html', question_number=question_number, question_text=question_text,
    #                                audio_file_name=audio_file_name)


    return render_template('question.html', question_number=question_number, question_text=question_text,
                           audio_file_name=audio_file_name)


@app.route('/summary', methods=['GET', 'POST'])
def summary():
    if request.method == 'POST':
        # You can process the submitted summary here or store it in the database
        session.pop('responses', None)
        return redirect(url_for('index'))
    responses = session.get('responses', {})
    print(responses)
    return render_template('summary.html',responses=responses,pre_defined_questions=pre_defined_questions)

@app.route('/submit-audio', methods=['POST'])
def submit_audio():
    # Access the submitted audio file using request.files
    audio_file = request.files['audio']

    # Process the audio file as needed
    # For example, you can save it to a specific folder
    # audio_file_path = 'audio.wav'
    # audio_file.save(audio_file_path)
    response = record_audio(audio_file)
    print(response)
    # Return a JSON response
    return jsonify({'message': 'Audio submitted successfully'})
if __name__ == "__main__":
    pre_defined_questions = {"Q1": "May I know your good Name ?", "Q2": "And how old are you?",
                             "Q3": "Where are you residing?"}
    # app.run(debug=True, host="10.10.145.212")
    app.run(debug=True) # run it in local host or the https due to mediaDevice only work on this types
