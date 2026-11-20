# CIP-pesuaseman automaatio ja FAT-testaus (ISA-88)

Tämä projekti demonstroi teollisuusautomaation ohjelmistokehitystä ja automaattista toimintatestausta (FAT). Projekti yhdistää **CODESYS V3.5 (Structured Text)** -logiikan, **OPC UA** -tiedonsiirron sekä **Robot Framework** -testiautomaation.

---

## Arkkitehtuuri

* **PLC-ohjaus (CODESYS):** ISA-88-standardin mukainen tilakone CIP-pesusyklille (esihuuhtelu, lipeäpesu, loppuhuuhtelu ja hätäpysäytys).
* **Versiohallinta:** CODESYS-projekti on viety avoimeen `PLCopenXML`-muotoon, jotta logiikkamuutokset ovat luettavissa suoraan Gitissä.
* **Testiautomaatio (Robot Framework + Python):** `asyncua`-kirjastoon pohjautuva rajapinta, joka ohjaa ja varmentaa prosessin tilat OPC UA:n yli.
* **Simulaatioympäristö (`sim`):** Kevyt Python-pohjainen OPC UA -palvelin, joka mahdollistaa testien ajamisen ilman fyysistä PLC-laitteistoa (esim. CI/CD-putkessa).

---

## Projektin rakenne

```text
plc-iot-simulaattori/
├── plc/                  # CODESYS-projektitiedostot ja PLCopenXML-vienti
├── sim/                  # Python-pohjainen CIP-prosessisimulaattori
├── OpcUaKeywords.py      # Robot Frameworkin OPC UA -avainsanakirjasto
├── testaa_cip.robot      # Automaattiset FAT-testitapaukset
└── README.md             # Projektin dokumentaatio

Käyttöönotto ja testien ajo
1. Riippuvuuksien asennus
pip install robotframework asyncua

2. Testien ajo simulaattoria vasten (oletus)
Käynnistä ensimmäisessä terminaalissa simulaattori:
PowerShell
python sim/cip_simulaattori.py

Aja toisessa terminaalissa Robot Framework -testit:
PowerShell
$env:PLC_TARGET="sim"
robot testaa_cip.robot

3. Testien ajo CODESYS-ohjainta vasten
PowerShell
$env:PLC_TARGET="codesys"
robot testaa_cip.robot

Testatut toiminnallisuudet         
Testitapaus                               Kuvaus                                      Odotettu tulos       
CIP Pesusyklin Normaalitoiminta           Käynnistää pesusyklin ja                    Pesu etenee tilojen läpi ja
                                          seuraa vaiheiden etenemistä                 palautuu valmiustilaan

Hätäpysäytys (Estop)                      Aktivoi hätäpysäytyksen                     Venttiilit ja pumput sulkeutuvat
                                          kesken pesuvaiheen                          välittömästi

Jatkokehitys (Future Improvements)
Seuraavat FAT-testitapaukset ja ominaisuudet on tunnistettu luonteviksi laajennuksiksi tuotantotason validointiin:

Prosessilukitukset (Interlocks): Käynnistyksen eston varmentaminen tilanteissa, joissa pesuainesäiliön pinta on liian matala, huuhteluvesi puuttuu tai linjaventtiili on väärässä asennossa.

Prosessiparametrien poikkeamat: Lipeäpesun lämpötilan laskun tai virtauksen katkeamisen simulointi kesken pesun (pesuvaiheen ajastimen pysäytys / siirtyminen HOLDING-tilaan, kunnes arvot palautuvat).

Täysi ISA-88-tilahallinta (Hold / Restart / Reset): Keskeytys- ja jatkamiskomentojen testaus sekä varmistus siitä, että hätäpysäytyksen vapauttaminen vaatii erillisen kuittauksen (Reset) ennen paluuta IDLE-tilaan.

Aikakatkaisut ja laiteviat (Watchdog / Timeout): Venttiilien rajakytkinten tai säiliön täyttöajan aikakatkaisuhälytysten testaus laiterikkojen ehkäisemiseksi.

CI/CD-automaatio (GitHub Actions): Robot Framework -testisarjan automaattinen suoritus simulaattoria vasten jokaisen push- ja pull request -tapahtuman yhteydessä.                                            