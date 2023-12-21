import json
from flask import Flask, session, render_template
from flask_sock import Sock
from wonderwords import RandomWord

def get_random_word():
    return RandomWord().word(word_min_length=5, word_max_length=5)

#Evualtion functions
def is_valid_word(word):
    return word.isalpha() and len(word) == 5

def does_exist(guess, guesses):
    return guess in guesses

def evaluation(guess, hidden_word):
    result = []
    for n in range(5):
        if guess[n] == hidden_word[n]:
            result.append(f"{guess[n]} ")
            continue
        elif guess[n] in hidden_word:
            result.append(f"{guess[n]}* ")
        else:
            result.append("/ ")
    return "".join(result)


#Flask app
app = Flask(__name__)
app.secret_key = "secret_key"
sock = Sock(app)

#Index Page
@app.route('/')
def index():
    session.clear()
    return render_template('index.html')

#Game Page
@app.route('/game')
def game():
    #Checking if the user has already started a game
    if 'hidden_word' in session:
        return render_template('game.html')
    # Code to start a new game
    session['hidden_word'] = get_random_word()
    print(session["hidden_word"])
    return render_template('game.html')

@sock.route("/evaluate_game")
def evaluate_game(sock):
    while True:
        data = sock.receive()
        if "written" not in session:
            session["written"] = []

        if not is_valid_word(data):
            sock.send("Invalid Word")
            continue

        if does_exist(data, session["written"]):
            sock.send("You have already written that word")
            continue

        if data == session["hidden_word"]:
            sock.send("You win!")
            session.clear()
            continue
        
        if len(session["written"]) >= 4:
            sock.send(f"You lose!&{session['hidden_word']}")
            print(session["hidden_word"])
            session.clear()
            continue

        session["written"].append(data)
        word = evaluation(data, session["hidden_word"])
        data = {
            "word": word,
            "written" : session["written"]
        }
        sock.send(json.dumps(data))

if __name__ == '__main__':
    app.run(debug=True)