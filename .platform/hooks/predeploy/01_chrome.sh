#!/bin/bash

# Install Google Chrome
curl -sS https://intoli.com/install-google-chrome.sh | bash || exit 1
mv -f /usr/bin/google-chrome-stable /usr/bin/google-chrome || exit 1
google-chrome --version && which google-chrome || exit 1

# Clean up temporary files
rm chromedriver_linux64.zip

echo "Google Chrome installation completed successfully."
