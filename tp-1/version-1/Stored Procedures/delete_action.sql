CREATE DEFINER=`root`@`localhost` PROCEDURE `delete_action`(IN p_action_id INT)
BEGIN
    DECLARE action_exists INT DEFAULT 0;

    -- Verificar si la accion existe
    SELECT COUNT(*) INTO action_exists FROM Action WHERE id = p_action_id;

    -- Si la accion no existe, devolver un error
    IF action_exists = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La accion no existe';
    ELSE
        -- Eliminar todas las relaciones de CategoryAction para esta accion
        DELETE FROM CategoryAction WHERE Action_id = p_action_id;

        -- Eliminar la accion
        DELETE FROM Action WHERE id = p_action_id;
        
        -- Devolver un mensaje de éxito
        SELECT 'Accion eliminada exitosamente' AS message;
    END IF;
END