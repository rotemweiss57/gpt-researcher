#!/usr/bin/env bash

yum install -y libxml2-devel libxslt-devel python-devel redhat-rpm-config libffi-devel cairo pango

export PKG_CONFIG_PATH=/usr/lib64/pkgconfig:/usr/lib/pkgconfig
export PATH=/usr/bin:$PATH
export LDFLAGS=-L/usr/lib64:/usr/lib
export LD_LIBRARY_PATH=/usr/lib64:/usr/lib
export CPPFLAGS=-I/usr/include

sudo yum-config-manager --enable epel
sudo yum update -y
sudo yum install -y gcc gcc-c++ glib2-devel libxml2-devel libpng-devel \
libjpeg-turbo-devel gobject-introspection gobject-introspection-devel

wget http://ftp.gnome.org/pub/GNOME/sources/libcroco/0.6/libcroco-0.6.8.tar.xz
tar xvfJ libcroco-0.6.8.tar.xz
cd libcroco-0.6.8
./configure --prefix=/usr
make
sudo make install
cd ..

wget http://ftp.gnome.org/pub/GNOME/sources/gdk-pixbuf/2.28/gdk-pixbuf-2.28.2.tar.xz
tar xvfJ gdk-pixbuf-2.28.2.tar.xz
cd gdk-pixbuf-2.28.2
./configure --prefix=/usr --without-libtiff
make
sudo make install
cd ..

sudo yum install -y pixman-devel harfbuzz-devel freetype-devel

wget http://www.freedesktop.org/software/fontconfig/release/fontconfig-2.13.93.tar.gz
tar xvf fontconfig-2.13.93.tar.gz
cd fontconfig-2.13.93
./configure --prefix=/usr --enable-libxml2
make
sudo make install
cd ..

wget http://cairographics.org/releases/cairo-1.16.0.tar.xz
tar xvfJ cairo-1.16.0.tar.xz
cd cairo-1.16.0
./configure --prefix=/usr
make
sudo make install
cd ..

wget http://ftp.gnome.org/pub/GNOME/sources/pango/1.48/pango-1.48.4.tar.xz
tar xvfJ pango-1.48.4.tar.xz
cd pango-1.48.4
./configure --prefix=/usr
make
sudo make install
cd ..

wget http://ftp.gnome.org/pub/GNOME/sources/librsvg/2.40/librsvg-2.40.6.tar.xz
tar xvfJ librsvg-2.40.6.tar.xz
cd librsvg-2.40.6
./configure --prefix=/usr
make
sudo make install
cd ..

sudo ldconfig /usr/lib

cd /tmp/
sudo wget https://chromedriver.storage.googleapis.com/80.0.3987.106/chromedriver_linux64.zip
sudo unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/bin/chromedriver
chromedriver --version

sudo curl https://intoli.com/install-google-chrome.sh | bash
sudo mv /usr/bin/google-chrome-stable /usr/bin/google-chrome
google-chrome --version && which google-chrome
