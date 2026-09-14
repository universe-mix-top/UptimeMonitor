-- =============================================
-- Схема БД для системы мониторинга URL
-- PostgreSQL 13+
-- =============================================

-- 1. Таблица пользователей
CREATE TABLE users (
                        user_id   INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                        tg_id     BIGINT NOT NULL UNIQUE,
                        reg_date  TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

COMMENT ON TABLE  users              IS 'Пользователи системы (Telegram)';
COMMENT ON COLUMN users.user_id      IS 'Первичный ключ';
COMMENT ON COLUMN users.tg_id        IS 'Идентификатор Telegram';
COMMENT ON COLUMN users.reg_date     IS 'Дата и время регистрации';

CREATE INDEX idx_user_tg_id ON users (tg_id);


-- 2. Таблица интервалов проверки
CREATE TABLE timings (
                         timing_id   INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                         timing      INTEGER NOT NULL CHECK (timing > 0),
                         description TEXT  NOT NULL UNIQUE
);

COMMENT ON TABLE  "timings"           IS 'Интервалы проверки (в минутах)';
COMMENT ON COLUMN "timings".timing_id IS 'Первичный ключ';
COMMENT ON COLUMN "timings".timing    IS 'Интервал в минутах';

insert into timings (timing, description) values
                                              (10, '10 минут'),
                                              (30, '30 минут'),
                                              (60, '1 час'),
                                              (180, '3 часа'),
                                              (360, '6 часов');

-- 3. Таблица URL-адресов
CREATE TABLE urls (
                      url_id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                      url    TEXT NOT NULL UNIQUE
);

COMMENT ON TABLE  "urls"       IS 'Список URL для мониторинга';
COMMENT ON COLUMN "urls".url_id IS 'Первичный ключ';
COMMENT ON COLUMN "urls".url    IS 'URL-адрес';

CREATE INDEX idx_urls_url ON urls (url);


-- 4. Таблица мониторов
CREATE TABLE monitors (
                         monitor_id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                         datetime   TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
                         timing_id  INTEGER NOT NULL REFERENCES timings(timing_id) ON DELETE RESTRICT,
                         url_id     INTEGER NOT NULL REFERENCES urls(url_id)       ON DELETE RESTRICT
);

COMMENT ON TABLE  monitors             IS 'Мониторы (настройки проверки URL)';
COMMENT ON COLUMN monitors.monitor_id  IS 'Первичный ключ';
COMMENT ON COLUMN monitors.datetime    IS 'Дата создания монитора';
COMMENT ON COLUMN monitors.timing_id   IS 'Ссылка на интервал проверки';
COMMENT ON COLUMN monitors.url_id      IS 'Ссылка на URL';

CREATE INDEX idx_monitors_timing_id ON monitors (timing_id);
CREATE INDEX idx_monitors_url_id    ON monitors (url_id);


-- 5. Связующая таблица пресетов мониторинга (многие-ко-многим)
CREATE TABLE monitors_presets (
                                user_id    INTEGER NOT NULL REFERENCES users(user_id)       ON DELETE CASCADE,
                                monitor_id INTEGER NOT NULL REFERENCES monitors (monitor_id) ON DELETE CASCADE,
                                PRIMARY KEY (user_id, monitor_id)
);

COMMENT ON TABLE monitors_presets            IS 'Связь пользователей и мониторов (пресеты)';
COMMENT ON COLUMN monitors_presets.user_id   IS 'Ссылка на пользователя';
COMMENT ON COLUMN monitors_presets.monitor_id IS 'Ссылка на монитор';

CREATE INDEX idx_monitor_preset_user_id ON monitors_presets(user_id);

-- 6. Таблица лога запросов
CREATE TABLE requests_log (
                              log_id     BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                              datetime   TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
                              url_id     INTEGER NOT NULL REFERENCES urls(url_id)       ON DELETE CASCADE,
                              timing_id  INTEGER NOT NULL REFERENCES timings(timing_id) ON DELETE RESTRICT,
                              res_code   INTEGER,
                              ping       NUMERIC(10, 3)
);

COMMENT ON TABLE  "requests_log"         IS 'Лог выполненных запросов мониторинга';
COMMENT ON COLUMN "requests_log".log_id  IS 'Первичный ключ (автоинкремент)';
COMMENT ON COLUMN "requests_log".datetime IS 'Дата запроса';
COMMENT ON COLUMN "requests_log".url_id  IS 'Ссылка на URL';
COMMENT ON COLUMN "requests_log".timing_id IS 'Ссылка на интервал';
COMMENT ON COLUMN "requests_log".res_code IS 'HTTP-код ответа';
COMMENT ON COLUMN "requests_log".ping    IS 'Время отклика (мс)';

CREATE INDEX idx_requests_log_date     ON requests_log (datetime);
CREATE INDEX idx_requests_log_url_id   ON requests_log (url_id);
CREATE INDEX idx_requests_log_timing_id ON requests_log (timing_id);

SELECT
    urls.url,
    timings.description
FROM monitors_presets
JOIN monitors on monitors_presets.monitor_id = monitors.monitor_id
JOIN urls ON urls.url_id = monitors.url_id
JOIN timings ON monitors.timing_id = timings.timing_id
WHERE user_id = 1;