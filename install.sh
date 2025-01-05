#!/bin/bash
curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc \
	| sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null \
	&& echo "deb https://ngrok-agent.s3.amazonaws.com buster main" \
	| sudo tee /etc/apt/sources.list.d/ngrok.list \
	&& sudo apt update \
	&& sudo apt install ngrok

#!/bin/bash

# Install virtualenv if not already installed
sudo apt-get install virtualenv -y

# Create the virtual environment in $HOME/.venv
virtualenv -q -p /usr/bin/python $HOME/.venv

# Check if the activation script exists
if [ -f "$HOME/.venv/bin/activate" ]; then
  # Activate the virtual environment
  source "$HOME/.venv/bin/activate"
else
  echo "Error: Failed to create virtual environment at $HOME/.venv"
  exit 1
fi

# Install the required dependencies
pip install -r requirements.txt

# Generate a secret key and store it in a credentials file
SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
CREDENTIALS_FILE="$HOME/coop_controller/flask_credentials.env"

mkdir -p "$HOME/coop_controller"  # Ensure the directory exists
echo "FLASK_SECRET_KEY=$SECRET_KEY" > "$CREDENTIALS_FILE"
chmod 600 "$CREDENTIALS_FILE"  # Restrict permissions to the file

# Inform the user
echo "A secret key has been generated and stored in $CREDENTIALS_FILE"

# Define the cron job
CRON_ENTRY="@reboot $HOME/.venv/bin/python $HOME/coop_controller/coop_controller.py > $HOME/coop_controller/cron.log 2>&1"

# Check if the entry already exists to avoid duplicates
(crontab -l 2>/dev/null | grep -Fx "$CRON_ENTRY") || (crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -

echo "Cron job added successfully. Use 'crontab -l' to verify."

echo "enabling i2c"
sudo sudo raspi-config nonint do_i2c 0
echo "Generate credentials-config file.  Enter username and password for web interface:"
$HOME/.venv/bin/python $HOME/coop_controller/generate_credentials-config.py