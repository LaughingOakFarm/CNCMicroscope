import cv from 'opencv4nodejs';
import fs from 'fs';

// Verify OpenCV is correctly loaded
try {
  console.log('OpenCV version:', cv.version);
} catch (err) {
  console.error('Error loading OpenCV:', err);
  process.exit(1);
}

// Open a video capture stream from the default webcam (index 0)
const webcam = new cv.VideoCapture(0);

// Function to calculate the focus measure using the variance of the Laplacian
function calculateFocusMeasure(frame: cv.Mat): number {
  const grayFrame = frame.bgrToGray();
  const laplacian = grayFrame.laplacian(cv.Mat.CV_64F);
  const mean = laplacian.mean().w;
  const variance = laplacian.sub(new cv.Mat(grayFrame.rows, grayFrame.cols, cv.Mat.CV_64F, mean)).pow(2).mean().w;
  return variance;
}

// Capture frames in an interval
setInterval(() => {
  let frame = webcam.read();

  // If the frame is empty, reset the webcam and read again
  if (frame.empty) {
    webcam.reset();
    frame = webcam.read();
  }

  // Resize frame to make it easier to process and display
  const resizedFrame = frame.resize(640, 480);

  // Calculate focus measure
  const focusMeasure = calculateFocusMeasure(resizedFrame);
  console.log(`Focus Measure: ${focusMeasure}`);

  // Show the frame
  cv.imshow('Webcam', resizedFrame);

  // Exit if 'q' is pressed
  const key = cv.waitKey(1);
  if (key === 113) { // 'q' key
    webcam.release();
    cv.destroyAllWindows();
    process.exit(0);
  }
}, 100);

// Save a frame as an example
webcam.readAsync((err: Error | null, frame: cv.Mat) => {
  if (!err) {
    cv.imwrite('./example.jpg', frame);
  } else {
    console.error('Error capturing frame:', err);
  }
});
