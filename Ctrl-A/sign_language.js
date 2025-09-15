// Sign Language Recognition Module
class SignLanguageRecognition {
    constructor() {
        this.isActive = false;
        this.camera = null;
        this.canvas = null;
        this.ctx = null;
        this.recognitionInterval = null;
        this.gestureBuffer = '';
        this.lastGesture = '';
        this.gestureCooldown = 0;
        this.callbacks = [];
        this.socket = null;
        this.serverAvailable = false;
    }

    // Initialize camera for sign language recognition
    async initCamera() {
        try {
            // First try to connect to the prediction.py server
            await this.initServerConnection();
            
            if (this.serverAvailable) {
                console.log('Using prediction.py server for sign language detection');
                return true;
            }
            
            // Fallback to local camera processing
            const stream = await navigator.mediaDevices.getUserMedia({ 
                video: { 
                    width: { ideal: 640 },
                    height: { ideal: 480 },
                    facingMode: 'user'
                } 
            });
            
            this.camera = stream;
            
            // Create canvas for processing
            this.canvas = document.createElement('canvas');
            this.ctx = this.canvas.getContext('2d');
            this.canvas.width = 640;
            this.canvas.height = 480;
            
            return true;
        } catch (error) {
            console.error('Camera initialization failed:', error);
            return false;
        }
    }

