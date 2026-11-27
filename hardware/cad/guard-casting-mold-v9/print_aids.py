"""Sacrificial bed-plane frames, never permanent screw captures or blind caps."""
import numpy as np,trimesh,manifold3d as m
from pathlib import Path
import ast,re,json
from shapely.geometry import Polygon,Point,box,LineString
from shapely.ops import unary_union

def solid(t):return m.Manifold(m.Mesh64(np.asarray(t.vertices,dtype=np.float64),np.asarray(t.faces,dtype=np.uint64)))
def extrude(poly,h):
 polygons=[poly] if poly.geom_type=='Polygon' else list(poly.geoms)
 return m.Manifold.batch_boolean([m.CrossSection([np.asarray(p.exterior.coords[:-1]),*[np.asarray(r.coords[:-1]) for r in p.interiors]],m.FillRule.EvenOdd).extrude(h) for p in polygons if p.area>1e-6],m.OpType.Add)
def mesh(s):
 t=s.to_mesh64();return trimesh.Trimesh(vertices=t.vert_properties[:,:3],faces=t.tri_verts,process=False)
def add_print_aid(body,key):
 sx,sy,sz=body.extents;section=body.section([0,0,1],[0,0,.12]);foot=Polygon()
 for p in section.discrete:
  if len(p)>3:foot=foot.symmetric_difference(Polygon(p[:,:2]).buffer(0))
 assert not foot.is_empty
 if key=='screw' or key.startswith('clamp-'):
  center=np.array([sx/2,sy/2]);head_radius=22 if key=='screw' else 20;ring=Point(center).buffer(28,resolution=80).difference(Point(center).buffer(head_radius+.5,resolution=80))
  links=unary_union([LineString([center+np.array([np.cos(a),np.sin(a)])*(head_radius-.4),center+np.array([np.cos(a),np.sin(a)])*25]).buffer(1.2,cap_style=2) for a in np.arange(0,2*np.pi,np.pi/3)]);geometry=extrude(ring,1.2)+extrude(links,.4)
 else:
  frame=box(0,0,sx,sy).difference(box(3,3,sx-3,sy-3))
  # Clear the permanent solid on the first six layers; only the thin links join it.
  low=body.copy();mask=low.triangles_center[:,2]<1.8
  occupied=foot.buffer(.4)
  frame=frame.difference(occupied)
  anchor=np.array(foot.representative_point().coords[0]);targets=[[1.5,1.5],[sx-1.5,1.5],[sx-1.5,sy-1.5],[1.5,sy-1.5]]
  links=unary_union([LineString([anchor,p]).buffer(1.2,cap_style=2) for p in targets]).intersection(box(0,0,sx,sy))
  geometry=extrude(frame,1.2)+extrude(links,.4)
 if key=='lid':
  # For this flat pose the two original locator ends stop 1.6mm above the bed.
  # Add short removable feet and reduced necks; do not leave floating pin tips.
  source=(Path(__file__).resolve().parent.parent/'guard-casting-mold-v2/mold.scad').read_text()
  guides=ast.literal_eval(re.search(r'LID_GUIDES=(\[.*?\]);',source)[1])
  split=float(re.search(r'SPLIT_Z=([-\d.]+)',source)[1]);depth=float(re.search(r'GUIDE_DEPTH=([-\d.]+)',source)[1])
  original=json.loads((Path(__file__).resolve().parent.parent/'guard-casting-mold-v7/validation.json').read_text());bounds=next(p['bounds_mm'] for p in original['parts'] if p['id']=='lid');origin=np.array(bounds[:3]);gap=split-depth-origin[2]
  for x,y in guides:
   center=[x-origin[0],y-origin[1]]
   geometry+=m.Manifold.cylinder(gap-.4,3.2,3.2,48).translate([*center,0])+m.Manifold.cylinder(.45,2.25,2.25,48).translate([*center,gap-.4])
   tie=LineString([anchor,center]).buffer(1.2,cap_style=2);geometry+=extrude(tie,.4);links=links.union(tie).union(Point(center).buffer(3.2))
 base=solid(body);combined=base+geometry
 assert abs((base-combined).volume())<1e-6
 assert len(combined.decompose())==1,(key,'aid disconnected',len(combined.decompose()))
 t=mesh(combined);shift=-t.bounds[0];t.apply_translation(shift)
 aid=mesh(geometry);aid.apply_translation(shift)
 # First-layer combined hull contains static center of mass; not a motion/adhesion test.
 combined_foot=foot.union(ring if key=='screw' or key.startswith('clamp-') else frame).union(links);hull=combined_foot.convex_hull;cm=body.center_mass[:2]
 report={'locator_neck_diameter_mm':4.5 if key=='lid' else None,'locator_feet_removal':'Cut the short feet at the 0.4mm neck with flush cutters; trim flat before assembly' if key=='lid' else None,'kind':'removable_annular_knob_collar' if key=='screw' or key.startswith('clamp-') else 'removable_bed_perimeter_frame','frame_height_mm':1.2,'peel_links_height_mm':.4,'peel_links_width_mm':2.4,'functional_body_removed_mm3':abs((base-combined).volume()),'bed_contact_area_before_mm2':foot.area,'bed_contact_area_after_mm2':combined_foot.area,'COM_inside_bed_hull_after':hull.contains(Point(cm)),'COM_margin_after_mm':hull.boundary.distance(Point(cm)),'aid_volume_mm3':geometry.volume(),'removal':'Peel frame and 0.4mm links away before assembly; no ring remains in screw or tool envelope','_aid_mesh':aid}
 return t,report,shift
