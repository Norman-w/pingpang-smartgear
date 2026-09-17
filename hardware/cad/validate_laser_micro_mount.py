#!/usr/bin/env python3
"""Check exported solids, nine poses, and in-place access to all 20 adjusters."""
from __future__ import annotations

import concurrent.futures
import hashlib
import json
import math
import subprocess
import tempfile
from collections import defaultdict
from pathlib import Path

from export_laser_micro_mount import HERE, LIBRARY, OUTPUT, SOURCE
from validate_net_stand import _stl_topology, _stl_triangles, _stl_volume
from validate_scad import find_openscad

def component_count(path):
    triangles = _stl_triangles(path)
    at_vertex = defaultdict(set)
    for i,tri in enumerate(triangles):
        for vertex in tri:
            at_vertex[tuple(round(v,5) for v in vertex)].add(i)
    remaining=set(range(len(triangles)))
    count=0
    while remaining:
        count+=1
        pending=[next(iter(remaining))]
        while pending:
            index=pending.pop()
            if index not in remaining: continue
            remaining.remove(index)
            for vertex in triangles[index]:
                pending.extend(at_vertex[tuple(round(v,5) for v in vertex)] & remaining)
    return count

def front_skin_sections(path, z, wall):
    """Intersect exported triangles along x; catch erased curved side walls."""
    triangles=_stl_triangles(path)
    sections=[]
    for y in (-26,-22,-20,-10,0,10,20,22,26):
        hits=[]
        for a,b,c in triangles:
            u=[b[k]-a[k] for k in range(3)];v=[c[k]-a[k] for k in range(3)]
            determinant=u[1]*v[2]-u[2]*v[1]
            if abs(determinant)<1e-12:continue
            dy,dz=y-a[1],z-a[2]
            s=(dy*v[2]-dz*v[1])/determinant;t=(u[1]*dz-u[2]*dy)/determinant
            if s>=-1e-8 and t>=-1e-8 and s+t<=1+1e-8:hits.append(a[0]+s*u[0]+t*v[0])
        hits=sorted(set(round(x,6) for x in hits))
        assert len(hits)>=2,f"Front cover has an open side at y={y}: {hits}"
        thickness=hits[1]-hits[0]
        assert thickness>=wall-.02,f"Thin/missing front wall at y={y}: {thickness}"
        sections.append(dict(y_mm=y,z_mm=z,x_intersections_mm=hits,wall_along_x_mm=thickness))
    return sections

