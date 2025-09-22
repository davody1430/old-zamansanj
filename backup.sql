PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );
INSERT INTO categories VALUES(2,'کتاب اميني خواه');
INSERT INTO categories VALUES(3,'کتاب احکام');
INSERT INTO categories VALUES(5,'مباحث اعتقادي شذرات');
INSERT INTO categories VALUES(6,'اداري ( ثبت گزارش و ...)');
INSERT INTO categories VALUES(7,'کتاب راه روشن');
INSERT INTO categories VALUES(8,'عمومي');
INSERT INTO categories VALUES(9,'کتاب تاليفي');
INSERT INTO categories VALUES(10,'جلسه');
INSERT INTO categories VALUES(11,'نماز و ...');
CREATE TABLE time_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_name TEXT NOT NULL,
            category_id INTEGER,
            start_time TEXT NOT NULL,
            end_time TEXT,
            notes TEXT,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        );
INSERT INTO time_entries VALUES(2,'بررسي فصل اول به وقت شام',2,'2025-08-30 08:20:00','2025-08-30 09:06:00','');
INSERT INTO time_entries VALUES(3,'بودجه بندي جلسات ترم',5,'2025-08-30 09:06:21','2025-08-30 09:32:01','');
INSERT INTO time_entries VALUES(4,'گزارش جلسه پژوهش',6,'2025-08-30 09:33:07','2025-08-30 09:40:20','');
INSERT INTO time_entries VALUES(5,'بررسي کار خانم مطهري- آداب مهماني',7,'2025-08-30 09:41:06','2025-08-30 09:51:43','');
INSERT INTO time_entries VALUES(6,'آماده سازي منبع چت هوشمند',8,'2025-08-30 12:10:27','2025-08-30 13:01:59','');
INSERT INTO time_entries VALUES(7,'پيگيري مصوبات و ...',8,'2025-08-30 13:02:00','2025-08-30 13:43:00','');
INSERT INTO time_entries VALUES(9,'ميدان تبيين',9,'2025-08-30 13:44:42','2025-08-30 14:20:41','');
INSERT INTO time_entries VALUES(11,'ميدان تبيين',9,'2025-08-31 09:16:00','2025-08-31 10:00:00','');
INSERT INTO time_entries VALUES(12,'ميدان تبيين',9,'2025-08-31 12:10:00','2025-08-31 13:40:00','');
INSERT INTO time_entries VALUES(13,'جلسه آموزش',10,'2025-08-31 10:30:00','2025-08-31 11:20:00','');
INSERT INTO time_entries VALUES(14,'نماز',11,'2025-08-31 11:30:00','2025-08-31 12:05:00','');
INSERT INTO time_entries VALUES(15,'ميدان تبيين',9,'2025-08-31 13:43:21','2025-08-31 13:58:18','');
INSERT INTO time_entries VALUES(16,'ميدان تبيين',9,'2025-08-31 14:17:32','2025-08-31 14:53:12','');
INSERT INTO time_entries VALUES(17,'ميدان تبيين',9,'2025-08-31 15:53:47','2025-08-31 16:53:06','');
INSERT INTO time_entries VALUES(18,'کاسبي عارفانه',2,'2025-09-01 09:17:52','2025-09-01 10:00:00','');
INSERT INTO time_entries VALUES(19,'کاسبي عارفانه',2,'2025-09-01 11:51:20','2025-09-01 15:13:53','');
INSERT INTO time_entries VALUES(20,'کاسبي عارفانه',2,'2025-09-01 15:14:09','2025-09-01 16:23:37','');
INSERT INTO time_entries VALUES(21,'کاسبي عارفانه',2,'2025-09-03 08:45:32','2025-09-03 16:00:32','');
INSERT INTO time_entries VALUES(22,'کاسبي عارفانه',2,'2025-09-04 08:00:00','2025-09-04 13:34:00','');
INSERT INTO time_entries VALUES(23,'جلسه پيرامون mvp با  آقاي روحبخش',8,'2025-09-06 12:56:57','2025-09-06 14:33:50','');
INSERT INTO time_entries VALUES(24,'نظم دهي به ترلو',8,'2025-09-06 14:34:20','2025-09-06 17:00:44','');
INSERT INTO time_entries VALUES(25,'پيام براي دوره دو هفته براي خودت',8,'2025-09-06 17:01:23','2025-09-06 17:20:12','');
INSERT INTO time_entries VALUES(26,'جلسه آموزش',10,'2025-09-07 10:45:00','2025-09-07 11:25:00','');
INSERT INTO time_entries VALUES(27,'کاسبي عارفانه',2,'2025-09-07 12:26:19','2025-09-07 13:12:54','');
INSERT INTO time_entries VALUES(28,'جلسه دوره هاي کوتاه و سفر مشتري',10,'2025-09-07 13:13:00','2025-09-07 14:20:00','');
INSERT INTO time_entries VALUES(29,'مرتب سازي و پرينت اسناد',8,'2025-09-07 14:21:00','2025-09-07 16:21:00','');
INSERT INTO time_entries VALUES(30,'کاسبي عارفانه',2,'2025-09-07 16:30:50','2025-09-07 17:39:51','');
INSERT INTO time_entries VALUES(31,'کاسبي عارفانه',2,'2025-09-08 12:20:00','2025-09-08 15:23:00','');
INSERT INTO time_entries VALUES(32,'مرتب کردن فايلها',8,'2025-09-09 12:03:00','2025-09-09 15:03:00','');
INSERT INTO time_entries VALUES(33,'مباحث اعتقادي سلوک',8,'2025-09-09 15:04:00','2025-09-09 16:04:00','');
INSERT INTO sqlite_sequence VALUES('categories',11);
INSERT INTO sqlite_sequence VALUES('time_entries',33);
COMMIT;
