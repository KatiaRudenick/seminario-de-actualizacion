CREATE DEFINER=`root`@`localhost` PROCEDURE `edit_user`(IN p_user_id INT, IN p_new_username VARCHAR(45), IN p_new_category VARCHAR(45))
BEGIN
    DECLARE category_id INT;

    -- Actualizar el nombre de usuario
    UPDATE User SET username = p_new_username WHERE id = p_user_id;

    -- Verificar si se especificó una nueva categoría para el usuario
    IF p_new_category IS NOT NULL THEN
        -- Verificar si la categoría existe
        SELECT id INTO category_id FROM Category WHERE name = p_new_category;
        IF category_id IS NOT NULL THEN
            -- Verificar si ya existe una relación usuario-categoría para el usuario y la nueva categoría
            IF NOT EXISTS (SELECT 1 FROM UserCategory WHERE user_id = p_user_id AND category_id = category_id) THEN
                -- Si la relación no existe, crearla
                INSERT INTO UserCategory (user_id, category_id) VALUES (p_user_id, category_id);
            END IF;
        END IF;
    END IF;
END