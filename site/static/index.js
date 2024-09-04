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
    /*
    $(".bg-white").on("mousedown", function() {
        const midi = Number(this.dataset.note);
        sendNote(midi);
    })

    $(".bg-white").on("mouseup", function() {
        const midi = Number(this.dataset.note);
        stopNote(midi);
    })

    $(".bg-dark").on("mousedown", function() {
        const midi = Number(this.dataset.note);
        sendNote(midi);
    })

    $(".bg-dark").on("mouseup", function() {
        const midi = Number(this.dataset.note);
        stopNote(midi);
    })
    */
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
    /*
    $(".bg-white").on("touchend", function() {
        const midi = Number(this.dataset.note);
        stopNote(midi);
    })
    $(".bg-white").on("touchcancel", function() {
        const midi = Number(this.dataset.note);
        stopNote(midi);
    })
    
    $(".bg-dark").on("touchend", function() {
        const midi = Number(this.dataset.note);
        stopNote(midi);
    })
    $(".bg-dark").on("touchcancel", function() {
        const midi = Number(this.dataset.note);
        stopNote(midi);
    })
    */
})