    // Initialize connection to prediction.py server
    async initServerConnection() {
        try {
            // Try to start detection on the server
            const response = await fetch('http://localhost:5001/api/start_detection', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (response.ok) {
                this.serverAvailable = true;
                console.log('Connected to prediction.py server');
                
                // Initialize WebSocket for real-time updates
                this.initWebSocket();
                return true;
            } else {
                console.log('Prediction.py server not available');
                return false;
            }
        } catch (error) {
            console.log('Prediction.py server not available:', error.message);
            return false;
        }
    }

    // Initialize WebSocket connection for real-time updates
    initWebSocket() {
        try {
            this.socket = new WebSocket('ws://localhost:5001');
            
            this.socket.onopen = () => {
                console.log('WebSocket connected to sign language server');
            };
            
            this.socket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleServerData(data);
                } catch (error) {
                    console.error('Error parsing server data:', error);
                }
            };
            
            this.socket.onclose = () => {
                console.log('WebSocket disconnected from sign language server');
                this.socket = null;
            };
            
            this.socket.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
        } catch (error) {
            console.error('Failed to initialize WebSocket:', error);
        }
    }

    // Handle data from prediction.py server
    handleServerData(data) {
        if (data.type === 'sign_detected' && data.character) {
            const currentTime = Date.now();
            if (currentTime - this.gestureCooldown > 1500) { // 1.5 second cooldown
                this.gestureBuffer += data.character;
                console.log('Server detected sign:', data.character, 'Buffer:', this.gestureBuffer);
                
                // Process the detected character
                this.processServerGesture(data.character, data.confidence, data.action);
                
                this.gestureCooldown = currentTime;
            }
        }
    }

    // Process gesture from server
    processServerGesture(character, confidence, action) {
        // Map characters to commands
        const commandMap = {
            'A': 'help',
            'B': 'music', 
            'C': 'camera',
            'D': 'legal',
            'E': 'schemes',
            'F': 'assistant',
            'G': 'tasks',
            'H': 'clear',
            'I': 'stop',
            'J': 'start',
            'K': 'yes',
            'L': 'no',
            'M': 'more',
            'N': 'next',
            'O': 'ok',
            'P': 'play',
            'Q': 'quit',
            'R': 'repeat',
            'S': 'space',
            'T': 'time',
            'U': 'up',
            'V': 'down',
            'W': 'wait',
            'X': 'exit',
            'Y': 'yes',
            'Z': 'zero'
        };

        const command = commandMap[character] || character.toLowerCase();
        
        // Execute command
        this.executeCommand(command);
    }

    // Start sign language recognition
    startRecognition() {
        if (this.isActive) return;
        
        this.isActive = true;
        this.gestureBuffer = '';
        this.lastGesture = '';
        this.gestureCooldown = 0;
        
        if (this.serverAvailable) {
            // Server-based recognition is already running
            console.log('Sign language recognition started (server-based)');
        } else {
            // Start local recognition loop
            this.recognitionInterval = setInterval(() => {
                this.processFrame();
            }, 100); // Process every 100ms
            console.log('Sign language recognition started (local)');
        }
    }

    // Stop sign language recognition
    stopRecognition() {
        if (!this.isActive) return;
        
        this.isActive = false;
        
        if (this.serverAvailable) {
            // Stop server-based recognition
            fetch('http://localhost:5001/api/stop_detection', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            }).catch(error => {
                console.log('Server not available for stop command');
            });
        } else {
            // Stop local recognition
            if (this.recognitionInterval) {
                clearInterval(this.recognitionInterval);
                this.recognitionInterval = null;
            }
        }
        
        console.log('Sign language recognition stopped');
    }

    // Process video frame for gesture recognition
    processFrame() {
        if (!this.isActive || !this.camera) return;
        
        try {
            // Get video element (assuming it exists)
            const video = document.querySelector('video');
            if (!video || !video.videoWidth) return;
            
            // Draw frame to canvas
            this.ctx.drawImage(video, 0, 0, this.canvas.width, this.canvas.height);
            
            // Get image data
            const imageData = this.ctx.getImageData(0, 0, this.canvas.width, this.canvas.height);
            
            // Detect hand gestures
            const gesture = this.detectHandGesture(imageData);
            
            if (gesture && gesture !== this.lastGesture && this.gestureCooldown <= 0) {
                this.processGesture(gesture);
                this.lastGesture = gesture;
                this.gestureCooldown = 10; // 1 second cooldown
            }
            
            if (this.gestureCooldown > 0) {
                this.gestureCooldown--;
            }
            
        } catch (error) {
            console.error('Frame processing error:', error);
        }
    }

    // Detect hand gesture from image data
    detectHandGesture(imageData) {
        const data = imageData.data;
        const width = imageData.width;
        const height = imageData.height;
        
        // Simple gesture detection based on hand position and movement
        const handRegions = this.detectHandRegions(data, width, height);
        
        if (handRegions.length === 0) return null;
        
        // Analyze hand shape and position
        const gesture = this.analyzeHandShape(handRegions[0]);
        
        return gesture;
    }

    // Detect hand regions in image
    detectHandRegions(data, width, height) {
        const regions = [];
        const visited = new Array(width * height).fill(false);
        
        // Look for skin-colored regions
        for (let y = 0; y < height; y += 5) {
            for (let x = 0; x < width; x += 5) {
                const index = (y * width + x) * 4;
                if (visited[y * width + x]) continue;
                
                const r = data[index];
                const g = data[index + 1];
                const b = data[index + 2];
                
                // Check if pixel is skin-colored
                if (this.isSkinColor(r, g, b)) {
                    const region = this.floodFill(data, width, height, x, y, visited, r, g, b);
                    if (region.area > 1000) { // Minimum hand size
                        regions.push(region);
                    }
                }
            }
        }
        
        return regions;
    }

    // Check if color is skin-colored
    isSkinColor(r, g, b) {
        // Simple skin color detection
        const skinR = r > 95 && r < 255;
        const skinG = g > 40 && g < 255;
        const skinB = b > 20 && b < 255;
        const skinDiff = Math.abs(r - g) > 15;
        const skinRatio = r / g > 1.185;
        
        return skinR && skinG && skinB && skinDiff && skinRatio;
    }

    // Flood fill algorithm for region detection
    floodFill(data, width, height, startX, startY, visited, targetR, targetG, targetB) {
        const stack = [{x: startX, y: startY}];
        const region = {
            area: 0,
            minX: startX,
            maxX: startX,
            minY: startY,
            maxY: startY,
            centerX: startX,
            centerY: startY
        };
        
        while (stack.length > 0) {
            const {x, y} = stack.pop();
            const index = y * width + x;
            
            if (visited[index]) continue;
            if (x < 0 || x >= width || y < 0 || y >= height) continue;
            
            const pixelIndex = index * 4;
            const r = data[pixelIndex];
            const g = data[pixelIndex + 1];
            const b = data[pixelIndex + 2];
            
            // Check if pixel color is similar to target color
            const colorDiff = Math.abs(r - targetR) + Math.abs(g - targetG) + Math.abs(b - targetB);
            if (colorDiff > 30) continue;
            
            visited[index] = true;
            region.area++;
            region.minX = Math.min(region.minX, x);
            region.maxX = Math.max(region.maxX, x);
            region.minY = Math.min(region.minY, y);
            region.maxY = Math.max(region.maxY, y);
            
            // Add neighbors to stack
            stack.push({x: x + 1, y}, {x: x - 1, y}, {x, y: y + 1}, {x, y: y - 1});
        }
        
        region.centerX = (region.minX + region.maxX) / 2;
        region.centerY = (region.minY + region.maxY) / 2;
        
        return region;
    }

    // Analyze hand shape to determine gesture
    analyzeHandShape(handRegion) {
        const {centerX, centerY, minX, maxX, minY, maxY} = handRegion;
        const width = maxX - minX;
        const height = maxY - minY;
        const aspectRatio = width / height;
        
        // Simple gesture recognition based on hand position and shape
        if (centerY < 200) {
            return 'A'; // Hand at top
        } else if (centerY > 300) {
            return 'B'; // Hand at bottom
        } else if (centerX < 200) {
            return 'C'; // Hand at left
        } else if (centerX > 400) {
            return 'D'; // Hand at right
        } else if (aspectRatio > 1.2) {
            return 'E'; // Wide hand
        } else if (aspectRatio < 0.8) {
            return 'F'; // Tall hand
        } else {
            return 'G'; // Center hand
        }
    }

    // Process detected gesture
    processGesture(gesture) {
        this.gestureBuffer += gesture;
        
        // Check for complete words or commands
        if (this.gestureBuffer.length >= 3) {
            const word = this.gestureBuffer.slice(-3);
            this.processGestureWord(word);
        }
        
        // Notify callbacks
        this.callbacks.forEach(callback => {
            callback(gesture, this.gestureBuffer);
        });
    }

    // Process complete gesture word
    processGestureWord(word) {
        // Map gesture combinations to commands
        const commands = {
            'ABC': 'help',
            'DEF': 'music',
            'GHI': 'reminder',
            'JKL': 'camera',
            'MNO': 'legal',
            'PQR': 'schemes',
            'STU': 'assistant',
            'VWX': 'stop',
            'YZ': 'clear'
        };
        
        if (commands[word]) {
            this.executeCommand(commands[word]);
            this.gestureBuffer = ''; // Clear buffer
        }
    }

    // Execute gesture command
    executeCommand(command) {
        console.log('Executing gesture command:', command);
        
        // Dispatch custom event
        const event = new CustomEvent('signLanguageCommand', {
            detail: { command: command }
        });
        document.dispatchEvent(event);
    }

    // Add callback for gesture detection
    onGesture(callback) {
        this.callbacks.push(callback);
    }

    // Remove callback
    removeCallback(callback) {
        const index = this.callbacks.indexOf(callback);
        if (index > -1) {
            this.callbacks.splice(index, 1);
        }
    }

    // Get current gesture buffer
    getGestureBuffer() {
        return this.gestureBuffer;
    }

    // Clear gesture buffer
    clearBuffer() {
        this.gestureBuffer = '';
        
        // Also clear server buffer if available
        if (this.serverAvailable) {
            fetch('http://localhost:5001/api/clear_buffer', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            }).catch(error => {
                console.log('Server not available for clear command');
            });
        }
    }

    // Cleanup
    destroy() {
        this.stopRecognition();
        
        if (this.camera) {
            this.camera.getTracks().forEach(track => track.stop());
            this.camera = null;
        }
        
        if (this.socket) {
            this.socket.close();
            this.socket = null;
        }
        
        this.callbacks = [];
    }
}

