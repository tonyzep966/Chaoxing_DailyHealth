create table health_user
(
    username   varchar(16) not null
        primary key,
    password   varchar(16) not null,
    student_id char(8)     null,
    name       varchar(3)  null
);