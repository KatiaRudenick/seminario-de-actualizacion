const ws = new WebSocket(`ws://${window.location.host}`);
let username = '';

document.getElementById('set-username').onclick = () => {
    username = document.getElementById('username').value;
    document.getElementById('username').disabled = true;
    document.getElementById('set-username').disabled = true;
};

ws.onmessage = (event) => {
    const messagesDiv = document.getElementById('messages');

    // Convierte Blob a texto
    const reader = new FileReader();
    reader.onload = () => {
        const message = reader.result; // Esto es un string

        // Descifra el mensaje recibido
        const decryptedMessage = CryptoJS.AES.decrypt(message, 'mishka1234').toString(CryptoJS.enc.Utf8);

        // Evita mostrar el mismo mensaje que fue enviado por ese usuario
        if (decryptedMessage && !decryptedMessage.startsWith(username)) {
            // Div con estilo para el mensaje recibido
            const receivedMessageDiv = `<div class="message message-received">${decryptedMessage}</div>`;
            messagesDiv.innerHTML += receivedMessageDiv;
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
    };
    reader.readAsText(event.data); // Lee el Blob como texto
};

document.getElementById('send-message').onclick = () => {
    const messageInput = document.getElementById('message-input');
    const message = `${username}: ${messageInput.value}`;
    
    if (username && messageInput.value) {
        // Cifra el mensaje antes de enviarlo
        const encryptedMessage = CryptoJS.AES.encrypt(message, 'mishka1234').toString();
        console.log("Encrypted Message: ", encryptedMessage); 
        
        // Div con estilo para el mensaje enviado
        const messagesDiv = document.getElementById('messages');
        const sentMessageDiv = `<div class="message message-sent">${message}</div>`;
        messagesDiv.innerHTML += sentMessageDiv;

        ws.send(encryptedMessage);
        messageInput.value = ''; // Limpia el campo de entrada

        messagesDiv.scrollTop = messagesDiv.scrollHeight; 
    }
};
