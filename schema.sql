CREATE TABLE IF NOT EXISTS computers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    ip_address TEXT,
    device_type TEXT,
    status TEXT DEFAULT 'Healthy'
);

CREATE TABLE IF NOT EXISTS connections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER,
    destination_id INTEGER,
    connection_type TEXT,
    FOREIGN KEY(source_id) REFERENCES computers(id),
    FOREIGN KEY(destination_id) REFERENCES computers(id)
);

CREATE TABLE IF NOT EXISTS simulations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_node TEXT,
    infected_count INTEGER,
    simulation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cycles_found INTEGER,
    components_found INTEGER,
    isolated_nodes INTEGER,
    risk_level TEXT
);