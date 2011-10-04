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
version=$(grep Version xorg-x11-drv-nvidia*.spec | cut -f 2 -d ':' | sed 's/ //g')

for arch in x86 x64 ; do
 if [ ! -e NVIDIA-Linux-${arch}-${version}.run ] ; then
  wget -N ftp://download.nvidia.com/XFree86/Linux-${arch}/${version}/NVIDIA-Linux-${arch}-${version}.run
 fi
 sh NVIDIA-Linux-${arch}-${version}.run --extract-only --target nvidiapkg-${arch}
done

tar -cjf nvidia-kmod-data-${version}.tar.bz2 nvidiapkg-*/LICENSE nvidiapkg-*/kernel

