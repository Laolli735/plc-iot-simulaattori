import asyncio
from asyncua import Server, ua

# CIP-prosessin tilat (IEC 61131-3 / ISA-88 mukainen tilakone)
TILAT = {
    0: "IDLE (Valmiustila)",
    1: "PRE_RINSE (Esihuuhtelu)",
    2: "CAUSTIC_WASH (Lipeapesu 75C)",
    3: "FINAL_RINSE (Loppuhuuhtelu)",
    99: "ALARM / E-STOP"
}

async def main():
    # 1. Alustetaan OPC UA -palvelin
    server = Server()
    await server.init()
    server.set_endpoint("opc.tcp://127.0.0.1:48410/freeopcua/server/")
    server.set_server_name("Virtual_CIP_PLC_Server")

    # Rekisteröidään oma nimiavaruus (Namespace)
    uri = "http://portfolio.automaatio/cip-plc"
    idx = await server.register_namespace(uri)

    # 2. Luodaan PLC:n tagit (Nodes) OPC UA -puuhun
    cip_obj = await server.nodes.objects.add_object(idx, "CIP_Linja1")

    # Ohjausbitit (Writable - HMI/SCADA voi kirjoittaa näihin)
    cmd_start = await cip_obj.add_variable(idx, "Cmd_Start", False)
    cmd_estop = await cip_obj.add_variable(idx, "Cmd_EStop", False)
    await cmd_start.set_writable()
    await cmd_estop.set_writable()

    # Tilatiedot ja mittaukset (Read-only prosessiarvot)
    step_id = await cip_obj.add_variable(idx, "Step_ID", 0)
    step_name = await cip_obj.add_variable(idx, "Step_Name", TILAT[0])
    temp_c = await cip_obj.add_variable(idx, "Temperature_C", 20.0)
    conductivity = await cip_obj.add_variable(idx, "Conductivity_mScm", 0.5)
    pump_running = await cip_obj.add_variable(idx, "Pump_Running", False)
    caustic_valve = await cip_obj.add_variable(idx, "Caustic_Valve_Open", False)

    print("OPC UA CIP-simulaattori kaynnissa: opc.tcp://127.0.0.1:48410/freeopcua/server/")

    async with server:
        step_timer = 0
        while True:
            await asyncio.sleep(0.5)  # PLC-sykli 500 ms

            start = await cmd_start.get_value()
            estop = await cmd_estop.get_value()
            current_step = await step_id.get_value()
            temp = await temp_c.get_value()
            cond = await conductivity.get_value()

            # Turvalukitus (Hardwired / Safety E-Stop ohittaa kaiken)
            if estop:
                await step_id.write_value(99)
                await step_name.write_value(TILAT[99])
                await pump_running.write_value(False)
                await caustic_valve.write_value(False)
                await cmd_start.write_value(False)
                step_timer = 0
                continue

            # Palautuminen hälytyksestä kun E-Stop kuitataan pois
            if current_step == 99 and not estop:
                current_step = 0
                await step_id.write_value(0)
                await step_name.write_value(TILAT[0])

            # Tilakoneen logiikka
            if current_step == 0:  # IDLE
                await pump_running.write_value(False)
                await caustic_valve.write_value(False)
                temp = max(20.0, temp - 1.5)
                cond = max(0.5, cond - 1.0)
                if start:
                    await cmd_start.write_value(False)  # Nollataan pulssi
                    await step_id.write_value(1)
                    await step_name.write_value(TILAT[1])
                    step_timer = 0

            elif current_step == 1:  # PRE_RINSE (Esihuuhtelu vedellä)
                await pump_running.write_value(True)
                await caustic_valve.write_value(False)
                temp = min(40.0, temp + 4.0)
                cond = 1.2
                step_timer += 0.5
                if step_timer >= 3.0:
                    await step_id.write_value(2)
                    await step_name.write_value(TILAT[2])
                    step_timer = 0

            elif current_step == 2:  # CAUSTIC_WASH (Lipeäpesu: lämmitys + kemikaali)
                await pump_running.write_value(True)
                await caustic_valve.write_value(True)
                temp = min(75.0, temp + 7.0)
                cond = min(45.0, cond + 9.0)  # Lipeä nostaa johtokyvyn ~45 mS/cm
                step_timer += 0.5
                if step_timer >= 4.0 and temp >= 70.0:
                    await step_id.write_value(3)
                    await step_name.write_value(TILAT[3])
                    step_timer = 0

            elif current_step == 3:  # FINAL_RINSE (Loppuhuuhtelu kunnes johtokyky laskee)
                await pump_running.write_value(True)
                await caustic_valve.write_value(False)
                temp = max(25.0, temp - 8.0)
                cond = max(0.8, cond - 9.0)  # Huuhtelu laskee johtokyvyn puhtaaksi
                if cond <= 2.0:
                    await step_id.write_value(0)
                    await step_name.write_value(TILAT[0])

            await temp_c.write_value(round(temp, 1))
            await conductivity.write_value(round(cond, 1))

if __name__ == "__main__":
    asyncio.run(main())