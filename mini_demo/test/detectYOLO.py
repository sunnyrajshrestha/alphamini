import asyncio
import os
import logging
from mini.apis.api_sound import StartPlayTTS
from mini.dns.dns_browser import WiFiDevice
from test_connect import test_connect, shutdown, test_get_device_by_name, test_start_run_program
from mini import mini_sdk as MiniSdk

# Import YOLOv8
from ultralytics import YOLO
from PIL import Image

# Load YOLO model (can be "yolov8n.pt" for nano, "yolov8s.pt" for small)
model = YOLO("yolov8n.pt")

SAVE_FOLDER = "./images"


async def take_picture() -> str:
    """Take a picture on the robot and download locally."""
    success, resp = await MiniSdk.take_picture()
    if not success or not resp.isSuccess:
        logging.error(f"TakePicture failed: {resp}")
        return None

    pic_path_robot = resp.picPath
    if not os.path.exists(SAVE_FOLDER):
        os.makedirs(SAVE_FOLDER)

    local_path = os.path.join(SAVE_FOLDER, os.path.basename(pic_path_robot))
    await MiniSdk.download_file(remote_path=pic_path_robot, local_path=local_path)
    logging.info(f"Downloaded image to {local_path}")
    return local_path


async def detect_objects(local_image_path: str) -> list:
    """Run YOLO object detection on the image."""
    results = model(local_image_path)[0]  # YOLO returns a list of results
    objects = results.names  # Dictionary of class names
    detected_objects = [objects[int(cls)] for cls in results.boxes.cls]
    return detected_objects


async def speak(text: str):
    """Use robot TTS to speak."""
    await StartPlayTTS(text=text).execute()


async def main():
    # 1. Connect to robot
    device: WiFiDevice = await test_get_device_by_name()
    if not device:
        logging.error("Robot not found")
        return

    if not await test_connect(device):
        logging.error("Failed to connect to robot")
        return

    await test_start_run_program()  # enter program mode

    try:
        # 2. Take picture
        image_path = await take_picture()
        if not image_path:
            return

        # 3. Detect objects
        detected_objects = await detect_objects(image_path)
        if detected_objects:
            objects_text = ", ".join(detected_objects)
            await speak(f"I see the following objects: {objects_text}")
        else:
            await speak("I did not detect any objects.")
    finally:
        await shutdown()


if __name__ == "__main__":
    asyncio.run(main())

