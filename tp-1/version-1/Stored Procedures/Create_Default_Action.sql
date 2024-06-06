CREATE DEFINER=`root`@`localhost` PROCEDURE `Create_Default_Action`(IN action_name VARCHAR(45))
BEGIN
    IF NOT EXISTS (SELECT * FROM Action WHERE name = action_name) THEN
        INSERT INTO Action (name) VALUES (action_name);
    END IF;
END