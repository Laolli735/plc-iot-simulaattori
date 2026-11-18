import asyncio
from asyncua import Client

class OpcUaKeywords:
    def __init__(self):
        self.url = "opc.tcp://127.0.0.1:48410/freeopcua/server/"
        self.ns_uri = "http://portfolio.automaatio/cip-plc"

    async def _get_node(self, client, tag_name):
        idx = await client.get_namespace_index(self.ns_uri)
        return await client.nodes.objects.get_child([f"{idx}:CIP_Linja1", f"{idx}:{tag_name}"])

    async def _read(self, tag_name):
        client = Client(url=self.url)
        client.session_timeout = 600000
        async with client:
            node = await self._get_node(client, tag_name)
            return await node.get_value()

    async def _write(self, tag_name, value):
        client = Client(url=self.url)
        client.session_timeout = 600000
        async with client:
            node = await self._get_node(client, tag_name)
            await node.write_value(value)

    def lue_opc_tagi(self, tag_name):
        return asyncio.run(self._read(tag_name))

    def kirjoita_opc_bool(self, tag_name, value):
        bool_val = str(value).lower() in ("true", "1", "yes")
        asyncio.run(self._write(tag_name, bool_val))