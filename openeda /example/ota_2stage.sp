* OpenEDA Example: Two-Stage Miller OTA
* Sky130 compatible, 5-transistor design

.SUBCKT OTA_2STAGE VDD VSS VIN+ VIN- VOUT

* Differential pair
M1   D1 VIN+ S VSS nmos W=2.0u L=0.15u
M2   D2 VIN- S VSS nmos W=2.0u L=0.15u

* Tail current source
M3   S VBIAS VSS VSS nmos W=4.0u L=0.3u

* Active load (current mirror)
M4   D1 D1 VDD VDD pmos W=4.0u L=0.3u
M5   D2 D1 VDD VDD pmos W=4.0u L=0.3u

* Second stage (common source)
M6   VOUT VBIAS VSS VSS nmos W=8.0u L=0.15u
M7   VOUT D2 VDD VDD pmos W=16.0u L=0.3u

* Miller compensation capacitor
C1   VOUT D2 2.0p

.ENDS
