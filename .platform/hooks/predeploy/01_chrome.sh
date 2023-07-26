#!/bin/bash

# Check if Google Chrome is already installed
if ! command -v google-chrome &> /dev/null
then
    # Install Google Chrome
    curl -sS https://intoli.com/install-google-chrome.sh | bash
    if [ $? -ne 0 ]; then
        echo "Failed to install Google Chrome"
        exit 1
    fi
    mv -f /usr/bin/google-chrome-stable /usr/bin/google-chrome
    if [ $? -ne 0 ]; then
        echo "Failed to move Google Chrome executable"
        exit 1
    fi
else
    echo "Google Chrome is already installed"
fi

# Print the version and location
google-chrome --version && which google-chrome

# Check if the temporary file exists before trying to remove it
if [ -f "chromedriver_linux64.zip" ]; then
    rm chromedriver_linux64.zip
fi

echo "Google Chrome installation script completed successfully."
