import tkinter
import random
import math
from dataclasses import dataclass
from typing import Tuple
import yaml
import math


@dataclass
class Node:
    coords: Tuple[int, int]
    velocity: Tuple[float, float]
    canvas_id: int
    label_canvas_id: int
    fixed: bool

@dataclass
class Line:
    node_from: int
    node_to: int
    canvas_id: int

# input file
fname = "example_in/input1.yaml"

# mass
alpha = 1.0
beta = .0001
spring_characteristic = 1.0

#damping
eta = .99
delta_t = .01
wind = 1

# canvas
root = tkinter.Tk()
canvas = tkinter.Canvas(root, width=2000, height=2000, background="#FFFFFF")
canvas.pack()

# graph
adj_matrix = []
nodes = []
lines = []

def graph_input(nodes, edges):
    adj_matrix = []

    for i in range(len(nodes)):
        temp = []
        for j in range(len(nodes)):
            temp.append(0)
        adj_matrix.append(temp)

    for i in range(0, len(edges)):
        u = edges[i][0]
        v = edges[i][1]
        print(f"i = {i}, u = {u}, v = {v}")

        adj_matrix[v][u] = adj_matrix[u][v] = 0.1

    print("adjacency matrix is : ")
    for i in range(len(nodes)):
        print(adj_matrix[i])

    return adj_matrix


def move_nodes():
    for node in filter(lambda x: x is not None, nodes):
        canvas.coords(
            node.canvas_id,
            int(node.coords[0] * 500 - 5),
            int(node.coords[1] * 500 - 5),
            int(node.coords[0] * 500 + 5),
            int(node.coords[1] * 500 + 5)
        )
        canvas.coords(
            node.label_canvas_id,
            int(node.coords[0] * 500),
            int(node.coords[1] * 500 + 10)
        )


def move_lines():
    for line in filter(lambda x: x is not None, lines):
        canvas.coords(
            line.canvas_id,
            int(nodes[line.node_from].coords[0] * 500),
            int(nodes[line.node_from].coords[1] * 500),
            int(nodes[line.node_to].coords[0] * 500),
            int(nodes[line.node_to].coords[1] * 500)
        )


def coulomb_force(coords_i, coords_j):  #repulsive force
    distance_x = coords_j[0] - coords_i[0]
    distance_y = coords_j[1] - coords_i[1]
    distance = math.sqrt(
        distance_x * distance_x + 
        distance_y * distance_y
    )
    force = beta / (distance ** 3)
    return [-force * distance_x, -force * distance_y]


def hooke_force(coords_i, coords_j, adjacency_value): #attractive force
    distance_x = coords_j[0] - coords_i[0]
    distance_y = coords_j[1] - coords_i[1]
    distance = math.sqrt(
        distance_x * distance_x + 
        distance_y * distance_y
    )
    distance_delta = distance - adjacency_value
    force = spring_characteristic * distance_delta / distance
    return [force * distance_x, force * distance_y]


def move(time):
    e_kinetic = [0.0, 0.0]
    for i in range(len(adj_matrix)):
        if not nodes[i].fixed:
            force_x = 0.0
            force_y = 0.0
            for j in range(len(adj_matrix)):
                if i != j:
                    force = []
                    if adj_matrix[i][j] == 0.0: # nodes not connected
                        force = coulomb_force(nodes[i].coords, nodes[j].coords)
                    else:
                        force = hooke_force(nodes[i].coords, nodes[j].coords, adj_matrix[i][j])
                    force_x += force[0]
                    force_y += force[1]
            force_x = force_x + wind * math.e ** (-time / 100) + wind / 100
            nodes[i].velocity = (
                (nodes[i].velocity[0] + alpha * force_x * delta_t) * eta,
                (nodes[i].velocity[1] + alpha * force_y * delta_t) * eta
            )
            e_kinetic[0] = e_kinetic[0] + alpha * (nodes[i].velocity[0] ** 2)
            e_kinetic[1] = e_kinetic[1] + alpha * (nodes[i].velocity[1] ** 2)

    e_kinetic_total = math.sqrt(e_kinetic[0] * e_kinetic[0] + e_kinetic[1] * e_kinetic[1])
    print(f"total kinetic energy: {e_kinetic_total}")
    print(nodes)

    for i in range(len(adj_matrix)):
        nodes[i].coords = (
            nodes[i].coords[0] + nodes[i].velocity[0] * delta_t,
            nodes[i].coords[1] + nodes[i].velocity[1] * delta_t
        )

    move_nodes()
    move_lines()

    root.after(1, move, time + 1)


if __name__ == '__main__':
    with open(fname) as f:
        try:
            # parse yaml
            yml = yaml.safe_load(f)
            adj_matrix = graph_input(yml["nodes"], yml["edges"])

            # draw nodes
            nodes = [None for i in range(max([node["id"] for node in yml["nodes"]])+1)]
            for node in yml["nodes"]:
                nodes[node["id"]] = Node(
                    coords=(random.random(), random.random()),
                    velocity=(0.0, 0.0),
                    canvas_id=canvas.create_oval(0, 0, 0, 0, fill=node.get("color", "red")),
                    label_canvas_id=canvas.create_text(0, 0, text=node.get("name", str(node["id"]))),
                    fixed=node.get("fixed", False)
                )

            # draw lines
            for edge in yml["edges"]:
                lines.append(Line(
                    node_from=edge[0],
                    node_to=edge[1],
                    canvas_id=canvas.create_line(0, 0, 0, 0)
                ))

            # begin canvas main loop
            root.after(1, move, 0)
            root.mainloop()
        except yaml.YAMLError as exc:
            print(exc)