// Global sign language recognition instance
try {
    window.signLanguageRecognition = new SignLanguageRecognition();
    console.log('Sign language recognition module loaded successfully');
} catch (error) {
    console.error('Error creating sign language recognition module:', error);
    // Create a fallback instance
    window.signLanguageRecognition = {
        isActive: false,
        initCamera: async function() { 
            console.log('Fallback: Camera initialization not available');
            return false; 
        },
        startRecognition: function() { 
            console.log('Fallback: Sign language recognition not available');
        },
        stopRecognition: function() { 
            console.log('Fallback: Sign language recognition not available');
        },
        clearBuffer: function() { 
            console.log('Fallback: Buffer clear not available');
        }
    };
}

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SignLanguageRecognition;
}

// Lightweight page-level bootstrap to attach UI controls if container exists
document.addEventListener('DOMContentLoaded', async function() {
    if (!window.signLanguageRecognition) {
        console.error('Sign language module failed to initialize');
        return;
    }

    const container = document.querySelector('[data-sign-input-container]');
    if (!container) {
        console.log('Sign-language UI container not found on this page (data-sign-input-container).');
        return;
    }

    // Create minimal UI controls
    const startBtn = document.createElement('button');
    startBtn.textContent = 'Start Sign Input';
    startBtn.setAttribute('type', 'button');
    startBtn.style.marginRight = '8px';

    const stopBtn = document.createElement('button');
    stopBtn.textContent = 'Stop Sign Input';
    stopBtn.setAttribute('type', 'button');
    stopBtn.disabled = true;

    const bufferEl = document.createElement('div');
    bufferEl.style.marginTop = '8px';
    bufferEl.style.fontFamily = 'monospace';
    bufferEl.style.fontSize = '0.9rem';

    container.appendChild(startBtn);
    container.appendChild(stopBtn);
    container.appendChild(bufferEl);

    const updateBuffer = () => {
        try {
            bufferEl.textContent = window.signLanguageRecognition.getGestureBuffer?.() || '';
        } catch (e) {
            bufferEl.textContent = '';
        }
    };

    // Reflect commands to the page via custom event already implemented as signLanguageCommand
    const onGesture = (gesture, buffer) => {
        bufferEl.textContent = buffer;
    };

    startBtn.onclick = async () => {
        const ok = await window.signLanguageRecognition.initCamera();
        if (!ok) return;
        window.signLanguageRecognition.onGesture?.(onGesture);
        window.signLanguageRecognition.startRecognition();
        startBtn.disabled = true;
        stopBtn.disabled = false;
        updateBuffer();
    };

    stopBtn.onclick = () => {
        window.signLanguageRecognition.stopRecognition();
        stopBtn.disabled = true;
        startBtn.disabled = false;
        updateBuffer();
    };
});
