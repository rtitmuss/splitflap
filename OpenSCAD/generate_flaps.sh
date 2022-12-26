#!/bin/bash

mkdir -p stl/letters
mkdir stl/umlaute
mkdir stl/no_umlaute
mkdir stl/color

for LAYER in 0 1 2
do
    OpenSCAD -o stl/letters/flap_AY_${LAYER}.stl flaps.scad -D LAYER=${LAYER} -D SET=0

    # with umlaute
    OpenSCAD -o stl/umlaute/flap_umlaute_Z!_${LAYER}.stl flaps.scad -D LAYER=${LAYER} -D SET=1 \
        -D LETTERS='" ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÜ0123456789:.-?! "'

    # with no umlaute
    OpenSCAD -o stl/no_umlaute/flap_no_umlaute_Z!_${LAYER}.stl flaps.scad -D LAYER=${LAYER} -D SET=1 \
        -D LETTERS='" ABCDEFGHIJKLMNOPQRSTUVWXYZ$&#0123456789:.-?! "'

    # with colored flaps
    OpenSCAD -o stl/color/flap_color_Z#_${LAYER}.stl flaps.scad -D LAYER=${LAYER} -D SET=1 -D COLOR_FLAP='"$&# "' \
        -D LETTERS='" ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789:.-?!$&# "'

    OpenSCAD -o stl/color/flap_color_\!\$_${LAYER}.stl flaps.scad -D LAYER=${LAYER} -D COLOR_FLAP='"$&#"' -D SINGLE_FLAP='"!$"' \
        -D LETTERS='" ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789:.-?!$&# "' 
    OpenSCAD -o stl/color/flap_color_\$\&_${LAYER}.stl flaps.scad -D LAYER=${LAYER} -D COLOR_FLAP='"$&#"' -D SINGLE_FLAP='"$&"' \
        -D LETTERS='" ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789:.-?!$&# "' 
    OpenSCAD -o stl/color/flap_color_\&\#_${LAYER}.stl flaps.scad -D LAYER=${LAYER} -D COLOR_FLAP='"$&#"' -D SINGLE_FLAP='"&#"' \
        -D LETTERS='" ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789:.-?!$&# "' 
    OpenSCAD -o stl/color/flap_color_\#\ _${LAYER}.stl flaps.scad -D LAYER=${LAYER} -D COLOR_FLAP='"$&#"' -D SINGLE_FLAP='"# "' \
        -D LETTERS='" ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789:.-?!$&# "' 

done

