create table users(
    id integer PRIMARY KEY AUTOINCREMENT,
    name text NOT NULL,
    password text not NULL,
    expert boolean not null,
    admin boolean not null 
);

create table questions(
    id integer PRIMARY KEY AUTOINCREMENT,
    question_text text not NULL,
    answer_text text,
    asked_by_id integer not null,
    expert_id integer not null
);