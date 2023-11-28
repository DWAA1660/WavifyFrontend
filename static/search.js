// static/script.js
function playSong(songId) {
    // Create an audio element
    var audio = document.createElement('audio');
    audio.controls = true;
    audio.autoplay = true;

    // Set the source of the audio element based on the songId
    audio.src = `http://node2.lunes.host:27237/song_from_yt/${songId}`;
    
    // Add more conditions for additional songs

    // Append the audio element to the container div
    var container = document.getElementById('audioPlayerContainer');
    container.innerHTML = ''; // Clear previous content
    container.appendChild(audio);
}
