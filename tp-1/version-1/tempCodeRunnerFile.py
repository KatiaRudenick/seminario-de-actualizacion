@app.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def edit_user(user_id):
    try:
        data = request.json
        new_username = data.get('username')
        new_category_name = data.get('category')

        # Call stored procedure to edit user
        with app.app_context():
            conn = db.engine.raw_connection()
            cursor = conn.cursor()

            # Pass category ID (if exists) to the stored procedure
            category_id = None
            if new_category_name:
                category_id = get_category_id(new_category_name)

            cursor.callproc('EditUser', (user_id, new_username, category_id, ''))
            cursor.close()
            conn.commit()

        return jsonify({"message": "Usuario actualizado exitosamente"}), 200

    except Exception as e:
        print("Error al editar usuario:", e)  # Add error logging
        return jsonify({"error": str(e)}), 500