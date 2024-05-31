from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import timedelta
import mysql.connector
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity


# Creo la app Flask
app = Flask(__name__)
CORS(app)

# Configuraciones de la app Flask
app.config['JWT_SECRET_KEY'] = 'mishka' # Establezco la clave secreta que uso para firmar los tokens JWT
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/controlluser' # Configuro la URI de la base de datos para SQLAlchemy. En este caso uso MySQL con el usuario 'root' y la base de datos 'controlluser'.
app.config['JWT_EXPIRATION_DELTA'] = timedelta(days=1) # Configuro el tiempo de expiracion de los tokens JWT.Se vencen despues de 1 dia.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Inicializo extensiones
db = SQLAlchemy(app) #permite interactuar con la base de datos.
bcrypt = Bcrypt(app) # se usa para hashear y verificar contraseñas de manera segura
jwt = JWTManager(app)# se usa para manejar la autenticación basada en tokens JWT.


# Verifica la existencia de la base de datos
def check_database(cursor):
    cursor.execute("SHOW DATABASES")
    databases = cursor.fetchall()
    for database in databases:
        if database[0] == "controlluser":
            return True
    return False

# Crea las tablas en la base de datos si no existe
def create_tables(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS User (
            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(45) NOT NULL,
            password VARCHAR(255) NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Category (
            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(45) NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Action (
            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(45) NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS UserCategory (
            user_id INT,
            category_id INT,
            FOREIGN KEY (user_id) REFERENCES User(id),
            FOREIGN KEY (category_id) REFERENCES Category(id),
            PRIMARY KEY (user_id, category_id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS CategoryAction (
            category_id INT,
            action_id INT,
            FOREIGN KEY (category_id) REFERENCES Category(id),
            FOREIGN KEY (action_id) REFERENCES Action(id),
            PRIMARY KEY (category_id, action_id)
        )
    """)

# Crea categorias y acciones por defecto
def create_default_categories_and_actions():
    default_categories = ['admin', 'client']
    default_actions = {
        'client': ['agregarProducto', 'eliminarProducto', 'pagarCompra', 'pagarConTarjeta'],
        'admin': [
            'editarUsuario', 'eliminarUsuario', 'crearGrupo', 
            'editarGrupo', 'eliminarGrupo', 'crearAccion', 
            'editarAccion', 'eliminarAccion'
        ]
    }

    
    for category_name in default_categories:
        if not Category.query.filter_by(name=category_name).first():
            new_category = Category(name=category_name)
            db.session.add(new_category)
    db.session.commit()

    # Asocia las acciones con las categorias correspondientes
    for category_name, actions in default_actions.items():
        category = Category.query.filter_by(name=category_name).first()
        if category:
            for action_name in actions:
                action = Action.query.filter_by(name=action_name).first()
                if not action:
                    action = Action(name=action_name)
                    db.session.add(action)
                    db.session.commit()
                # Asocia la accion con la categoria correspondiente
                if not CategoryAction.query.filter_by(category_id=category.id, action_id=action.id).first():
                    category_action = CategoryAction(category_id=category.id, action_id=action.id)
                    db.session.add(category_action)
                    db.session.commit()

# Conexion a la base de datos MySQL
db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
)

cursor = db_connection.cursor()

# Verifica y crea la base de datos si no existe
if not check_database(cursor):
    cursor.execute("CREATE DATABASE controlluser")
    db_connection.commit()

# Conexion a la base de datos controlluser
db_connection = mysql.connector.connect(host="localhost", user="root", database="controlluser")
cursor = db_connection.cursor()


# Crea las tablas en la base de datos controlluser si no existen
create_tables(cursor)


# Definicion de modelos de base de datos con SQLAlchemy
class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(45), nullable=False)
    password = db.Column(db.String(255), nullable=False)

class Category(db.Model):
    __tablename__ = 'Category'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(45), unique=True, nullable=False)

class Action(db.Model):
    __tablename__ = 'Action'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(45), unique=True, nullable=False)

class UserCategory(db.Model):
    __tablename__ = 'UserCategory'
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('Category.id'), primary_key=True)

class CategoryAction(db.Model):
    __tablename__ = 'CategoryAction'
    category_id = db.Column(db.Integer, db.ForeignKey('Category.id'), primary_key=True)
    action_id = db.Column(db.Integer, db.ForeignKey('Action.id'), primary_key=True)


# Rutas y funciones para el manejo de usuarios, categorias, acciones, etc. :

# Ruta para registrar un nuevo usuario
@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        username = data['username']
        password = data['password']
        categories = data['category'].split(',')

         # Genera el hash de la contraseña
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Verifico si el usuario ya existe en la base de datos
        user = User.query.filter_by(username=username).first()

        if not user:
            # Si el usuario no existe, crea
            user = User(username=username, password=hashed_password)
            db.session.add(user)
            db.session.commit()
        else:
            # Si el usuario ya existe, se verifica la contraseña
            if not bcrypt.check_password_hash(user.password, password):
                return jsonify({"error": "Contraseña incorrecta para el usuario existente"}), 400

         # Itera sobre las categorias proporcionadas
        for category_name in categories:
            category_name = category_name.strip()
            category = Category.query.filter_by(name=category_name).first()
            if not category:
                return jsonify({"error": f"El grupo '{category_name}' no existe"}), 400

            # Verifico si la relacion usuario-categoria ya existe
            user_category = UserCategory.query.filter_by(user_id=user.id, category_id=category.id).first()
            if not user_category:
                # Si no existe, se crea
                user_category = UserCategory(user_id=user.id, category_id=category.id)
                db.session.add(user_category)

         # Confirmo los cambios en la base de datos
        db.session.commit()

        return jsonify({"message": "Usuario registrado o añadido a los grupos exitosamente"}), 201

    except KeyError:
        return jsonify({"error": "Faltan datos en la solicitud"}), 400

# Ruta para ingresar a la pagina web
@app.route('/login', methods=['POST'])
def login():
    data = request.json  # Obtiene los datos JSON de la solicitud
    username = data.get('username')  
    password = data.get('password')  
    category_name = data.get('category')  

    user = User.query.filter_by(username=username).first()  # Busco el usuario en la base de datos
    if not user:
        return jsonify({"message": "Usuario no encontrado"}), 401 

    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"message": "Credenciales inválidas"}), 401 

    category = Category.query.filter_by(name=category_name).first()  # Busca la categoria en la base de datos
    if not category:
        return jsonify({"message": "Grupo no encontrado"}), 401 
    user_category = UserCategory.query.filter_by(user_id=user.id, category_id=category.id).first()  # Verifica la relacion usuario-categoria
    if not user_category:
        return jsonify({"message": "El usuario no pertenece al grupo especificado"}), 401  # Si el usuario no pertenece a la categoria, devuelve un mensaje de error

    # Crea un token de acceso JWT con la identidad del usuario y la categoria
    access_token = create_access_token(identity={'user_id': user.id, 'category_id': category.id})
    return jsonify(access_token=access_token, category=category.name), 200  # Devuelve el token de acceso y el nombre de la categoria

# Ruta para obtener las acciones
@app.route('/actions', methods=['GET'])
def get_actions():
    actions = Action.query.all()
    actions_data = []
    for action in actions:
        action_actions = CategoryAction.query.filter_by(action_id=action.id).all()
        actions = [Action.query.filter_by(id=ca.action_id).first().name for ca in action_actions]
        actions_data.append({
            'id': action.id,
            'name': action.name
        })
    return jsonify(actions_data), 200

    return jsonify([action.name for action in actions])

# Ruta para eliminar una categoria nueva
@app.route('/categories', methods=['POST'])
def create_category():
    data = request.json
    name = data['name']
    if Category.query.filter_by(name=name).first():
        return jsonify({"error": "El grupo ya existe"}), 400
    new_category = Category(name=name)
    db.session.add(new_category)
    db.session.commit()
    return jsonify({"message": "Grupo creado exitosamente"}), 201

# Ruta para crear una accion nueva
@app.route('/actions', methods=['POST'])
def create_action():
    data = request.json
    name = data['name']
    if Action.query.filter_by(name=name).first():
        return jsonify({"error": "La accion ya existe"}), 400
    new_action = Action(name=name)
    db.session.add(new_action)
    db.session.commit()
    return jsonify({"message": "Accion creada exitosamente"}), 201

# Ruta para obtener los grupos
@app.route('/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    categories_data = []
    for category in categories:
        category_actions = CategoryAction.query.filter_by(category_id=category.id).all()
        actions = [Action.query.filter_by(id=ca.action_id).first().name for ca in category_actions]
        categories_data.append({
            'id': category.id,
            'name': category.name,
            'actions': actions
        })
    return jsonify(categories_data), 200

# Ruta para asignar una accion a una categoria
@app.route('/assign-action-to-category', methods=['POST'])
def assign_action_to_category():
    data = request.json
    category_id = data.get('categoryId')
    action_id = data.get('actionId')

    # Verifica si se proporcionaron category_id y action_id
    if category_id is None or action_id is None:
        return jsonify({"error": "Debe proporcionar categoryId y actionId"}), 400

    # Verifica si la categoria y la accion existen en la base de datos
    category = Category.query.get(category_id)
    action = Action.query.get(action_id)
    if not category or not action:
        return jsonify({"error": "La categoria o la accion no existen"}), 404

    # Verifica si la relacion ya existe en la tabla de asociacion
    existing_relation = CategoryAction.query.filter_by(category_id=category_id, action_id=action_id).first()
    if existing_relation:
        return jsonify({"error": "La accion ya está asignada a la categoria"}), 400

    # Crea una nueva entrada en la tabla de asociacion
    new_relation = CategoryAction(category_id=category_id, action_id=action_id)
    db.session.add(new_relation)
    db.session.commit()

    return jsonify({"message": "Accion asignada a la categoria exitosamente"}), 200

# Ruta para obtener los usuarios
@app.route('/users', methods=['GET'])
@jwt_required() #decorador de Flask-JWT-Extended para proteger la ruta, asegura la solicitud incluyendo un token de acceso valido en el encabezado y autentica al usuario q la realiza 
def get_users():
    users = User.query.all()
    users_data = []
    for user in users:
        user_categories = UserCategory.query.filter_by(user_id=user.id).all()
        categories = [Category.query.filter_by(id=uc.category_id).first().name for uc in user_categories]
        user_actions = []
        for category in categories:
            category_id = Category.query.filter_by(name=category).first().id
            category_actions = CategoryAction.query.filter_by(category_id=category_id).all()
            user_actions.extend([Action.query.filter_by(id=ca.action_id).first().name for ca in category_actions])
        users_data.append({
            'id': user.id,
            'username': user.username,
            'category': ', '.join(categories),
            'actions': user_actions
        })
    return jsonify(users_data), 200

# Ruta para editar un usuario
@app.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required() #decorador de Flask-JWT-Extended para proteger la ruta, asegura la solicitud incluyendo un token de acceso valido en el encabezado y autentica al usuario q la realiza 
def edit_user(user_id):
    try:
        data = request.json
        new_username = data.get('username')
        new_category = data.get('category')

        user = User.query.filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404

        user.username = new_username

        # Verifico si se especifico un grupo nuevo para el usuario
        if new_category:
            category = Category.query.filter_by(name=new_category).first()
            if not category:
                return jsonify({"error": f"El grupo '{new_category}' no existe"}), 400

            user_category = UserCategory.query.filter_by(user_id=user_id, category_id=category.id).first()
            if not user_category:
                # Si la relacion usuario-categoria no existe, se crea
                user_category = UserCategory(user_id=user_id, category_id=category.id)
                db.session.add(user_category)

        db.session.commit()
        return jsonify({"message": "Usuario actualizado exitosamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ruta para eliminar un usuario
@app.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    try:
        # Busco el usuario
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404

        # Elimino todas las relaciones de UserCategory para este usuario
        UserCategory.query.filter_by(user_id=user_id).delete()

        # Luego elimino el usuario
        db.session.delete(user)
        db.session.commit()

        return jsonify({"message": "Usuario eliminado exitosamente"}), 200
    except Exception as e:
        # Si hay un error, se revierte la operacion
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Ruta para editar un grupo
@app.route('/categories/<int:category_id>', methods=['PUT'])
@jwt_required()
def edit_category(category_id):
    try:
        data = request.json
        new_categoryname = data.get('name')

        category = Category.query.filter_by(id=category_id).first()
        if not category:
            return jsonify({"error": "Categoria no encontrada"}), 404

        category.name = new_categoryname

        db.session.commit()

        return jsonify({"message": "Categoria actualizada exitosamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Ruta para eliminar un grupo
@app.route('/categories/<int:category_id>', methods=['DELETE'])
@jwt_required()
def delete_category(category_id):
    try:
        # Busco el usuario
        category = Category.query.get(category_id)
        if not category:
            return jsonify({"error": "Categoria no encontrada"}), 404

        # Elimino todas las relaciones de CategoryAction para esta categoria
        CategoryAction.query.filter_by(category_id=category_id).delete()

        # desp elimino la categoria
        db.session.delete(category)
        db.session.commit()

        return jsonify({"message": "Categoria eliminada exitosamente"}), 200
    except Exception as e:
        # Si hay un error, se revierte la operacion
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/actions/<int:action_id>', methods=['PUT'])
@jwt_required()
def edit_action(action_id):
    try:
        data = request.json
        new_actionname = data.get('name')

        action = Action.query.filter_by(id=action_id).first()
        if not action:
            return jsonify({"error": "Accion no encontrada"}), 404

        action.name = new_actionname

        db.session.commit()

        return jsonify({"message": "Accion actualizada exitosamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Ruta para eliminar una accion
@app.route('/actions/<int:action_id>', methods=['DELETE'])
@jwt_required() 
def delete_action(action_id):
    try:
        # Busco el usuario
        action = Action.query.get(action_id)
        if not action:
            return jsonify({"error": "Accion no encontrada"}), 404

        CategoryAction.query.filter_by(action_id=action_id).delete()

        db.session.delete(action)
        db.session.commit()

        return jsonify({"message": "Accion eliminada exitosamente"}), 200
    except Exception as e:
    
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # Verifica si el script se esta ejecutando directamente (no importado como modulo)
    with app.app_context():
        # Crea el contexto de la aplicacion para operaciones con la base de datos
        db.create_all()
        # Crea todas las tablas definidas en los modelos si no existen
        create_default_categories_and_actions()
    app.run(debug=True) # Inicia la app Flask 