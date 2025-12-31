#!/usr/bin/env python3
"""
Test OpenAI SDK's images.generate() API
"""
import os
import asyncio
import base64
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

BASE_URL = "https://space.ai-builders.com/backend/v1"
TOKEN = os.getenv("AI_BUILDER_TOKEN")

async def test_images_generate():
    """Test using OpenAI SDK's high-level images.generate() API"""
    print("Testing client.images.generate()...")
    
    client = AsyncOpenAI(
        api_key=TOKEN,
        base_url=BASE_URL
    )
    
    try:
        response = await client.images.generate(
            prompt="A simple red car",
            model="gemini-2.5-flash-image",
            size="1024x1024",
            n=1,
            response_format="b64_json"
        )
        
        print(f"✅ SUCCESS!")
        print(f"Response type: {type(response)}")
        print(f"Response data length: {len(response.data)}")
        
        if response.data and response.data[0].b64_json:
            image_data = base64.b64decode(response.data[0].b64_json)
            print(f"✅ Image decoded: {len(image_data)} bytes")
            return True
        else:
            print("❌ No image data in response")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(test_images_generate())

