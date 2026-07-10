
from fastapi import FastAPI, Form
from pydantic import ValidationError
import asyncio

app = FastAPI()

@app.post("/test")
async def test_form(val: bool = Form(...)):
    return {"val": val}

async def run_tests():
    from httpx import AsyncClient
    client = AsyncClient(app=app, base_url="http://testserver")
    
    print("Testing 'on':")
    try:
        response = await client.post("/test", data={"val": "on"})
        print(response.status_code, response.json())
    except Exception as e:
        print(f"Error: {e}")

    print("\nTesting 'true':")
    try:
        response = await client.post("/test", data={"val": "true"})
        print(response.status_code, response.json())
    except Exception as e:
        print(f"Error: {e}")

    print("\nTesting missing:")
    try:
        response = await client.post("/test", data={})
        print(response.status_code, response.json())
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(run_tests())
