var HID = require('node-hid');
const express = require('express');

// Steam Neptune Controller
var device = new HID.HID("/dev/hidraw2");
var port = 8000

var controller = {
    id: "Steam Controller (Neptune)",
    index: 0,
    connected: true,
    timestamp: 0,
    mapping: "standard",
    axes: [0, 0, 0, 0],
    buttons: new Array(17).fill().map(m => ({pressed: false, touched: false, value: 0}))
}

device.on("data", (data) => {

    // Reset controls to default
    controller.buttons.forEach((x) => { 
        x.pressed = false; 
        x.value = 0;
    });

    // A 128
    controller.buttons[0].pressed = isPressed(128, data[8]);
    // B 32
    controller.buttons[1].pressed = isPressed(32, data[8]);
    // X 64
    controller.buttons[2].pressed = isPressed(64, data[8]);
    // Y 16
    controller.buttons[3].pressed = isPressed(16, data[8]);
    // LB 8
    controller.buttons[4].pressed = isPressed(8, data[8]);
    // RB 4
    controller.buttons[5].pressed = isPressed(4, data[8]);
    // LT 2
    controller.buttons[6].pressed = isPressed(2, data[8]);
    // RT 1
    controller.buttons[7].pressed = isPressed(1, data[8]);
    
    // SELECT 16
    controller.buttons[8].pressed = isPressed(16, data[9]);
    // START 64
    controller.buttons[9].pressed = isPressed(64, data[9]);
    // L3 64
    controller.buttons[10].pressed = isPressed(64, data[10]);
    // R3 4
    controller.buttons[11].pressed = isPressed(4, data[11]);
    // DPAD UP 1
    controller.buttons[12].pressed = isPressed(1, data[9]);
    // DPAD DOWN 8
    controller.buttons[13].pressed = isPressed(8, data[9]);
    // DPAD LEFT 4
    controller.buttons[14].pressed = isPressed(4, data[9]);
    // DPAD RIGHT 2
    controller.buttons[15].pressed = isPressed(2, data[9]);
    // STEAM BUTTON 32
    controller.buttons[16].pressed = isPressed(32, data[9]);


    // data[13][14] = touch sensor on L3 R3

    // Axis
    controller.axes[0] = convertInputValue(data[49]);
    controller.axes[1] = -1 * convertInputValue(data[51]);
    controller.axes[2] = convertInputValue(data[53]);
    controller.axes[3] = -1 * convertInputValue(data[55]);

    controller.buttons.forEach((x) => {
        x.value = x.pressed ? 1 : 0;
    });

    // Direction
    //l3xDir = data[48];
    //l3yDir = data[50];

    //r3xDir = data[52];
    //r3yDir = data[54];
});

const app = express()

// respond with "hello world" when a GET request is made to the homepage
app.get('/', (req, res) => {
    res.contentType('json');
    res.send(JSON.stringify(controller));
})

app.listen(port, () => {
    console.log(`Example app listening on port ${port}`)
  })


// Checks if a given key is currently being pressed
var isPressed = function(mask, bits) {
    return (bits & mask) > 0;
}

// Steam input goes from 0 -> 127 and from 128 to 255
var convertInputValue = function(value) {

    // Upperbound value
    if (value >= 128) {
        return norm(value, 128, 255) - 1;
    }
    
    // Lowerbound value
    return norm(value, 0, 127);
}

// Simple normalise method
var norm = function(value, min, max) {
    return (value - min) / (max - min);
}