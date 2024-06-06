CREATE DEFINER=`root`@`localhost` PROCEDURE `CreateCategoryAction`(IN category_name VARCHAR(255), IN action_name VARCHAR(255))
BEGIN
	DECLARE category_id INT;
    DECLARE action_id INT;
    
    SELECT id INTO category_id FROM Category WHERE name = category_name;
    SELECT id INTO action_id FROM Action WHERE name = action_name;

    IF NOT EXISTS (SELECT * FROM CategoryAction WHERE category_id = category_id AND action_id = action_id) THEN
        INSERT INTO CategoryAction (category_id, action_id) VALUES (category_id, action_id);
    END IF;
END