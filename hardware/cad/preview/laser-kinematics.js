// Dimensions and disassembly transforms come from the SCAD export manifest.
// Angles here are radians. No rendering or DOM state in these calculations.
export function flatTip(parameters, sign, pitch, yaw) {
  const a=[Math.cos(pitch)*Math.cos(yaw),Math.cos(pitch)*Math.sin(yaw),-Math.sin(pitch)];
  const c=(sign*a[1]+a[2])/Math.SQRT2,aa=1-c*c,r=parameters.screw_d/2;
  const ray=angle=>{
    const q=[parameters.lever+r*Math.cos(angle),r*Math.sin(angle)/Math.SQRT2,-sign*r*Math.sin(angle)/Math.SQRT2];
    const b=q.reduce((sum,v,i)=>sum+v*a[i],0),bb=-2*b*c;
    const cc=q.reduce((sum,v)=>sum+v*v,0)-b*b-(parameters.tail_d/2)**2;
    return (-bb+Math.sqrt(bb*bb-4*aa*cc))/(2*aa);
  };
  const step=Math.PI/12;
  let centre=0,best=-Infinity;
  for(let i=0;i<24;i++){const value=ray(i*step);if(value>best){best=value;centre=i*step;}}
  let lo=centre-step,hi=centre+step;
  for(let i=0;i<28;i++){
    const a=lo+(hi-lo)/3,b=hi-(hi-lo)/3;
    if(ray(a)>ray(b))hi=b;else lo=a;
  }
  return ray((lo+hi)/2);
}
export function motionAt(samples, progress) {
  if(!samples?.length)throw new Error("缺少 CAD 拆装路径，请重新导出模型");
  const e=Math.max(0,Math.min(1,progress));
  let i=samples.findIndex(sample=>sample.progress>=e);
  if(i<=0)return samples[0].values;
  const a=samples[i-1],b=samples[i],t=(e-a.progress)/(b.progress-a.progress);
  const lerp=(a,b)=>Array.isArray(a)?a.map((v,i)=>lerp(v,b[i])):a+(b-a)*t;
  return lerp(a.values,b.values);
}
export function rotate(v,p,y) {
  return [Math.cos(y)*(Math.cos(p)*v[0]+Math.sin(p)*v[2])-Math.sin(y)*v[1],
    Math.sin(y)*(Math.cos(p)*v[0]+Math.sin(p)*v[2])+Math.cos(y)*v[1],-Math.sin(p)*v[0]+Math.cos(p)*v[2]];
}
export function springPoints(parameters,pitch,yaw,lift=0) {
  const p=parameters,w=p.spring_wire,turns=p.spring_turns;
  const bottom=[p.lever,0,p.spring_floor+w/2];
  const top=rotate([p.lever,0,p.spring_pad-w/2],pitch,yaw);top[2]+=lift;
  const h=top[2]-bottom[2],points=[];
  for(let i=0;i<=turns*32;i++){
    const t=i/32,z=t<1?w*t:t>turns-1?h-w*(turns-t):w+(h-2*w)*(t-1)/(turns-2),f=z/h;
    const ring=rotate([p.spring_radius*Math.cos(2*Math.PI*t),p.spring_radius*Math.sin(2*Math.PI*t),0],pitch*f,yaw*f);
    points.push(bottom.map((v,k)=>v+(top[k]-v)*f+ring[k]));
  }
  return points;
}
export const benchSteps=[
  [0,"完整夹座；先归零，再在工作台上拆解"],
  [.08,"松开 A、B 锁母，夹筒保持托住"],
  [.18,"两颗顶丝沿自身轴线退让"],
  [.30,"旋出 M2 合拢螺钉，直到杆端退出上盖"],
  [.36,"螺钉移到侧面，捕获螺母留在底座"],
  [.44,"托住夹筒，向上取下上夹座"],
  [.52,"上夹座与调节螺钉一起移到后侧"],
  [.60,"向上取出上半球面衬垫"],
  [.66,"将上衬垫移到侧面"],
  [.76,"向上抬起夹筒；弹簧释放到自由高度"],
  [.84,"夹筒离开底座后移到前方；后段反侧短顶丝和正侧限位顶丝开始退让"],
  [.92,"两颗防退顶丝完全退出，解除裸头固定"],
  [1,"裸头沿夹筒轴线从后端抽出"],
];
export function benchStep(progress) {
  return (benchSteps.find(([end])=>progress<=end+1e-9)||benchSteps.at(-1))[1];
}
