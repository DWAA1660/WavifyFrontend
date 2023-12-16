// static/script.js
var queue = []
var playedSongs = []
function almostPlaySong(songId, title) {
    console.log(title);
    var player = document.getElementById("dynamicplayer");
    if (player == null ) {
        playSong(songId, title);
    }
    else{
        queue.push({"yt_id": songId, "title": title});
    }
}

function playNextSong(reversed){
    if (!reversed) {
    var item = queue.shift();
    console.log(item);
    playSong(item.yt_id, item.title);
    }
    else{
        var song_item = playedSongs[playedSongs.length - 1]
        playSong(song_item.yt_id, song_item.title);
    }
}

function playSong(songId, title) {
    // Create an audio element
    console.log(title);
    var audio = document.createElement('audio');
    audio.controls = true;
    audio.autoplay = true;
    audio.src = `https://musicbackend.lunes.host/song_from_yt/${songId}`;
    audio.id = "dynamicplayer"
    
    // Add a loop button
    var loopButton = document.createElement('button');
    var titleElement = document.createElement('h4');
    titleElement.textContent = title;
    loopButton.textContent = 'Loop Off';
    loopButton.onclick = function() {
        audio.loop = !audio.loop;
        loopButton.textContent = audio.loop ? 'Loop: On' : 'Loop: Off';
    };
    
    var skipButton = document.createElement('button');
    skipButton.textContent = 'Skip';
    skipButton.onclick = function() {
        playedSongs.push({"yt_id": songId, "title": title});
        playNextSong();
    }
    var rewindButton = document.createElement('button');
    rewindButton.textContent = 'Rewind';
    rewindButton.onclick = function() {
        playNextSong(true);
    }

    audio.addEventListener('ended', function() {
        // If loop is enabled, start the song over
        playedSongs.push({"yt_id": songId, "title": title});
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
    container.innerHTML = '';
    container.appendChild(titleElement);
    container.appendChild(audio);
    container.appendChild(loopButton);
    container.appendChild(skipButton);
    container.appendChild(rewindButton);

}

