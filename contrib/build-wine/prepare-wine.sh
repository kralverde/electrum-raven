#!/bin/bash

# Please update these carefully, some versions won't work under Wine
NSIS_FILENAME=nsis-3.04-setup.exe
NSIS_URL=https://prdownloads.sourceforge.net/nsis/$NSIS_FILENAME?download
NSIS_SHA256=4e1db5a7400e348b1b46a4a11b6d9557fd84368e4ad3d4bc4c1be636c89638aa

X16R_HASH_FILENAME=x16r_hash-1.0-cp36-cp36m-win32.whl
X16R_HASH_PYTHON_URL=https://files.pythonhosted.org/packages/2e/ae/dabd6df3d3d148bbd19305c0c8e415f4ffd6e67646a67e0689e5a48cdb58/$X16R_HASH_FILENAME
X16R_HASH_SHA256=c0c73fce1dd3cc40bb3a31ad1865917ad1d4ff2dfc747790f65746aa590a1f22

LIB_GCC_FILENAME=libgcc-6.3.0-1-mingw32-dll-1.tar.xz
LIB_GCC_URL=https://netix.dl.sourceforge.net/project/mingw/MinGW/Base/gcc/Version6/gcc-6.3.0/$LIB_GCC_FILENAME
LIB_GCC_SHA256=8cbfa963f645cc0f81c08df2a3ecbcefc776606f0fb9db7a280d79f05209a1c3

ZBAR_FILENAME=zbarw-20121031-setup.exe
ZBAR_URL=https://astuteinternet.dl.sourceforge.net/project/zbarw/$ZBAR_FILENAME
ZBAR_SHA256=177e32b272fa76528a3af486b74e9cb356707be1c5ace4ed3fcee9723e2c2c02

LIBUSB_FILENAME=libusb-1.0.22.7z
LIBUSB_URL=https://prdownloads.sourceforge.net/project/libusb/libusb-1.0/libusb-1.0.22/$LIBUSB_FILENAME?download
LIBUSB_SHA256=671f1a420757b4480e7fadc8313d6fb3cbb75ca00934c417c1efa6e77fb8779b

PYTHON_VERSION=3.6.8

## These settings probably don't need change
export WINEPREFIX=/opt/wine64
#export WINEARCH='win32'

PYTHON_FOLDER="python3"
PYHOME="c:/$PYTHON_FOLDER"
PYTHON="wine $PYHOME/python.exe -OO -B"


# based on https://superuser.com/questions/497940/script-to-verify-a-signature-with-gpg
verify_signature() {
    local file=$1 keyring=$2 out=
    if out=$(gpg --no-default-keyring --keyring "$keyring" --status-fd 1 --verify "$file" 2>/dev/null) &&
       echo "$out" | grep -qs "^\[GNUPG:\] VALIDSIG "; then
        return 0
    else
        echo "$out" >&2
        exit 1
    fi
}

verify_hash() {
    local file=$1 expected_hash=$2
    actual_hash=$(sha256sum $file | awk '{print $1}')
    if [ "$actual_hash" == "$expected_hash" ]; then
        return 0
    else
        echo "$file $actual_hash (unexpected hash)" >&2
        rm "$file"
        exit 1
    fi
}

download_if_not_exist() {
    local file_name=$1 url=$2
    if [ ! -e $file_name ] ; then
        wget -O "$PWD/$file_name" "$url"
    fi
}

# https://github.com/travis-ci/travis-build/blob/master/lib/travis/build/templates/header.sh
retry() {
  local result=0
  local count=1
  while [ $count -le 3 ]; do
    [ $result -ne 0 ] && {
      echo -e "\nThe command \"$@\" failed. Retrying, $count of 3.\n" >&2
    }
    ! { "$@"; result=$?; }
    [ $result -eq 0 ] && break
    count=$(($count + 1))
    sleep 1
  done

  [ $count -gt 3 ] && {
    echo -e "\nThe command \"$@\" failed 3 times.\n" >&2
  }

  return $result
}

# Let's begin!
here="$(dirname "$(readlink -e "$0")")"
set -e

