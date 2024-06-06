CREATE DEFINER=`root`@`localhost` PROCEDURE `RegisterUser`(
    IN p_username VARCHAR(45),
    IN p_password VARCHAR(255),
    IN p_categories TEXT
)
BEGIN
    DECLARE v_user_id INT;
    DECLARE v_category_id INT;
    DECLARE v_hashed_password VARCHAR(255);
    DECLARE v_category_name VARCHAR(45);
    DECLARE v_category_count INT DEFAULT 0;
    DECLARE done INT DEFAULT 0;
    DECLARE error_message VARCHAR(255) DEFAULT '';

    -- Cursor para iterar sobre las categorías
    DECLARE category_cursor CURSOR FOR
        SELECT TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(p_categories, ',', numbers.n), ',', -1)) AS category_name
        FROM (
            SELECT 1 n UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL
            SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL
            SELECT 9 UNION ALL SELECT 10
        ) numbers
        WHERE numbers.n <= CHAR_LENGTH(p_categories) - CHAR_LENGTH(REPLACE(p_categories, ',', '')) + 1;

    -- Handler para salir del loop en caso de final de cursor
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    -- Genera el hash de la contraseña
    SET v_hashed_password = p_password;

    -- Verifica si el usuario ya existe
    SELECT id INTO v_user_id FROM User WHERE username = p_username;

    IF v_user_id IS NULL THEN
        -- Si el usuario no existe, lo crea
        INSERT INTO User (username, password) VALUES (p_username, v_hashed_password);
        SET v_user_id = LAST_INSERT_ID();
    ELSE
        -- Verifica si la contraseña es correcta
        IF NOT (SELECT p_password = password FROM User WHERE id = v_user_id) THEN
            SET error_message = 'Contraseña incorrecta para el usuario existente';
        END IF;
    END IF;

    -- Registro de depuración
    INSERT INTO debug_log (message) VALUES (CONCAT('v_user_id:', v_user_id));

    IF error_message = '' THEN
        -- Abre el cursor
        OPEN category_cursor;

        -- Itera sobre las categorías
        read_loop: LOOP
            FETCH category_cursor INTO v_category_name;

            IF done THEN
                LEAVE read_loop;
            END IF;

            -- Verifica si la categoría existe
            SELECT id INTO v_category_id FROM Category WHERE name = v_category_name;

            IF v_category_id IS NULL THEN
                SET error_message = CONCAT('El grupo "', v_category_name, '" no existe');
                LEAVE read_loop;
            END IF;

            -- Verifica si la relación usuario-categoría ya existe
            IF NOT EXISTS (SELECT 1 FROM UserCategory WHERE User_id = v_user_id AND Category_id = v_category_id) THEN
                INSERT INTO UserCategory (User_id, Category_id) VALUES (v_user_id, v_category_id);
            END IF;
        END LOOP read_loop;

        -- Cierra el cursor
        CLOSE category_cursor;
    END IF;

    -- Manejo de confirmación y rollback
    IF error_message != '' THEN
        ROLLBACK;
        SELECT error_message AS error;
    ELSE
        COMMIT;
    END IF;

END