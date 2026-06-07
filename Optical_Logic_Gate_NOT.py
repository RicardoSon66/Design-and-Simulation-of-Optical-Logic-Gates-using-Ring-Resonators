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

heater_ON = True #히터 상태 즉 입력 값 설정 True = 1, False = 0

silicon_value = 4.5 if heater_ON else 3.47 # heater 가 True(1) 이면 실리콘 굴절률 4.5로 조정 아닐 경우 기본 값 3.47로 조정

#히터의 상태에 따라 실리콘 굴절률 변화를 위해 marerial mapping 작업
material_mapping = {
    "si" : mp.Medium(index = silicon_value),
    "sio2" : mp.Medium(index=1.45)
}

c = gf.components.ring_double(gap = 0.2, radius = 5.0, length_x = 4.0, length_y = 0.0 )
c = gf.add_padding_container(c, default = 3)

sim_results = gm.get_simulation(
    component=c,
    resolution=20,
    is_3d=False,
    material_name_to_meep=material_mapping
)
#mapping를 해야하니 material_name_to_meep 를 이용하여 sim에 대한 정보를 입력해야함

sim = sim_results['sim']

Source_vector1 = mp.Vector3(-12, 11.2,0)
Source_vector2 = mp.Vector3(-12, 0, 0)
Source_f = 1 / 1.55

sim.sources = [
    # CW Source 1
    mp.EigenModeSource(
        src = mp.ContinuousSource(frequency=Source_f),
        center = Source_vector1,
        size = mp.Vector3(0, 1, 0),
        direction = mp.X,
        eig_band = 1
    )
]

fig = plt.figure(figsize=(10,8))
animate = mp.Animate2D(sim, fields=mp.Ez, f=fig, realtime=False, normalize=True)

#flux 측정을 위한 측정 위치 설정
flux_output_left = sim.add_flux(
    Source_f, 0.1, 100,
    mp.FluxRegion(center = mp.Vector3(-8.0, 0.0, 0), size=mp.Vector3(0, 2.0, 0))
)

print("Loading")
sim.run(mp.at_every(5, animate), until = 800) 

Data_ADD_Port = mp.get_fluxes(flux_output_left) #측정값 가져오는 변수

filename = "파일이름설정.gif"
animate.to_gif(10, filename)
print("ADDPort_flux_Value:", sum(Data_ADD_Port)) #flux 측정값 출력
print("End")