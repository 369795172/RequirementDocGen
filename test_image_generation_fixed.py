#!/usr/bin/env python3
"""
Fixed test script for image generation API.
Tests with proper authentication headers.
"""
import os
import asyncio
import json
import base64
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

BASE_URL = "https://space.ai-builders.com/backend/v1"
TOKEN = os.getenv("AI_BUILDER_TOKEN")

if not TOKEN:
    print("❌ Error: AI_BUILDER_TOKEN not found in environment")
    exit(1)

async def test_image_with_auth_header():
    """Test image generation with explicit Authorization header"""
    print("=" * 60)
    print("Test: Image Generation with Explicit Auth Header")
    print("=" * 60)
    try:
        client = AsyncOpenAI(
            api_key=TOKEN,
            base_url=BASE_URL
        )
        
        # Use _client.post with explicit headers
        response = await client._client.post(
            "/images/generations",
            json={
                "prompt": "A simple test image",
                "model": "gemini-2.5-flash-image",
                "size": "1024x1024",
                "n": 1,
                "response_format": "b64_json"
            },
            headers={
                "Authorization": f"Bearer {TOKEN}"
            }
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS!")
            print(f"Response keys: {list(result.keys())}")
            if result.get("data") and result["data"][0].get("b64_json"):
                print(f"✅ Image data received (length: {len(result['data'][0]['b64_json'])} chars)")
            return True
        else:
            result = response.json()
            print(f"❌ FAILED: {response.status_code}")
            print(f"Response: {json.dumps(result, indent=2)}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("\n🔍 Testing Image Generation with Auth Header Fix\n")
    success = await test_image_with_auth_header()
    
    if success:
        print("\n✅ Fix confirmed: Need to add Authorization header manually")
    else:
        print("\n❌ Still failing - need backend investigation")
    
    client = AsyncOpenAI(api_key=TOKEN, base_url=BASE_URL)
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())

