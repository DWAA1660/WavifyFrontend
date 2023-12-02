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
    var audio = document.createElement('audio');
    audio.controls = true;
    audio.autoplay = true;
    audio.src = `https://musicbackend.lunes.host/song_from_yt/${songId}`;
    audio.id = "dynamicplayer"

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
        playedSongs.push(songId);
        if (audio.loop) {
            audio.currentTime = 0;
            audio.play();
        }
        else {
            if (queue.length > 0){
                playNextSong()
            }
        }
    });

    var container = document.getElementById('audioPlayerContainer');
    container.innerHTML = '';
    container.appendChild(audio);
    container.appendChild(loopButton);
    container.appendChild(skipButton);
    container.appendChild(rewindButton);
}

