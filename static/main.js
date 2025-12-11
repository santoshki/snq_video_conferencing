// Assuming your HTML template includes:// <script>const localUsername = "{{ username }}";</script>

// Initialize Socket.IO
const socket = io();

// Extract room ID from URL
const roomId = window.location.pathname.split("/")[2];

// DOM references
const localVideo = document.getElementById("localVideo");
const remoteVideo = document.getElementById("remoteVideo");
const localUsernamePlaceholder = document.getElementById("localUsername");
const remoteUsernamePlaceholder = document.getElementById("remoteUsername");
const chatInput = document.getElementById("chatInput");
const sendBtn = document.getElementById("sendBtn");
const messages = document.getElementById("messages");
const muteAudioBtn = document.getElementById("muteAudioBtn");
const disableVideoBtn = document.getElementById("disableVideoBtn");

let localStream = null; // store media stream here
let videoEnabled = false;
let audioEnabled = true;

// Join the room when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
 socket.emit("join", { room: roomId, username: localUsername });

 // Show username placeholder initially, hide video
 localVideo.style.display = "none";
 if (localUsernamePlaceholder) {
 localUsernamePlaceholder.textContent = localUsername;
 localUsernamePlaceholder.style.display = "flex";
 }
});

// Toggle Audio On/Off
function toggleAudio() {
 if (!localStream) {
 alert("Enable video (and allow camera access) first.");
 return;
 }

 const audioTrack = localStream.getAudioTracks()[0];
 if (audioTrack) {
 audioTrack.enabled = !audioTrack.enabled;
 audioEnabled = audioTrack.enabled;
 if (muteAudioBtn) {
 muteAudioBtn.innerText = audioTrack.enabled ? " Mute Audio" : " Unmute Audio";
 }
 console.log("Audio toggled:", audioTrack.enabled);
 } else {
 console.warn("No audio track found.");
 }
}

// Toggle Video On/Off with camera fully stopped when off
async function toggleVideo() {
 if (!localStream) {
 // Request permission and get media stream with audio + video
 try {
 localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
 window.localStream = localStream;

 // Set initial audio/video track states
 const audioTrack = localStream.getAudioTracks()[0];
 if (audioTrack) {
 audioTrack.enabled = true;
 audioEnabled = true;
 if (muteAudioBtn) {
 muteAudioBtn.innerText = " Mute Audio";
 }
 }

 const videoTrack = localStream.getVideoTracks()[0];
 if (videoTrack) {
 videoTrack.enabled = true;
 videoEnabled = true;
 }

 localVideo.srcObject = localStream;

 // Update UI for enabled video
 localVideo.style.display = "block";
 if (localUsernamePlaceholder) localUsernamePlaceholder.style.display = "none";

 if (disableVideoBtn) {
 disableVideoBtn.innerText = " Disable Video";
 }

 // Notify others
 socket.emit("video-toggle", {
 room: roomId,
 enabled: true,
 username: localUsername
 });

 console.log("Media stream initialized on video enable.");
 } catch (error) {
 console.error("Error accessing media devices:", error);
 alert("Please allow access to camera and microphone.");
 return;
 }
 } else {
 const videoTrack = localStream.getVideoTracks()[0];

 if (videoTrack) {
 if (videoEnabled) {
 // Stop and remove the video track to fully disable camera
 videoTrack.stop();
 localStream.removeTrack(videoTrack);

 videoEnabled = false;

 localVideo.style.display = "none";
 if (localUsernamePlaceholder) localUsernamePlaceholder.style.display = "flex";

 if (disableVideoBtn) {
 disableVideoBtn.innerText = " Enable Video";
 }

 // Notify others
 socket.emit("video-toggle", {
 room: roomId,
 enabled: false,
 username: localUsername
 });

 console.log("Video track stopped and disabled.");
 } else {
 // Enable video: request new video track
 try {
 const newStream = await navigator.mediaDevices.getUserMedia({ video: true });
 const newVideoTrack = newStream.getVideoTracks()[0];
 if (newVideoTrack) {
 localStream.addTrack(newVideoTrack);
 newVideoTrack.enabled = true;
 videoEnabled = true;

 localVideo.srcObject = localStream;
 localVideo.style.display = "block";
 if (localUsernamePlaceholder) localUsernamePlaceholder.style.display = "none";

 if (disableVideoBtn) {
 disableVideoBtn.innerText = " Disable Video";
 }

 // Notify others
 socket.emit("video-toggle", {
 room: roomId,
 enabled: true,
 username: localUsername
 });

 console.log("Video track added and enabled.");
 }
 } catch (err) {
 console.error("Error enabling video:", err);
 alert("Unable to enable camera.");
 }
 }
 } else {
 // No video track present at all — request it
 try {
 const newStream = await navigator.mediaDevices.getUserMedia({ video: true });
 const newVideoTrack = newStream.getVideoTracks()[0];
 if (newVideoTrack) {
 localStream.addTrack(newVideoTrack);
 newVideoTrack.enabled = true;
 videoEnabled = true;

 localVideo.srcObject = localStream;
 localVideo.style.display = "block";
 if (localUsernamePlaceholder) localUsernamePlaceholder.style.display = "none";

 if (disableVideoBtn) {
 disableVideoBtn.innerText = " Disable Video";
 }

 socket.emit("video-toggle", {
 room: roomId,
 enabled: true,
 username: localUsername
 });

 console.log("Video track added and enabled.");
 }
 } catch (err) {
 console.error("Error enabling video:", err);
 alert("Unable to enable camera.");
 }
 }
 }
}

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
 text: `${localUsername}: ${message}`
 });

 // Also display the message locally
 appendMessage(`${localUsername}: ${message}`);
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

// Listen for remote user's video toggle events
socket.on("video-toggle", (data) => {
 const { enabled, username } = data;
 if (!remoteVideo || !remoteUsernamePlaceholder) return;

 if (enabled) {
 remoteVideo.style.display = "block";
 remoteUsernamePlaceholder.style.display = "none";
 } else {
 remoteVideo.style.display = "none";
 remoteUsernamePlaceholder.style.display = "flex";
 remoteUsernamePlaceholder.textContent = username;
 }

 console.log(`Remote user ${username} video ${enabled ? "enabled" : "disabled"}`);
});

// Exit meeting
function exitMeeting() {
 if (window.localStream) {
 window.localStream.getTracks().forEach(track => track.stop());
 }
 window.location.href = "/home";
}

// Meeting timer
let seconds = 0;
let minutes = 0;

function updateTimer() {
 seconds++;
 if (seconds >= 60) {
 seconds = 0;
 minutes++;
 }

 const formattedMinutes = String(minutes).padStart(2, '0');
 const formattedSeconds = String(seconds).padStart(2, '0');
 document.getElementById("meetingTimer").textContent = `Meeting Duration: ${formattedMinutes}:${formattedSeconds}`;
}

setInterval(updateTimer, 1000);