const baseApiUrl = "http://127.0.0.1:5000";

document.addEventListener("DOMContentLoaded", function () {
    getContacts();
});

// Función para enviar una solicitud POST para agregar un nuevo contacto
function addContact() {
    var data = {
        first_name: document.getElementById("first_name").value,
        surnames: document.getElementById("surnames").value,
        address: document.getElementById("address").value,
        phones: [{ phone: document.getElementById("phone").value }]
    };

    fetch('http://127.0.0.1:5000/add_contact', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        alert(data.mensaje);
        // Recargar la lista de contactos después de agregar uno nuevo
        getContacts();
    })
    .catch(error => {
        console.error('Error al agregar contacto:', error);
    });
}

// Función para cargar todos los contactos existentes
function getContacts() {
    fetch('http://127.0.0.1:5000/get_contacts')
      .then(response => response.json())
      .then(data => {
        var tableBody = document.getElementById("tabla-contactos-body");
        tableBody.innerHTML = "";
  
        data.forEach(contact => {
          var newRow = tableBody.insertRow();
  
          // Insert cells with contact data
          newRow.insertCell().textContent = contact.id;
          newRow.insertCell().textContent = contact.first_name;
          newRow.insertCell().textContent = contact.surnames;
          newRow.insertCell().textContent = contact.address;
  
          // Concatenate phone numbers
          var phones = contact.phones.join(", ");
          newRow.insertCell().textContent = phones;
  
          // Create a container element for the buttons
          var buttonContainer = document.createElement("div");
          buttonContainer.style.textAlign = "center"; // Centrar los botones verticalmente
  
          // Create edit button
          var editButton = document.createElement("button");
          editButton.textContent = "UPDATE";
          editButton.style.backgroundColor = "#B2B3F4"; // Pink color
          editButton.style.color = "white"; // White text color
          editButton.style.border = "2px solid #B2B3F4"; // Border color
          editButton.style.borderRadius = "5px";
          editButton.style.cursor = "pointer"; // Change cursor to pointer on hover
          editButton.style.marginBottom = "10px";
          editButton.style.fontFamily = "'Monaco', monospace";
          
          editButton.onclick = function() {
            updateContact(contact.id);
          };
          buttonContainer.appendChild(editButton);

          buttonContainer.appendChild(document.createElement("br"));

          // Create delete button
          var deleteButton = document.createElement("button");
          deleteButton.style.backgroundColor = "#B2B3F4";
          deleteButton.style.color = "white";
          deleteButton.style.border = "2px solid #B2B3F4";
          deleteButton.style.borderRadius = "5px";
          deleteButton.style.cursor = "pointer"; // Change cursor to pointer on hover
          deleteButton.style.fontFamily = "'Monaco', monospace";
          deleteButton.textContent = "DELETE";
          deleteButton.onclick = function() {
            deleteContact(contact.id);
          };
          buttonContainer.appendChild(deleteButton);
  
          // Add button container to the last cell
          var lastCell = newRow.insertCell();
          lastCell.appendChild(buttonContainer);
        });
      })
      .catch(error => {
        console.error('Error al cargar contactos:', error);
      });
  }

// Función para actualizar un contacto existente
function updateContact(id) {
    var data = {
        first_name: document.getElementById("first_name").value,
        surnames: document.getElementById("surnames").value,
        address: document.getElementById("address").value,
        phones: [{ phone: document.getElementById("phone").value }]
    };

    fetch(baseApiUrl + '/update_contact/' + id, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        alert(data.mensaje);
    })
    .catch(error => {
        console.error('Error al actualizar contacto:', error);
    });
}

// Función para eliminar un contacto existente
function deleteContact(id) {
    fetch(baseApiUrl + '/delete_contact/' + id, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        alert(data.mensaje);
    })
    .catch(error => {
        console.error('Error al eliminar contacto:', error);
    });
}
