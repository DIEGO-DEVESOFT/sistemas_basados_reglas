# sistema_rutas_colombia.py
# Sistema inteligente para encontrar la mejor ruta en un sistema de transporte masivo
# Basado en una base de conocimiento (reglas lógicas) adaptada a TransMilenio (ejemplo Colombia)

import re
import heapq
from collections import defaultdict

# --------------------------
# 1. PARSEAR LA BASE DE CONOCIMIENTO
# --------------------------
def parse_kb(kb_lines):
    connects = []
    transfers = []
    walks = []
    stops = set()

    for raw in kb_lines:
        s = raw.strip()
        if not s or s.startswith('%') or s.startswith('#'):
            continue
        s = s.rstrip('.')

        m = re.match(
            r'connects\(\s*([a-zA-Z0-9_]+)\s*,\s*([a-zA-Z0-9_]+)\s*,\s*([a-zA-Z0-9_]+)\s*,\s*([0-9]+)\s*\)\s*', s)
        if m:
            line, a, b, t = m.groups()
            connects.append((line, a, b, int(t)))
            stops.update([a, b])
            continue

        m = re.match(
            r'transfer\(\s*([a-zA-Z0-9_]+)\s*,\s*([a-zA-Z0-9_]+)\s*,\s*([a-zA-Z0-9_]+)\s*,\s*([0-9]+)\s*\)\s*', s)
        if m:
            stop, l1, l2, t = m.groups()
            transfers.append((stop, l1, l2, int(t)))
            stops.add(stop)
            continue

        m = re.match(r'walk\(\s*([a-zA-Z0-9_]+)\s*,\s*([a-zA-Z0-9_]+)\s*,\s*([0-9]+)\s*\)\s*', s)
        if m:
            a, b, t = m.groups()
            walks.append((a, b, int(t)))
            stops.update([a, b])
            continue

        m = re.match(r'stop\(\s*([a-zA-Z0-9_]+)\s*\)\s*', s)
        if m:
            stops.add(m.group(1))
            continue

    return {'connects': connects, 'transfers': transfers, 'walks': walks, 'stops': stops}


# --------------------------
# 2. CONSTRUIR EL GRAFO A PARTIR DE LA KB
# --------------------------
def build_graph_from_kb(kb):
    graph = defaultdict(list)
    nodes = set()

    # conexiones de líneas
    for line, a, b, t in kb['connects']:
        n1 = (a, line)
        n2 = (b, line)
        nodes.update([n1, n2])
        graph[n1].append((n2, t, f"ride {line} {a}->{b}"))
        graph[n2].append((n1, t, f"ride {line} {b}->{a}"))

    # transferencias entre líneas
    for stop, l1, l2, t in kb['transfers']:
        n1 = (stop, l1)
        n2 = (stop, l2)
        nodes.update([n1, n2])
        graph[n1].append((n2, t, f"transfer {stop} {l1}->{l2}"))
        graph[n2].append((n1, t, f"transfer {stop} {l2}->{l1}"))

    # nodos neutrales para subirse/bajarse
    for stop in kb['stops']:
        neutral = (stop, None)
        nodes.add(neutral)
        lines_pasan = {line for (line, a, b, t) in kb['connects'] if a == stop or b == stop}
        for line in lines_pasan:
            node_line = (stop, line)
            nodes.add(node_line)
            graph[neutral].append((node_line, 0, f"board {line} at {stop}"))
            graph[node_line].append((neutral, 0, f"alight {line} at {stop}"))

    # caminatas entre estaciones
    for a, b, t in kb['walks']:
        n1 = (a, None)
        n2 = (b, None)
        graph[n1].append((n2, t, f"walk {a}->{b}"))
        graph[n2].append((n1, t, f"walk {b}->{a}"))

    return graph, nodes


# --------------------------
# 3. ALGORITMO DIJKSTRA PARA MEJOR RUTA
# --------------------------
def shortest_path(graph, start_stop, end_stop):
    start = (start_stop, None)
    target = (end_stop, None)

    pq = []
    counter = 0
    heapq.heappush(pq, (0, counter, start, None, None))

    dist = {start: 0}
    pred = {}
    visited = set()

    while pq:
        d, _, node, prev, action = heapq.heappop(pq)
        if node in visited:
            continue
        visited.add(node)

        if prev is not None:
            pred[node] = (prev, action)

        if node == target:
            break

        for nei, cost, act in graph.get(node, []):
            nd = d + cost
            if nd < dist.get(nei, float('inf')):
                dist[nei] = nd
                counter += 1
                heapq.heappush(pq, (nd, counter, nei, node, act))

    if target not in dist:
        return None

    # reconstruir ruta
    path_nodes = []
    actions = []
    cur = target
    while cur != start:
        path_nodes.append(cur)
        prev, act = pred[cur]
        actions.append(act)
        cur = prev
    path_nodes.append(start)
    path_nodes.reverse()
    actions.reverse()

    return dist[target], path_nodes, actions


# --------------------------
# 4. FORMATEAR RESULTADO
# --------------------------
def pretty_route(time_total, path_nodes, actions):
    lines = []
    lines.append(f"Tiempo total estimado: {time_total} minutos.")
    lines.append("Ruta (nodos -> estado línea):")
    for n in path_nodes:
        lines.append(f"  - {n[0]}  (línea: {n[1]})")
    lines.append("Acciones:")
    for i, a in enumerate(actions, start=1):
        lines.append(f"  {i}. {a}")
    return "\n".join(lines)


# --------------------------
# 5. BASE DE CONOCIMIENTO COLOMBIA (TRANSMILENIO)
# --------------------------
kb_text = [
    "connects(L1, Portal_Norte, Heroes, 12).",
    "connects(L1, Heroes, Calle_72, 8).",
    "connects(L1, Calle_72, Calle_26, 10).",
    "connects(L1, Calle_26, Portal_Americas, 15).",

    "connects(L2, Portal_80, Heroes, 14).",
    "connects(L2, Heroes, Calle_26, 11).",
    "connects(L2, Calle_26, Banderas, 16).",

    "transfer(Heroes, L1, L2, 5).",
    "transfer(Calle_26, L1, L2, 5).",

    "walk(Portal_Norte, Portal_80, 20).",

    "stop(Portal_Norte).",
    "stop(Heroes).",
    "stop(Calle_72).",
    "stop(Calle_26).",
    "stop(Portal_Americas).",
    "stop(Portal_80).",
    "stop(Banderas)."
]

# --------------------------
# 6. EJECUTAR EJEMPLO
# --------------------------
if __name__ == "__main__":
    kb = parse_kb(kb_text)
    graph, nodes = build_graph_from_kb(kb)
    resultado = shortest_path(graph, "Portal_Norte", "Calle_72")

    if resultado is None:
        print("No se encontró ruta entre Portal_Norte y Portal_Americas.")
    else:
        tiempo, path_nodes, acciones = resultado
        print(pretty_route(tiempo, path_nodes, acciones))
