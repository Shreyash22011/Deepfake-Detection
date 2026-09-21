import asyncio
import httpx

async def test():
    async with httpx.AsyncClient() as client:
        # Create a dummy file
        files = {'file': ('test.txt', b'hello world', 'text/plain')}
        try:
            resp = await client.post('http://localhost:8000/api/analyze', files=files)
            print(f"Status: {resp.status_code}")
            print(f"Response: {resp.text}")
        except Exception as e:
            print(f"Request failed: {e}")

if __name__ == "__main__":
    asyncio.run(test())
