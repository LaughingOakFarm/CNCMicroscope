import { Controller, IController } from './controller';
import { EventEmitter } from 'events';

class MockHID extends EventEmitter {
    write() {}
}

jest.mock('node-hid', () => {
    return {
        HID: jest.fn().mockImplementation(() => new MockHID())
    };
});

describe('Controller', () => {
    let controller: Controller;
    let mockDevice: MockHID;

    beforeEach(() => {
        controller = new Controller('/dev/hidraw2');
        mockDevice = (controller as any).device;
    });

    it('should initialize with default state', () => {
        expect(controller.state).toMatchObject({
            name: 'Steam Controller (Neptune)',
            index: 0,
            connected: true,
            lastUpdate: null,
            joysticks: {
                left: { x: 0, y: 0 },
                right: { x: 0, y: 0 }
            },
            dpad: {
                up: false,
                down: false,
                left: false,
                right: false
            },
            buttons: {
                a: false, b: false, x: false, y: false,
                lb: false, rb: false, lt: false, rt: false,
                select: false, start: false, steam: false,
                leftJoystick: false, rightJoystick: false,
            }
        });
    });

    it('should update button state on data event', (done) => {
        controller.on('button.a', (state) => {
            try {
                expect(state).toBe(true);
                done();
            } catch (error) {
                done(error);
            }
        });

        // Simulate data from the HID device
        const data = buildBuffer({ button: 'a' });
        mockDevice.emit('data', data);
    });

    it('should update dpad state on data event', (done) => {
        controller.on('dpad.up', (state) => {
            try {
                expect(state).toBe(true);
                done();
            } catch (error) {
                done(error);
            }
        });

        // Simulate data from the HID device
        const data = buildBuffer({ dpad: 'up' });
        mockDevice.emit('data', data);
    });

    it('should update joystick state on data event', (done) => {
        controller.on('joystick.left.x', (state) => {
            try {
                expect(state).toBe(0.25196850393700787);
                done();
            } catch (error) {
                done(error);
            }
        });

        // Simulate data from the HID device
        const data = buildBuffer({ joystick: { side: 'left', axis: 'x', value: 32 } });
        mockDevice.emit('data', data);
    });

    // Additional tests for other buttons, dpad, and joystick states
});

function buildBuffer(options: { button?: keyof IController['buttons'], dpad?: keyof IController['dpad'], joystick?: { side: keyof IController['joysticks'], axis: keyof IController['joysticks']['left'], value: number } }): Buffer {
    const buffer = Buffer.alloc(64); // Create a buffer of 64 bytes initialized with zeros

    if (options.button) {
        switch (options.button) {
            case 'a': buffer[8] = 128; break;
            case 'b': buffer[8] = 32; break;
            case 'x': buffer[8] = 64; break;
            case 'y': buffer[8] = 16; break;
            case 'lb': buffer[8] = 8; break;
            case 'rb': buffer[8] = 4; break;
            case 'lt': buffer[8] = 2; break;
            case 'rt': buffer[8] = 1; break;
            case 'select': buffer[9] = 16; break;
            case 'start': buffer[9] = 64; break;
            case 'steam': buffer[9] = 32; break;
            case 'leftJoystick': buffer[10] = 64; break;
            case 'rightJoystick': buffer[11] = 4; break;
            default: break;
        }
    }

    if (options.dpad) {
        switch (options.dpad) {
            case 'up': buffer[9] = 1; break;
            case 'down': buffer[9] = 8; break;
            case 'left': buffer[9] = 4; break;
            case 'right': buffer[9] = 2; break;
            default: break;
        }
    }

    if (options.joystick) {
        const { side, axis, value } = options.joystick;
        if (side === 'left') {
            if (axis === 'x') buffer[49] = value;
            if (axis === 'y') buffer[51] = value;
        } else if (side === 'right') {
            if (axis === 'x') buffer[53] = value;
            if (axis === 'y') buffer[55] = value;
        }
    }

    return buffer;
}
