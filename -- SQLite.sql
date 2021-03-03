-- SQLite
delete from balance where fecha = (select max(fecha) from balance)