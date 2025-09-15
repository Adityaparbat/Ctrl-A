// Accessible Image Narrator - JavaScript
'use strict';

// DOM elements - will be populated after DOM loads
let elements = {};

function initializeElements() {
    elements = {
        fileInput: document.getElementById('fileInput'),
        uploadArea: document.querySelector('.upload-area'),
        browseButton: document.getElementById('browseButton'),
        testButton: document.getElementById('testButton'),
        narrateBtn: document.getElementById('narrateUpload'),
        styleSelect: document.getElementById('style'),
        languageSelect: document.getElementById('language'),
        voiceSpeedSelect: document.getElementById('voice-speed'),
        statusIndicator: document.getElementById('status'),
        textOutput: document.getElementById('text'),
        audioElement: document.getElementById('audio'),
        audioControls: document.getElementById('audioControls'),
        replayBtn: document.getElementById('replayAudio')
    };
    
    // Debug: Check if elements exist
    console.log('Elements initialized:', elements);
    console.log('Element existence check:', {
        fileInput: !!elements.fileInput,
        browseButton: !!elements.browseButton,
        testButton: !!elements.testButton
    });
    
    // If elements are missing, try to find them again
    if (!elements.fileInput || !elements.browseButton) {
        console.warn('Some elements not found, retrying...');
        setTimeout(() => {
            elements.fileInput = document.getElementById('fileInput');
            elements.browseButton = document.getElementById('browseButton');
            console.log('Retry result:', {
                fileInput: !!elements.fileInput,
                browseButton: !!elements.browseButton
            });
            
            // If still missing, try alternative selectors
            if (!elements.fileInput) {
                elements.fileInput = document.querySelector('input[type="file"]');
                console.log('Alternative file input search:', !!elements.fileInput);
            }
        }, 100);
    }
}

// State management
let currentFile = null;
let isProcessing = false;
let currentAudioSrc = null;

// Test function for debugging - can be called from browser console
window.testFileInput = function() {
    console.log('Testing file input functionality...');
    
    // Test 1: Check if elements exist
    console.log('Elements check:', {
        browseButton: !!document.getElementById('browseButton'),
        fileInput: !!document.getElementById('fileInput'),
        uploadArea: !!document.querySelector('.upload-area')
    });
    
    // Test 2: Try to create and click a file input
    const testInput = document.createElement('input');
    testInput.type = 'file';
    testInput.accept = 'image/*';
    testInput.style.display = 'none';
    testInput.addEventListener('change', (e) => {
        console.log('Test file input change event fired!', e.target.files);
    });
    
    document.body.appendChild(testInput);
    console.log('Created test file input, attempting to click...');
    testInput.click();
    
    // Clean up
    setTimeout(() => {
        if (document.body.contains(testInput)) {
            document.body.removeChild(testInput);
            console.log('Test file input cleaned up');
        }
    }, 2000);
};

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM Content Loaded');
    // Add a small delay to ensure all elements are ready
    setTimeout(() => {
        initializeApp();
        initializeLiveCamera(); // Initialize live camera here instead of separate listener
    }, 500);
});

function initializeApp() {
    console.log('Initializing app...');
    
    // Try multiple times to ensure elements are found
    let attempts = 0;
    const maxAttempts = 5;
    
    const tryInitialize = () => {
        attempts++;
        console.log(`Initialization attempt ${attempts}/${maxAttempts}`);
        
        initializeElements();
        
        if (elements.fileInput && elements.browseButton) {
            console.log('All elements found, setting up event listeners...');
            setupEventListeners();
            loadPreferences();
            updateStatus('Ready to upload an image', 'success');
            announceToScreenReader('Accessible Image Narrator loaded. Please upload an image to get started.');
        } else if (attempts < maxAttempts) {
            console.log('Elements not ready, retrying in 200ms...');
            setTimeout(tryInitialize, 200);
        } else {
            console.error('Failed to find elements after maximum attempts');
            setupEventListeners(); // Try anyway
            loadPreferences();
            updateStatus('Warning: Some elements may not be working properly', 'warning');
        }
    };
    
    tryInitialize();
}

