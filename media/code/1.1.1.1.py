import math
'''
1.1.1.1 = Bemaling - freatisch - stationair - onttrekking
'''
k=20
H=50
dH=5
t=14
eps=0.35
L=10
B=10
R=1.5*math.sqrt(k*H*t/eps) # reikwijdte
r=(L+B)/math.pi # equivalente straal
h=H-dH # stijghoogte of afstand r
Q=math.pi*k*(H*H-h*h) / (math.log(R) - math.log(r))