. $here/../build_tools_util.sh

wine 'wineboot'


cd /tmp/electrum-rvn-build

# Install Python
# note: you might need "sudo apt-get install dirmngr" for the following
# keys from https://www.python.org/downloads/#pubkeys
KEYLIST_PYTHON_DEV="531F072D39700991925FED0C0EDDC5F26A45C816 26DEA9D4613391EF3E25C9FF0A5B101836580288 CBC547978A3964D14B9AB36A6AF053F07D9DC8D2 C01E1CAD5EA2C4F0B8E3571504C367C218ADD4FF 12EF3DC38047DA382D18A5B999CDEA9DA4135B38 8417157EDBE73D9EAC1E539B126EB563A74B06BF DBBF2EEBF925FAADCF1F3FFFD9866941EA5BBD71 2BA0DB82515BBB9EFFAC71C5C9BE28DEE6DF025C 0D96DF4D4110E5C43FBFB17F2D347EA6AA65421D C9B104B3DD3AA72D7CCB1066FB9921286F5E1540 97FC712E4C024BBEA48A61ED3A5CA953F73C700D 7ED10B6531D7C8E1BC296021FC624643487034E5"
KEYRING_PYTHON_DEV="keyring-electrum-build-python-dev.gpg"
for server in $(shuf -e ha.pool.sks-keyservers.net \
                        hkp://p80.pool.sks-keyservers.net:80 \
                        keyserver.ubuntu.com \
                        hkp://keyserver.ubuntu.com:80) ; do
    retry gpg --no-default-keyring --keyring $KEYRING_PYTHON_DEV --keyserver "$server" --recv-keys $KEYLIST_PYTHON_DEV \
    && break || : ;
done
for msifile in core dev exe lib pip tools; do
    echo "Installing $msifile..."
    wget -N -c "https://www.python.org/ftp/python/$PYTHON_VERSION/win32/${msifile}.msi"
    wget -N -c "https://www.python.org/ftp/python/$PYTHON_VERSION/win32/${msifile}.msi.asc"
    verify_signature "${msifile}.msi.asc" $KEYRING_PYTHON_DEV
    wine msiexec /i "${msifile}.msi" /qb TARGETDIR=$PYHOME
done

# Install dependencies specific to binaries
# note that this also installs pinned versions of both pip and setuptools
$PYTHON -m pip install -r "$here"/../deterministic-build/requirements-binaries.txt

# Install PyInstaller
$PYTHON -m pip install pyinstaller==3.4 --no-use-pep517

# Install ZBar
download_if_not_exist $ZBAR_FILENAME "$ZBAR_URL"
verify_hash $ZBAR_FILENAME "$ZBAR_SHA256"
wine "$PWD/$ZBAR_FILENAME" /S

# Install NSIS installer
download_if_not_exist $NSIS_FILENAME "$NSIS_URL"
verify_hash $NSIS_FILENAME "$NSIS_SHA256"
wine "$PWD/$NSIS_FILENAME" /S

download_if_not_exist $LIBUSB_FILENAME "$LIBUSB_URL"
verify_hash $LIBUSB_FILENAME "$LIBUSB_SHA256"
7z x -olibusb $LIBUSB_FILENAME -aoa

cp libusb/MS32/dll/libusb-1.0.dll $WINEPREFIX/drive_c/$PYTHON_FOLDER/


# install x16r_hash
$PYTHON -m pip install $X16R_HASH_PYTHON_URL

# copy from mingw for lyra2re2_hash
wget -q -O $LIB_GCC_FILENAME "$LIB_GCC_URL"
verify_hash $LIB_GCC_FILENAME $LIB_GCC_SHA256
tar Jxfv $LIB_GCC_FILENAME
cp bin/libgcc_s_dw2-1.dll $WINEPREFIX/drive_c/python$PYTHON_VERSION/Lib/site-packages/

mkdir -p $WINEPREFIX/drive_c/tmp
cp secp256k1/libsecp256k1.dll $WINEPREFIX/drive_c/tmp/

echo "Wine is configured."
