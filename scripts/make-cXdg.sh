#! /bin/bash

if [[ -n $1 ]]
then
  PYXDG_VERSION="$1"
else
  echo "No package version specified"
  exit 1
fi

if [[ -n $2 ]]
then
  ARCH="$2"
else
  ARCH=$(uname -m)
fi


APP_DIR=$(dirname $(readlink -f $0))
CXDG_DIR=$APP_DIR/../src/cXdg

echo "======================================="
echo "Will now try to build cXdg extension..."

pushd $CXDG_DIR

# Extract source tarball...
TARBALL="pyxdg-$PYXDG_VERSION.tar.gz"
if [[ -f $TARBALL ]]
then
  rm -R "pyxdg-$PYXDG_VERSION" 2> /dev/null
  echo "Extracting $TARBALL..."
  tar -xvf "$TARBALL" > /dev/null
else
  echo "Tarball $TARBALL not found"
  exit 1
fi

# Copy the source dir to cXdg
SOURCE_DIR=cXdg
if [[ -d ./cXdg ]]
then
  rm -R ./cXdg
fi
cp -R "pyxdg-$PYXDG_VERSION/xdg" ./cXdg

# Replace all references to xdg. by cXdg.
sed -i 's/xdg\./cXdg\./g' ./cXdg/*.py

# test if everything works
echo "Running preliminary tests..."
if ./test.py
then
  echo "Tests passed"
else
  echo "Something went wrong while testing the library..."
  exit 1
fi

# Backup __init__.py
mkdir ./tmp
cp ./cXdg/__init__.py ./tmp

# Rename .py files to .pyx
rename 's/(.*)\.py$/$1.pyx/' ./cXdg/*.py

# Compile everything !
echo "Compiling cXdg extension, please wait..."
python setup.py build_ext -p "$ARCH" > /dev/null

# Remove the source tree and copy build dir to cXdg
rm -R ./cXdg
cp -R ./build/lib.linux-$ARCH-*/cXdg ./cXdg

# reintroduce __init__.py
mv ./tmp/__init__.py ./cXdg
rm -R ./tmp

# And re-test
echo "Running final tests..."
if ./test.py
then
  echo "Tests passed"
else
  echo "Something went wrong while testing the library..."
  exit 1
fi

# Everything is OK, so move files in the right place
mv ./cXdg $APP_DIR/../usr/lib/fluxdgmenu

# Clean up and exit
rm -R ./build "./pyxdg-$PYXDG_VERSION"

popd

exit 0
