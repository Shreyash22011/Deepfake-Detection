import torch
import numpy as np
from PIL import Image
from facenet_pytorch import MTCNN
import cv2

class FaceDetector:
    def __init__(self, device='cpu', image_size=(224, 224), margin=0.2):
        self.device = torch.device(device)
        self.image_size = image_size
        self.target_box = None
        
        # Calculate margin in pixels assuming an average initial face crop size around 160
        margin_px = int(160 * margin)
        
        # Initialize MTCNN for face detection
        # keep_all=False ensures we only get the most prominent face if multiple exist
        self.mtcnn = MTCNN(
            image_size=image_size[0], 
            margin=margin_px, 
            min_face_size=20,
            thresholds=[0.6, 0.7, 0.7], 
            factor=0.709, 
            post_process=True,
            device=self.device,
            keep_all=True  # We will manually select the largest face
        )
        
    def reset_tracking(self):
        """Reset the face tracking state between videos."""
        self.target_box = None

    def _calculate_iou(self, boxA: np.ndarray, boxB: np.ndarray) -> float:
        """Calculate Intersection over Union (IoU) of two bounding boxes."""
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])

        interArea = max(0, xB - xA) * max(0, yB - yA)
        if interArea == 0:
            return 0.0

        boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
        boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

        iou = interArea / float(boxAArea + boxBArea - interArea)
        return iou

    def _select_target_face(self, boxes: np.ndarray) -> np.ndarray:
        """Select the target face using IoU tracking, falling back to max area."""
        if boxes is None or len(boxes) == 0:
            return None
            
        if len(boxes) == 1:
            self.target_box = boxes[0]
            return boxes[0]
            
        if self.target_box is not None:
            ious = [self._calculate_iou(self.target_box, box) for box in boxes]
            best_idx = np.argmax(ious)
            if ious[best_idx] > 0.1:
                self.target_box = boxes[best_idx]
                return boxes[best_idx]
                
        # Calculate areas: (x2 - x1) * (y2 - y1)
        areas = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
        largest_idx = np.argmax(areas)
        self.target_box = boxes[largest_idx]
        return boxes[largest_idx]

    def detect_and_crop(self, frame_rgb: np.ndarray) -> torch.Tensor:
        """
        Detects face in an RGB frame, crops, and resizes.
        Returns a normalized PyTorch tensor of shape (3, H, W).
        If no face is detected, returns a center crop of the frame as a fallback.
        """
        # Convert numpy array (from OpenCV) to PIL Image for MTCNN
        pil_image = Image.fromarray(frame_rgb)
        
        # Detect faces
        boxes, probs = self.mtcnn.detect(pil_image)
        
        if boxes is not None and len(boxes) > 0:
            # Select the target face using tracking
            largest_box = self._select_target_face(boxes)
            
            # Use MTCNN's internal extract method to handle margin and resize
            # MTCNN extract returns a normalized tensor
            face_tensor = self.mtcnn.extract(pil_image, [largest_box], save_path=None)[0]
            return face_tensor, True
        else:
            # Fallback: No face detected. Use a center crop of the original image
            # Convert to tensor and normalize similarly to MTCNN
            center_crop = self._center_crop(frame_rgb, self.image_size)
            center_crop = center_crop.astype(np.float32) / 127.5 - 1.0 # normalize to [-1, 1]
            # Convert HWC to CHW
            center_crop = np.transpose(center_crop, (2, 0, 1))
            return torch.tensor(center_crop), False
            
    def _center_crop(self, img: np.ndarray, target_size: tuple) -> np.ndarray:
        """Fallback method if no face is found."""
        h, w, _ = img.shape
        th, tw = target_size
        
        # If image is smaller than target, just resize
        if h < th or w < tw:
            return cv2.resize(img, target_size)
            
        # Crop center
        x = w // 2 - tw // 2
        y = h // 2 - th // 2
        crop = img[y:y+th, x:x+tw]
        
        return crop
