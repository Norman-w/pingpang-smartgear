// Export-only assembly of meshes generated FROM edge_safe_guard.scad.
// Not the geometry authority. Rebuild both inputs with build_export.py.
// CGAL regularizes the body; Manifold handles the curved font robustly.
union() {
    import("../exports/perpendicular-u-joint-v1.13-edge-safe-label/guard-v1.13-body.stl",convexity=16);
    import("../exports/perpendicular-u-joint-v1.13-edge-safe-label/guard-v1.13-lettering.stl",convexity=16);
}
