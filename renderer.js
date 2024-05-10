const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('controller', {
    onInput: (callback) => ipcRenderer.on('controller-input', (event, input) => callback(input)),
});
