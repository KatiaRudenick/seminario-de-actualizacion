CREATE DEFINER=`root`@`localhost` PROCEDURE `create_action`(IN p_action_name VARCHAR(45))
BEGIN
    DECLARE action_exists INT DEFAULT 0;

    -- Verificar si la categoría ya existe
    SELECT COUNT(*) INTO action_exists FROM Action WHERE name = p_action_name;

    -- Si la categoría ya existe, devolver un error
    IF action_exists > 0 THEN
        SELECT CONCAT('La accion ', p_action_name, ' ya existe') AS message;
    ELSE
        -- Crear la nueva categoría
        INSERT INTO Action (name) VALUES (p_action_name);
        
        -- Devolver un mensaje de éxito
        SELECT 'Accion creada exitosamente' AS message;
    END IF;
END