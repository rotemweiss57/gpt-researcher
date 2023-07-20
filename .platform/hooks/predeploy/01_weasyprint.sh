#!/usr/bin/env bash

declare -a packages=("libxml2-devel" "libxslt-devel" "python-devel" "redhat-rpm-config" "libffi-devel" "cairo" "pango")

for package in "${packages[@]}"; do
    if ! rpm -q $package; then
        yum install -y $package
    fi
done

export PKG_CONFIG_PATH=/usr/lib64/pkgconfig:/usr/lib/pkgconfig
export PATH=/usr/bin:$PATH
export LDFLAGS=-L/usr/lib64:/usr/lib
export LD_LIBRARY_PATH=/usr/lib64:/usr/lib
export CPPFLAGS=-I/usr/include

sudo yum-config-manager --enable epel

sudo yum update -y

declare -a packages2=("gcc" "gcc-c++" "glib2-devel" "libxml2-devel" "libpng-devel" "libjpeg-turbo-devel" "gobject-introspection" "gobject-introspection-devel")

for package in "${packages2[@]}"; do
    if ! rpm -q $package; then
        yum install -y $package
    fi
done

if [ ! -f /usr/lib/libcroco-0.6.8/libcroco.la ]; then
    wget http://ftp.gnome.org/pub/GNOME/sources/libcroco/0.6/libcroco-0.6.8.tar.xz
    tar xvfJ libcroco-0.6.8.tar.xz
    cd libcroco-0.6.8
    ./configure --prefix=/usr
    make
    sudo make install
    cd ..
fi

if [ ! -f /usr/lib/gdk-pixbuf-2.0/2.10.0/loaders/libpixbufloader-svg.so ]; then
    wget http://ftp.gnome.org/pub/GNOME/sources/gdk-pixbuf/2.28/gdk-pixbuf-2.28.2.tar.xz
    tar xvfJ gdk-pixbuf-2.28.2.tar.xz
    cd gdk-pixbuf-2.28.2
    ./configure --prefix=/usr --without-libtiff
    make
    sudo make install
    cd ..
fi

if [ ! -f /usr/lib/pkgconfig/fontconfig.pc ]; then
    wget http://www.freedesktop.org/software/fontconfig/release/fontconfig-2.13.93.tar.gz
    tar xvf fontconfig-2.13.93.tar.gz
    cd fontconfig-2.13.93
    ./configure --prefix=/usr --enable-libxml2
    make
    sudo make install
    cd ..
fi

if [ ! -f /usr/lib/libcairo.so ]; then
    wget http://cairographics.org/releases/cairo-1.16.0.tar.xz
    tar xvfJ cairo-1.16.0.tar.xz
    cd cairo-1.16.0
    ./configure --prefix=/usr
    make
    sudo make install
    cd ..
fi

if [ ! -f /usr/lib/libpango-1.0.so ]; then
    wget http://ftp.gnome.org/pub/GNOME/sources/pango/1.48/pango-1.48.4.tar.xz
    tar xvfJ pango-1.48.4.tar.xz
    cd pango-1.48.4
    ./configure --prefix=/usr
    make
    sudo make install
    cd ..
fi

if [ ! -f /usr/lib/librsvg-2.so ]; then
    wget http://ftp.gnome.org/pub/GNOME/sources/librsvg/2.40/librsvg-2.40.6.tar.xz
    tar xvfJ librsvg-2.40.6.tar.xz
    cd librsvg-2.40.6
    ./configure --prefix=/usr
    make
    sudo make install
    cd ..
fi

sudo ldconfig /usr/lib


cd /tmp/

sudo curl https://intoli.com/install-google-chrome.sh | bash
sudo mv -f /usr/bin/google-chrome-stable /usr/bin/google-chrome
google-chrome --version && which google-chrome

