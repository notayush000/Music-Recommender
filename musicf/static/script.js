try{
    document.getElementById("btn-back").onclick = () => {
        window.location.assign("http://127.0.0.1:5000/home")
    }
}
catch (err){
    console.log(err)
}

try{
    document.getElementById("search_song").onclick = () => {
        const song_name = document.getElementById("search_name").value
        fetch("http://127.0.0.1:5000/api/search/"+song_name)
        .then(res => res.json())
        .then(d => {
            const headSong = document.querySelector(".top-song-details")
            headSong.innerHTML = `<h4>${d.results[0].name}</h4>
                                  <p>${d.results[0].artists}</p>`
            const mainSongImg = document.querySelector(".song-img img")
            mainSongImg.src = `${d.results[0].image}`
            const songArea = document.querySelector(".song-area")
            songArea.innerHTML += `
                <a href="/play" onclick="playMusic(['${d.results[0].name}', '${d.results[0].image}', '${d.results[0].uri}', '${d.results[0].duration}','${d.results[0].artists}'])">
            `

            const ulTag = document.querySelector(".songs ul")
            for (let i = 1; i < d.results.length; i++){
                const time = getTiming(d.results[i].duration);
                let liTag = `
                    <li>
                        <a href="/play" onclick="playMusic(['${d.results[i].name}', '${d.results[i].image}', '${d.results[i].uri}', '${d.results[i].duration}','${d.results[i].artists}'])">
                            <div class="search-details">
                                <img src="${d.results[i].image}" alt="" height="40px" width="40px">
                                <div class="result-details">
                                    <h5>${d.results[i].name}</h5>
                                    <p>${d.results[i].artists}</p>
                                </div>
                            </div>
                            <div class="search-time">${time}</div>
                        </a>
                    </li>
                `
                ulTag.insertAdjacentHTML("beforeend", liTag)
            }
            document.getElementById("search-area").style.display = "none";
            document.getElementById("cgp").style.display = "block";
        })
    }
}
catch(err){
    console.log(err)
}

function getTiming(time_in_ms){
    let currentMin = Math.floor(Number((time_in_ms/1000) / 60));
    let currentSec = Math.floor(Number(((time_in_ms/1000)) % 60));
    if (currentSec < 10){
        currentSec = `0${currentSec}`;
    }
    const time = `${currentMin}:${currentSec}`
    return time
}

function playMusic(list){
    window.localStorage.setItem("duration", Math.round(list[3] / 1000));
    let current_playing = {
        name: list[0],
        img_url: list[1],
        uri: list[2],
        artists: list[4],
        duration: list[3]
    }
    window.localStorage.setItem("current_playing", JSON.stringify(current_playing)) 
    fetch("http://127.0.0.1:5000/api/get_play", {
        method: 'POST',
        body: JSON.stringify({
            name: list[0],
            img_url: list[1],
            uri: list[2],
            artists: list[4],
            duration: list[3]
        }),
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        }
    })
}

function _pauseMusic(){
    document.querySelector(".player").classList.remove("paused");
    stopTimer();
    stopPlaying();
    document.querySelector("#play-pause").querySelector("i").innerText = "play_arrow";
}

function _playMusic(){
    document.querySelector(".player").classList.add("paused");
    startResumePlaying();
    startTimer();
    document.querySelector("#play-pause").querySelector("i").innerText = "pause";
}

try{
    document.getElementById("play-pause").addEventListener("click", () => {
        const isMusicPaused = document.querySelector(".player").classList.contains("paused");
        isMusicPaused ? _pauseMusic() : _playMusic();
    })
}
catch(err){
    console.log(err)
}

function stopPlaying(){
    fetch("http://127.0.0.1:5000/api/pause")
    .then(res => res.json())
    .then(d => {
        let progress = window.localStorage.getItem("progress_ms");
        if (progress == null){
            window.localStorage.setItem("progress_ms", d);
        }
        else{
            window.localStorage.progress_ms = d;
        }
    })
}

function startResumePlaying(){
    let data = []
    if (musicIdx == -1){
        data[0] = JSON.parse(window.localStorage.getItem('current_playing'))['uri']
    }
    else{
        data[0] = queuedMusic[musicIdx].uri
    }

    fetch("http://127.0.0.1:5000/api/play-resume", {
        method: 'POST',
        body: JSON.stringify({
            uri: data,
            progress: Number(window.localStorage.getItem("progress_ms"))
        }),
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        }
    })
}

function startTimer(){
    const timer = setInterval(updateProgressBar, 1000);
    window.localStorage.setItem("timeObj", timer);
}

function stopTimer(){
    clearTimeout(window.localStorage.getItem("timeObj"));
}

function updateProgressBar(){
    let current_time = window.localStorage.getItem("current_time");
    if (current_time == null){
        window.localStorage.setItem("current_time", 0)
        current_time = 0
    }
    let progressWidth = (current_time / Number(window.localStorage.duration)) * 100;
    document.querySelector(".progress-bar").style.width = `${progressWidth}%`
    window.localStorage.current_time = Number(window.localStorage.current_time) + 1;

    let currentMin = Math.floor(Number(window.localStorage.current_time / 60));
    let currentSec = Math.floor(Number(window.localStorage.current_time % 60));
    if (currentSec < 10){
        currentSec = `0${currentSec}`;
    }
    document.querySelector(".current").innerText = `${currentMin}:${currentSec}`;

    if (Number(window.localStorage.current_time) + 1 == Number(window.localStorage.duration)){
        _pauseMusic();
        window.localStorage.current_time = 0;
        window.localStorage.progress_ms = 0;
    }
}

