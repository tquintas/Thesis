import mido

inports = mido.get_input_names()
print(inports)

with mido.open_input('Arturia KeyStep 32') as inport:
    for msg in inport:
        print(msg)