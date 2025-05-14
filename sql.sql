-- Active: 1745254394133@@127.0.0.1@5432@Project


-- Create orders table with summary, item_names, and quantities
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    summary TEXT,
    item_names TEXT,
    quantities TEXT,
    order_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Create order_items table for normalized item storage
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    item_name TEXT,
    quantity INTEGER
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE checkouts (
    id SERIAL PRIMARY KEY,
    customer_name VARCHAR(100),
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    total_amount NUMERIC(10, 2)
);


CREATE TABLE menu_items (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    price NUMERIC(6, 2) NOT NULL,
    image TEXT,
    category TEXT
);



-- new features

-- Create orders table with summary, item_names, and quantities
CREATE TABLE del_orders (
    id SERIAL PRIMARY KEY,
    summary TEXT,
    item_names TEXT,
    quantities TEXT,
    order_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create order_items table for normalized item storage
CREATE TABLE del_order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    item_name TEXT,
    quantity INTEGER
);

CREATE TABLE del_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE del_checkouts (
    id SERIAL PRIMARY KEY,
    customer_name VARCHAR(100),
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    total_amount NUMERIC(10, 2)
);



create function backup_users()
returns trigger
language plpgsql
as $$
begin
insert into del_users values
(old.id ,old.username , old.email,old.password_hash);
return old;
end; $$

create trigger back_users
before delete
on users
for each row
execute procedure backup_users();







CREATE OR REPLACE FUNCTION backup_orders()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
  INSERT INTO del_orders (id, summary, item_names, quantities, order_time)
  VALUES (OLD.id, OLD.summary, OLD.item_names, OLD.quantities, OLD.order_time);
  RETURN OLD;
END;
$$;

CREATE TRIGGER trigger_backup_orders
BEFORE DELETE ON orders
FOR EACH ROW
EXECUTE PROCEDURE backup_orders();


CREATE OR REPLACE FUNCTION backup_order_items()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
  INSERT INTO del_order_items (id, order_id, item_name, quantity)
  VALUES (OLD.id, OLD.order_id, OLD.item_name, OLD.quantity);
  RETURN OLD;
END;
$$;

CREATE TRIGGER trigger_backup_order_items
BEFORE DELETE ON order_items
FOR EACH ROW
EXECUTE PROCEDURE backup_order_items();


CREATE OR REPLACE FUNCTION backup_checkouts()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
  INSERT INTO del_checkouts (id, customer_name, order_id, total_amount)
  VALUES (OLD.id, OLD.customer_name, OLD.order_id, OLD.total_amount);
  RETURN OLD;
END;
$$;

CREATE TRIGGER trigger_backup_checkouts
BEFORE DELETE ON checkouts
FOR EACH ROW
EXECUTE PROCEDURE backup_checkouts();

select * from checkouts;

-- Creating feedbacks table to store user feedback on orders
CREATE TABLE feedbacks (
    id SERIAL PRIMARY KEY,
    user_name VARCHAR(100) NOT NULL,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    order_name TEXT NOT NULL,
    description TEXT,
    bad_order_image BYTEA -- Stores binary image data
);
-- Creating deleted feedbacks table for backup
CREATE TABLE del_feedbacks (
    id SERIAL PRIMARY KEY,
    user_name VARCHAR(100) NOT NULL,
    order_id INTEGER NOT NULL REFERENCES del_orders(id) ON DELETE CASCADE,
    order_name TEXT NOT NULL,
    description TEXT,
    bad_order_image BYTEA -- Stores binary image data
    
);

-- Creating backup function for feedbacks
CREATE OR REPLACE FUNCTION backup_feedbacks()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
  INSERT INTO del_feedbacks (id, user_name, order_id, order_name, description, bad_order_image, created_at)
  VALUES (OLD.id, OLD.user_name, OLD.order_id, OLD.order_name, OLD.description, OLD.bad_order_image, OLD.created_at);
  RETURN OLD;
END;
$$;

-- Creating trigger to back up deleted feedbacks
CREATE TRIGGER trigger_backup_feedbacks
BEFORE DELETE ON feedbacks
FOR EACH ROW
EXECUTE PROCEDURE backup_feedbacks();

-- Adding indexes on order_id for performance
CREATE INDEX idx_feedbacks_order_id ON feedbacks(order_id);
CREATE INDEX idx_del_feedbacks_order_id ON del_feedbacks(order_id);


CREATE OR REPLACE FUNCTION backup_menu_items()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
  INSERT INTO deleted_menu_items (id, name, description, price, image, category, deleted_at)
  VALUES (OLD.id, OLD.name, OLD.description, OLD.price, OLD.image, OLD.category, CURRENT_TIMESTAMP);
  RETURN OLD;
END;
$$;


CREATE TRIGGER trigger_backup_menu_items
BEFORE DELETE ON menu_items
FOR EACH ROW
EXECUTE PROCEDURE backup_menu_items();


select * from users;

select* from  menu_items;
select * from checkouts;
select *  from orders;
select *  from order_items;


CREATE VIEW view_order_summary AS
SELECT 
    o.id AS order_id,
    c.customer_name,
    o.order_time,
    c.total_amount AS total_price
FROM 
    checkouts c
JOIN 
    orders o ON c.order_id = o.id;

select * from view_order_summary;


CREATE OR REPLACE FUNCTION get_total_orders()
RETURNS INTEGER AS $$
DECLARE
    total INTEGER;
BEGIN
    SELECT COUNT(*) INTO total FROM orders;
    RETURN total;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE PROCEDURE insert_dummy_order_item(dummy_order_id INTEGER)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO order_items (order_id, item_name, quantity)
    VALUES (dummy_order_id, 'Sample Burger', 1);
END;
$$;



CREATE OR REPLACE PROCEDURE soft_delete_feedback(feedback_id INTEGER)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE feedbacks SET description = NULL WHERE id = feedback_id;
END;
$$;


CREATE OR REPLACE FUNCTION get_total_spent(customer TEXT)
RETURNS NUMERIC(10,2) AS $$
DECLARE
    total_spent NUMERIC(10,2);
BEGIN
    SELECT SUM(total_amount) INTO total_spent FROM checkouts WHERE customer_name = customer;
    RETURN COALESCE(total_spent, 0);
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE PROCEDURE add_new_user(p_username TEXT, p_email TEXT, p_password TEXT)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO users (username, email, password_hash)
    VALUES (p_username, p_email, p_password);
END;
$$;


CREATE OR REPLACE FUNCTION get_feedback_count(order_id INTEGER)
RETURNS INTEGER AS $$
DECLARE
    fb_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO fb_count FROM feedbacks WHERE order_id = order_id;
    RETURN fb_count;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE PROCEDURE assign_test_feedback(order_id INTEGER)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO feedbacks (user_name, order_id, order_name, description)
    VALUES ('Test User', order_id, 'Test Order', 'Delicious and hot!');
END;
$$;


SELECT get_total_orders();


