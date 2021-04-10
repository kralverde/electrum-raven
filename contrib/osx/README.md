Building MacOS binaries
========================

This guide explains how to build Electrum binaries for macOS systems.

## Building macOS version dependent binaries

- Install [Xcode](https://apps.apple.com/us/app/xcode/id497799835)
- Install [Homebrew](https://brew.sh/)
- Install and set up pyenv: 
```
   brew install pyenv 
   echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bash_profile
   echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bash_profile
   echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n  eval "$(pyenv init -)"\nfi' >> ~/.bash_profile
   echo 'export PATH="$PATH:$HOME/.local/bin/"' >> ~/.bash_profile
   source ~/.bash_profile
```
- Install python 3.6.4 [using a homebrew patch](https://github.com/Homebrew/homebrew-core/blob/master/Formula/python@3.8.rb#L74) 
```
   PYTHON_VERSION=3.6.4
   PYTHON_CONFIGURE_OPTS="--enable-framework" pyenv install --patch 3.6.4 < <(curl -sSL https://github.com/python/cpython/commit/8ea6353.patch) && \
   pyenv global $PYTHON_VERSION
```
- Make sure to get an up to date and working pip
```
   curl https://bootstrap.pypa.io/get-pip.py | python3
```
- Install cmake to build e.g., kawpow
```
   brew install cmake
```
- Build electrum-raven
```
   cd electrum-raven
   ./contrib/osx/make_osx
```

This creates both a folder named Electrum.app and the .dmg file.

## Building version independent binaries (untested for electrum-raven)

This needs to be done on a system running macOS or OS X. We use El Capitan (10.11.6) as building it
on High Sierra (or later) makes the binaries [incompatible with older versions](https://github.com/pyinstaller/pyinstaller/issues/1191).

Another factor for the minimum supported macOS version is the
[bundled Qt version](https://github.com/spesmilo/electrum/issues/3685).

Before starting, make sure that the Xcode command line tools are installed (e.g. you have `git`).

#### Get Xcode

Building the QR scanner (CalinsQRReader) requires full Xcode (not just command line tools).

The last Xcode version compatible with El Capitan is Xcode 8.2.1

Get it from [here](https://developer.apple.com/download/more/).

Unfortunately, you need an "Apple ID" account.

After downloading, uncompress it.

Make sure it is the "selected" xcode (e.g.):

    sudo xcode-select -s $HOME/Downloads/Xcode.app/Contents/Developer/

#### (Optional) Build QR scanner separately on newer Mac 

Alternatively, you can try building just the QR scanner on newer macOS.

On newer Mac, run:

    pushd contrib/osx/CalinsQRReader; xcodebuild; popd
    cp -r contrib/osx/CalinsQRReader/build prebuilt_qr

Move `prebuilt_qr` to El Capitan: `contrib/osx/CalinsQRReader/prebuilt_qr`.


#### Build Electrum

    cd electrum-raven
    ./contrib/osx/make_osx
    
This creates both a folder named Electrum.app and the .dmg file.


## Building the image deterministically (WIP) (untested for electrum-raven)
The usual way to distribute macOS applications is to use image files containing the 
application. Although these images can be created on a Mac with the built-in `hdiutil`,
they are not deterministic.

Instead, we use the toolchain that Bitcoin uses: genisoimage and libdmg-hfsplus.
These tools do not work on macOS, so you need a separate Linux machine (or VM).

Copy the Electrum.app directory over and install the dependencies, e.g.:

    apt install libcap-dev cmake make gcc faketime
    
Then you can just invoke `package.sh` with the path to the app:

    cd electrum
    ./contrib/osx/package.sh ~/Electrum.app/
