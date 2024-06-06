CREATE DEFINER=`root`@`localhost` PROCEDURE `delete_user`(IN p_user_id INT)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        -- Si ocurre un error, revertimos la transacción
        ROLLBACK;
        RESIGNAL;
    END;

    -- Iniciamos una transacción
    START TRANSACTION;

    -- Eliminamos todas las relaciones en UserCategory para el usuario especificado
    DELETE FROM UserCategory WHERE User_id = p_user_id;

    -- Eliminamos el usuario
    DELETE FROM User WHERE id = p_user_id;

    -- Si todo va bien, hacemos commit de la transacción
    COMMIT;
END