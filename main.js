let mediaRecorder;
let audioChunks = [];
let isRecording = false;

document.addEventListener('DOMContentLoaded', function() {
    initNavigation();
    initVoiceRecording();
    initTextInput();
});

function initNavigation() {
    const navLinks = document.querySelectorAll('[data-page]');
    const pages = {
        'home': document.getElementById('page-home'),
        'vani-voice': document.getElementById('page-vani-voice'),
        'analytics': document.getElementById('page-analytics')
    };
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetPage = this.getAttribute('data-page');
            
            navLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
            
            Object.keys(pages).forEach(pageKey => {
                if (pageKey === targetPage) {
                    pages[pageKey].style.display = 'block';
                } else {
                    pages[pageKey].style.display = 'none';
                }
            });
        });
    });
    
    document.querySelector('[data-page="home"]').classList.add('active');
    pages['home'].style.display = 'block';
    pages['vani-voice'].style.display = 'none';
    pages['analytics'].style.display = 'none';
}

function initVoiceRecording() {
    const recordButton = document.getElementById('record-button');
    const chatWindow = document.getElementById('chat-window');
    const confirmationButtons = document.getElementById('confirmation-buttons');
    
    confirmationButtons.style.display = 'none';
    
    recordButton.addEventListener('click', async function() {
        if (!isRecording) {
            await startRecording();
        } else {
            await stopRecording();
        }
    });
}

async function startRecording() {
    const recordButton = document.getElementById('record-button');
    const chatWindow = document.getElementById('chat-window');
    
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        
        mediaRecorder.addEventListener('dataavailable', event => {
            audioChunks.push(event.data);
        });
        
        mediaRecorder.addEventListener('stop', async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            stream.getTracks().forEach(track => track.stop());
            await sendAudioToBackend(audioBlob);
        });
        
        mediaRecorder.start();
        isRecording = true;
        
        recordButton.textContent = 'Stop Recording';
        recordButton.classList.add('recording');
        
        addMessageToChat('🎙️ Recording... Speak your command now!', 'system');
        
    } catch (error) {
        console.error('Error accessing microphone:', error);
        addMessageToChat('❌ Error: Could not access microphone. Please check permissions.', 'error');
    }
}

async function stopRecording() {
    const recordButton = document.getElementById('record-button');
    
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
        isRecording = false;
        
        recordButton.textContent = 'Record Voice';
        recordButton.classList.remove('recording');
        
        addMessageToChat('⏸️ Processing your voice command...', 'system');
    }
}

async function sendAudioToBackend(audioBlob) {
    const chatWindow = document.getElementById('chat-window');
    
    try {
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.webm');
        
        const response = await fetch('/process-audio', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`Server returned ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            addMessageToChat(`📝 You said: "${result.transcription}"`, 'user');
            
            if (result.action === 'update' && result.field && result.value) {
                const fieldNames = {
                    'shop_name': 'Shop Name',
                    'description': 'Description',
                    'announcement': 'Announcement'
                };
                
                const fieldDisplayName = fieldNames[result.field] || result.field;
                
                addMessageToChat(`✅ ${result.message || 'Updated successfully!'}`, 'success');
                addMessageToChat(`📊 ${fieldDisplayName}: "${result.value}"`, 'info');
                
                if (result.website) {
                    setTimeout(() => {
                        addMessageToChat('🎉 Your website has been updated! Visit the Analytics page to see it live.', 'success');
                    }, 500);
                }
            } else if (result.action === 'unknown') {
                addMessageToChat('🤔 Sorry, I didn\'t understand that command. Try saying "Change my shop name to..." or "Update my description to..."', 'info');
            } else {
                addMessageToChat('✅ Command processed successfully!', 'success');
            }
        } else {
            addMessageToChat(`❌ Error: ${result.error || 'Failed to process audio'}`, 'error');
        }
        
    } catch (error) {
        console.error('Error sending audio:', error);
        addMessageToChat(`❌ Error: Failed to send audio to server. ${error.message}`, 'error');
    }
}

function addMessageToChat(message, type = 'system') {
    const chatWindow = document.getElementById('chat-window');
    
    if (chatWindow.querySelector('p')?.textContent === 'Chat messages will appear here...') {
        chatWindow.innerHTML = '';
    }
    
    const messageElement = document.createElement('div');
    messageElement.className = `chat-message ${type}`;
    messageElement.textContent = message;
    
    chatWindow.appendChild(messageElement);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

function initTextInput() {
    const textInput = document.getElementById('text-input');
    const sendButton = document.getElementById('text-send-button');
    
    async function sendTextCommand() {
        const text = textInput.value.trim();
        
        if (!text) {
            addMessageToChat('⚠️ Please type a command first.', 'info');
            return;
        }
        
        addMessageToChat(`💬 You typed: "${text}"`, 'user');
        addMessageToChat('⏸️ Processing your command...', 'system');
        
        textInput.value = '';
        
        try {
            const response = await fetch('/process-text', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text: text })
            });
            
            if (!response.ok) {
                throw new Error(`Server returned ${response.status}`);
            }
            
            const result = await response.json();
            
            if (result.success) {
                if (result.action === 'update' && result.field && result.value) {
                    const fieldNames = {
                        'shop_name': 'Shop Name',
                        'description': 'Description',
                        'announcement': 'Announcement'
                    };
                    
                    const fieldDisplayName = fieldNames[result.field] || result.field;
                    
                    addMessageToChat(`✅ ${result.message || 'Updated successfully!'}`, 'success');
                    addMessageToChat(`📊 ${fieldDisplayName}: "${result.value}"`, 'info');
                    
                    if (result.website) {
                        setTimeout(() => {
                            addMessageToChat('🎉 Your website has been updated! Visit the Analytics page to see it live.', 'success');
                        }, 500);
                    }
                } else if (result.action === 'unknown') {
                    addMessageToChat('🤔 Sorry, I didn\'t understand that command. Try typing "Change my shop name to..." or "Update my description to..."', 'info');
                } else {
                    addMessageToChat('✅ Command processed successfully!', 'success');
                }
            } else {
                addMessageToChat(`❌ Error: ${result.error || 'Failed to process command'}`, 'error');
            }
            
        } catch (error) {
            console.error('Error sending text:', error);
            addMessageToChat(`❌ Error: Failed to send command to server. ${error.message}`, 'error');
        }
    }
    
    sendButton.addEventListener('click', sendTextCommand);
    
    textInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendTextCommand();
        }
    });
}
