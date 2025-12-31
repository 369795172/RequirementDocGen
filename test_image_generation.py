#!/usr/bin/env python3
"""
Standalone test script for image generation API.
Tests different approaches to diagnose 401 Unauthorized issue.
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

print(f"✅ Token found: {TOKEN[:20]}...")
print(f"✅ Base URL: {BASE_URL}\n")

async def test_chat_completions():
    """Test chat completions (known working)"""
    print("=" * 60)
    print("Test 1: Chat Completions (should work)")
    print("=" * 60)
    try:
        client = AsyncOpenAI(
            api_key=TOKEN,
            base_url=BASE_URL
        )
        
        response = await client.chat.completions.create(
            model="gemini-3-flash-preview",
            messages=[{"role": "user", "content": "Say hello"}],
            max_tokens=10
        )
        
        print(f"✅ Chat completions SUCCESS")
        print(f"   Response: {response.choices[0].message.content}")
        print(f"   Model: {response.model}")
        return True
    except Exception as e:
        print(f"❌ Chat completions FAILED: {e}")
        return False

async def test_image_generation_method1():
    """Test image generation using OpenAI SDK's _client.post"""
    print("\n" + "=" * 60)
    print("Test 2: Image Generation - Method 1 (current implementation)")
    print("Using: client._client.post('/images/generations')")
    print("=" * 60)
    try:
        client = AsyncOpenAI(
            api_key=TOKEN,
            base_url=BASE_URL
        )
        
        response = await client._client.post(
            "/images/generations",
            json={
                "prompt": "A simple test image",
                "model": "gemini-2.5-flash-image",
                "size": "1024x1024",
                "n": 1,
                "response_format": "b64_json"
            }
        )
        
        print(f"✅ Status Code: {response.status_code}")
        result = response.json()
        print(f"✅ Response: {json.dumps(result, indent=2)}")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        if hasattr(e, 'response'):
            print(f"   Status: {e.response.status_code if hasattr(e.response, 'status_code') else 'N/A'}")
            print(f"   Body: {e.response.text if hasattr(e.response, 'text') else 'N/A'}")
        return False

async def test_image_generation_method2():
    """Test image generation using full URL path"""
    print("\n" + "=" * 60)
    print("Test 3: Image Generation - Method 2")
    print("Using: client._client.post('/v1/images/generations')")
    print("=" * 60)
    try:
        client = AsyncOpenAI(
            api_key=TOKEN,
            base_url=BASE_URL
        )
        
        response = await client._client.post(
            "/v1/images/generations",
            json={
                "prompt": "A simple test image",
                "model": "gemini-2.5-flash-image",
                "size": "1024x1024",
                "n": 1,
                "response_format": "b64_json"
            }
        )
        
        print(f"✅ Status Code: {response.status_code}")
        result = response.json()
        print(f"✅ Response: {json.dumps(result, indent=2)}")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        if hasattr(e, 'response'):
            print(f"   Status: {e.response.status_code if hasattr(e.response, 'status_code') else 'N/A'}")
            print(f"   Body: {e.response.text if hasattr(e.response, 'text') else 'N/A'}")
        return False

async def test_image_generation_method3():
    """Test image generation with different base_url"""
    print("\n" + "=" * 60)
    print("Test 4: Image Generation - Method 3")
    print("Using base_url without /v1: https://space.ai-builders.com/backend")
    print("=" * 60)
    try:
        client = AsyncOpenAI(
            api_key=TOKEN,
            base_url="https://space.ai-builders.com/backend/v1"
        )
        
        response = await client._client.post(
            "/images/generations",
            json={
                "prompt": "A simple test image",
                "model": "gemini-2.5-flash-image",
                "size": "1024x1024",
                "n": 1,
                "response_format": "b64_json"
            }
        )
        
        print(f"✅ Status Code: {response.status_code}")
        result = response.json()
        print(f"✅ Response: {json.dumps(result, indent=2)}")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        if hasattr(e, 'response'):
            print(f"   Status: {e.response.status_code if hasattr(e.response, 'status_code') else 'N/A'}")
            print(f"   Body: {e.response.text if hasattr(e.response, 'text') else 'N/A'}")
        return False

async def inspect_client_internals():
    """Inspect OpenAI client internals to understand how it handles requests"""
    print("\n" + "=" * 60)
    print("Test 5: Inspect Client Internals")
    print("=" * 60)
    try:
        client = AsyncOpenAI(
            api_key=TOKEN,
            base_url=BASE_URL
        )
        
        print(f"Client base_url: {client.base_url}")
        print(f"Client api_key: {client.api_key[:20]}...")
        print(f"Client _client type: {type(client._client)}")
        
        # Check if _client has methods we can use
        if hasattr(client._client, 'post'):
            print(f"✅ _client.post method exists")
        else:
            print(f"❌ _client.post method NOT found")
            print(f"   Available methods: {[m for m in dir(client._client) if not m.startswith('_')]}")
        
        # Check headers
        if hasattr(client._client, '_headers'):
            print(f"Headers: {client._client._headers}")
        elif hasattr(client._client, 'headers'):
            print(f"Headers: {client._client.headers}")
        
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("\n" + "🔍 Image Generation API Diagnostic Test")
    print("=" * 60 + "\n")
    
    # Test 1: Verify chat completions work
    chat_works = await test_chat_completions()
    
    if not chat_works:
        print("\n❌ Chat completions failed - authentication issue!")
        return
    
    # Inspect client internals
    await inspect_client_internals()
    
    # Test different image generation methods
    results = []
    results.append(("Method 1", await test_image_generation_method1()))
    results.append(("Method 2", await test_image_generation_method2()))
    results.append(("Method 3", await test_image_generation_method3()))
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Chat Completions: {'✅ WORKING' if chat_works else '❌ FAILED'}")
    for name, result in results:
        status = "✅ WORKING" if result else "❌ FAILED"
        print(f"{name}: {status}")
    
    # Cleanup
    client = AsyncOpenAI(api_key=TOKEN, base_url=BASE_URL)
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())

