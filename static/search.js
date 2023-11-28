// static/script.js
var queue = []
var playedSongs = []
function almostPlaySong(songId) {
    var player = document.getElementById("dynamicplayer");
    if (player == null ) {
        playSong(songId);
    }
    else{
        queue.push(songId);
    }
}

function playNextSong(reversed){
    if (!reversed) {
    playSong(queue.shift());
    }
    else{
        playSong(playedSongs[playedSongs.length - 1])
    }
}

function playSong(songId) {
    // Create an audio element
    var audio = document.createElement('audio');
    audio.controls = true;
    audio.autoplay = true;
    audio.src = `http://node2.lunes.host:27237/song_from_yt/${songId}`;
    audio.id = "dynamicplayer"
    
    // Add a loop button
    var loopButton = document.createElement('button');
    loopButton.textContent = 'Loop Off';
    loopButton.onclick = function() {
        audio.loop = !audio.loop;
        loopButton.textContent = audio.loop ? 'Loop: On' : 'Loop: Off';
    };
    
    var skipButton = document.createElement('button');
    skipButton.textContent = 'Skip';
    skipButton.onclick = function() {
        playedSongs.push(songId);
        playNextSong();
    }
    var rewindButton = document.createElement('button');
    rewindButton.textContent = 'Rewind';
    rewindButton.onclick = function() {
        playNextSong(true);
    }

    audio.addEventListener('ended', function() {
        // If loop is enabled, start the song over
        playedSongs.push(songId);
        if (audio.loop) {
            audio.currentTime = 0;
            audio.play(); // Restart the audio
        }
        else {
            if (queue.length > 0){
                playNextSong()
            }
        }
    });

    // Create a container div for both the audio element and loop button
    var container = document.getElementById('audioPlayerContainer');
    container.innerHTML = ''; // Clear previous content
    container.appendChild(audio);
    container.appendChild(loopButton);
    container.appendChild(skipButton);
    container.appendChild(rewindButton);
}

