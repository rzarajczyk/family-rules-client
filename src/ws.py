import asyncio
import websockets
import json

async def send_report_request():
    uri = "ws://localhost:8080/api/v1/streaming-report"
    headers = {
        "Authorization": "Basic ..."
    }
    async with websockets.connect(uri, extra_headers=headers) as websocket:
        for _ in range(5):
            report_request = {
                "instanceId": "4d6fe5c9-7bfc-46de-b97c-6326f5e82d29",
                "screenTime": 3600,
                "applications": {"app1": 1200, "app2": 2400}
            }

            await websocket.send(json.dumps(report_request))
            print(f"Sent: {report_request}")

            response = await websocket.recv()
            print(f"Received: {response}")

            await asyncio.sleep(5)

asyncio.get_event_loop().run_until_complete(send_report_request())