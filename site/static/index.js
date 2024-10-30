var oct;

function sendNote(midi, vel) {
    $.ajax({
        url: '/midi_note_on',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({note_on: midi+(12*oct), velocity: vel}),
        success: function(res) {
            console.log(res)
        }
    })
}

function stopNote(midi) {
    $.ajax({
        url: '/midi_note_off',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({note_off: midi+(12*oct)}),
        success: function(res) {
            console.log(res)
        }
    })
}

$(function() {
    oct = Math.floor(Math.random() * 7) - 3
    $(".bg-white").on("touchstart", function(event) {
        var touch = event.originalEvent.touches[0];
        var y = touch.clientY;
        var rect = this.getBoundingClientRect();
        var vel = Math.floor(((y - rect.top) / rect.height) * 127)
        const midi = Number(this.dataset.note);
        sendNote(midi, vel);
    })
    $(".bg-dark").on("touchstart", function(event) {
        var touch = event.originalEvent.touches[0];
        var y = touch.clientY;
        var rect = this.getBoundingClientRect();
        var vel = Math.floor(((y - rect.top) / rect.height) * 127)
        const midi = Number(this.dataset.note);
        sendNote(midi, vel);
    })
})