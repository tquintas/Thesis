import mido
import rtmidi
import random2 as _r
import threading
import time
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
mido.set_backend('mido.backends.rtmidi')
global outport
outport = mido.open_output('WebApp MIDI', virtual=True)
print("Virtual MIDI port created. Name:", outport.name)

def stopNote(midi, sec):
    time.sleep(sec)
    msg = mido.Message('note_off', note=midi, velocity=0)
    outport.send(msg)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/midi_note_on", methods=["POST"])
def NoteOn():
    data = request.get_json()
    midi = data.get('note_on', None)
    vel = data.get('velocity', None)
    rel = _r.randint(10, 5000) / 1000
    if midi is not None and vel is not None:
        msg = mido.Message('note_on', note=midi, velocity=vel)
        outport.send(msg)
        threading.Thread(target=lambda: stopNote(midi, rel)).start()
        json = {'note_on': midi, 'velocity':vel, 'release': rel}
        print(json)
        return jsonify(json)
    else:
        return jsonify({'error': 'No number provided'}), 400
    
@app.route("/midi_note_off", methods=["POST"])
def NoteOff():
    data = request.get_json()
    midi = data.get('note_off', None)
    if midi is not None:
        msg = mido.Message('note_off', note=midi, velocity=0)
        outport.send(msg)
        return jsonify({'note_off': midi, 'velocity':0})
    else:
        return jsonify({'error': 'No number provided'}), 400

if __name__ == "__main__":
    app.run(host='0.0.0.0')
