declare module 'opencv4nodejs' {
    export const version: string;
  
    export class Mat {
      constructor(rows: number, cols: number, type: number, fillValue?: any);
      rows: number;
      cols: number;
      empty: boolean;
      bgrToGray(): Mat;
      laplacian(depth: number): Mat;
      mean(): { w: number };
      sub(mat: Mat): Mat;
      pow(power: number): Mat;
      resize(width: number, height: number): Mat;
      static CV_64F: number;
    }
  
    export class VideoCapture {
      constructor(device: number);
      read(): Mat;
      readAsync(callback: (err: Error | null, mat: Mat) => void): void;
      reset(): void;
      release(): void;
    }
  
    export function imshow(winname: string, mat: Mat): void;
    export function waitKey(delay: number): number;
    export function imwrite(filename: string, mat: Mat): void;
    export function destroyAllWindows(): void;
  }
  