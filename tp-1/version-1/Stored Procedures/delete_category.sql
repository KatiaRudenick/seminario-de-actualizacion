CREATE DEFINER=`root`@`localhost` PROCEDURE `delete_category`(IN p_category_id INT)
BEGIN
    DECLARE category_exists INT DEFAULT 0;

    -- Verificar si la categoría existe
    SELECT COUNT(*) INTO category_exists FROM Category WHERE id = p_category_id;

    -- Si la categoría no existe, devolver un error
    IF category_exists = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La categoría no existe';
    ELSE
        -- Eliminar todas las relaciones de CategoryAction para esta categoría
        DELETE FROM CategoryAction WHERE Category_id = p_category_id;

        -- Eliminar la categoría
        DELETE FROM Category WHERE id = p_category_id;
        
        -- Devolver un mensaje de éxito
        SELECT 'Categoría eliminada exitosamente' AS message;
    END IF;
END