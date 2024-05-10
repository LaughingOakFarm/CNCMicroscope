const { app, BrowserWindow } = require('electron');
const path = require('path');
const HID = require('node-hid');

let mainWindow;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
        },
    });

    mainWindow.loadFile('index.html');
}

app.whenReady().then(() => {
    createWindow();
    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

// List connected HID devices and find the Steam Deck controller
const devices = HID.devices();
const steamDeckDevice = devices.find(device => {
    console.log(device);
    // Replace these with your Steam Deck controller's VendorID and ProductID
    return device.vendorId === 10462 && device.productId === 4613;
});

if (steamDeckDevice) {
    const controller = new HID.HID(steamDeckDevice.path);

    // Example: handle incoming data for buttons
    controller.on('data', (data) => {
        const input = parseControllerInput(data);
        mainWindow.webContents.send('controller-input', input);
    });
} else {
    console.error('Steam Deck controller not found!');
}

// Parses the incoming data buffer into readable input events
function parseControllerInput(data) {
    console.log(data);
    return data;
}
