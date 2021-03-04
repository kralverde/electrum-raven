Notes from kralverde
=====================================
Future notes will go here....
(RVN Tips if you're feeling generous: RDRczYCUeLwXVnrKMYHKYLS1oPc9aCxGnG)

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
