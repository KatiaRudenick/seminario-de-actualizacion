CREATE DEFINER=`root`@`localhost` PROCEDURE `edit_action`(IN p_action_id INT, IN p_new_action_name VARCHAR(45))
BEGIN
    -- Actualizar el nombre de la accion
    UPDATE Action SET name = p_new_action_name WHERE id = p_action_id;
    
    -- Devolver un mensaje de éxito
    SELECT 'Accion actualizada exitosamente' AS message;
END