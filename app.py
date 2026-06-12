from flask import Flask, render_template, request, redirect
import sqlite3
import json
import re
from algorithms.critical_node import find_critical_node
from utils.graphBuilder import build_graph
from algorithms.cycle_detection import has_cycle
from algorithms.connected_components import count_components
from algorithms.shortest_path import shortest_path
from algorithms.malware_simulation import simulate_malware
from algorithms.risk_analysis import calculate_risk
from flask import send_file
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from utils.data_cleaner import clean_computers, clean_connections
from utils.data_cleaner import clean_computers, clean_connections

app = Flask(__name__)

DATABASE = "database.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    with open("schema.sql", "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

@app.route("/")
def index():

    conn = get_db_connection()

    computers = conn.execute(
        "SELECT * FROM computers"
    ).fetchall()

    connections_db = conn.execute("""
        SELECT
            s.name AS source,
            d.name AS destination
        FROM connections c
        JOIN computers s
            ON c.source_id = s.id
        JOIN computers d
            ON c.destination_id = d.id
    """).fetchall()

    conn.close()

    graph = build_graph(connections_db)

    cycle_found = has_cycle(graph)

    components = count_components(graph)

    total_nodes = len(computers)

    score, risk_level = calculate_risk(
        cycle_found,
        components,
        total_nodes
    )

    if cycle_found:
        cycle_status = "Cycle Detected"
    else:
        cycle_status = "Safe"

    return render_template(
        "index.html",
        computers=computers,
        connections=connections_db,
        cycle_status=cycle_status,
        risk_level=risk_level
    )

@app.route("/add_computer", methods=["POST"])
def add_computer():

    name = request.form["name"].strip()
    ip_address = request.form["ip_address"].strip()
    device_type = request.form["device_type"]

    # IPv4 validation
    ip_pattern = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"

    if ip_address:

        if not re.match(ip_pattern, ip_address):
            return "Invalid IP Address"

        parts = ip_address.split(".")

        for part in parts:
            if int(part) > 255:
                return "Invalid IP Address"

    conn = get_db_connection()

    try:

        conn.execute(
            """
            INSERT INTO computers
            (name, ip_address, device_type)
            VALUES (?, ?, ?)
            """,
            (name, ip_address, device_type)
        )

        conn.commit()

    except sqlite3.IntegrityError:
        print("Computer already exists!")

    conn.close()

    return redirect("/")


@app.route("/add_connection", methods=["POST"])
def add_connection():

    source_id = request.form["source_id"]
    destination_id = request.form["destination_id"]
    connection_type = request.form["connection_type"]

    conn = get_db_connection()

    existing = conn.execute(
        """
        SELECT *
        FROM connections
        WHERE source_id = ?
        AND destination_id = ?
        """,
        (source_id, destination_id)
    ).fetchone()

    if existing:

        conn.close()
        return redirect("/")

    conn.execute(
        """
        INSERT INTO connections
        (source_id, destination_id, connection_type)
        VALUES (?, ?, ?)
        """,
        (
            source_id,
            destination_id,
            connection_type
        )
    )

    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/analyze")
def analyze():

    conn = get_db_connection()

    # RAW DATA
    computers_raw = conn.execute("SELECT name FROM computers").fetchall()

    connections_raw = conn.execute("""
        SELECT
            s.name AS source,
            d.name AS destination
        FROM connections c
        JOIN computers s ON c.source_id = s.id
        JOIN computers d ON c.destination_id = d.id
    """).fetchall()

    conn.close()

    nodes = clean_computers(computers_raw)
    connections = clean_connections(connections_raw, nodes)

    graph = {node: [] for node in nodes}

    for c in connections:
        graph[c["source"]].append(c["destination"])

    # ANALYSIS
    cycle_found = has_cycle(graph)
    components = count_components(graph)

    total_nodes = len(nodes)

    score, level = calculate_risk(
        cycle_found,
        components,
        total_nodes
    )
    critical_node, impact = find_critical_node(graph)
    result = "Cycle Detected!" if cycle_found else "No Cycle Found!"

    # CYTOSCAPE DATA
    elements = []

    for node in nodes:
        elements.append({
            "data": {"id": node}
        })

    for c in connections:
        elements.append({
            "data": {
                "source": c["source"],
                "target": c["destination"]
            }
        })

    return render_template(
        "analysis.html",
        result=result,
        graph=graph,
        components=components,
        score=score,
        level=level,
        cytoscape_data=json.dumps(elements),
        critical_node=critical_node,
        impact=impact
    )


