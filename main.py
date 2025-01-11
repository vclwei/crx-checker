import requests
from lxml import html
import time
import random
import schedule
from datetime import datetime, timedelta
from telegram.ext import Application, CommandHandler
from telegram.constants import ParseMode
import asyncio
import logging
import yaml
import os

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def load_config():
    """
    Load configuration from yaml file
    """
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    try:
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)
    except Exception as e:
        logging.error(f"Failed to load config: {str(e)}")
        raise

# Load configuration
config = load_config()

# Get configuration values
TELEGRAM_BOT_TOKEN = config['telegram']['bot_token']
TELEGRAM_CHAT_ID = config['telegram']['chat_id']
CHECK_DAYS = config['schedule']['check_days']
CHECK_TIME = config['schedule']['check_time']

async def send_telegram_message(message: str) -> None:
    """
    Asynchronously send Telegram message
    
    Args:
        message: Message content to send
    """
    try:
        # Create application using builder pattern
        application = (
            Application.builder()
            .token(TELEGRAM_BOT_TOKEN)
            .build()
        )
        
        async with application:
            await application.bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=message,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True
            )
    except Exception as e:
        logging.error(f"Failed to send Telegram message: {str(e)}")

async def check_extensions_async(extension_ids: list, min_delay: int = 1, max_delay: int = 3) -> None:
    """
    Asynchronously check multiple extensions' information
    """
    print(f"\nExecution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    total = len(extension_ids)
    recent_updates = []
    
    for index, ext_id in enumerate(extension_ids, 1):
        name, version, update_time = get_extension_info(ext_id)
        print(f"{name or 'Unknown'} ｜ {ext_id} | {version or 'Unknown'} | {update_time or 'Unknown'}")
        
        if update_time:
            update_date = parse_update_time(update_time)
            
            if update_date and (datetime.now() - update_date) <= timedelta(days=CHECK_DAYS):
                recent_updates.append(f"Extension <b>{name}</b>\nID: <code>{ext_id}</code>\nUpdate Time: {update_time}\nVersion: {version}")
        
        if index < total:
            delay = random.uniform(min_delay, max_delay)
            await asyncio.sleep(delay)
    
    if recent_updates:
        message = f"Detected extensions updated in the last {CHECK_DAYS} days:\n\n" + "\n\n".join(recent_updates)
        await send_telegram_message(message)

def parse_update_time(update_time_str):
    """
    Parse update time string
    """
    try:
        # Handle English month format "Month DD, YYYY"
        if any(month in update_time_str for month in ['January', 'February', 'March', 'April', 'May', 'June', 
                                                     'July', 'August', 'September', 'October', 'November', 'December']):
            return datetime.strptime(update_time_str, '%B %d, %Y')
        elif "年" in update_time_str and "月" in update_time_str and "日" in update_time_str:
            # Handle Chinese date format "YYYY年MM月DD日"
            date_str = update_time_str.replace('年', '-').replace('月', '-').replace('日', '')
            return datetime.strptime(date_str, '%Y-%m-%d')
        elif "/" in update_time_str:
            # Handle "MM/DD/YYYY" format
            return datetime.strptime(update_time_str, '%m/%d/%Y')
        elif "-" in update_time_str:
            # Handle "YYYY-MM-DD" format
            return datetime.strptime(update_time_str, '%Y-%m-%d')
        else:
            logging.error(f"Unknown date format: {update_time_str}")
            return None
    except Exception as e:
        logging.error(f"Failed to parse time string: {update_time_str}, error: {str(e)}")
        return None

def get_extension_info(extension_id):
    """
    Get Chrome extension name, version and update time
    
    Args:
        extension_id: Chrome extension ID
    
    Returns:
        tuple: (name, version, update_time), returns None for failed items
    """
    url = f"https://chromewebstore.google.com/detail/{extension_id}"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        tree = html.fromstring(response.content)
        
        # Get name, version and update time
        name_element = tree.xpath('//*[@id="yDmH0d"]/c-wiz/div/div/main/div/section[1]/section/div[1]/div[1]/h1')
        version_element = tree.xpath('//*[@id="yDmH0d"]/c-wiz/div/div/main/div/section[4]/div[2]/ul/li[1]/div[2]')
        update_time_element = tree.xpath('//*[@id="yDmH0d"]/c-wiz/div/div/main/div/section[4]/div[2]/ul/li[2]/div[2]')
        
        name = name_element[0].text.strip() if name_element else None
        version = version_element[0].text.strip() if version_element else None
        update_time = update_time_element[0].text.strip() if update_time_element else None
        
        return name, version, update_time
            
    except requests.RequestException as e:
        logging.error(f"Failed to get extension info: {e}")
        return None, None, None

def scheduled_task():
    """
    Task to be executed on schedule
    """
    # Get extension IDs list from config
    extension_ids = config['extensions']
    
    # Run async function using asyncio.run
    asyncio.run(check_extensions_async(extension_ids, min_delay=1, max_delay=3))

def main():
    logging.info(f"Starting scheduled task, will check extensions at {CHECK_TIME} daily...")
    
    # Schedule daily execution at configured time
    schedule.every().day.at(CHECK_TIME).do(scheduled_task)
    
    # Execute immediately on startup
    scheduled_task()
    
    # Keep running and wait for scheduled tasks
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main() 