function setupEventListeners() {
    console.log('Setting up event listeners...');
    console.log('Elements found:', {
        fileInput: !!elements.fileInput,
        browseButton: !!elements.browseButton
    });
    
    // File input handling
    if (elements.fileInput) {
        elements.fileInput.addEventListener('change', handleFileSelect);
        console.log('File input listener added');
    }

    // Upload area interactions
    if (elements.uploadArea) {
        elements.uploadArea.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Upload area clicked');
            
            // Try the main file input first
            if (elements.fileInput) {
                console.log('File input found from upload area, clicking...');
                try {
                    // Make file input temporarily visible for click
                    elements.fileInput.style.display = 'block';
                    elements.fileInput.style.position = 'absolute';
                    elements.fileInput.style.left = '-9999px';
                    elements.fileInput.click();
                    elements.fileInput.style.display = 'none';
                    console.log('File input clicked successfully from upload area');
                    return;
                } catch (error) {
                    console.error('Error clicking file input from upload area:', error);
                }
            }
            
            // Fallback: Create new file input
            console.log('Creating new file input for upload area...');
            const newFileInput = document.createElement('input');
            newFileInput.type = 'file';
            newFileInput.accept = 'image/*';
            newFileInput.style.display = 'none';
            newFileInput.addEventListener('change', handleFileSelect);
            
            document.body.appendChild(newFileInput);
            
            // Use setTimeout to ensure proper attachment
            setTimeout(() => {
                try {
                    newFileInput.click();
                    console.log('Upload area fallback file input clicked');
                } catch (error) {
                    console.error('Upload area fallback click failed:', error);
                }
            }, 10);
            
            // Clean up after a delay
            setTimeout(() => {
                if (document.body.contains(newFileInput)) {
                    document.body.removeChild(newFileInput);
                }
            }, 1000);
        });
        elements.uploadArea.addEventListener('keydown', handleUploadAreaKeydown);
        elements.uploadArea.addEventListener('dragover', handleDragOver);
        elements.uploadArea.addEventListener('dragleave', handleDragLeave);
        elements.uploadArea.addEventListener('drop', handleDrop);
    }

    // Browse button - Enhanced approach
    if (elements.browseButton) {
        elements.browseButton.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            console.log('Browse button clicked');
            
            // Visual feedback
            this.style.backgroundColor = '#ff6b6b';
            setTimeout(() => {
                this.style.backgroundColor = '';
            }, 200);
            
            // Force trigger file input
            console.log('Attempting to trigger file input...');
            
            // Method 1: Direct click on existing file input
            if (elements.fileInput) {
                console.log('File input found, clicking directly...');
                try {
                    // Ensure the file input is visible for a moment to allow click
                    elements.fileInput.style.display = 'block';
                    elements.fileInput.style.position = 'absolute';
                    elements.fileInput.style.left = '-9999px';
                    elements.fileInput.click();
                    elements.fileInput.style.display = 'none';
                    console.log('File input clicked successfully');
                    return;
                } catch (error) {
                    console.error('Direct click failed:', error);
                }
            }
            
            // Method 2: Create new file input as fallback
            console.log('Creating new file input as fallback...');
            const newFileInput = document.createElement('input');
            newFileInput.type = 'file';
            newFileInput.accept = 'image/*';
            newFileInput.style.display = 'none';
            newFileInput.addEventListener('change', handleFileSelect);
            
            document.body.appendChild(newFileInput);
            
            // Use setTimeout to ensure the element is properly attached
            setTimeout(() => {
                try {
                    newFileInput.click();
                    console.log('Fallback file input clicked');
                } catch (error) {
                    console.error('Fallback click failed:', error);
                }
            }, 10);
            
            // Clean up after a delay
            setTimeout(() => {
                if (document.body.contains(newFileInput)) {
                    document.body.removeChild(newFileInput);
                }
            }, 1000);
            
        });
        console.log('Browse button listener added');
    } else {
        console.log('Browse button not found!');
    }


    // Test button
    if (elements.testButton) {
        elements.testButton.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Test button clicked - running comprehensive test...');
            
            // Test 1: Check element existence
            console.log('=== ELEMENT EXISTENCE TEST ===');
            console.log('Browse button:', !!elements.browseButton);
            console.log('File input:', !!elements.fileInput);
            console.log('Upload area:', !!elements.uploadArea);
            console.log('Test button:', !!elements.testButton);
            
            // Test 2: Try to click browse button programmatically
            console.log('=== PROGRAMMATIC CLICK TEST ===');
            if (elements.browseButton) {
                console.log('Attempting to click browse button...');
                elements.browseButton.click();
            }
            
            // Test 3: Try to click file input directly
            console.log('=== DIRECT FILE INPUT TEST ===');
            if (elements.fileInput) {
                console.log('Attempting to click file input directly...');
                try {
                    elements.fileInput.style.display = 'block';
                    elements.fileInput.style.position = 'absolute';
                    elements.fileInput.style.left = '-9999px';
                    elements.fileInput.click();
                    elements.fileInput.style.display = 'none';
                    console.log('File input clicked successfully');
                } catch (error) {
                    console.error('File input click failed:', error);
                }
            }
            
            // Test 4: Create and click new file input
            console.log('=== NEW FILE INPUT TEST ===');
            const testInput = document.createElement('input');
            testInput.type = 'file';
            testInput.accept = 'image/*';
            testInput.style.display = 'none';
            testInput.addEventListener('change', (e) => {
                console.log('Test file input change event fired!', e.target.files);
                if (e.target.files.length > 0) {
                    handleFile(e.target.files[0]);
                }
            });
            
            document.body.appendChild(testInput);
            setTimeout(() => {
                try {
                    testInput.click();
                    console.log('Test file input clicked');
                } catch (error) {
                    console.error('Test file input click failed:', error);
                }
                
                // Clean up
                setTimeout(() => {
                    if (document.body.contains(testInput)) {
                        document.body.removeChild(testInput);
                    }
                }, 2000);
            }, 100);
            
            console.log('=== TEST COMPLETE ===');
        });
        console.log('Test button listener added');
    }

    // Process button
    if (elements.narrateBtn) {
        elements.narrateBtn.addEventListener('click', processImage);
    }


    // Preference changes
    if (elements.styleSelect) {
        elements.styleSelect.addEventListener('change', savePreferences);
    }
    if (elements.languageSelect) {
        elements.languageSelect.addEventListener('change', savePreferences);
    }
    if (elements.voiceSpeedSelect) {
        elements.voiceSpeedSelect.addEventListener('change', savePreferences);
    }

    // Audio controls
    if (elements.replayBtn) {
        elements.replayBtn.addEventListener('click', replayAudio);
    }

    // Keyboard shortcuts
    document.addEventListener('keydown', handleKeyboardShortcuts);
}

