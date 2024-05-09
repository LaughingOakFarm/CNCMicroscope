const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const NodeWebcam = require('node-webcam');

// Initialize a NodeWebcam instance
const webcam = NodeWebcam.create({
    width: 1280,
    height: 720,
    delay: 0,
    saveShots: false,
    output: 'jpeg',
    device: false,
    callbackReturn: 'buffer',
    verbose: false
});

// Create the main application window
let mainWindow;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            preload: path.join(__dirname, 'renderer.js')
        }
    });
    mainWindow.loadFile('index.html');
}

NodeWebcam.list((list) => {
    console.log('Available devices:', list);
});

app.whenReady().then(createWindow);

// Capture image periodically and send to renderer via IPC
setInterval(() => {
    webcam.capture('temp', (err, buffer) => {
        if (err) {
            console.error('Webcam error:', err.message);
            return;
        }
        // Send captured image to renderer
        mainWindow.webContents.send('camera-frame', buffer.toString('base64'));
    });
}, 100);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});
