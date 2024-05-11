const ffi = require('ffi-napi');
const path = require('path');

const libPath = path.join(__dirname, 'libtoupcam.so');
const lib = ffi.Library(libPath, {
  'Toupcam_Open': ['pointer', []]  // Indicates no parameters are expected
});

try {
  const camHandle = lib.Toupcam_Open(); // Make sure no arguments are passed here
  if (!camHandle.isNull()) {
    console.log('Camera opened successfully');
  } else {
    console.log('Failed to open camera');
  }
} catch (err) {
  console.error('Error operating the camera:', err);
}