const musicList = document.querySelector(".music-list")
const showMoreMusicBtn = document.querySelector("#more-music")
const closeMoreMusicBtn = musicList.querySelector("#close")

showMoreMusicBtn.addEventListener("click", () => {
    musicList.classList.toggle("show");
})

closeMoreMusicBtn.addEventListener("click", () => {
    showMoreMusicBtn.click();
})

const queuedMusic = []
let queueIdx = 0
let musicIdx = -1

function showRecommendations(){
    let current_song_details = window.localStorage.getItem("current_playing")
    let current = JSON.parse(current_song_details)
    fetch("http://127.0.0.1:5000/api/get_recommendations/"+current.name)
    .then(res => res.json())
    .then(d => {
        const ulTag = document.querySelector(".recommendations ul")
        for (let i = 0; i < d.results.length; i++){
            const time = getTiming(d.results[i].duration);
            let liTag = `
                <li>
                    <div class="search-details">
                        <img src="${d.results[i].image}" alt="" height="40px" width="40px">
                        <div class="result-details">
                            <h5>${d.results[i].name}</h5>
                            <p>${d.results[i].artists}</p>
                        </div>
                    </div>
                    <div class="extras">
                        <span id="song-${i}" class="material-symbols-outlined" onclick="addToQueue(${i}, ['${d.results[i].name.replace("'", "")}', '${d.results[i].image}', '${d.results[i].uri}', '${d.results[i].duration}','${d.results[i].artists}'])">queue_music</span>
                        <div class="search-time">${time}</div>
                    </div>
                </li>
            `
            console.log(liTag)
            ulTag.insertAdjacentHTML("beforeend", liTag);
        }
    })
    
    document.querySelector(".recommendations").classList.toggle("show")
    if (document.getElementById("rccBtn").innerText === "Show Recommendations"){
        document.getElementById("rccBtn").innerText = "Hide Recommendations";
    }
    else{
        document.getElementById("rccBtn").innerText = "Show Recommendations";
        
    }
}


function addToQueue(idx, list){
    const ulTag = musicList.querySelector("ul");
    let currentMin = Math.floor(Number((list[3]/1000) / 60));
    let currentSec = Math.floor(Number(((list[3]/1000)) % 60));
    if (currentSec < 10){
        currentSec = `0${currentSec}`;
    }
    queuedMusic[queueIdx] = {
        name: list[0],
        img_url: list[1],
        uri: list[2],
        duration: list[3],
        artists: list[4]
    }
    queueIdx++;
    let liTag = `
        <li>
            <div class="row">
                <span>${list[0]}</span>
                <p>${list[4]}</p>
            </div>
            <span class="audio-duration">${currentMin}:${currentSec}</span>
        </li>
    `
    ulTag.insertAdjacentHTML("beforeend", liTag);
    const tarSpan = document.getElementById(`song-${idx}`)
    tarSpan.innerText = playlist_add_check
    console.log(queuedMusic)
}

try{
    document.getElementById("next").addEventListener("click", () => {
        nextMusic();
    })
}
catch(err){
    console.log(err)
}

try{
    document.getElementById("prev").addEventListener("click", () => {
        prevMusic();
    })
}
catch(err){
    console.log(err)
}


function loadMusic(){
    window.localStorage.duration = Number(queuedMusic[musicIdx].duration / 1000);
    window.localStorage.current_time = 0;
    window.localStorage.progress_ms = 0;
    const playArea = document.querySelector(".player");
    const songName = playArea.querySelector(".show-area .song-details .song-name");
    const artistName = playArea.querySelector(".show-area .song-details .artists-name");
    const img = playArea.querySelector(".img-area img")
    const time_dur = playArea.querySelector(".show-area .progress-area .timer .duration")
    let currentMin = Math.floor(Number((queuedMusic[musicIdx].duration/1000) / 60));
    let currentSec = Math.floor(Number(((queuedMusic[musicIdx].duration/1000)) % 60));
    if (currentSec < 10){
        currentSec = `0${currentSec}`;
    }
    songName.innerText = queuedMusic[musicIdx].name;
    artistName.innerText = queuedMusic[musicIdx].artists;
    img.src = `${queuedMusic[musicIdx].img_url}`
    time_dur.innerText = `${currentMin}:${currentSec}`
    _pauseMusic();
    updateProgressBar();
}


function clearProgress(){
    window.localStorage.progress_ms = 0;
}

function nextMusic(){
    if ((musicIdx + 1) < queueIdx){
        musicIdx++;
        loadMusic();
        setTimeout(clearProgress, 5000);
    }
}

function prevMusic(){
    if((musicIdx - 1) >= 0){
        musicIdx--;
        loadMusic();
        setTimeout(clearProgress, 5000);
    }
}