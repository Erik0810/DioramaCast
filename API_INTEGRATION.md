# API Integration Guide

## Overview

This document explains how to integrate the Nano Banana Pro API (or any other image generation API) into DioramaCast.

## Current Implementation

The application is structured to easily integrate with image generation APIs. The prompt is automatically generated in the exact format specified for isometric diorama generation.

## Integration Steps

### 1. Set Your API Key

Add your image generation API key to the `.env` file:

```bash
NANABANA_API_KEY=your_actual_api_key_here
```

### 2. Update the Image Generation Function

Edit `app.py` and locate the `generate_image()` function. Replace the placeholder implementation with your actual API call:

```python
@app.route('/api/generate-image', methods=['POST'])
def generate_image():
    # ... existing code for prompt generation ...
    
    if not IMAGE_API_KEY:
        # Return placeholder if no API key
        return jsonify({
            'image_url': 'https://via.placeholder.com/1000x1000.png?text=Configure+API+Key',
            'prompt': prompt,
            'message': 'Image API key not configured. This is a placeholder.'
        })
    
    try:
        # REPLACE THIS SECTION WITH YOUR API CALL
        # Example for a generic image generation API:
        
        api_response = requests.post(
            'https://api.your-image-service.com/generate',
            headers={
                'Authorization': f'Bearer {IMAGE_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'prompt': prompt,
                'width': 1000,
                'height': 1000,
                # Add any other required parameters
            },
            timeout=60
        )
        
        api_response.raise_for_status()
        result = api_response.json()
        
        # Extract the image URL from the API response
        # Adjust this based on your API's response format
        image_url = result.get('image_url') or result.get('url')
        
        return jsonify({
            'image_url': image_url,
            'prompt': prompt,
            'message': 'Image generation successful'
        })
    except Exception as e:
        return jsonify({'error': f'Failed to generate image: {str(e)}'}), 500
```

## Prompt Format

The application generates prompts in the following format:

```
Present a clear, 45° top-down isometric miniature 3D cartoon scene of [CITY], 
featuring its most iconic landmarks and architectural elements. Use soft, refined 
textures with realistic PBR materials and gentle, lifelike lighting and shadows. 
Integrate [weather condition] weather directly into the city environment to create 
an immersive atmospheric mood. Use a clean, minimalistic composition with a 
soft, solid-colored background. At the top-center, place the title "[CITY]" in 
large bold text, a prominent weather icon beneath it, then the date ([current date]) 
(small text) and temperature ([temp]°C) (medium text). All text must be centered 
with consistent spacing, and may subtly overlap the tops of the buildings. 
Square 1000x1000 dimension
```

### Variables Automatically Inserted:
- **[CITY]**: The selected location name (e.g., "New York City", "Tokyo")
- **[weather condition]**: Current weather from API (e.g., "clear sky", "rainy", "partly cloudy")
- **[current date]**: Automatically generated (e.g., "December 10, 2025")
- **[temp]**: Current temperature in Celsius

## Example API Implementations

### OpenAI DALL-E

```python
import openai

openai.api_key = IMAGE_API_KEY

response = openai.Image.create(
    prompt=prompt,
    n=1,
    size="1024x1024"  # Closest to 1000x1000
)

image_url = response['data'][0]['url']
```

### Stability AI

```python
import requests

response = requests.post(
    "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
    headers={
        "Authorization": f"Bearer {IMAGE_API_KEY}",
        "Content-Type": "application/json",
    },
    json={
        "text_prompts": [{"text": prompt}],
        "cfg_scale": 7,
        "height": 1024,
        "width": 1024,
        "samples": 1,
    }
)
```

### Replicate API

```python
import replicate

output = replicate.run(
    "stability-ai/sdxl:image-model",
    input={"prompt": prompt, "width": 1024, "height": 1024}
)

image_url = output[0]
```

## Testing

After integration, test your implementation:

1. Start the Flask application:
   ```bash
   python app.py
   ```

2. Open your browser and navigate to `http://localhost:5000`

3. Select a location on the map

4. View the weather information

5. Click "Generate Diorama"

6. Verify the image is generated and displayed

## Troubleshooting

### Common Issues:

1. **API Key Not Working**
   - Verify your API key is correctly set in `.env`
   - Check if the API key has proper permissions
   - Ensure you haven't exceeded rate limits

2. **Timeout Errors**
   - Image generation can take time; increase the timeout value
   - Consider implementing async generation with webhooks

3. **Image Not Displaying**
   - Verify the API returns a valid image URL
   - Check browser console for CORS issues
   - Ensure the image URL is publicly accessible

4. **Prompt Too Long**
   - Some APIs have prompt length limits
   - Consider summarizing or truncating the prompt if needed

## Rate Limiting

Consider implementing rate limiting to prevent API abuse:

```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/api/generate-image', methods=['POST'])
@limiter.limit("10 per hour")  # Adjust as needed
def generate_image():
    # ... your code ...
```

## Caching

To reduce API costs, consider caching generated images:

```python
import hashlib

def generate_cache_key(location, weather, temperature):
    data = f"{location}_{weather}_{temperature}"
    return hashlib.md5(data.encode()).hexdigest()

# Store in database or Redis
cache_key = generate_cache_key(location, weather, temperature)
cached_image = get_from_cache(cache_key)
if cached_image:
    return jsonify({'image_url': cached_image, 'prompt': prompt, 'cached': True})
```

## Support

For questions or issues with the DioramaCast application, please open an issue on GitHub.
