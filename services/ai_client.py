"""
AI Client abstraction layer for AI Builder Space platform.
Supports both text generation (planning) and image generation.
"""
import os
import json
import base64
from typing import Optional, Dict, Any
import httpx
from dotenv import load_dotenv

load_dotenv()

class AIClient:
    """Unified AI client for AI Builder Space platform."""
    
    def __init__(self):
        self.base_url = "https://space.ai-builders.com/backend"
        self.token = os.getenv("AI_BUILDER_TOKEN")
        if not self.token:
            raise ValueError("AI_BUILDER_TOKEN environment variable is required")
        
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            },
            timeout=60.0
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
            # Prepare request payload
            payload = {
                "model": "gemini-3-flash-preview",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 4096,
                # Gemini-specific settings via extra_body
                "extra_body": {
                    "gemini": {
                        "response_mime_type": "application/json",
                        "thinking_config": {
                            "thinking_level": "HIGH"
                        }
                    }
                }
            }
            
            response = await self.client.post(
                "/v1/chat/completions",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Extract content from OpenAI-compatible response
            if not result.get("choices") or not result["choices"][0].get("message"):
                raise Exception("AI Planning failed: No content returned from model.")
            
            content = result["choices"][0]["message"]["content"]
            
            # Parse JSON response
            plan_data = json.loads(content)
            return plan_data
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 503:
                raise Exception("Model overloaded, please retry")
            raise Exception(f"API error: {e.response.status_code} - {e.response.text}")
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse JSON response: {e}")
        except Exception as e:
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
            payload = {
                "prompt": prompt,
                "model": "gemini-2.5-flash-image",
                "size": size,
                "n": 1,
                "response_format": "b64_json"
            }
            
            response = await self.client.post(
                "/v1/images/generations",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Extract base64 image data
            if not result.get("data") or not result["data"][0].get("b64_json"):
                return None
            
            b64_data = result["data"][0]["b64_json"]
            image_data = base64.b64decode(b64_data)
            return image_data
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 503:
                raise Exception("Model overloaded, please retry")
            print(f"Image generation API error: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            print(f"Image generation failed: {str(e)}")
            return None
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