function handleFileSelect(event) {
    console.log('File selected:', event.target.id, event.target.files[0]);
    const file = event.target.files[0];
    if (file) {
        handleFile(file);
    }
}

function handleUploadAreaKeydown(event) {
    if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        elements.fileInput?.click();
    }
}

function handleDragOver(event) {
    event.preventDefault();
    elements.uploadArea?.classList.add('dragover');
}

function handleDragLeave(event) {
    event.preventDefault();
    elements.uploadArea?.classList.remove('dragover');
}

function handleDrop(event) {
    event.preventDefault();
    elements.uploadArea?.classList.remove('dragover');
    
    const files = event.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

function handleFile(file) {
    console.log('Handling file:', file.name, file.type, file.size);
    
    // Validate file type
    if (!file.type.startsWith('image/')) {
        console.log('Invalid file type:', file.type);
        updateStatus('Please select a valid image file (JPG, PNG, GIF, WebP)', 'error');
        announceToScreenReader('Invalid file type. Please select an image file.');
        return;
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
        console.log('File too large:', file.size);
        updateStatus('File too large. Please select an image smaller than 10MB', 'error');
        announceToScreenReader('File too large. Please select a smaller image.');
        return;
    }

    currentFile = file;
    elements.narrateBtn.disabled = false;
    updateStatus(`Image selected: ${file.name} (${formatFileSize(file.size)})`, 'success');
    announceToScreenReader(`Image selected: ${file.name}. You can now click the Describe Image button to process it.`);
    console.log('File processed successfully');
}


function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

async function processImage() {
    if (!currentFile || isProcessing) return;

    isProcessing = true;
    elements.narrateBtn.disabled = true;
    updateStatus('Processing image...', 'processing');
    announceToScreenReader('Processing your image. Please wait.');

    try {
        const dataUrl = await fileToDataURL(currentFile);
        const result = await narrateImage(dataUrl);
        
        if (result.success) {
            displayResult(result);
            announceToScreenReader('Image processing complete. Description is now available.');
        } else {
            throw new Error(result.error || 'Processing failed');
        }
    } catch (error) {
        console.error('Processing error:', error);
        updateStatus(`Error: ${error.message}`, 'error');
        announceToScreenReader(`Error processing image: ${error.message}`);
    } finally {
        isProcessing = false;
        elements.narrateBtn.disabled = false;
    }
}

async function narrateImage(imageBase64) {
    const preferences = getPreferences();
    
    try {
        const response = await fetch('api/narrate', {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                image_base64: imageBase64, 
                preferences: preferences 
            })
        });

        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Request failed');
        }

        return {
            success: true,
            text: data.text || 'No description available',
            audio: data.audio_base64,
            detections: data.detections,
            processingTime: data.elapsed_ms
        };
    } catch (error) {
        return {
            success: false,
            error: error.message
        };
    }
}

