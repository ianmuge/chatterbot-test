from flask import Flask, render_template, session
import os
from flask_socketio import SocketIO, send, emit
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer, ChatterBotCorpusTrainer, UbuntuCorpusTrainer

app = Flask(__name__)
app.config['SECRET_KEY'] = "a-secret-key"

socketio = SocketIO(app)
total_users = 0

chatbot = ChatBot(
    "Kim",
    storage_adapter='chatterbot.storage.MongoDatabaseAdapter',
    database_uri='mongodb://localhost:27017/chatterbot',
    logic_adapters=[
        'chatterbot.logic.MathematicalEvaluation',
        'chatterbot.logic.TimeLogicAdapter',
        'chatterbot.logic.UnitConversion',
        # 'chatterbot.logic.BestMatch',
        {
            'import_path': 'chatterbot.logic.BestMatch',
            'default_response': 'I am sorry, but I do not understand.',
            'maximum_similarity_threshold': 0.90
        }
    ],
    preprocessors=[
        'chatterbot.preprocessors.clean_whitespace',
        "chatterbot.preprocessors.unescape_html"
    ],

)
trainer = ListTrainer(chatbot)
trainer.train([
    "Hello there?",
    "General Kenobi!",
])
# trainer = ChatterBotCorpusTrainer(chatbot)
# trainer.train(
#     "chatterbot.corpus.english"
# )
trainer = UbuntuCorpusTrainer(chatbot)
trainer.train()


@app.route('/')
def home():
    return render_template('index.html')


@socketio.on('connect')
def on_connect():
    global total_users
    total_users += 1
    print(f'Client connected!| Total users: {total_users}')


@socketio.on('disconnect')
def on_disconnect():
    global total_users
    total_users -= 1
    print(f'Client disconnected!| Total users: {total_users}')


@socketio.on('new_message')
def on_message(data):
    global total_users
    message = data["message"]
    print(f'{session["username"]}:{message}')
    emit('receive_message', {"message": message, "username": session["username"]}, broadcast=True,
         namespace="/")
    if total_users < 2 or "@bot" in data["message"]:
        message = message.replace('@bot', '')
        print(message)
        resp = chatbot.get_response(message)
        emit('receive_message', {"message": str(resp), "username": chatbot.name}, broadcast=True,
             namespace="/")


@socketio.on('change_username')
def on_change_username(data):
    session['username'] = data['username']
    print(f'Anonymous registered as {session["username"]}')
    emit('receive_message', {"message": f'{session["username"]} joined the chat', "username": session["username"]},
         broadcast=True, namespace="/", include_self=False)


#
@socketio.on('typing')
def on_typing():
    emit('typing', {"username": session["username"]}, broadcast=True, namespace="/", include_self=False)


if __name__ == '__main__':
    # app.run(threaded=True,port=5000)
    socketio.run(app, manage_session=True, logger=True)
