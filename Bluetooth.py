from bleak import BleakScanner
import asyncio
import aiohttp

TARGET_BLUETOOTH_ADDRESSES = ["54:9A:8F:4B:C4:7A", "F4:B6:2D:C0:94:6C"]

async def send_bluetooth_device(addr, name):
    async with aiohttp.ClientSession() as session:
        async with session.post('http://localhost:5000/api/bluetooth_device', json={'address': addr, 'name': name}) as response:
            print(f"Sent Bluetooth device: {addr} - {name} to server, response: {response.status}")

async def discover_bluetooth_devices():
    while True:
        print("Discovering nearby Bluetooth devices...")
        devices = await BleakScanner.discover()
        print(f"Found {len(devices)} devices")

        for device in devices:
            addr = device.address
            name = device.name if device.name else "Unknown"
            print(f" {addr} - {name}")
            await send_bluetooth_device(addr, name)
            if addr in TARGET_BLUETOOTH_ADDRESSES:
                print(f"Target Bluetooth device found: {addr} - {name}")
                print("Target found")
                return  

        await asyncio.sleep(10)  

async def main():
    await discover_bluetooth_devices()

if __name__ == "__main__":
    asyncio.run(main())
