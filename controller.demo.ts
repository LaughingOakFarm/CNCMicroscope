import express from "express";
import { Controller } from "./controller";

const port = 8000;
const controller = new Controller("/dev/hidraw2");

const app = express();

app.get("/", (req, res) => {
    res.contentType("json");
    res.send(JSON.stringify(controller.state));
});

app.listen(port, () => {
    console.log(`Server listening on port ${port}`);
});

controller.on("button.a", (state) => {
    console.log("Button A state changed:", state);
});

controller.on("dpad.up", (state) => {
    console.log("D-Pad Up state changed:", state);
});
