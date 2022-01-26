import io
import os

from PIL import Image
from google.cloud import vision


class ImageClassification:
    MIN_SCORE = .9

    def __init__(self):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Users/User1/Desktop/Perstagram/keyFile.json"
        # Instantiates a client
        self.client = vision.ImageAnnotatorClient()

    def classify(self, image: Image):
        image = vision.Image(content=self.image_to_bytes(image))

        # Performs label detection on the image file
        response = self.client.label_detection(image=image)
        labels = response.label_annotations

        return list(label.description for label in labels if label.score >= self.MIN_SCORE)

    @staticmethod
    def image_to_bytes(image: Image):
        img_bytes = io.BytesIO()
        image.save(img_bytes, "PNG")
        img_bytes = img_bytes.getvalue()
        return img_bytes
