CREATE TABLE IF NOT EXISTS Contact (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    firstName VARCHAR(45) NOT NULL,
    surnames VARCHAR(45) NOT NULL,
    address VARCHAR(45) NOT NULL
);

CREATE TABLE IF NOT EXISTS Contact_Phone (
    phone VARCHAR(45) NOT NULL,
    Contact_id INT NOT NULL,
    FOREIGN KEY (Contact_id) REFERENCES Contact(id),

);