
// Number of flaps to print in eash set
ROWS = 5;
COLS = 5;

FLAPS = ROWS * COLS;

// Font for the letters
FONT = "Expressway";
FONT_SIZE = 57;
// W needs to be smaller to fit
FONT_SCALE_W = 0.8;

// Thickness of the flap and letters
FLAP_THICKNESS = 1;
LETTER_THICKNESS = 0.4;

// Change this to customise the letters / ordering
// ' ' should be the first and last characters
LETTERS = " ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789:.-?!$&# ";

// Replace these letters with a solid colored flap
COLOR_FLAP = "";

// Set these variables from generation script
LAYER = 1;              // Layer [0, 1, 2] to render
SET = 0;                // Set to render [0, 1] for 5 rows & cols

SINGLE_FLAP = false;    // Letters for a single flap
COUNT = 4;             // Number of single letters

if (SINGLE_FLAP) {
    // Run FlapLetter for the colored flaps
    FlapLetter(SINGLE_FLAP, LAYER, COUNT);
} else {
    // Run FlapGrid and save the output as an STL file. You need to run this for layers
    // [ 0, 1, 2 ] and to print all the letters needs multiple printJobs.
    FlapGrid(SET, LAYER);
}

// A grid if flaps
module FlapGrid(printJob, layer) {
    offset = printJob * FLAPS;
    letters = substring(LETTERS, offset, min([offset + FLAPS, len(LETTERS)]));
    
    echo(letters)
    
    for (i = [0 : len(letters)-1]) {
        row = i % ROWS;
        col = floor(i / ROWS);

        if (!(instr(COLOR_FLAP, letters[i]) || instr(COLOR_FLAP, letters[i+1]))) {
            translate([row*45, col*40, 0])
                if (layer == 0) {
                    FlapBottom(letters[i], letters[i+1]);
                } else if (layer == 1) {
                    FlapMiddle(letters[i], letters[i+1]);
                } else {
                    FlapTop(letters[i], letters[i+1]);
                }
        }
    }    
}

// A single flap repeated count times
module FlapLetter(letters, layer, count) {
    for (i = [0 : count - 1]) {
        row = i % ROWS;
        col = floor(i / ROWS);    
            translate([row*45, col*40, 0])
            if (layer == 0) {
                FlapBottom(letters[0], letters[1]);
            } else if (layer == 1) {
                FlapMiddle(letters[0], letters[1]);
            } else {
                FlapTop(letters[0], letters[1]);
            }
        }
}

module FlapMiddle(letter1, letter2) {
    difference() {
        Flap();
        translate([0,0,FLAP_THICKNESS-LETTER_THICKNESS]) {
            Letter(letter1);
        }
        translate([0,0,0]) mirror([0,1,0]) {
            Letter(letter2);
        }
    }
}

module FlapTop(letter1, letter2) {
    intersection() {
        Flap();
        translate([0,0,FLAP_THICKNESS-LETTER_THICKNESS]) {
            Letter(letter1);
        }
    }
}

module FlapBottom(letter1, letter2) {
    intersection() {
        Flap();
        translate([0,0,0]) mirror([0,1,0]) {
            Letter(letter2);
        }
    }
}

module Flap(height=FLAP_THICKNESS) {
    translate([0,0.5,0])
        linear_extrude(height=height, convexity=4)
        polygon([
            [19.5,0],
            [19.5,1.2],
            [21.5,1.2],
            [21.5,2.4],
            [19.5,2.4],
            [19.5,18],
            [21.5,18],
            [21.5,35],

            [-21.5,35],
            [-21.5,18],
            [-19.5,18],
            [-19.5,2.4],
            [-21.5,2.4],
            [-21.5,1.2],
            [-19.5,1.2],
            [-19.5,0],
        ]);
}

module Letter(letter) {
    if (instr(COLOR_FLAP, letter)) {
        Flap(height=LETTER_THICKNESS);
        mirror([0,1,0]) {
            Flap(height=LETTER_THICKNESS);
        }
    } else {
        scale([letter == "W" ? FONT_SCALE_W : 1, 1, 1])
        translate([0, -FONT_SIZE/2, 0])
        linear_extrude(height=LETTER_THICKNESS, convexity=4)
            text(letter, 
                 size=FONT_SIZE, //letter == "W" ? FONT_SIZE_W : FONT_SIZE,
                 font=FONT,
                 halign="center",
                 valign="baseline");
    }
}

function instr(string, letter, i=0) = i < len(string) ?
    string[i] == letter || instr(string, letter, i+1) : false;

function substring(string, start, length) = start < length ?
    str(string[start], substring(string, start + 1, length)) : "";
