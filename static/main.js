/* -------------------- Socket -------------------- */
const socket = io();
const roomId = window.location.pathname.split("/")[2];

/* -------------------- DOM -------------------- */
const localVideo = document.getElementById("localVideo");
const remoteVideo = document.getElementById("remoteVideo");
const localUsernamePlaceholder = document.getElementById("localUsername");
const remoteUsernamePlaceholder = document.getElementById("remoteUsername");
const chatInput = document.getElementById("chatInput");
const sendBtn = document.getElementById("sendBtn");
const messages = document.getElementById("messages");
const muteAudioBtn = document.getElementById("muteAudioBtn");
const disableVideoBtn = document.getElementById("disableVideoBtn");

/* -------------------- Media State -------------------- */
let localStream = null;
let peerConnection = null;
let remoteSocketId = null;

let videoEnabled = false;
let audioEnabled = true;

/* -------------------- WebRTC Config -------------------- */
const rtcConfig = {
 iceServers: [{ urls: "stun:stun.l.google.com:19302" }]
};

/* -------------------- Init -------------------- */
document.addEventListener("DOMContentLoaded", () => {
 socket.emit("join", { room: roomId, username: localUsername });

 localVideo.style.display = "none";
 localUsernamePlaceholder.textContent = localUsername;
 localUsernamePlaceholder.style.display = "flex";

 console.log("Socket connected:", socket.id);
});

/* -------------------- WebRTC Helpers -------------------- */
function createPeerConnection() {
 peerConnection = new RTCPeerConnection(rtcConfig);

 peerConnection.onicecandidate = (event) => {
 if (event.candidate && remoteSocketId) {
 socket.emit("ice-candidate", {
 to: remoteSocketId,
 candidate: event.candidate
 });
 }
 };

 peerConnection.ontrack = (event) => {
 remoteVideo.srcObject = event.streams[0];
 remoteVideo.style.display = "block";
 remoteUsernamePlaceholder.style.display = "none";
 };

 if (localStream) {
 localStream.getTracks().forEach(track =>
 peerConnection.addTrack(track, localStream)
 );
 }
}

/* -------------------- WebRTC Signaling -------------------- */
socket.on("user-joined", async (data) => {
 console.log("User joined:", data.socketId);
 remoteSocketId = data.socketId;

 if (!localStream) return;

 createPeerConnection();

 const offer = await peerConnection.createOffer();
 await peerConnection.setLocalDescription(offer);

 socket.emit("offer", {
 to: remoteSocketId,
 sdp: offer
 });
});

socket.on("offer", async (data) => {
 remoteSocketId = data.from;

 createPeerConnection();

 await peerConnection.setRemoteDescription(
 new RTCSessionDescription(data.sdp)
 );

 const answer = await peerConnection.createAnswer();
 await peerConnection.setLocalDescription(answer);

 socket.emit("answer", {
 to: remoteSocketId,
 sdp: answer
 });
});

socket.on("answer", async (data) => {
 await peerConnection.setRemoteDescription(
 new RTCSessionDescription(data.sdp)
 );
});

socket.on("ice-candidate", async (data) => {
 if (peerConnection) {
 await peerConnection.addIceCandidate(data.candidate);
 }
});

/* -------------------- Media Controls -------------------- */
async function toggleVideo() {
 if (!localStream) {
 try {
 localStream = await navigator.mediaDevices.getUserMedia({
 video: true,
 audio: true
 });

 localVideo.srcObject = localStream;
 localVideo.style.display = "block";
 localUsernamePlaceholder.style.display = "none";

 videoEnabled = true;
 audioEnabled = true;

 disableVideoBtn.innerText = " Disable Video";
 muteAudioBtn.innerText = " Mute Audio";

 if (peerConnection) {
 localStream.getTracks().forEach(track =>
 peerConnection.addTrack(track, localStream)
 );
 }
 } catch (err) {
 alert("Camera/Microphone permission denied");
 return;
 }
 } else {
 const track = localStream.getVideoTracks()[0];
 if (track) {
 track.enabled = !track.enabled;
 videoEnabled = track.enabled;
 disableVideoBtn.innerText = videoEnabled
 ? " Disable Video"
 : " Enable Video";
 }
 }
}

function toggleAudio() {
 if (!localStream) return;

 const track = localStream.getAudioTracks()[0];
 if (track) {
 track.enabled = !track.enabled;
 audioEnabled = track.enabled;
 muteAudioBtn.innerText = audioEnabled
 ? " Mute Audio"
 : " Unmute Audio";
 }
}

/* -------------------- Screen Share -------------------- */
function startScreenShare() {
 navigator.mediaDevices.getDisplayMedia({ video: true })
 .then(stream => {
 const screenTrack = stream.getVideoTracks()[0];
 const sender = peerConnection
 ?.getSenders()
 .find(s => s.track.kind === "video");

 if (sender) sender.replaceTrack(screenTrack);

 localVideo.srcObject = stream;

 screenTrack.onended = () => toggleVideo();
 })
 .catch(() => alert("Screen share cancelled"));
}

/* -------------------- Chat -------------------- */
sendBtn.addEventListener("click", () => {
 const msg = chatInput.value.trim();
 if (!msg) return;

 socket.emit("message", {
 room: roomId,
 text: `${localUsername}: ${msg}`
 });

 appendMessage(`${localUsername}: ${msg}`);
 chatInput.value = "";
});

socket.on("message", (data) => {
 if (data.text) appendMessage(data.text);
});

function appendMessage(msg) {
 const div = document.createElement("div");
 div.textContent = msg;
 messages.appendChild(div);
 messages.scrollTop = messages.scrollHeight;
}

/* -------------------- Exit -------------------- */
function exitMeeting() {
 if (localStream) {
 localStream.getTracks().forEach(track => track.stop());
 }
 if (peerConnection) peerConnection.close();
 window.location.href = "/home";
}

/* -------------------- Timer -------------------- */
let seconds = 0;
let minutes = 0;

setInterval(() => {
 seconds++;
 if (seconds === 60) {
 seconds = 0;
 minutes++;
 }
 document.getElementById("meetingTimer").textContent =
 `Meeting Duration: ${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
}, 1000);