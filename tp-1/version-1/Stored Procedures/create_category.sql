CREATE DEFINER=`root`@`localhost` PROCEDURE `create_category`(IN p_category_name VARCHAR(45))
BEGIN
    DECLARE category_exists INT DEFAULT 0;

    -- Verificar si la categoría ya existe
    SELECT COUNT(*) INTO category_exists FROM Category WHERE name = p_category_name;

    -- Si la categoría ya existe, devolver un error
    IF category_exists > 0 THEN
        SELECT CONCAT('La categoría ', p_category_name, ' ya existe') AS message;
    ELSE
        -- Crear la nueva categoría
        INSERT INTO Category (name) VALUES (p_category_name);
        
        -- Devolver un mensaje de éxito
        SELECT 'Categoría creada exitosamente' AS message;
    END IF;
END