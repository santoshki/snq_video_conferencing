// Initialize Socket.IO
const socket = io();

// Extract room ID from URL
const roomId = window.location.pathname.split("/")[2];

// DOM references
const localVideo = document.getElementById("localVideo");
const remoteVideo = document.getElementById("remoteVideo");
const chatInput = document.getElementById("chatInput");
const sendBtn = document.getElementById("sendBtn");
const messages = document.getElementById("messages");

// Join the room when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
    socket.emit("join", { room: roomId });

    // Request access to webcam and microphone
    navigator.mediaDevices.getUserMedia({ video: true, audio: true })
        .then(stream => {
            localVideo.srcObject = stream;
            window.localStream = stream;

            // Debug logs to confirm stream assignment
            console.log("Media stream initialized:", stream);
            console.log("Audio tracks:", stream.getAudioTracks());
            console.log("Video tracks:", stream.getVideoTracks());
        })
        .catch(error => {
            console.error("Error accessing media devices:", error);
            alert("Please allow access to camera and microphone.");
        });
});

// Handle screen sharing
function startScreenShare() {
    navigator.mediaDevices.getDisplayMedia({ video: true })
        .then(screenStream => {
            localVideo.srcObject = screenStream;
            window.screenStream = screenStream;
        })
        .catch(err => {
            console.error("Screen share error:", err);
            alert("Screen share permission denied.");
        });
}

// Handle sending chat message
sendBtn.addEventListener("click", () => {
    const message = chatInput.value.trim();
    if (message) {
        socket.emit("message", {
            room: roomId,
            text: `You: ${message}`
        });

        // Also display the message locally
        appendMessage(`You: ${message}`);
        chatInput.value = "";
    }
});

// Receive messages from server
socket.on("message", (data) => {
    if (data.text) {
        appendMessage(data.text);
    }
});

// Append message to chat UI
function appendMessage(msg) {
    const div = document.createElement("div");
    div.textContent = msg;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
}

// Toggle Audio On/Off
function toggleAudio() {
    const audioTrack = window.localStream?.getAudioTracks()[0];
    if (audioTrack) {
        audioTrack.enabled = !audioTrack.enabled;
        const btn = document.getElementById('muteAudioBtn');
        if (btn) {
            btn.innerText = audioTrack.enabled ? "🔇 Mute Audio" : "🔈 Unmute Audio";
        }
        console.log("Audio toggled:", audioTrack.enabled);
    } else {
        console.warn("No audio track found.");
    }
}

// Toggle Video On/Off
function toggleVideo() {
    console.log("toggleVideo called");
    const videoTrack = window.localStream?.getVideoTracks()[0];
    console.log("Video track:", videoTrack);

    if (videoTrack) {
        videoTrack.enabled = !videoTrack.enabled;
        const btn = document.getElementById('disableVideoBtn');
        if (btn) {
            btn.innerText = videoTrack.enabled ? "📷 Disable Video" : "📸 Enable Video";
        }
        console.log("Video toggled:", videoTrack.enabled);
    } else {
        console.warn("No video track found.");
    }
}

function exitMeeting() {
    if (localStream) {
        localStream.getTracks().forEach(track => track.stop());
    }
    window.location.href = "/home";
}