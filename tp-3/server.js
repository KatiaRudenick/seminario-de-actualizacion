const express = require('express');
const WebSocket = require('ws');

const app = express();
const PORT = 3000;

app.use(express.static('public'));

//Inicio el servidor HTTP
const server = app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});

// Creo el servidor WebSocket
const wss = new WebSocket.Server({ server });

wss.on('connection', (ws) => {
    console.log('New client connected!');

    ws.on('message', (message) => {
        console.log(`Received message: ${message}`);

        
        wss.clients.forEach(client => {
            if (client.readyState === WebSocket.OPEN) {
                client.send(message); // Envia el msj cifrado
            }
        });
    });

    ws.on('close', () => {
        console.log('Client disconnected');
    });
});

console.log('WebSocket server is running on ws://localhost:8080');
