CREATE DEFINER=`root`@`localhost` PROCEDURE `Create_Default_Category`(IN category_name VARCHAR(255))
BEGIN
IF NOT EXISTS (SELECT * FROM Category WHERE name = category_name) THEN
        INSERT INTO Category (name) VALUES (category_name);
    END IF;
END