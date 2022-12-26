# 3d printed Split Flap Generator

This is an OpenSCAD program to generate 3d printed Flaps compatible with [Split Flap Display by David Kingsman](https://www.printables.com/model/69464-split-flap-display).

This generator is useful if you want to:
- Fit more flaps on the build plate, the Prusa Mk3 can print up to 25 flaps at once
- Easily change the letters or ordering of your flaps
- Fixes 'W' to be full height
- Supports flaps with a solid color
- Customise the font or size of the letters

You will need to install the [Expressway Condensed Bold font](https://fontsgeek.com/fonts/Expressway-Condensed-Bold).

## Creating flap STL files

The  `generate_flaps.sh` shows how to create the STL files. You need three STL files for the different layers, the top and bottom layers contain letter halfs, and the middle layer is the flap.

This script outputs several STL files in different directories:
- **letters**: The basic 25 letters Space A-Y.

You also need to pick one of the following. 
- **umlaute**: Z, ÄÖÜ, numbers and symbols; matches the letters on [Split Flap Display](https://www.printables.com/model/69464-split-flap-display).
- **no_umlaute**: Z, numbers and symbols; matches the no umlaute letters on [Split Flap Display](https://www.printables.com/model/69464-split-flap-display).
- **color**: Z, numbers and symbols; replaces $&# with three single color flaps

You may want to generate STL files for single flaps, for example to fix failed prints. You can do this with  `single_flap.sh`, this creates the B/C flap:
```
./single_flap.sh BC
```

## Prusaslicer

The flaps are printed by changing the color mid-print and mid-layer. To enable this in Prusaslicer  make sure that you are in  **Advanced Mode**, or  **Expert mode**  

- In the 'Printer settings>General' tab, and increase the number of extruders to '**2**'
- In the 'Printer settings>Custom Gcode' tab, and open the Tool Change Gcode box... and type in **M600**

Then load the three STL files, for example `flap_AY_0.stl`, `flap_AY_1.stl` and  `flap_AY_2.stl`. In the 'Multi-part object detected' dialog, select **Yes**.

You can then slice and generate the gcode. Optionally edit the gcode file and delete the first M600 instruction, then you don't need to change the filament every time the print starts. Start with the letter color filament (eg white). Part way through the print the printer will stop and bleep, you now need to change to the flap filament (eg black). Follow the instructions on the printer. There will be a wormcast of waste filament - don't pull it off, just hold it and answer that the color is clear. As the printer resumes printing it will expel a little more filament, now is the time to pull it off and discard it. This will happen several times during the print.

## Customization

You can make customizations in `flaps.scad`. For example to change the number of flaps on the build plate, or to try different fonts (hint: the font needs to be narrow to work).

