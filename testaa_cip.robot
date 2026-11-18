*** Settings ***
Documentation     CIP-pesuaseman automaattinen toimintatestaus (FAT) OPC UA -rajapinnan yli.
Library           OpcUaKeywords.py

*** Test Cases ***
CIP Pesusyklin Normaalitoiminta
    [Documentation]    Käynnistää pesun ja varmistaa esihuuhtelun, lipeäpesun (lämpö + johtokyky) ja loppuhuuhtelun.
    Kirjoita Opc Bool    Cmd_EStop    False
    Sleep    1s

    # Varmistetaan alkutila (IDLE)
    ${alkutila}=    Lue Opc Tagi    Step_ID
    Should Be Equal As Integers    ${alkutila}    0

    # Käynnistetään CIP-pesu
    Kirjoita Opc Bool    Cmd_Start    True
    Sleep    1s

    # 1. Vaihe: Esihuuhtelu
    ${vaihe1}=    Lue Opc Tagi    Step_ID
    ${pumppu}=    Lue Opc Tagi    Pump_Running
    Should Be Equal As Integers    ${vaihe1}    1
    Should Be True    ${pumppu}

    # 2. Vaihe: Lipeäpesu (odotetaan että lipeäventtiili aukeaa ja lämpö/johtokyky nousee)
    Wait Until Keyword Succeeds    8s    0.5s    Tarkista Lipeapesu Kaynnissa

    # 3. Vaihe: Loppuhuuhtelu ja paluu valmiustilaan (johtokyky laskee alle 2.0 mS/cm)
    Wait Until Keyword Succeeds    12s    0.5s    Tarkista Pesu Valmis

Hatapysaytys Keskeyttaa Pesun Valittomasti
    [Documentation]    Varmistaa, että E-Stop pysäyttää pumpun, sulkee lipeäventtiilin ja vie tilakoneen hälytystilaan (99).
    Kirjoita Opc Bool    Cmd_Start    True
    Sleep    1s
    Kirjoita Opc Bool    Cmd_EStop    True
    Sleep    1s

    ${tila}=         Lue Opc Tagi    Step_ID
    ${pumppu}=       Lue Opc Tagi    Pump_Running
    ${venttiili}=    Lue Opc Tagi    Caustic_Valve_Open

    Should Be Equal As Integers    ${tila}    99
    Should Not Be True    ${pumppu}
    Should Not Be True    ${venttiili}

    # Kuitataan hätäpysäytys lopuksi pois
    Kirjoita Opc Bool    Cmd_EStop    False

*** Keywords ***
Tarkista Lipeapesu Kaynnissa
    ${tila}=         Lue Opc Tagi    Step_ID
    ${venttiili}=    Lue Opc Tagi    Caustic_Valve_Open
    ${lampo}=        Lue Opc Tagi    Temperature_C
    ${johtokyky}=    Lue Opc Tagi    Conductivity_mScm
    Should Be Equal As Integers    ${tila}    2
    Should Be True    ${venttiili}
    Should Be True    ${lampo} >= 70.0
    Should Be True    ${johtokyky} >= 30.0

Tarkista Pesu Valmis
    ${tila}=         Lue Opc Tagi    Step_ID
    ${johtokyky}=    Lue Opc Tagi    Conductivity_mScm
    Should Be Equal As Integers    ${tila}    0
    Should Be True    ${johtokyky} <= 2.0