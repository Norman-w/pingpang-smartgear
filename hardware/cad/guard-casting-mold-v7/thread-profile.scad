// Generic axial coarse-thread generator for custom FDM interfaces.
//
// This is intentionally not an ISO/metric-standard thread generator. Define
// the radial x axial profile first, then sweep that profile along a helix.
// Use the same z0, pitch and phase for the male ridge and female cutter.
// Units: caller-defined, normally millimetres.

module tp_helical_thread(
    z0,
    length,
    base_r,
    height,
    pitch,
    root_width_fraction = 0.72,
    crest_width_fraction = 0.28,
    axial_clearance = 0,
    slices_per_turn = 64,
    root_overlap = 0.18
) {
    assert(length > 0);
    assert(base_r > 0);
    assert(height > 0);
    assert(pitch > 0);
    assert(root_width_fraction > crest_width_fraction);
    assert(root_width_fraction <= 1);
    assert(crest_width_fraction > 0);
    assert(axial_clearance >= 0);
    assert(slices_per_turn >= 8);
    assert(root_overlap >= 0 && root_overlap < base_r);
    assert(length > pitch * root_width_fraction + 2 * axial_clearance);

    // r x z profile: broad root, slanted flanks and a finite flat crest.
    nominal_root_half = pitch * root_width_fraction / 2;
    root_half = nominal_root_half + axial_clearance;
    crest_half = pitch * crest_width_fraction / 2 + axial_clearance;
    flank_half = crest_half + (root_half - crest_half) * 0.35;
    profile = [
        [base_r - root_overlap, -root_half],
        [base_r + height * 0.68, -flank_half],
        [base_r + height, -crest_half],
        [base_r + height, crest_half],
        [base_r + height * 0.68, flank_half],
        [base_r - root_overlap, root_half]
    ];

    // One continuous polyhedron avoids non-manifold seams from unioning
    // independently generated helical segments.
    travel = length - 2 * nominal_root_half;
    steps = max(1, ceil(travel / pitch * slices_per_turn));
    n = len(profile);
    points = [
        for (i = [0:steps])
            for (p = profile)
                let(
                    theta = 360 * travel / pitch * i / steps,
                    center_z = z0 + nominal_root_half + travel * i / steps
                )
                [p[0] * cos(theta), p[0] * sin(theta), center_z + p[1]]
    ];
    start_cap = [[for (j = [n - 1:-1:0]) j]];
    end_offset = steps * n;
    end_cap = [[for (j = [0:n - 1]) end_offset + j]];
    side_faces = [
        for (i = [0:steps - 1])
            for (j = [0:n - 1])
                [
                    i * n + j,
                    i * n + (j + 1) % n,
                    (i + 1) * n + (j + 1) % n,
                    (i + 1) * n + j
                ]
    ];
    polyhedron(
        points = points,
        faces = concat(start_cap, end_cap, side_faces),
        convexity = 10
    );
}

// Cut an inward helical groove into an existing external cylinder.
// The cutter reaches slightly past outer_r for a clean opening. Its groove
// bottom is nominally outer_r - groove_depth; root_overlap keeps the boolean
// robust without changing the intended outer envelope of the finished male.
module tp_helical_external_groove_cut(
    z0,
    length,
    outer_r,
    groove_depth,
    pitch,
    root_width_fraction = 0.72,
    crest_width_fraction = 0.28,
    axial_clearance = 0,
    slices_per_turn = 64,
    root_overlap = 0.18
) {
    assert(outer_r > 0);
    assert(groove_depth > 0 && groove_depth < outer_r);
    tp_helical_thread(
        z0 = z0,
        length = length,
        base_r = outer_r - groove_depth + root_overlap,
        height = groove_depth,
        pitch = pitch,
        root_width_fraction = root_width_fraction,
        crest_width_fraction = crest_width_fraction,
        axial_clearance = axial_clearance,
        slices_per_turn = slices_per_turn,
        root_overlap = root_overlap
    );
}

// Sweep a true radial/axial trapezoid. Phase is anchored independently of
// cutter length and axial clearance. Radial clearance translates the SAME
// profile; rebuilding from the female minor radius would change the flank.
module tp_anchored_helix(zlo,zhi,anchor,base_r,height,pitch,root_w,crest_w,
                radial=0,axial=0,phase=0,embed=0.2,steps_turn=128) {
    assert(zhi>zlo && root_w>crest_w && crest_w>0);
    assert(root_w+2*axial<pitch && radial>=0 && axial>=0);
    profile=[[base_r-embed+radial,-root_w/2-axial],
             [base_r+height+radial,-crest_w/2-axial],
             [base_r+height+radial,crest_w/2+axial],
             [base_r-embed+radial,root_w/2+axial]];
    // Whole-turn extension opens groove at both ends; clip after sweep.
    start=anchor+floor((zlo-anchor)/pitch-1)*pitch;
    stop=anchor+ceil((zhi-anchor)/pitch+1)*pitch;
    steps=round((stop-start)/pitch*steps_turn);
    pts=[for(i=[0:steps]) for(p=profile)
        let(z=start+(stop-start)*i/steps,a=phase+360*(z-anchor)/pitch)
        [p[0]*cos(a),p[0]*sin(a),z+p[1]]];
    faces=concat([[3,2,1,0]],[[steps*4,steps*4+1,steps*4+2,steps*4+3]],
        [for(i=[0:steps-1]) for(j=[0:3])
        [i*4+j,i*4+(j+1)%4,(i+1)*4+(j+1)%4,(i+1)*4+j]]);
    intersection() {
        polyhedron(points=pts,faces=faces,convexity=20);
        let(bound=base_r+height+radial+1)
            translate([-bound,-bound,zlo]) cube([2*bound,2*bound,zhi-zlo]);
    }
}
