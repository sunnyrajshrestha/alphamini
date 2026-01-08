import asyncio
import logging
import os

from mini import mini_sdk as MiniSdk
from mini.dns.dns_browser import WiFiDevice
from test_connect import test_connect, shutdown, test_get_device_by_name, test_start_run_program

# Configure logging
logging.basicConfig(level=logging.INFO)

SAVE_FOLDER = "/home/sunny/Desktop/alphamini/mini_demo/test"

async def prepare_robot() -> WiFiDevice:
    device: WiFiDevice = await test_get_device_by_name()
    if not device:
        logging.error("No AlphaMini device found.")
        return None

    await asyncio.sleep(2)  # give robot time to start WS
    if not await test_connect(device):
        logging.error("Failed to connect to robot.")
        return None

    await test_start_run_program()
    return device


async def take_picture_and_download(save_folder: str = SAVE_FOLDER):
    """Take picture and download via WebSocket bytes."""
    logging.info("Taking picture…")
    resp = await MiniSdk.take_picture()  # resp.picPath contains the remote path

    if not resp.isSuccess:
        logging.error("Failed to take picture")
        return

    pic_path = resp.picPath
    logging.info(f"Picture taken on robot: {pic_path}")

    # Ask the robot to send the file bytes
    try:
        # send_cmd_file_read is internal; fetch bytes in chunks
        chunks = await MiniSdk.channel.send_cmd(
            cmd=22,  # cmd 22 seems to correspond to file read in EDU
            identify="0",
            message={"path": pic_path}
        )

        # Assemble bytes (depends on SDK response format)
        img_bytes = b"".join([c for c in chunks])  # adjust if SDK wraps bytes differently

        # Ensure folder exists
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        local_file = os.path.join(save_folder, os.path.basename(pic_path))
        with open(local_file, "wb") as f:
            f.write(img_bytes)

        logging.info(f"Saved picture locally: {local_file}")
        return local_file

    except Exception as e:
        logging.error(f"Failed to get image bytes: {e}")


async def main():
    MiniSdk.set_log_level(logging.INFO)
    MiniSdk.set_robot_type(MiniSdk.RobotType.EDU)

    device = await prepare_robot()
    if not device:
        return

    try:
        await take_picture_and_download()
    finally:
        await shutdown()
        logging.info("Robot connection closed.")


if __name__ == "__main__":
    asyncio.run(main())

