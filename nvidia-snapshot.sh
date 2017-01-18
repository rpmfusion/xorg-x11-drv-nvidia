#!/bin/bash

set -e

tmp=$(mktemp -d)

trap cleanup EXIT
cleanup() {
    set +e
    [ -z "$tmp" -o ! -d "$tmp" ] || rm -rf "$tmp"
}

unset CDPATH
pwd=$(pwd)
nvspec=$(ls ${pwd}/xorg-x11-drv-nvidia*.spec)
version=$(grep ^Version: ${nvspec} | awk '{print $2}')
arches="$(grep ^ExclusiveArch: ${nvspec} | awk '{print $2,$3,$4}')"

for arch in ${arches} ; do
 nvarch=${arch}
 [ ${arch} == i686 ]  && nvarch=x86
 [ ${arch} == armv7hl ]  && nvarch=armv7l-gnueabihf
 if [ ! -e NVIDIA-Linux-${nvarch}-${version}.run ] ; then
    spectool --gf -S ${nvspec}
 fi
done

