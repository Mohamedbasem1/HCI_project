import bluetooth
import asyncio
import aiohttp

TARGET_BLUETOOTH_ADDRESS = "54:9A:8F:4B:C4:7A"

async def send_bluetooth_device(addr, name):
    async with aiohttp.ClientSession() as session:
        async with session.post('http://localhost:5000/api/bluetooth_device', json={'address': addr, 'name': name}) as response:
            print(f"Sent Bluetooth device: {addr} - {name} to server, response: {response.status}")

async def discover_bluetooth_devices():
    while True:
        print("Discovering nearby Bluetooth devices...")
        nearby_devices = bluetooth.discover_devices(lookup_names=True)
        print(f"Found {len(nearby_devices)} devices")

        for addr, name in nearby_devices:
            print(f" {addr} - {name}")
            await send_bluetooth_device(addr, name)
            if addr == TARGET_BLUETOOTH_ADDRESS:
                print(f"Target Bluetooth device found: {addr} - {name}")
                return  # Stop searching once the target device is found

        await asyncio.sleep(10)  # Wait for 10 seconds before the next discovery

async def main():
    await discover_bluetooth_devices()

if __name__ == "__main__":
    asyncio.run(main())
