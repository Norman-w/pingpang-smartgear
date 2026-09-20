// Mechanical first-article envelope for a vertical 16-pin USB-C receptacle.
// The purchased connector remains the electrical source of truth; this model
// keeps the panel-side opening and board-to-panel clearance reviewable until
// the exact vendor STEP is frozen.
$fn = 48;

body_w = 9.0;
body_d = 5.2;
body_h = 5.8;
mouth_w = 7.4;
mouth_d = 3.4;
mouth_depth = 1.8;

difference() {
    translate([-body_w / 2, -body_d / 2, 0])
        cube([body_w, body_d, body_h]);
    // The mating opening faces local +z, which becomes the y+ service face
    // after the UI PCB is installed vertically in the enclosure.
    translate([-mouth_w / 2, -mouth_d / 2, body_h - mouth_depth])
        cube([mouth_w, mouth_d, mouth_depth + 0.2]);
}
