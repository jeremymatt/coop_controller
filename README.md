coop_controller

Setup steps:
1. Set up your Raspberry pi using the Rasberry Pi imager
1. Clone the git repo: `git clone https://github.com/jeremymatt/coop_controller ~/coop_controller`
1. Navigate to the coop controller directory: `cd ~/coop_controller`
1. Save the `sample_settings.py` file as `settings.py` and add your specific information:
    * ngrok static URL
    * names/phone numbers
    * latitude and longitude of your coop
1. run `./install.sh`
1. add your ngrok key with `ngrok config add-authtoken <your_ngrok_key>`.  Your key can be obtained from the [Ngrok setup & installation page](https://dashboard.ngrok.com/get-started/setup/linux)