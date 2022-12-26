#!/bin/bash

SINGLE_FLAP=$1
SINGLE_FILE=$(echo "${SINGLE_FLAP}" | tr ' ' '_' )

mkdir -p tmp

for LAYER in 0 1 2
do
    OpenSCAD -o tmp/flap_${SINGLE_FILE}_${LAYER}.stl flaps.scad -D LAYER=${LAYER} -D COUNT=1 -D COLOR_FLAP='"$&#"' -D SINGLE_FLAP='"'${SINGLE_FLAP}'"'
done

