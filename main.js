const { app, BrowserWindow } = require('electron');
const express = require('express');
const bodyParser = require('body-parser');
const server = express();
const serverPort = 8000; // Define a port for the HTTP server
var NodeWebcam = require("node-webcam");

server.use(bodyParser.json({ limit: '50mb' }));
let mainWindow;

// Default options
var opts = {
    width: 1280,
    height: 720,
    quality: 100,
    delay: 0,
    saveShots: true,
    output: "jpeg",
    device: false,
    callbackReturn: "location",
    verbose: false
};

var Webcam = NodeWebcam.create(opts);

// Capture image
Webcam.capture("test_picture", function(err, data) {
    if (err) {
        console.error(err);
    } else {
        console.log("Image saved:", data);
    }
});

function createWindow() {
    const path = require('path');

    const mainWindow = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'), // Make sure this path is correct
            contextIsolation: true,
            nodeIntegration: false
        }
    });

    mainWindow.loadFile('index.html');

    mainWindow.on('closed', () => {
        mainWindow = null;
    });

    // Start the Express server within the Electron app
    server.post('/image', (req, res) => {
        const imageBase64 = req.body.image;
        console.log("Received an image");
        if (mainWindow) {
            mainWindow.webContents.send('image', imageBase64);
        }
        res.send('Image received');
    });

    server.listen(serverPort, () => {
        console.log(`Server listening on port ${serverPort}`);
    });
}

app.on('ready', createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (mainWindow === null) {
        createWindow();
    }
});
