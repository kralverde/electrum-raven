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

Electrum-raven is a pure python application. If you want to use the Qt interface, install the Qt dependencies::

    sudo apt-get install python3-pyqt5

If you downloaded the official package (tar.gz), you can run Electrum-raven from its root directory, without installing it on your system; all the python dependencies are included in the 'packages' directory. To run Electrum-raven from its root directory, just do::

    ./run_electrum

You can also install Electrum-raven on your system, by running these commands::

    cd ~
    virtualenv -p /usr/local/bin/python3.7 pve
    source ~/pve/bin/activate
    git clone https://github.com/standard-error/electrum-raven
    cd electrum-raven
    pip3 install x16r-hash x16rv2-hash pyqt5
    python3 -m pip install .[fast]
    pyrcc5 icons.qrc -o electrum/gui/qt/icons_rc.py
    ./run_electrum

Creating Binaries
=================

To create binaries, create the 'packages' directory::

    ./contrib/make_packages

This directory contains the python dependencies used by Electrum-raven.

Mac OS X / macOS
--------

See `contrib/build-osx/`.

Windows
-------

See `contrib/build-wine/`.


Android
-------

See `electrum/gui/kivy/Readme.md` file.
