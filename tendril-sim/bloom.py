"""The Bloom: a smooth orb that opens into six curved petals. Generates petal meshes and hands/bloom.xml."""
import math, os, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); HD = os.path.join(HERE, "hands")
R, T, N = 0.070, 0.008, 6          # orb radius, shell thickness, petals
LAT_TOP, LAT_MID, LAT_TIP = 8, 52, 88   # degrees below the wrist ring where the petal starts, splits, and ends
HALF_LON = 27                        # each petal spans 54 of its 60 degrees, leaving seams
def sph(lat, lon, r):                # lat measured down from the ring plane; z points along the tool
    la, lo = math.radians(lat), math.radians(lon); return np.array([r*math.cos(la)*math.cos(lo), r*math.cos(la)*math.sin(lo), r*math.sin(la)])
def shell_mesh(lat0, lat1, origin, nlat=10, nlon=12):
    """closed shell patch between two radii, vertices relative to origin, as an OBJ string"""
    V, F = [], []
    def grid(r):
        base = len(V)
        for i in range(nlat+1):
            for j in range(nlon+1):
                V.append(sph(lat0 + (lat1-lat0)*i/nlat, -HALF_LON + 2*HALF_LON*j/nlon, r) - origin)
        return base
    o = grid(R); n = grid(R - T)
    def quad(a, b, c, d, flip=False): F.append((a, c, b) if flip else (a, b, c)); F.append((a, d, c) if flip else (a, c, d))
    for i in range(nlat):
        for j in range(nlon):
            a = o + i*(nlon+1) + j; quad(a, a+1, a+nlon+2, a+nlon+1)
            b = n + i*(nlon+1) + j; quad(b, b+1, b+nlon+2, b+nlon+1, flip=True)
    for j in range(nlon):   # rims top and bottom
        quad(o + j, n + j, n + j + 1, o + j + 1, flip=True); a = o + nlat*(nlon+1) + j; b = n + nlat*(nlon+1) + j; quad(a, a+1, b+1, b, flip=True)
    for i in range(nlat):   # side rims
        a = o + i*(nlon+1); b = n + i*(nlon+1); quad(a, b, b+nlon+1, a+nlon+1, flip=True)
        a = o + i*(nlon+1) + nlon; b = n + i*(nlon+1) + nlon; quad(a, a+nlon+1, b+nlon+1, b, flip=True)
    return "".join(f"v {v[0]:.5f} {v[1]:.5f} {v[2]:.5f}\n" for v in V) + "".join(f"f {a+1} {b+1} {c+1}\n" for a, b, c in F)
