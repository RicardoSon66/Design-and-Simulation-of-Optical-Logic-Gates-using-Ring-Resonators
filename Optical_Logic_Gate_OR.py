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

c = gf.components.ring_double(gap = 0.15, radius = 5.0, length_x = 4.0, length_y = 0.0 ) # gap 0.15, 반지름 5.0 커플링 구간 4μm인 Ring Resonator Layout

c = gf.add_padding_container(c, default = 3) #주변 영역 확장

#시뮬레이션 환경 설정
sim_results = gm.get_simulation(
    component=c,
    resolution=20,
    is_3d=False,
)
#1μm당 격자를 20개로 조정

sim = sim_results['sim']

Source_vector1 = mp.Vector3(-12, 11.2,0) #Input A에 대한 좌표
Source_vector2 = mp.Vector3(8, 11.2, 0) #Input B에 대한 좌표
Source_f = 1 / 1.55 # wave의 추파수
Source_fwidth = 0.1 
Y_bottom = 0.0

sim.sources = [
    # Pulse Source 1 (input A)
    mp.EigenModeSource( 
        src = mp.GaussianSource(frequency=Source_f, fwidth = Source_fwidth),
        center = Source_vector1,
        size = mp.Vector3(0, 1.0, 0),
        direction = mp.X,
        eig_band = 1,
        eig_match_freq = True
    ),
    
    # Pulse Source 2 (input B)
    #eig_kpoint가 굉장히 중요함 해당 값을 설정하지 않으면 빛이 기본값인 +X축으로 나아가버림
    #해당 파라미터에 벡터값을 주고 x축의 값을 -1로 줘서 빛이 -X축으로 가게 설정
    #direction 에서 mp.X 부분을 -mp.X로 하던 뭘하던 인식불가 무조건 eig_kpoint를 사용
    mp.EigenModeSource(
        src = mp.GaussianSource(frequency=Source_f, fwidth =  Source_fwidth),
        center = Source_vector2,
        size = mp.Vector3(0, 1, 0),
        direction = mp.X, 
        eig_kpoint = mp.Vector3(-1, 0, 0),
        eig_band = 1,
        eig_match_freq = True
    )
]

fig = plt.figure(figsize=(10,8))
animate = mp.Animate2D(sim, fields=mp.Ez, f=fig, realtime=False, normalize=True)

print("Loading")

#flux 측정을 위한 변수 선언 및 위치 설정
flux_output_left = sim.add_flux(
    Source_f, Source_fwidth, 100,
    mp.FluxRegion(center = mp.Vector3(-8.0, Y_bottom, 0), size=mp.Vector3(0, 2.0, 0))
)

flux_output_right = sim.add_flux(
    Source_f, Source_fwidth, 100,
    mp.FluxRegion(center = mp.Vector3(8.0, Y_bottom, 0), size=mp.Vector3(0, 2.0, 0))
)

sim.run(mp.at_every(5, animate), until = 500) 

Data_OUTPUT_C = mp.get_fluxes(flux_output_left) #측정된 flux값을 받아올 변수 선언 및 삽입
Data_OUTPUT_D = mp.get_fluxes(flux_output_right)

filename = "파일 이름설정.gif"
animate.to_gif(10, filename)
print("OUTPUT_C_flux_Value:", sum(Data_OUTPUT_C)) #flux값을 받아온 변수를 호출하여 출력
print("OUTPUT_D_flux_Value:", sum(Data_OUTPUT_D))
print("End")