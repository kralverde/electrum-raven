kralverde's notes
=====================================

Botched together tweaks:

- Hardware (ledger) support fix
- Updated defunct default electrumx servers
- Implemented an automatic blockchain base install (based on https://github.com/standard-error/electrum-raven/releases/tag/3.3.8-rvn3)
- Crude wine docker fix

Running the software presteps (tested on ubuntu 20.04):

1. Familiarize yourself with git
2. Clone this repo
3. The rest of the steps in this temporary guide assume you are in the root of the project

Running with python3 (recommended for linux):

1. sudo apt-get install python3-pyqt5
2. sudo python3 -m pip install cmake
3. ./electrum-env

Building executables for windows:

1. Install docker (if using windows use the ubuntu vm)
2. sudo docker build -t electrum-wine-builder-img contrib/build-wine
3. Create Executables::

    $ sudo docker run -it \
        --name electrum-wine-builder-cont \
        -v $PWD:/opt/wine64/drive_c/electrum \
        --rm \
        --workdir /opt/wine64/drive_c/electrum/contrib/build-wine \
        electrum-wine-builder-img \
        ./build.sh
4. The generated binaries are in ./contrib/build-wine/dist
5. Refer to https://github.com/kralverde/electrum-raven/tree/master/contrib/build-wine for more information.

Other docker build files are currently broken

Electrum-raven - Lightweight Ravencoin client
=====================================

.. image:: https://travis-ci.com/standard-error/electrum-raven.svg?branch=master
    :target: https://travis-ci.com/standard-error/electrum-raven
    :alt: Build Status

::

  Licence: MIT Licence
  Author: Thomas Voegtlin
  Port Maintainer: standard-error@github (Electrum-raven)
  Language: Python (>= 3.6)
  Homepage: https://ravencoin.org/


.. image:: http://corvus.nbits.dev/raven.jpg
    :width: 100px
    :target: https://github.com/standard-error/electrum-raven
    :alt: Ravencoin logo


Getting started
===============

Electrum-RVN is a pure python application. If you want to use the Qt interface, install the Qt dependencies::

    sudo apt-get install python3-pyqt5

If you downloaded the official package (tar.gz), you can run
Electrum-RVN from its root directory without installing it on your
system; all the python dependencies are included in the 'packages'
directory. To run Electrum-RVN from its root directory, just do::

    ./run_electrum

You can also install Electrum-RVN on your system, by running these commands::

    cd ~
    virtualenv -p /usr/local/bin/python3.7 pve
    source ~/pve/bin/activate
    git clone https://github.com/standard-error/electrum-raven
    cd electrum-raven
    pip3 install x16r-hash x16rv2-hash pyqt5
    python3 -m pip install .[fast]

This will download and install the Python dependencies used by
Electrum-RVN instead of using the 'packages' directory.
The 'fast' extra contains some optional dependencies that we think
are often useful but they are not strictly needed.

If you cloned the git repository, you need to compile extra files
before you can run Electrum-RVN. Read the next section, "Development
Version".



Development version
===================

Check out the code from GitHub::

    git clone git://github.com/standard-error/electrum-raven.git
    cd electrum-raven

Run install (this should install dependencies)::

    python3 -m pip install .[fast]


Compile the protobuf description file::

    sudo apt-get install protobuf-compiler
    protoc --proto_path=electrum --python_out=electrum electrum/paymentrequest.proto

Create translations (optional)::

    sudo apt-get install python-requests gettext
    ./contrib/pull_locale



Creating Binaries
=================

Linux (tarball)
---------------

See :code:`contrib/build-linux/README.md`.


Linux (AppImage)
----------------

See :code:`contrib/build-linux/appimage/README.md`.


Mac OS X / macOS
----------------

See :code:`contrib/osx/README.md`.


Windows
-------

See :code:`contrib/build-wine/README.md`.


Android
-------

See :code:`electrum/gui/kivy/Readme.md`.
