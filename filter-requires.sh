#!/bin/sh

if [ -x /usr/lib/rpm/redhat/find-provides ]; then
   FINDREQ=/usr/lib/rpm/redhat/find-requires
else
   FINDREQ=/usr/lib/rpm/find-requires
fi

$FINDREQ $* | sed -e '/libnvidia-tls.so/d' | sed -e '/libGLcore.so/d'