def main():
    manifest=json.loads((OUTPUT/"manifest.json").read_text())
    for source in (SOURCE,LIBRARY):
        assert hashlib.sha256(source.read_bytes()).hexdigest()==manifest["source_hashes"][source.name], f"Stale source: {source.name}"
    parts=[]
    for part in manifest["parts"]:
        path=OUTPUT/part["file"]
        assert hashlib.sha256(path.read_bytes()).hexdigest()==part["sha256"],f"Stale STL: {path}"
        closed,_=_stl_topology(path)
        assert closed and _stl_volume(path)>0,part["id"]
        count=component_count(path) if part["printable"] else None
        assert count in (None,1),f"Floating printable islands: {part['id']}: {count}"
        parts.append(dict(id=part["id"],closed=closed,solid_components=count,bounds=part["bounds"]))
    for asset in manifest["service_assets"]:
        path=OUTPUT/asset["file"]
        assert hashlib.sha256(path.read_bytes()).hexdigest()==asset["sha256"]
        assert _stl_topology(path)[0] and _stl_volume(path)>0
    p=manifest["parameters"]
    # 2 mm beam diameter through the existing Ø6.6 optical hole. This checks
    # geometry only, not the purchased laser's true axis, lens, or divergence.
    front_part=next(part for part in manifest["parts"] if part["id"]=="front_cover")
    front_travel=p["origin_x"]-front_part["bounds"]["min"][0]
    corner_offset=front_travel*math.sqrt(2)*math.tan(math.radians(p["range_deg"]))
    optical_margin=p["optical_bore_d"]/2-1-corner_offset
    assert optical_margin>0
    sections=front_skin_sections(OUTPUT/"front_cover.stl",p["first_z"]+4.5*p["pitch"],p["front_wall"])
    openscad=find_openscad()
    with tempfile.TemporaryDirectory(prefix="laser-micro-check-") as directory:
        def check_pose(pose):
            pitch,yaw=pose
            path=Path(directory)/f"pose-{pitch}-{yaw}.stl"
            result=subprocess.run([openscad,"-o",str(path),"-D",'PART="laser_micro_collision"',
                "-D",f"laser_micro_pitch_deg={pitch}","-D",f"laser_micro_yaw_deg={yaw}",str(SOURCE)],capture_output=True,text=True)
            log=result.stdout+result.stderr
            assert "ERROR:" not in log and "WARNING:" not in log, log
            volume=_stl_volume(path) if path.exists() else 0.0
            assert path.exists() or "top level object is empty" in log,log
            # Coplanar zero-volume ear/rail contact is the intentional seating
            # face at x=0; positive solid overlap is a failure.
            assert abs(volume)<1e-6,f"Interference at {pose}: {volume} mm3"
            containment=Path(directory)/f"containment-{pitch}-{yaw}.stl"
            result=subprocess.run([openscad,"-o",str(containment),"-D",'PART="laser_micro_cover_containment"',
                "-D",f"laser_micro_pitch_deg={pitch}","-D",f"laser_micro_yaw_deg={yaw}",str(SOURCE)],capture_output=True,text=True)
            log=result.stdout+result.stderr
            assert "ERROR:" not in log and "WARNING:" not in log,log
            assert containment.exists() or "top level object is empty" in log,log
            outside=_stl_volume(containment) if containment.exists() else 0
            assert abs(outside)<1e-6,f"Outside front cavity clearance at {pose}: {outside}"
            return dict(pitch_deg=pitch,yaw_deg=yaw,rigid_interference_mm3=volume,outside_front_clearance_mm3=outside)
        extent=p["range_deg"]
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            poses=list(pool.map(check_pose,[(x,y) for x in (-extent,0,extent) for y in (-extent,0,extent)]))
        def probe_intersection(name,body):
            wrapper=Path(directory)/f"{name}.scad"
            wrapper.write_text(f'include <{SOURCE}>\nintersection() {{ {body}; }}\n')
            path=wrapper.with_suffix(".stl")
            result=subprocess.run([openscad,"-o",str(path),"-D",'PART="laser_micro_metadata"',str(wrapper)],capture_output=True,text=True)
            log=result.stdout+result.stderr
            assert "ERROR:" not in log and "WARNING:" not in log,log
            return _stl_volume(path) if path.exists() else 0.0
        # The nominal pusher is deliberately just off the copper shell.  The
        # separate boss must also leave the full Ø6 mm rear insertion path open.
        pusher_laser_overlap=probe_intersection("rear-pusher-laser-overlap",
            "lm_rear_pusher_screw(); lm_laser()")
        pusher_boss_insertion_overlap=probe_intersection("rear-pusher-boss-insertion",
            "lm_rear_pusher_boss(); lm_laser()")
        assert abs(pusher_laser_overlap)<1e-6, (
            f"Rear pusher nominally penetrates laser body: {pusher_laser_overlap} mm3")
        assert abs(pusher_boss_insertion_overlap)<1e-6, (
            f"Rear pusher boss blocks laser insertion: {pusher_boss_insertion_overlap} mm3")
        assert p["rear_pusher_tap_d"] < p["rear_pusher_d"], (
            "Rear pusher boss pilot must be smaller than the screw OD")
        def check_install(distance):
            wrapper=Path(directory)/f"cover-install-{distance}.scad"
            wrapper.write_text(f'include <{SOURCE}>\nintersection() {{ translate([-{distance},0,0]) laser_micro_front_cover(); '
                'union(){laser_micro_array_positive();laser_micro_rear_cover();laser_micro_bottom_cover();} }\n')
            path=wrapper.with_suffix('.stl')
            result=subprocess.run([openscad,"-o",str(path),"-D",'PART="laser_micro_metadata"',str(wrapper)],capture_output=True,text=True)
            log=result.stdout+result.stderr
            assert "ERROR:" not in log and "WARNING:" not in log,log
            assert path.exists() or "top level object is empty" in log,log
            volume=_stl_volume(path) if path.exists() else 0
            assert abs(volume)<1e-6,f"Front insertion blocked at {distance} mm: {volume}"
            return dict(withdrawal_mm=distance,interference_mm3=volume)
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            installation=list(pool.map(check_install,[0,2,5,10,20,30,50]))
        def check_access(case):
            channel,sign,pitch,yaw=case
            path=Path(directory)/f"access-{channel}-{sign}-{pitch}-{yaw}.stl"
            args=[openscad,"-o",str(path),"-D",'PART="laser_micro_service_collision"']
            for key,value in [("service_channel",channel),("service_sign",sign),("pitch_deg",pitch),("yaw_deg",yaw)]:
                args += ["-D",f"laser_micro_{key}={value}"]
            result=subprocess.run(args+[str(SOURCE)],capture_output=True,text=True)
            log=result.stdout+result.stderr
            assert "ERROR:" not in log and "WARNING:" not in log,log
            assert path.exists() or "top level object is empty" in log,log
            volume=_stl_volume(path) if path.exists() else 0.0
            assert abs(volume)<1e-6,f"Tool blocked at {case}: {volume} mm3"
            return dict(channel=channel+1,side="A" if sign>0 else "B",pitch_deg=pitch,yaw_deg=yaw,interference_mm3=volume)
        cases=[(channel,sign,x,y) for channel in range(int(p["count"])) for sign in (-1,1)
               for x in (-extent,0,extent) for y in (-extent,0,extent)]
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            access=[]
            for result in pool.map(check_access,cases):
                access.append(result)
                if len(access)%18==0: print(f"TOOL_ACCESS: channel {len(access)//18}/10 clear",flush=True)
        # Regression guard: the old solid side rail must fail the same path.
        # This prevents an empty/wrongly positioned sweep from passing all cases.
        regression=Path(directory)/"blocked-old-side-rail.scad"
        regression.write_text(f'include <{SOURCE}>\nintersection() {{ lm_service_sweep(1); '
            'translate([3,11,11]) cube([14,3,18]); }\n')
        target=regression.with_suffix(".stl")
        result=subprocess.run([openscad,"-o",str(target),"-D",'PART="laser_micro_metadata"',str(regression)],capture_output=True,text=True)
        assert result.returncode==0 and target.exists(),result.stderr
        blocked_volume=_stl_volume(target)
        assert blocked_volume>1,"Tool-access regression probe missed the original obstruction"
    report=dict(source_hashes=manifest["source_hashes"],units="mm",parts=parts,poses=poses,
                rear_pusher=dict(nominal_laser_overlap_mm3=pusher_laser_overlap,
                    boss_insertion_overlap_mm3=pusher_boss_insertion_overlap,
                    nominal_tip_y_mm=p["rear_pusher_axis_y"]-p["rear_pusher_tip_setback"]+
                        p["rear_pusher_length"],
                    nominal_tip_clearance_mm=(-p["module_d"]/2)-(
                        p["rear_pusher_axis_y"]-p["rear_pusher_tip_setback"]+
                        p["rear_pusher_length"])),
                front_cover=dict(minimum_wall_mm=p["front_wall"],skin_sections=sections,
                    cavity_clearance_mm=.5,installation_samples=installation),
                nominal_2mm_beam_front_aperture_margin_mm=round(optical_margin,4),
                tool_access=dict(cases=access,tube_outer_d_mm=p["tool_d"],shaft_length_mm=p["tool_length"],
                    handle_swept_d_mm=p["tool_handle_d"],port_d_mm=p["access_d"],
                    nominal_radial_clearance_mm=p["tool_clearance"],withdrawal_sweep_mm=60,
                    covers="front, rear and bottom remain installed; ballhead remains attached",
                    original_obstruction_regression_mm3=blocked_volume),
                excluded_from_rigid_interference=["TPU liner preload", "nominal thread envelopes", "elastic spring deformation"],
                unmodelled=["flexible wire routing", "real tool tolerances", "hands and external workspace"],
                physical_validation="not performed")
    (OUTPUT/"validation.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    printed=sum(part["printable"] for part in manifest["parts"])
    print(f"LASER_MICRO_OK: {len(parts)} closed meshes; {printed} connected printable parts; {len(poses)} poses; {len(access)} tool-access cases; {len(sections)} closed skin sections; {len(installation)} insertion positions; aperture margin {optical_margin:.3f} mm")

if __name__=="__main__":main()