function displayResult(result) {
    // Update status
    const timeInfo = result.processingTime ? ` (processed in ${result.processingTime}ms)` : '';
    updateStatus(`Description generated successfully${timeInfo}`, 'success');

    // Display text description
    elements.textOutput.textContent = result.text;

    // Handle audio
    if (result.audio) {
        currentAudioSrc = result.audio;
        elements.audioElement.src = result.audio;
        elements.audioControls.style.display = 'flex';
        
        // Auto-play audio for accessibility
        elements.audioElement.play().catch(error => {
            console.log('Auto-play prevented:', error);
            announceToScreenReader('Audio description is ready. Click the play button to listen.');
        });
    } else {
        // Fallback to browser TTS
        speakText(result.text);
    }
}

function speakText(text) {
    if (!window.speechSynthesis) {
        announceToScreenReader('Text-to-speech not available in this browser.');
        return;
    }

    // Stop any current speech
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    const preferences = getPreferences();
    
    utterance.lang = preferences.language || 'en';
    utterance.rate = getSpeechRate(preferences.voiceSpeed);
    utterance.volume = 1.0;
    utterance.pitch = 1.0;

    utterance.onstart = () => {
        announceToScreenReader('Speaking description...');
    };

    utterance.onend = () => {
        announceToScreenReader('Description finished.');
    };

    utterance.onerror = (event) => {
        console.error('Speech synthesis error:', event);
        announceToScreenReader('Error with text-to-speech.');
    };

    window.speechSynthesis.speak(utterance);
}

function getSpeechRate(speed) {
    switch (speed) {
        case 'slow': return 0.7;
        case 'fast': return 1.3;
        default: return 1.0;
    }
}

function replayAudio() {
    if (currentAudioSrc) {
        elements.audioElement.currentTime = 0;
        elements.audioElement.play().catch(error => {
            console.error('Audio replay error:', error);
            announceToScreenReader('Error replaying audio.');
        });
    } else {
        // Replay with TTS
        const text = elements.textOutput.textContent;
        if (text) {
            speakText(text);
        }
    }
}

function updateStatus(message, type) {
    if (elements.statusIndicator) {
        elements.statusIndicator.textContent = message;
        elements.statusIndicator.className = `status-indicator ${type}`;
    }
}

