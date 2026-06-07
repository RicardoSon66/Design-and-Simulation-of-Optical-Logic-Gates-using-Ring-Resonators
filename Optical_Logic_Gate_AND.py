import numpy as np
import sys

if not hasattr(np, "float_"):
    np.float_ = np.float64
if not hasattr(np, "int_"):
    np.int_ = np.int64
if not hasattr(np, "asfarray"):

    np.asfarray = lambda x, **kwargs: np.array(x, dtype=np.float64, **kwargs)

import meep as mp
import gdsfactory as gf
import gplugins.gmeep as gm
import matplotlib.pyplot as plt
from gdsfactory.generic_tech import get_generic_pdk

get_generic_pdk().activate() #PDK 활성화

c = gf.components.ring_double(gap = 0.2, radius = 5.0, length_x = 4.0, length_y = 0.0 ) #Ring Resonator 스펙 

c = gf.add_padding_container(c, default = 3) #주변 영역 확장

#시뮬레이션 환경 설정
sim_results = gm.get_simulation(
    component=c,
    resolution=20,
    is_3d=False,
)

sim = sim_results['sim']

Source_vector1 = mp.Vector3(-12, 11.2,0)
Source_vector2 = mp.Vector3(-12, 0, 0)
Source_f = 1 / 1.55
Source_f2 = Source_f * 1.01 # 맥놀이 현상 관찰을 위한 주파수

sim.sources = [
    # Pulse Source 1 
    #mp.EigenModeSource(
    #    src = mp.GaussianSource(frequency=Source_f, fwidth = Source_f * 0.1 ),
    #    center = Source_vector1,
    #    size = mp.Vector3(0, 1, 0),
    #    direction = mp.X,
    #    eig_band = 1
    #),
    
    # Pulse Source 2
    #mp.EigenModeSource(
    #    src = mp.GaussianSource(frequency=Source_f2, fwidth = Source_f * 0.1),
    #    center = Source_vector2,
    #    size = mp.Vector3(0, 1, 0),
    #    direction = mp.X,
    #    eig_band = 1
    #)

    # CW Source 1
    mp.EigenModeSource(
        src = mp.ContinuousSource(frequency=Source_f),
        center = Source_vector1,
        size = mp.Vector3(0, 1, 0),
        direction = mp.X,
        eig_band = 1
    ),

    # CW soure 2
    mp.EigenModeSource(
        src = mp.ContinuousSource(frequency=Source_f),
        center = Source_vector2,
        size = mp.Vector3(0, 1, 0),
        direction = mp.X,
        eig_band = 1
    )
]

fig = plt.figure(figsize=(10,8))
animate = mp.Animate2D(sim, fields=mp.Ez, f=fig, realtime=False, normalize=True)

print("Loading")
sim.run(mp.at_every(5, animate), until = 500)

filename = "파일 이름설정.gif"
animate.to_gif(10, filename)
print("End")