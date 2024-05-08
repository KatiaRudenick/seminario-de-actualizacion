from flask import Flask, request, jsonify
from flask_cors import CORS #Import the CORS extension
import mysql.connector


app = Flask(__name__)
CORS(app)

# Función para verificar si la base de datos existe
def check_database(cursor):
    cursor.execute("SHOW DATABASES")
    databases = cursor.fetchall()
    for database in databases:
        if database[0] == 'myagenda':
            return True
    return False

# Función para crear las tablas si no existen
def create_tables(cursor):
    cursor.execute("CREATE TABLE IF NOT EXISTS Contact (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, firstName VARCHAR(45) NOT NULL, surnames VARCHAR(45) NOT NULL, address VARCHAR(45) NOT NULL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS Contact_Phone (phone VARCHAR(45) NOT NULL, Contact_id INT NOT NULL, FOREIGN KEY (Contact_id) REFERENCES Contact(id))")

# Configuración de la base de datos
db = mysql.connector.connect(
    host="localhost",
    user="root",
)

cursor = db.cursor()

# Verificar si la base de datos existe
if not check_database(cursor):
    cursor.execute("CREATE DATABASE myagenda")
    db.commit()

# Conectar a la base de datos myagenda
db = mysql.connector.connect(
    host="localhost",
    user="root",
    database="myagenda"
)
cursor = db.cursor()

# Crear las tablas si no existen
create_tables(cursor)


# Ruta para crear un nuevo contacto
@app.route('/add_contact', methods=['POST'])
def add_contact():

    print("Se recibio una solicitud POST en /add_contact")
    data = request.json
    first_name = data['first_name']
    surnames = data['surnames']
    address = data['address']
    phones = data.get('phones', [])  # Si no se proporcionan teléfonos, se establece como una lista vacía
    query = "INSERT INTO Contact (firstName, surnames, address) VALUES (%s, %s, %s)"
    cursor.execute(query, (first_name, surnames, address))
    contact_id = cursor.lastrowid
    # Insertar los teléfonos del contacto
    for phone in phones:
        phone_number = phone['phone']
        query = "INSERT INTO Contact_Phone (phone, Contact_id) VALUES (%s, %s)"
        cursor.execute(query, (phone_number, contact_id))
    db.commit()
    return jsonify({"mensaje": "Contacto creado exitosamente"})

# Ruta para obtener todos los contactos
@app.route('/get_contacts', methods=['GET'])
def get_contacts():
    cursor.execute("SELECT * FROM Contact")
    contacts = cursor.fetchall()
    contacts_json = []
    for contact in contacts:
        contact_dict = {
            "id": contact[0],
            "first_name": contact[1],
            "surnames": contact[2],
            "address": contact[3]
        }
        # Obtener los teléfonos del contacto
        cursor.execute("SELECT phone FROM Contact_Phone WHERE Contact_id = %s", (contact[0],))
        phones = cursor.fetchall()
        phones_list = [phone[0] for phone in phones]
        contact_dict["phones"] = phones_list
        contacts_json.append(contact_dict)
    return jsonify(contacts_json)

# Ruta para actualizar un contacto existente
@app.route('/update_contact/<int:id>', methods=['PUT'])
def update_contact(id):
    data = request.json
    first_name = data.get('first_name')
    surnames = data.get('surnames')
    address = data.get('address')
    phones = data.get('phones', [])

    # Construir la consulta SQL para actualizar los datos del contacto
    query = "UPDATE Contact SET "
    placeholders = []
    values = []

    if first_name:
        placeholders.append("firstName = %s")
        values.append(first_name)
    if surnames:
        placeholders.append("surnames = %s")
        values.append(surnames)
    if address:
        placeholders.append("address = %s")
        values.append(address)

    # Si hay campos para actualizar
    if placeholders:
        query += ", ".join(placeholders)
        query += " WHERE id = %s"
        values.append(id)
        cursor.execute(query, tuple(values))
        db.commit()

    # Insertar nuevos teléfonos si se proporcionan
    for phone in phones:
        phone_number = phone['phone']
        query = "INSERT INTO Contact_Phone (phone, Contact_id) VALUES (%s, %s)"
        cursor.execute(query, (phone_number, id))
        db.commit()

    return jsonify({"mensaje": "Contacto actualizado exitosamente"})

# Ruta para eliminar un contacto
@app.route('/delete_contact/<int:id>', methods=['DELETE'])
def delete_contact(id):
    # Eliminar los teléfonos del contacto
    cursor.execute("DELETE FROM Contact_Phone WHERE Contact_id = %s", (id,))
    # Eliminar el contacto
    cursor.execute("DELETE FROM Contact WHERE id = %s", (id,))
    db.commit()
    return jsonify({"mensaje": "Contacto eliminado exitosamente"})

if __name__ == '__main__':
    app.run(debug=True)