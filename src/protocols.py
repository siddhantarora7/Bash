import json

async def send_msg(writer, obj):
    line = json.dumps(obj) + "\n"
    writer.write(line.encode())
    await writer.drain()

async def read_msg(reader):
    line = await reader.readline()
    if not line:
        return None
    return json.loads(line.decode())