CREATE USER user_svc WITH PASSWORD 'password';
CREATE USER wishlist_svc WITH PASSWORD 'password';
CREATE USER reserv_svc WITH PASSWORD 'password';

CREATE DATABASE user_db OWNER user_svc;
CREATE DATABASE wishlist_db OWNER wishlist_svc;
CREATE DATABASE reserv_db OWNER reserv_svc;
