alert("Renderer script is running");


electron.receiveImage('image', (imageBase64) => {
    console.log("Image Data Received in Renderer (truncated):", imageBase64.substr(0, 100));
    const img = document.getElementById('live-image');
    img.src = `data:image/png;base64,${imageBase64}`;
});

console.log('Renderer script running');
if (window.electron) {
    console.log('Electron object is available');
} else {
    console.log('Electron object is NOT available');
}