const { ipcRenderer } = require('electron');

// Listen for the camera frames sent from the main process
ipcRenderer.on('camera-frame', (event, frame) => {
  const imgElement = document.getElementById('live-feed');
  imgElement.src = `data:image/jpeg;base64,${frame}`;
});
