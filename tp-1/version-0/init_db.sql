CREATE TABLE User (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(45) NOT NULL,
  password VARCHAR(255) NOT NULL
);

CREATE TABLE Category (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(45) NOT NULL
);

CREATE TABLE Action (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(45) NOT NULL
);

CREATE TABLE UserCategory (
  User_id INT,
  Category_id INT,
  FOREIGN KEY (User_id) REFERENCES User(id),
  FOREIGN KEY (Category_id) REFERENCES Category(id)
);

CREATE TABLE CategoryAction (
  Category_id INT,
  Action_id INT,
  FOREIGN KEY (Category_id) REFERENCES Category(id),
  FOREIGN KEY (Action_id) REFERENCES Action(id)
);