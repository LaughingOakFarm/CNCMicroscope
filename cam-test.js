const { lib, Cameras, callback, alloc } = require('./node-toupcam/toupcam');
const ref = require('ref-napi');

// Simple still image callback
function onStillImage(eventType, contextPtr) {
    if (eventType === 5) {
        const cameraHandle = contextPtr.deref();
        const widthPtr = ref.alloc(ref.types.int);
        const heightPtr = ref.alloc(ref.types.int);
        
        // Use ref.alloc to create an image buffer
        const imageBuffer = ref.alloc({ size: 1920 * 1080 * 3, indirection: 1 });

        const result = lib.Toupcam_PullStillImage(cameraHandle, imageBuffer, 24, widthPtr, heightPtr);
        if (result === 0) {
            const width = widthPtr.deref();
            const height = heightPtr.deref();
            console.log(`Still image of size ${width}x${height} captured successfully.`);
        } else {
            console.error(`Error pulling still image: ${lib.getError(result)}`);
        }
    }
}

const cameraCount = lib.Toupcam_Enum(Cameras);
if (cameraCount > 0) {
    const firstCamera = Cameras[0];
    const cameraId = firstCamera.id.buffer.toString('utf8');
    const cameraHandle = lib.Toupcam_Open(cameraId);

    if (cameraHandle !== lib.NullPtr) {
        const eventCallback = callback.PullMode(onStillImage);
        const contextPointer = ref.alloc(ref.refType(ref.types.void), cameraHandle);

        const startResult = lib.Toupcam_StartPullModeWithCallback(cameraHandle, eventCallback, contextPointer);
        if (startResult === 0) {
            console.log('Camera started successfully. Taking a still image...');
            const snapResult = lib.Toupcam_Snap(cameraHandle, 0);
            if (snapResult !== 0) {
                console.error(`Error taking snapshot: ${lib.getError(snapResult)}`);
                lib.Toupcam_Close(cameraHandle);
            }
        } else {
            console.error(`Error starting camera: ${lib.getError(startResult)}`);
            lib.Toupcam_Close(cameraHandle);
        }
    } else {
        console.error('Failed to open camera.');
    }
} else {
    console.error('No cameras found.');
}