@app.route("/shortest_path", methods=["POST"])
def find_shortest_path():

    start = request.form["start"]
    end = request.form["end"]

    conn = get_db_connection()

    connections = conn.execute("""
        SELECT
            s.name AS source,
            d.name AS destination
        FROM connections c
        JOIN computers s ON c.source_id = s.id
        JOIN computers d ON c.destination_id = d.id
    """).fetchall()

    conn.close()

    graph = build_graph(connections)

    path = shortest_path(graph, start, end)

    return render_template(
        "path_result.html",
        path=path,
        start=start,
        end=end
    )


@app.route("/simulate", methods=["POST"])
def simulate():

    start_node = request.form["start_node"]

    conn = get_db_connection()

    connections = conn.execute("""
        SELECT
            s.name AS source,
            d.name AS destination
        FROM connections c
        JOIN computers s ON c.source_id = s.id
        JOIN computers d ON c.destination_id = d.id
    """).fetchall()

    computers = conn.execute("SELECT name FROM computers").fetchall()

    conn.close()

    graph = build_graph(connections)

    timeline = simulate_malware(graph, start_node)

    elements = []

    for computer in computers:
        elements.append({
            "data": {"id": computer["name"]}
        })

    for connection in connections:
        elements.append({
            "data": {
                "source": connection["source"],
                "target": connection["destination"]
            }
        })

    return render_template(
        "simulation.html",
        timeline=timeline,
        start_node=start_node,
        cytoscape_data=json.dumps(elements),
        timeline_json=json.dumps(timeline)
    )


@app.route("/reset")
def reset():

    conn = get_db_connection()

    conn.execute("DELETE FROM connections")
    conn.execute("DELETE FROM computers")

    conn.commit()
    conn.close()

    return redirect("/")

@app.route("/generate_report")
def generate_report():

    conn = get_db_connection()

    computers_raw = conn.execute(
        "SELECT name FROM computers"
    ).fetchall()

    connections_raw = conn.execute("""
        SELECT
            s.name AS source,
            d.name AS destination
        FROM connections c
        JOIN computers s ON c.source_id = s.id
        JOIN computers d ON c.destination_id = d.id
    """).fetchall()

    conn.close()

    nodes = clean_computers(computers_raw)
    connections = clean_connections(
        connections_raw,
        nodes
    )

    graph = {node: [] for node in nodes}

    for c in connections:
        graph[c["source"]].append(
            c["destination"]
        )

    cycle_found = has_cycle(graph)

    components = count_components(graph)

    score, level = calculate_risk(
        cycle_found,
        components,
        len(nodes)
    )

    critical_node, impact = find_critical_node(graph)

    pdf_file = "GraphGuard_Report.pdf"

    doc = SimpleDocTemplate(pdf_file)

    styles = getSampleStyleSheet()

    content = []

    content.append(
        Paragraph(
            "GraphGuard Security Report",
            styles["Title"]
        )
    )

    content.append(Spacer(1, 20))

    content.append(
        Paragraph(
            f"Risk Score: {score}/100",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"Risk Level: {level}",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"Connected Components: {components}",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"Critical Node: {critical_node}",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"Network Impact: {impact} node(s)",
            styles["Normal"]
        )
    )

    doc.build(content)

    return send_file(
        pdf_file,
        as_attachment=True
    )


if __name__ == "__main__":
    init_db()
    app.run(debug=True)