function announceToScreenReader(message) {
    // Create a temporary element for screen reader announcements
    const announcement = document.createElement('div');
    announcement.setAttribute('aria-live', 'polite');
    announcement.setAttribute('aria-atomic', 'true');
    announcement.className = 'sr-only';
    announcement.textContent = message;
    
    document.body.appendChild(announcement);
    
    // Remove after announcement
    setTimeout(() => {
        document.body.removeChild(announcement);
    }, 1000);
}

function handleKeyboardShortcuts(event) {
    // Ctrl/Cmd + U to focus upload area
    if ((event.ctrlKey || event.metaKey) && event.key === 'u') {
        event.preventDefault();
        elements.uploadArea?.focus();
    }
    
    // Ctrl/Cmd + Enter to process image
    if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
        event.preventDefault();
        if (!elements.narrateBtn.disabled) {
            processImage();
        }
    }
    
    // Space to replay audio when focused on replay button
    if (event.key === ' ' && event.target === elements.replayBtn) {
        event.preventDefault();
        replayAudio();
    }
}

// Preferences management
function loadPreferences() {
    const saved = JSON.parse(localStorage.getItem('accessible_narrator_prefs') || '{}');
    
    if (elements.styleSelect && saved.style) {
        elements.styleSelect.value = saved.style;
    }
    if (elements.languageSelect && saved.language) {
        elements.languageSelect.value = saved.language;
    }
    if (elements.voiceSpeedSelect && saved.voiceSpeed) {
        elements.voiceSpeedSelect.value = saved.voiceSpeed;
    }
}

function savePreferences() {
    const preferences = {
        style: elements.styleSelect?.value || 'detailed',
        language: elements.languageSelect?.value || 'en',
        voiceSpeed: elements.voiceSpeedSelect?.value || 'normal'
    };
    
    localStorage.setItem('accessible_narrator_prefs', JSON.stringify(preferences));
}

function getPreferences() {
    return {
        style: elements.styleSelect?.value || 'detailed',
        language: elements.languageSelect?.value || 'en',
        voiceSpeed: elements.voiceSpeedSelect?.value || 'normal'
    };
}

// Utility functions
function fileToDataURL(file) {
	return new Promise((resolve, reject) => {
		const reader = new FileReader();
		reader.onload = () => resolve(reader.result);
		reader.onerror = reject;
		reader.readAsDataURL(file);
	});
}

// Add screen reader only class for announcements
const style = document.createElement('style');
style.textContent = `
    .sr-only {
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        white-space: nowrap;
        border: 0;
    }
`;
document.head.appendChild(style);

// Live Camera Functionality
let liveCamera = {
    stream: null,
    isActive: false,
    detectionInterval: null,
    lastDetection: null,
    detectionCooldown: 3000, // 3 seconds between detections for better accuracy
    currentAudio: null,
    isPlaying: false,
    audioQueue: [],
    elements: {
        liveButton: document.getElementById('liveButton'),
        liveCameraSection: document.getElementById('liveCameraSection'),
        liveVideo: document.getElementById('liveVideo'),
        liveCanvas: document.getElementById('liveCanvas'),
        startLiveButton: document.getElementById('startLiveButton'),
        stopLiveButton: document.getElementById('stopLiveButton'),
        captureLiveButton: document.getElementById('captureLiveButton'),
        stopSpeechButton: document.getElementById('stopSpeechButton'),
        liveStatus: document.getElementById('liveStatus')
    }
};

// Initialize live camera functionality
function initializeLiveCamera() {
    if (liveCamera.elements.liveButton) {
        liveCamera.elements.liveButton.addEventListener('click', toggleLiveCamera);
    }
    
    if (liveCamera.elements.startLiveButton) {
        liveCamera.elements.startLiveButton.addEventListener('click', startLiveDetection);
    }
    
    if (liveCamera.elements.stopLiveButton) {
        liveCamera.elements.stopLiveButton.addEventListener('click', stopLiveDetection);
    }
    
    if (liveCamera.elements.captureLiveButton) {
        liveCamera.elements.captureLiveButton.addEventListener('click', captureAndDescribe);
    }
    
    if (liveCamera.elements.stopSpeechButton) {
        liveCamera.elements.stopSpeechButton.addEventListener('click', stopSpeech);
    }
}

