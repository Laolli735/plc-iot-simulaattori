# CIP-prosessin PLC-simulaattori & OPC UA -testiautomaatio

![CIP OPC UA FAT-testit](https://github.com/Laolli735/plc-iot-simulaattori/actions/workflows/cip_fat_testit.yml/badge.svg?branch=main)

Teollisuusautomaation (PLC) ja automaattisen tehdastestauksen (FAT) integraatioprojekti. Projekti mallintaa elintarvike- ja prosessiteollisuudesta tutun **CIP-pesuaseman (Clean-in-Place)** tilakoneen Pythonilla, julkaisee sen rajapinnat **OPC UA** -palvelimena ja varmistaa prosessin sekä turvalukitusten toiminnan **Robot Framework** -testeillä CI/CD-putkessa.

## Arkkitehtuuri ja tilakone

Simulaattori (`cip_plc_simulaattori.py`) ajaa 500 ms logiikkasykliä ja noudattaa ISA-88 / IEC 61131-3 -tyyppistä tilakonemallia:

```text
[ 0: IDLE (Valmiustila) ]
       │  (Cmd_Start = True)
       ▼
[ 1: PRE_RINSE (Esihuuhtelu) ] ──► Pumppu ON, lämmitys -> 40 °C (3 s)
       │
       ▼
[ 2: CAUSTIC_WASH (Lipeäpesu) ] ──► Lipeäventtiili ON, lämmitys -> 75 °C, johtokyky -> 45 mS/cm
       │
       ▼
[ 3: FINAL_RINSE (Loppuhuuhtelu) ] ──► Lipeäventtiili OFF, huuhtelu kunnes johtokyky <= 2.0 mS/cm
       │
       └───────────────────────────► Paluu tilaan 0 (IDLE)

* Turvalukitus: Cmd_EStop = True keskeyttää minkä tahansa vaiheen välittömästi tilaan [ 99: ALARM / E-STOP ].
Tagi (Node),Tyyppi,Oikeudet,Kuvaus
Cmd_Start,Boolean,Read / Write,Käynnistyspulssi pesuohjelmalle
Cmd_EStop,Boolean,Read / Write,Hätäpysäytys- ja turvalukitustieto
Step_ID,Int64,Read-only,"Aktiivisen tilakonevaiheen numero (0, 1, 2, 3, 99)"
Step_Name,String,Read-only,Aktiivisen vaiheen selkokielinen nimi
Temperature_C,Double,Read-only,Pesuliuoksen lämpötila (°C)
Conductivity_mScm,Double,Read-only,Paluulinjan sähkönjohtokyky (mS/cm)
Pump_Running,Boolean,Read-only,Kiertovesipumpun käyntitieto
Caustic_Valve_Open,Boolean,Read-only,Lipeäannosteluventtiilin tila