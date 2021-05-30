CREATE SCHEMA pidorbot;

create table if not exists pidorbot.vkuser (
    id integer PRIMARY KEY,
    name text NOT NULL,
    surname text NOT NULL
);

create table if not exists pidorbot.vkchat (
    id integer PRIMARY KEY,
    godovaliy integer
        REFERENCES pidorbot.vkuser(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    lastgodovaliyroll date NOT NULL,
    lastroll date NOT NULL,
    lastpotd integer
        REFERENCES pidorbot.vkuser(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    lastpassive integer
        REFERENCES pidorbot.vkuser(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

create table if not exists pidorbot.participation (
    chatid integer NOT NULL
        REFERENCES pidorbot.vkchat(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    userid integer NOT NULL
        REFERENCES pidorbot.vkuser(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    amount integer NOT NULL
);

create table if not exists pidorbot.winners (
    id serial not null,
    uid integer NOT NULL
);

create or replace function pidorbot.register(uid INT, cid INT, n TEXT, sn TEXT)  returns boolean as $$
    declare isRegistered boolean;
    begin
        if (SELECT COUNT(*) FROM pidorbot.vkchat WHERE pidorbot.vkchat.id = cid) = 0 THEN
            INSERT INTO pidorbot.vkchat (id, godovaliy, lastgodovaliyroll, lastroll, lastpotd, lastpassive) VALUES (
                cid,
                null,
                '1970-01-01',
                '1970-01-01',
                null,
                null
            );
        end if;

        if (SELECT COUNT(*) FROM pidorbot.vkuser WHERE pidorbot.vkuser.id = uid) = 0 THEN
            INSERT INTO pidorbot.vkuser (id, name, surname) VALUES (
                uid,
                n,
                sn
            );
        end if;

        if (SELECT COUNT(*) FROM pidorbot.participation WHERE userid = uid AND chatid = cid) = 0 THEN
            INSERT INTO pidorbot.participation (chatid, userid, amount) VALUES (
                cid,
                uid,
                0
            );
            isRegistered = false;
        else
            isRegistered = true;
        end if;
    return isRegistered;
    end;
$$ language plpgsql;

create or replace function pidorbot.randomize(cid INT)  returns table(b BOOLEAN, actid INT, actn TEXT, actsn TEXT, pasid INT, pasn TEXT, passn TEXT) as $$
    declare potd integer;
    declare potdn text;
    declare potdsn text;
    declare passive integer;
    declare pasn text;
    declare passn text;
    declare isUpdated boolean;
    begin
        if (CURRENT_DATE != (SELECT lastroll from pidorbot.vkchat where id = cid)) then
                TRUNCATE TABLE pidorbot.winners;
                INSERT INTO pidorbot.winners(uid) SELECT userid FROM pidorbot.participation where chatid = cid ORDER BY random() LIMIT 2;
                SELECT uid INTO potd FROM pidorbot.winners ORDER BY id LIMIT 1;
                SELECT uid INTO passive FROM pidorbot.winners ORDER BY id DESC LIMIT 1;

                UPDATE pidorbot.vkchat SET lastroll = CURRENT_DATE, lastpotd = potd, lastpassive = passive WHERE id = cid;
                UPDATE pidorbot.participation SET amount = amount + 1 WHERE chatid = cid AND userid = potd;
                isUpdated = true;
        else
                SELECT lastpotd INTO potd FROM pidorbot.vkchat WHERE id = cid;
                SELECT lastpassive INTO passive FROM pidorbot.vkchat WHERE id = cid;
                isUpdated = false;
        end if;
        SELECT name, surname INTO potdn, potdsn FROM pidorbot.vkuser WHERE id = potd;
        SELECT name, surname INTO pasn, passn FROM pidorbot.vkuser WHERE id = passive;

        return query WITH t as (SELECT isUpdated, potd, potdn, potdsn, passive, pasn, passn) SELECT * FROM t;

    end;
$$ language plpgsql;

create or replace function pidorbot.stats(cid INT) returns table(retid INT, n TEXT, sn TEXT, am INT) as $$
    begin
        return query WITH t as (
            SELECT userid, name, surname, amount
                FROM pidorbot.participation
                INNER JOIN pidorbot.vkuser ON participation.userid = vkuser.id
                WHERE chatid = cid AND amount > 0
                ORDER BY amount DESC
        )
        SELECT t.userid::INT,
                t.name::TEXT,
                t.surname::TEXT,
                t.amount::INT
                FROM t;
    end;
$$ language plpgsql;

create or replace function pidorbot.godovaliy(cid INT)  returns table(b BOOLEAN, retgodid INT, retgodn TEXT, retgodsn TEXT) as $$
    declare god integer;
    declare godn text;
    declare godsn text;
    declare isUpdated boolean;
    begin
        if (EXTRACT(YEAR FROM CURRENT_DATE) != EXTRACT(YEAR FROM (SELECT lastgodovaliyroll from pidorbot.vkchat where id = cid))) then
                SELECT userid INTO god FROM pidorbot.participation where chatid = cid ORDER BY random() LIMIT 1;
                UPDATE pidorbot.vkchat SET lastgodovaliyroll = CURRENT_DATE, godovaliy = god WHERE id = cid;
                isUpdated = true;
        else
                SELECT godovaliy INTO god FROM pidorbot.vkchat WHERE id = cid;
                isUpdated = false;
        end if;

        SELECT name, surname INTO godn, godsn FROM pidorbot.vkuser WHERE id = god;

        return query WITH t as (SELECT isUpdated, god, godn, godsn) SELECT * FROM t;

    end;
$$ language plpgsql;