function toggleLiveCamera() {
    if (liveCamera.isActive) {
        stopLiveDetection();
    } else {
        showLiveCameraSection();
    }
}

function showLiveCameraSection() {
    liveCamera.elements.liveCameraSection.style.display = 'block';
    liveCamera.elements.liveCameraSection.scrollIntoView({ behavior: 'smooth' });
    updateLiveStatus('Click "Start Live Detection" to begin', 'info');
}

async function startLiveDetection() {
    try {
        updateLiveStatus('Starting camera...', 'detecting');
        
        // Request camera access
        liveCamera.stream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 640 },
                height: { ideal: 480 },
                facingMode: 'environment' // Use back camera if available
            },
            audio: false
        });
        
        // Set video source
        liveCamera.elements.liveVideo.srcObject = liveCamera.stream;
        
        // Wait for video to be ready
        liveCamera.elements.liveVideo.onloadedmetadata = () => {
            liveCamera.elements.liveVideo.play();
            liveCamera.isActive = true;
            
    // Update UI
    liveCamera.elements.startLiveButton.style.display = 'none';
    liveCamera.elements.stopLiveButton.style.display = 'inline-flex';
    liveCamera.elements.captureLiveButton.style.display = 'inline-flex';
    liveCamera.elements.stopSpeechButton.style.display = 'inline-flex';
            
            updateLiveStatus('Camera active - Starting object detection...', 'detecting');
            
            // Start periodic detection
            startPeriodicDetection();
            
            announceToScreenReader('Live camera started. Object detection is now active.');
        };
        
    } catch (error) {
        console.error('Camera access error:', error);
        updateLiveStatus(`Camera error: ${error.message}`, 'error');
        announceToScreenReader('Failed to access camera. Please check permissions.');
    }
}

function stopLiveDetection() {
    // Stop detection
    if (liveCamera.detectionInterval) {
        clearInterval(liveCamera.detectionInterval);
        liveCamera.detectionInterval = null;
    }
    
    // Stop current audio and clear queue
    if (liveCamera.currentAudio) {
        liveCamera.currentAudio.pause();
        liveCamera.currentAudio = null;
    }
    liveCamera.isPlaying = false;
    liveCamera.audioQueue = [];
    
    // Stop camera
    if (liveCamera.stream) {
        liveCamera.stream.getTracks().forEach(track => track.stop());
        liveCamera.stream = null;
    }
    
    // Reset video
    liveCamera.elements.liveVideo.srcObject = null;
    liveCamera.isActive = false;
    
    // Update UI
    liveCamera.elements.startLiveButton.style.display = 'inline-flex';
    liveCamera.elements.stopLiveButton.style.display = 'none';
    liveCamera.elements.captureLiveButton.style.display = 'none';
    liveCamera.elements.stopSpeechButton.style.display = 'none';
    
    updateLiveStatus('Camera stopped', 'info');
    announceToScreenReader('Live camera stopped.');
}

function startPeriodicDetection() {
    // Run detection every 3 seconds for better accuracy
    liveCamera.detectionInterval = setInterval(() => {
        if (liveCamera.isActive && liveCamera.elements.liveVideo.videoWidth > 0) {
            captureAndDetect();
        }
    }, liveCamera.detectionCooldown);
}

async function captureAndDetect() {
    try {
        const canvas = liveCamera.elements.liveCanvas;
        const video = liveCamera.elements.liveVideo;
        const ctx = canvas.getContext('2d');
        
        // Set canvas size to match video
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        // Draw current video frame to canvas
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        // Convert to base64 with higher quality for better detection
        const imageData = canvas.toDataURL('image/jpeg', 0.95);
        
        // Send for detection
        await processLiveImage(imageData);
        
    } catch (error) {
        console.error('Live detection error:', error);
        updateLiveStatus(`Detection error: ${error.message}`, 'error');
    }
}

