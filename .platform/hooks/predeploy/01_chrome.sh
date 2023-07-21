#!/bin/bash

# Download ChromeDriver
cd /tmp
wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/115.0.5790.98/linux64/chromedriver-linux64.zip || exit 1
unzip -o chromedriver_linux64.zip || exit 1

# Move ChromeDriver to /usr/bin/
mv -f chromedriver /usr/bin/chromedriver || exit 1
chromedriver --version || exit 1

# Download Google Chrome
wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/115.0.5790.98/linux64/chrome-linux64.zip || exit 1
unzip -o chrome-linux64.zip || exit 1

# Move Chrome to /usr/bin/
mv -f chrome /usr/bin/chrome || exit 1
chrome --version && which chrome || exit 1

# Clean up temporary files
rm chromedriver_linux64.zip chrome-linux64.zip

echo "ChromeDriver and Google Chrome installation completed successfully."
