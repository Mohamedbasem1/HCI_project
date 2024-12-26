import socket
import asyncio
import aiohttp
import json

async def send_rotation_event(message):
    async with aiohttp.ClientSession() as session:
        async with session.post('http://localhost:5000/tuio_rotation', json={'rotationDirection': message}) as response:
            print(f"Sent rotate event: {message} to server, response: {response.status}")

async def send_click_event():
    async with aiohttp.ClientSession() as session:
        async with session.post('http://localhost:5000/tuio_click') as response:
            print(f"Sent click event to server, response: {response.status}")

async def send_tuio_id(tuio_id):
    async with aiohttp.ClientSession() as session:
        async with session.post('http://localhost:5000/api/tuio_event', json={'tuio_id': tuio_id}) as response:
            print(f"Sent TUIO ID: {tuio_id} to server, response: {response.status}")
            if response.status == 200:
                data = await response.json()
                if data.get('type') == 'kid':
                    print(f"Redirecting to kid exercises for TUIO ID: {tuio_id}")
                else:
                    print(f"Redirecting to patient exercises for TUIO ID: {tuio_id}")

async def send_marker_id(marker_id):
    async with aiohttp.ClientSession() as session:
        async with session.post('http://localhost:5000/api/marker_event', json={'marker_id': marker_id}) as response:
            print(f"Sent marker ID: {marker_id} to server, response: {response.status}")

async def handle_client(conn):
    buffer = ""
    while True:
        data = conn.recv(1024)
        if not data:
            break

        buffer += data.decode('utf-8')
        messages = buffer.split('\n')
        buffer = messages.pop()

        for message in messages:
            if message.strip():
                print(f"Received message: {message.strip()}")
                if message.strip().startswith("tuio_id:"):
                    tuio_id = message.strip().split(":")[1]
                    await send_tuio_id(tuio_id)
                elif message.strip().startswith("marker_id:"):
                    marker_id = message.strip().split(":")[1]
                    await send_marker_id(marker_id)
                elif message.strip() in ["rotate_left", "rotate_right"]:
                    await send_rotation_event(message.strip())
                elif message.strip() == "click":
                    await send_click_event()
                if message.strip() == "exit":
                    break
    conn.close()

async def main():
    soc = socket.socket()
    hostname = "localhost"
    port = 65434
    soc.bind((hostname, port))
    soc.listen(5)
    print("Waiting for connections...")

    while True:
        conn, addr = await asyncio.get_event_loop().sock_accept(soc)
        print("Device connected:", addr)
        asyncio.create_task(handle_client(conn))

if __name__ == "__main__":
    asyncio.run(main())