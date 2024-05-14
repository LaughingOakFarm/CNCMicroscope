electron.receiveImage('image', (imageBase64) => {
    const img = document.getElementById('live-image');
    img.src = `data:image/png;base64,${imageBase64}`;
});

console.log('Renderer script running');
if (window.electron) {
    console.log('Electron object is available');
} else {
    console.log('Electron object is NOT available');
}

document.addEventListener('DOMContentLoaded', () => {
    const video = document.getElementById('webcam');

    if (navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(function (stream) {
                video.srcObject = stream;
            })
            .catch(function (error) {
                console.log("Something went wrong!", error);
            });
    }
});