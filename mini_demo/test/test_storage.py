import asyncio
import logging
import os
import subprocess
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


async def take_picture_and_get_path():
    """Take picture and return the path on the robot."""
    logging.info("Taking picture…")
    resp = await MiniSdk.take_picture()
    
    if not resp.isSuccess:
        logging.error("Failed to take picture")
        return None
    
    pic_path = resp.picPath
    logging.info(f"Picture taken on robot at: {pic_path}")
    return pic_path


def download_via_adb(robot_ip: str, remote_path: str, local_folder: str = SAVE_FOLDER):
    """
    Download file from robot using ADB.
    
    The AlphaMini SDK does not include file transfer functionality.
    The most reliable way to download files is using ADB.
    """
    try:
        # Ensure folder exists
        if not os.path.exists(local_folder):
            os.makedirs(local_folder)
        
        local_file = os.path.join(local_folder, os.path.basename(remote_path))
        
        logging.info(f"Connecting to robot via ADB at {robot_ip}:5555...")
        
        # Connect to robot via ADB over network
        connect_result = subprocess.run(
            ["adb", "connect", f"{robot_ip}:5555"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if "connected" not in connect_result.stdout.lower() and "already connected" not in connect_result.stdout.lower():
            logging.error(f"Failed to connect via ADB: {connect_result.stdout}")
            logging.info("Make sure ADB is installed and robot ADB debugging is enabled")
            return None
        
        logging.info("Connected via ADB. Pulling file...")
        
        # Pull the file from robot
        pull_result = subprocess.run(
            ["adb", "pull", remote_path, local_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if pull_result.returncode == 0:
            logging.info(f"Successfully downloaded to: {local_file}")
            return local_file
        else:
            logging.error(f"Failed to pull file: {pull_result.stderr}")
            return None
            
    except FileNotFoundError:
        logging.error("ADB not found. Please install Android Platform Tools")
        logging.info("Install: https://developer.android.com/studio/releases/platform-tools")
        return None
    except subprocess.TimeoutExpired:
        logging.error("ADB operation timed out")
        return None
    except Exception as e:
        logging.error(f"Error during ADB transfer: {e}")
        return None


def enable_adb_on_robot(robot_id: str):
    """
    Enable ADB debugging on the robot using the SDK's pkg_tool.
    This must be done before you can use ADB to download files.
    """
    try:
        import mini.pkg_tool as Tool
        logging.info("Enabling ADB debugging on robot...")
        Tool.set_adb_debug_switch(switch=True, robot_id=robot_id)
        logging.info("ADB debugging enabled. Please wait a moment for it to take effect.")
    except Exception as e:
        logging.error(f"Failed to enable ADB: {e}")


async def main():
    MiniSdk.set_log_level(logging.INFO)
    MiniSdk.set_robot_type(MiniSdk.RobotType.EDU)
    
    device = await prepare_robot()
    if not device:
        return
    
    try:
        # Step 1: Enable ADB on the robot (only needs to be done once)
        # Uncomment this line if ADB is not already enabled:
        # enable_adb_on_robot(device.name)
        # await asyncio.sleep(5)  # Wait for ADB to start
        
        # Step 2: Take picture and get path
        pic_path = await take_picture_and_get_path()
        if not pic_path:
            return
        
        # Step 3: Download via ADB
        # IMPORTANT: The SDK does NOT support direct file transfer
        # You MUST use ADB to download files
        logging.info("\n" + "="*60)
        logging.info("IMPORTANT: The AlphaMini SDK does not support file downloads.")
        logging.info("To download the image, use one of these methods:")
        logging.info("="*60)
        logging.info(f"\n1. ADB Method (recommended):")
        logging.info(f"   adb connect {device.ip}:5555")
        logging.info(f"   adb pull {pic_path} {SAVE_FOLDER}/")
        logging.info(f"\n2. Use the AlphaMini mobile app to view/download photos")
        logging.info(f"\n3. Attempt automatic download via ADB (if installed):")
        
        # Try automatic ADB download
        downloaded_file = download_via_adb(device.ip, pic_path)
        
        if downloaded_file:
            logging.info(f"\n✓ Success! Image saved to: {downloaded_file}")
        else:
            logging.warning("\n✗ Automatic ADB download failed.")
            logging.info("Please download manually using the commands above.")
        
    finally:
        await shutdown()
        logging.info("Robot connection closed.")


if __name__ == "__main__":
    asyncio.run(main())
