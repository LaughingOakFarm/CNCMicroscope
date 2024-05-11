const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electron', {
    sendImage: (channel, data) => ipcRenderer.send(channel, data),
    receiveImage: (channel, func) => {
        ipcRenderer.on(channel, (event, ...args) => func(...args));
    }
});

console.log("Preload script running");
