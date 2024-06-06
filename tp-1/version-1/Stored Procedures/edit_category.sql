CREATE DEFINER=`root`@`localhost` PROCEDURE `edit_category`(IN p_category_id INT, IN p_new_category_name VARCHAR(45))
BEGIN
    -- Actualizar el nombre de la categoría
    UPDATE Category SET name = p_new_category_name WHERE id = p_category_id;
    
    -- Devolver un mensaje de éxito
    SELECT 'Categoría actualizada exitosamente' AS message;
END