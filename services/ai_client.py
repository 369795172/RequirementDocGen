"""
AI Client abstraction layer for AI Builder Space platform.
Supports both text generation (planning) and image generation.
Uses OpenAI SDK for OpenAI-compatible API calls.
"""
import os
import json
import base64
from typing import Optional, Dict, Any
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

class AIClient:
    """Unified AI client for AI Builder Space platform."""
    
    def __init__(self):
        self.base_url = "https://space.ai-builders.com/backend/v1"
        self.token = os.getenv("AI_BUILDER_TOKEN")
        if not self.token:
            raise ValueError("AI_BUILDER_TOKEN environment variable is required")
        
        self.client = AsyncOpenAI(
            api_key=self.token,
            base_url=self.base_url
        )
    
    async def generate_plan(
        self, 
        prompt: str, 
        state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate design plan using gemini-3-flash-preview model.
        
        Args:
            prompt: The planning prompt
            state: Current design state
            
        Returns:
            Parsed JSON response with plan data
        """
        try:
            # Use OpenAI SDK to call chat completions
            response = await self.client.chat.completions.create(
                model="gemini-3-flash-preview",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=4096,
                # Gemini-specific settings via extra_body
                extra_body={
                    "gemini": {
                        "response_mime_type": "application/json",
                        "thinking_config": {
                            "thinking_level": "HIGH"
                        }
                    }
                }
            )
            
            # Extract content from OpenAI-compatible response
            if not response.choices or not response.choices[0].message:
                raise Exception("AI Planning failed: No content returned from model.")
            
            content = response.choices[0].message.content
            if not content:
                raise Exception("AI Planning failed: Empty content returned.")
            
            # Parse JSON response
            plan_data = json.loads(content)
            return plan_data
            
        except Exception as e:
            err_str = str(e).lower()
            if "503" in err_str or "overloaded" in err_str:
                raise Exception("Model overloaded, please retry")
            raise Exception(f"Planning failed: {str(e)}")
    
    async def generate_image(
        self,
        prompt: str,
        size: str = "1536x1024"  # 16:9 aspect ratio
    ) -> Optional[bytes]:
        """
        Generate image using gemini-2.5-flash-image model.
        
        Args:
            prompt: Image generation prompt
            size: Image size (default: 1536x1024 for 16:9)
            
        Returns:
            Image data as bytes, or None if generation failed
        """
        try:
            # Use OpenAI SDK's high-level images.generate() API
            # This automatically handles authentication headers
            response = await self.client.images.generate(
                prompt=prompt,
                model="gemini-2.5-flash-image",
                size=size,
                n=1,
                response_format="b64_json"
            )
            
            # Extract base64 image data from response
            if not response.data or not response.data[0].b64_json:
                print("Warning: Image generation returned no data")
                return None
            
            b64_data = response.data[0].b64_json
            image_data = base64.b64decode(b64_data)
            return image_data
            
        except Exception as e:
            err_str = str(e).lower()
            if "503" in err_str or "overloaded" in err_str:
                raise Exception("Model overloaded, please retry")
            print(f"Image generation failed: {str(e)}")
            return None
    
    async def transcribe_audio(
        self,
        audio_file: bytes,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribe audio using AI Builder Space transcription API.
        
        Args:
            audio_file: Audio file data as bytes
            language: Optional BCP-47 language code hint (e.g., 'en', 'zh-CN')
            
        Returns:
            Transcription response with text and metadata
        """
        try:
            import io
            import httpx
            
            # Create a file-like object from bytes
            audio_io = io.BytesIO(audio_file)
            
            # Prepare multipart form data
            files = {
                "audio_file": ("audio.webm", audio_io, "audio/webm")
            }
            data = {}
            if language:
                data["language"] = language
            
            # Use httpx to make multipart/form-data request
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/audio/transcriptions",
                    headers={
                        "Authorization": f"Bearer {self.token}"
                    },
                    files=files,
                    data=data,
                    timeout=60.0
                )
                
                if response.status_code != 200:
                    raise Exception(f"Transcription failed: {response.text}")
                
                result = response.json()
                return result
            
        except Exception as e:
            print(f"Audio transcription failed: {str(e)}")
            raise Exception(f"Transcription failed: {str(e)}")
    
    async def close(self):
        """Close the OpenAI client."""
        await self.client.close()

