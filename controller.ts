import  HID from 'node-hid';
import EventEmitter from 'events';

export interface IController {
    name: string;
    index: number;
    connected: boolean;
    lastUpdate: Date | null;
    joysticks: {
        left: {
            x: number;
            y: number;
        };
        right: {
            x: number;
            y: number;
        };
    };
    dpad: {
        up: boolean;
        down: boolean;
        left: boolean;
        right: boolean;
    };
    buttons: {
        a: boolean;
        b: boolean;
        x: boolean;
        y: boolean;

        lb: boolean;
        rb: boolean;

        lt: boolean;
        rt: boolean;

        select: boolean;
        start: boolean;
        steam: boolean;

        leftJoystick: boolean;
        rightJoystick: boolean;
    };
}

export class Controller extends EventEmitter {
    private device: HID.HID;
    public state: IController;

    constructor(devicePath: string) {
        super();
        this.device = new HID.HID(devicePath);
        this.state = this.createInitialState();

        this.device.on("data", (data) => this.updateState(data));
    }

    private createInitialState(): IController {
        return {
            name: "Steam Controller (Neptune)",
            index: 0,
            connected: true,
            lastUpdate: null,
            joysticks: {
                left: { x: 0, y: 0 },
                right: { x: 0, y: 0 },
            },
            dpad: {
                up: false,
                down: false,
                left: false,
                right: false,
            },
            buttons: {
                a: false, b: false, x: false, y: false,
                lb: false, rb: false, lt: false, rt: false,
                select: false, start: false, steam: false,
                leftJoystick: false, rightJoystick: false,
            }
        };
    }

    private updateState(data: Buffer) {
        this.state.lastUpdate = new Date();

        this.updateButton("a", 128, data[8]);
        this.updateButton("b", 32, data[8]);
        this.updateButton("x", 64, data[8]);
        this.updateButton("y", 16, data[8]);
        this.updateButton("lb", 8, data[8]);
        this.updateButton("rb", 4, data[8]);
        this.updateButton("lt", 2, data[8]);
        this.updateButton("rt", 1, data[8]);

        this.updateDpad("up", 1, data[9]);
        this.updateDpad("down", 8, data[9]);
        this.updateDpad("left", 4, data[9]);
        this.updateDpad("right", 2, data[9]);

        this.updateButton("select", 16, data[9]);
        this.updateButton("start", 64, data[9]);
        this.updateButton("steam", 32, data[9]);

        this.updateButton("leftJoystick", 64, data[10]);
        this.updateButton("rightJoystick", 4, data[11]);

        this.updateJoystick("left", "x", data[49]);
        this.updateJoystick("left", "y", -1 * this.convertInputValue(data[51]));
        this.updateJoystick("right", "x", data[53]);
        this.updateJoystick("right", "y", -1 * this.convertInputValue(data[55]));
    }

    private updateButton(button: keyof IController['buttons'], mask: number, data: number) {
        const oldValue = this.state.buttons[button];
        this.state.buttons[button] = this.isPressed(mask, data);
        if (this.state.buttons[button] !== oldValue) {
            this.emit(`button.${button}`, this.state.buttons[button]);
        }
    }

    private updateDpad(direction: keyof IController['dpad'], mask: number, data: number) {
        const oldValue = this.state.dpad[direction];
        this.state.dpad[direction] = this.isPressed(mask, data);
        if (this.state.dpad[direction] !== oldValue) {
            this.emit(`dpad.${direction}`, this.state.dpad[direction]);
        }
    }

    private updateJoystick(side: keyof IController['joysticks'], axis: keyof IController['joysticks']['left'], value: number) {
        const oldValue = this.state.joysticks[side][axis];
        this.state.joysticks[side][axis] = this.convertInputValue(value);
        if (this.state.joysticks[side][axis] !== oldValue) {
            this.emit(`joystick.${side}.${axis}`, this.state.joysticks[side][axis]);
        }
    }

    private isPressed(mask: number, bits: number): boolean {
        return (bits & mask) > 0;
    }

    private convertInputValue(value: number): number {
        if (value >= 128) {
            return this.norm(value, 128, 255) - 1;
        }
        return this.norm(value, 0, 127);
    }

    private norm(value: number, min: number, max: number): number {
        return (value - min) / (max - min);
    }
}
