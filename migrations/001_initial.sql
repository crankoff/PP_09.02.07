CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE COLLATE NOCASE,
    password_hash TEXT NOT NULL,
    display_name TEXT NOT NULL CHECK(length(display_name) BETWEEN 2 AND 80),
    role TEXT NOT NULL DEFAULT 'user' CHECK(role IN ('user', 'admin')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL CHECK(length(title) BETWEEN 1 AND 120),
    description TEXT NOT NULL DEFAULT '' CHECK(length(description) <= 1000),
    status TEXT NOT NULL DEFAULT 'backlog'
        CHECK(status IN ('backlog', 'in_progress', 'done')),
    priority TEXT NOT NULL DEFAULT 'medium'
        CHECK(priority IN ('low', 'medium', 'high')),
    due_date TEXT CHECK(due_date IS NULL OR due_date GLOB '????-??-??'),
    position INTEGER NOT NULL DEFAULT 10 CHECK(position >= 0),
    version INTEGER NOT NULL DEFAULT 1 CHECK(version > 0),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    task_id INTEGER,
    action TEXT NOT NULL CHECK(length(action) BETWEEN 1 AND 40),
    details TEXT NOT NULL DEFAULT '' CHECK(length(details) <= 500),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE SET NULL
);

CREATE INDEX idx_tasks_user_status_position
    ON tasks(user_id, status, position, updated_at DESC);
CREATE INDEX idx_tasks_user_priority ON tasks(user_id, priority);
CREATE INDEX idx_activities_user_created ON activities(user_id, created_at DESC);
