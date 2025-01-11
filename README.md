# Chrome Extension Update Monitor

A Python application that monitors Chrome Web Store extensions for updates and sends notifications via Telegram.

## Features

- Monitors multiple Chrome extensions for updates
- Sends notifications through Telegram when updates are detected
- Configurable check schedule and update detection period
- Easy to configure through YAML file

## Prerequisites

- Python 3.7 or higher
- A Telegram bot token
- A Telegram account

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd chrome-extension-monitor
```

2. Create a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create configuration file:

```bash
cp config.yaml.example config.yaml
```

## Configuration

Edit `config.yaml` with your settings:

```yaml
# Telegram configuration
telegram:
  bot_token: "YOUR_BOT_TOKEN"
  chat_id: "YOUR_CHAT_ID"

# Schedule configuration
schedule:
  check_time: "11:00"  # Daily check time (24-hour format)
  check_days: 3        # Number of days to check for updates

# Extensions to monitor (ID list)
extensions:
  - "extension_id_1"
  - "extension_id_2"
```

### Configuration Parameters

- `telegram.bot_token`: Your Telegram bot token
- `telegram.chat_id`: Your Telegram chat ID
- `schedule.check_time`: Time to perform daily checks (24-hour format)
- `schedule.check_days`: Number of days to look back for updates
- `extensions`: List of Chrome extension IDs to monitor

### How to Get Telegram Parameters

1. Create a Telegram Bot:
   - Open Telegram and search for `@BotFather`
   - Send `/newbot` command
   - Follow the instructions to create your bot
   - Copy the bot token provided

2. Get Your Chat ID:
   - Send a message to your bot
   - Visit `https://api.telegram.org/bot<YourBOTToken>/getUpdates`
   - Look for `"chat":{"id":123456789}` in the response
   - Copy the chat ID number

### How to Get Chrome Extension IDs

1. Visit the Chrome Web Store page of the extension
2. The ID is the string in the URL after `detail/`
   - Example: For `https://chromewebstore.google.com/detail/abcdefghijklmnop`
   - The ID is `abcdefghijklmnop`

## Running the Application

1. Start the monitor:
```bash
python main.py
```

The application will:
- Start immediately with a first check
- Run checks daily at the configured time
- Send Telegram notifications for extensions updated within the configured period

## Logging

The application logs its activities with timestamps and error information. Monitor the console output or redirect to a log file:

```bash
python main.py > monitor.log 2>&1
```

## Running as a Background Service

### On Linux (using systemd)

1. Create a service file:
```bash
sudo nano /etc/systemd/system/chrome-extension-monitor.service
```

2. Add the following content (adjust paths as needed):
```ini
[Unit]
Description=Chrome Extension Update Monitor
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/chrome-extension-monitor
ExecStart=/path/to/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

3. Enable and start the service:
```bash
sudo systemctl enable chrome-extension-monitor
sudo systemctl start chrome-extension-monitor
```

## Project Structure

```
chrome-extension-monitor/
├── main.py              # Main application script
├── config.yaml          # Configuration file (create from example)
├── config.yaml.example  # Example configuration file
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## License

[MIT License](LICENSE)
