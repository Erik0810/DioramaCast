// Image API Module
// Handles all image generation API calls and display logic

// Generate diorama image
async function generateDiorama(selectedLocation, weatherData) {
    if (!selectedLocation || !weatherData) {
        showStatus('Please select a location first', 'error');
        return;
    }
    
    // Disable button during generation
    const generateBtn = document.getElementById('generate-btn');
    generateBtn.disabled = true;
    
    showStatus('Generating your diorama... This may take a moment.', 'loading');
    
    try {
        // Gather settings
        const settings = {
            style: document.getElementById('style-select').value,
            time_of_day: document.getElementById('time-select').value,
            season: document.getElementById('season-select').value
        };
        
        // Prepare request data
        const requestData = {
            location: weatherData.location,
            weather: weatherData.description,
            temperature: weatherData.temperature,
            settings: settings,
            coordinates: selectedLocation
        };
        
        // Call image generation API
        const response = await fetch('/api/generate-image', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        if (!response.ok) {
            throw new Error('Image generation failed');
        }
        
        const data = await response.json();
        
        // Display generated image
        displayGeneratedImage(data);
        
        showStatus('Diorama generated successfully!', 'success');
        
        setTimeout(() => {
            hideStatus();
        }, 3000);
    } catch (error) {
        console.error('Generation error:', error);
        showStatus('Failed to generate diorama. Please try again.', 'error');
    } finally {
        generateBtn.disabled = false;
    }
}

// Display generated image
function displayGeneratedImage(data) {
    document.querySelector('#image-display .placeholder-text').style.display = 'none';
    document.getElementById('image-content').style.display = 'flex';
    
    const imgElement = document.getElementById('generated-image');
    imgElement.src = data.image_url;
    
    const promptElement = document.getElementById('image-prompt');
    promptElement.textContent = `Prompt: ${data.prompt}`;
    
    if (data.message) {
        const messageP = document.createElement('p');
        messageP.textContent = data.message;
        messageP.style.marginTop = '0.5rem';
        messageP.style.fontStyle = 'italic';
        messageP.style.color = 'var(--accent-blue)';
        
        const imageInfo = document.querySelector('.image-info');
        const existingMessage = imageInfo.querySelector('p:last-child');
        if (existingMessage && existingMessage !== promptElement) {
            existingMessage.remove();
        }
        imageInfo.appendChild(messageP);
    }
}