async function processLiveImage(imageData) {
    try {
        updateLiveStatus('Detecting objects...', 'detecting');
        
        const response = await fetch('api/narrate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                image_base64: imageData,
                preferences: {
                    style: elements.styleSelect.value,
                    language: elements.languageSelect.value,
                    voiceSpeed: elements.voiceSpeedSelect.value
                }
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Update status with detection results
        const objectCount = data.detections?.total_count || 0;
        updateLiveStatus(`Detected ${objectCount} objects - Speaking: ${data.text.substring(0, 50)}...`, 'success');
        
        // Play TTS for live detection
        if (data.audio_base64) {
            playLiveAudio(data.audio_base64);
        }
        
        // Update main output area
        elements.textOutput.textContent = data.text;
        elements.audioControls.style.display = 'block';
        
        announceToScreenReader(`Live detection: ${data.text}`);
        
    } catch (error) {
        console.error('Live processing error:', error);
        updateLiveStatus(`Processing error: ${error.message}`, 'error');
    }
}

async function captureAndDescribe() {
    if (!liveCamera.isActive) return;
    
    try {
        updateLiveStatus('Capturing and describing...', 'detecting');
        await captureAndDetect();
    } catch (error) {
        console.error('Capture error:', error);
        updateLiveStatus(`Capture error: ${error.message}`, 'error');
    }
}

function playLiveAudio(audioBase64) {
    try {
        const audioBlob = base64ToBlob(audioBase64, 'audio/wav');
        const audioUrl = URL.createObjectURL(audioBlob);
        
        // If audio is currently playing, queue this one
        if (liveCamera.isPlaying) {
            liveCamera.audioQueue.push(audioUrl);
            return;
        }
        
        // Play immediately
        playNextAudio(audioUrl);
        
    } catch (error) {
        console.error('Live audio error:', error);
    }
}

function playNextAudio(audioUrl) {
    if (!audioUrl && liveCamera.audioQueue.length > 0) {
        audioUrl = liveCamera.audioQueue.shift();
    }
    
    if (!audioUrl) {
        liveCamera.isPlaying = false;
        return;
    }
    
    liveCamera.isPlaying = true;
    liveCamera.currentAudio = new Audio(audioUrl);
    
    liveCamera.currentAudio.play().catch(error => {
        console.error('Live audio playback error:', error);
        liveCamera.isPlaying = false;
        // Try next audio in queue
        playNextAudio();
    });
    
    // When current audio ends, play next in queue
    liveCamera.currentAudio.onended = () => {
        URL.revokeObjectURL(audioUrl);
        liveCamera.isPlaying = false;
        liveCamera.currentAudio = null;
        
        // Play next audio in queue after a short delay
        setTimeout(() => {
            playNextAudio();
        }, 100);
    };
    
    // Handle audio errors
    liveCamera.currentAudio.onerror = () => {
        console.error('Audio playback error');
        liveCamera.isPlaying = false;
        liveCamera.currentAudio = null;
        URL.revokeObjectURL(audioUrl);
        
        // Try next audio in queue
        setTimeout(() => {
            playNextAudio();
        }, 100);
    };
}

function stopSpeech() {
    // Stop current audio
    if (liveCamera.currentAudio) {
        liveCamera.currentAudio.pause();
        liveCamera.currentAudio = null;
    }
    
    // Clear audio queue
    liveCamera.audioQueue = [];
    liveCamera.isPlaying = false;
    
    // Update status
    updateLiveStatus('Speech stopped', 'info');
    announceToScreenReader('Speech stopped.');
}

function updateLiveStatus(message, type = 'info') {
    const statusElement = liveCamera.elements.liveStatus;
    if (statusElement) {
        statusElement.textContent = message;
        statusElement.className = `live-status ${type}`;
    }
}

function base64ToBlob(base64, mimeType) {
    const byteCharacters = atob(base64);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    return new Blob([byteArray], { type: mimeType });
}

// Live camera initialization moved to main DOMContentLoaded listener