def build():
    os.makedirs(HD, exist_ok=True)
    cz = 0.03 + R*math.sin(math.radians(LAT_TOP))*0 + R   # orb centre sits R below the ring plane at z = 0.03
    centre = np.array([0, 0, 0.03 + R])
    p_origin = sph(LAT_TOP, 0, R); d_origin = sph(LAT_MID, 0, R)                 # link origins on the shell, petal 0 (meshes are shared, rotated per petal)
    open(os.path.join(HD, "petal_prox.obj"), "w").write(shell_mesh(LAT_TOP, LAT_MID, p_origin))
    open(os.path.join(HD, "petal_dist.obj"), "w").write(shell_mesh(LAT_MID, LAT_TIP, d_origin))
    x = ['<mujoco model="bloom"><compiler angle="radian" autolimits="true" meshdir="."/>',
         '<asset><mesh name="petal_prox" file="petal_prox.obj"/><mesh name="petal_dist" file="petal_dist.obj"/></asset>',
         '<default><default class="bloom"><joint type="hinge" damping="0.05" armature="0.0005"/><geom condim="4" contype="1" conaffinity="2" friction="1.0 0.02 0.001" solref="0.005 1" solimp="0.9 0.97 0.001"/>',
         '<position kp="40" kv="1.5" forcelimited="true" forcerange="-1.5 1.5"/></default></default>',
         '<worldbody><body name="mount" childclass="bloom">',
         '<geom type="cylinder" size="0.045 0.015" pos="0 0 0.015" rgba="0.36 0.37 0.40 1" mass="0.4"/>',
         f'<geom type="cylinder" size="0.062 0.006" pos="0 0 {0.03 + 0.006:.4f}" rgba="0.95 0.94 0.92 1" mass="0.2"/>',
         f'<geom type="cylinder" size="0.063 0.002" pos="0 0 {0.03 + 0.013:.4f}" rgba="0.12 0.62 0.58 1" contype="0" conaffinity="0" mass="0.001"/>',
         f'<geom name="core" type="sphere" size="0.028" pos="0 0 0.030" rgba="0.15 0.16 0.19 1" mass="0.25"/>',
         f'<site name="eye" pos="0 0 0.030" size="0.004" rgba="0.12 0.62 0.58 1"/>']
    for i in range(N):
        lon = 360*i/N; q = math.radians(lon)
        p0 = sph(LAT_TOP, lon, R); p0 = p0 + centre - np.array([0, 0, R])         # shell point in the hand frame: centre + sph offset (sph is around the centre)
        d0 = sph(LAT_MID, lon, R) + centre - np.array([0, 0, R])
        # hinge axes are tangential (east) at each petal: (-sin lon, cos lon, 0)
        ax = f"{-math.sin(q):.5f} {math.cos(q):.5f} 0"
        x.append(f'<body name="p{i}_prox" pos="{p0[0]:.5f} {p0[1]:.5f} {p0[2]:.5f}" euler="0 0 {q:.5f}">')
        x.append(f'<joint name="p{i}_j1" axis="0 1 0" range="-0.7 1.7"/>')                     # local y is the east tangent after the yaw
        x.append('<geom type="mesh" mesh="petal_prox" rgba="0.95 0.94 0.92 1" mass="0.05"/>')
        # collision along the petal arc: capsules under the shell
        for k in range(3):
            la = LAT_TOP + (LAT_MID - LAT_TOP)*(k + 0.5)/3; c = sph(la, 0, R - T/2) - sph(LAT_TOP, 0, R)
            x.append(f'<geom type="sphere" size="0.014" pos="{c[0]:.5f} {c[1]:.5f} {c[2]:.5f}" rgba="0 0 0 0" mass="0.01"/>')
        d_rel = sph(LAT_MID, 0, R) - sph(LAT_TOP, 0, R)
        x.append(f'<body name="p{i}_dist" pos="{d_rel[0]:.5f} {d_rel[1]:.5f} {d_rel[2]:.5f}"><joint name="p{i}_j2" axis="0 1 0" range="-0.6 1.2"/>')
        x.append('<geom type="mesh" mesh="petal_dist" rgba="0.95 0.94 0.92 1" mass="0.03"/>')
        for k in range(3):
            la = LAT_MID + (LAT_TIP - LAT_MID)*(k + 0.5)/3; c = sph(la, 0, R - T/2) - sph(LAT_MID, 0, R)
            x.append(f'<geom type="sphere" size="0.012" pos="{c[0]:.5f} {c[1]:.5f} {c[2]:.5f}" rgba="0 0 0 0" mass="0.008"/>')
        tip = sph(LAT_TIP - 2, 0, R - T - 0.004) - sph(LAT_MID, 0, R)   # tucked just inside the shell edge, so the closed orb is seamless
        x.append(f'<geom name="p{i}_tip" type="sphere" size="0.009" pos="{tip[0]:.5f} {tip[1]:.5f} {tip[2]:.5f}" rgba="0.12 0.62 0.58 1" mass="0.01" friction="1.2 0.02 0.001"/>')
        x.append("</body></body>")
    x.append("</body></worldbody><actuator>" + "".join(f'<position name="p{i}_a1" class="bloom" joint="p{i}_j1"/><position name="p{i}_a2" class="bloom" joint="p{i}_j2"/>' for i in range(N)) + "</actuator></mujoco>")
    open(os.path.join(HD, "bloom.xml"), "w").write("\n".join(x)); return os.path.join(HD, "bloom.xml")
if __name__ == "__main__":
    import mujoco; p = build(); m = mujoco.MjModel.from_xml_path(p); print("bloom compiles: bodies", m.nbody, "nu", m.nu, "meshes", m.nmesh)
