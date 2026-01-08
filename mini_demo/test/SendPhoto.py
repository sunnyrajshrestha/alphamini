import asyncio
import logging
import os

from mini import mini_sdk as MiniSdk   # ← correct import for your SDK
from mini.dns.dns_browser import WiFiDevice
from test_connect import test_connect, shutdown, test_get_device_by_name, test_start_run_program

# Configure logging
logging.basicConfig(level=logging.INFO)
SAVE_FOLDER = "/home/sunny/Desktop/alphamini/mini_demo/test"

async def prepare_robot() -> WiFiDevice:
    """Scan, connect, and start program mode on EDU AlphaMini."""
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
    """Take picture and download via internal _channel (fallback for EDU SDK without download_file)."""
    logging.info("Taking picture…")
    resp = await MiniSdk.take_picture()
    if not resp.isSuccess:
        logging.error("Failed to take picture")
        return

    pic_path = resp.picPath
    logging.info(f"Picture taken on robot: {pic_path}")

    # Ensure local folder exists
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    local_file = os.path.join(save_folder, os.path.basename(pic_path))

    try:
        # Use internal _channel to fetch file bytes
        channel = MiniSdk._channel
        chunks = await channel.send_cmd(
            cmd=22,               # EDU internal file read command
            identify="0",
            message={"path": pic_path}
        )

        # Assemble bytes
        img_bytes = b"".join([c for c in chunks])
        with open(local_file, "wb") as f:
            f.write(img_bytes)

        logging.info(f"Saved picture locally: {local_file}")
        return local_file

    except Exception as e:
        logging.error(f"Failed to download image from robot: {e}")


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

