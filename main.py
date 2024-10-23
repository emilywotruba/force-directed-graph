#!/usr/bin/python3

import tkinter
import random
import math
from dataclasses import dataclass
from typing import Tuple
import yaml
import math
import argparse


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
    strength: float

# canvas
root = tkinter.Tk()
canvas = tkinter.Canvas(root, width=2000, height=2000, background="#FFFFFF")
canvas.pack()

# graph
nodes = []
lines = []

# configuration
args = None


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
    force = args.beta / (distance ** 3)
    return [-force * distance_x, -force * distance_y]


def hooke_force(coords_i, coords_j, strength): #attractive force
    distance_x = coords_j[0] - coords_i[0]
    distance_y = coords_j[1] - coords_i[1]
    distance = math.sqrt(
        distance_x * distance_x + 
        distance_y * distance_y
    )
    distance_delta = distance - strength
    force = args.spring_characteristic * distance_delta / distance
    return [force * distance_x, force * distance_y]


def connection_strength(i, j):
    for edge in lines:
        if edge.node_from == i and edge.node_to == j:
            return edge.strength
        if edge.node_from == j and edge.node_to == i:
            return edge.strength
    return 0.0


def move(time):
    e_kinetic = [0.0, 0.0]
    for i in range(len(nodes)):
        if not nodes[i].fixed:
            force_x = 0.0
            force_y = 0.0
            for j in range(len(nodes)):
                if i != j:
                    force = []
                    con_strength = connection_strength(i, j)
                    if con_strength == 0.0:
                        force = coulomb_force(nodes[i].coords, nodes[j].coords)
                    else:
                        force = hooke_force(nodes[i].coords, nodes[j].coords, con_strength)
                    force_x += force[0]
                    force_y += force[1]
            force_x = force_x + args.wind * math.e ** (-time) + args.wind / 100
            nodes[i].velocity = (
                (nodes[i].velocity[0] + args.alpha * force_x * args.delta_t) * args.eta,
                (nodes[i].velocity[1] + args.alpha * force_y * args.delta_t) * args.eta
            )
            e_kinetic[0] = e_kinetic[0] + args.alpha * (nodes[i].velocity[0] ** 2)
            e_kinetic[1] = e_kinetic[1] + args.alpha * (nodes[i].velocity[1] ** 2)

    if args.verbose:
        e_kinetic_total = math.sqrt(e_kinetic[0] * e_kinetic[0] + e_kinetic[1] * e_kinetic[1])
        print(f"total kinetic energy: {e_kinetic_total}")

    for node in nodes:
        node.coords = (
            node.coords[0] + node.velocity[0] * args.delta_t,
            node.coords[1] + node.velocity[1] * args.delta_t
        )

    move_nodes()
    move_lines()

    root.after(1, move, time + args.delta_t)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='fdg-draw',
        description='Draws a graph using force-directed algorithm using an input yaml file',
        epilog='For more information, see https://github.com/emilywotruba/force-directed-graph'
    )
    parser.add_argument(
        'filename',
        type=str,
        help='Input YAML file'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose mode'
    )
    parser.add_argument(
        '-w', '--wind',
        type=float,
        help='Wind force',
        default=1.0
    )
    parser.add_argument(
        '-d', '--delta_t',
        type=float,
        help='Time step',
        default=0.01
    )
    parser.add_argument(
        '-a', '--alpha',
        type=float,
        help='Mass',
        default=1.0
    )
    parser.add_argument(
        '-b', '--beta',
        type=float,
        help='Damping',
        default=0.0001
    )
    parser.add_argument(
        '-s', '--spring_characteristic',
        type=float,
        help='Spring characteristic',
        default=1.0
    )
    parser.add_argument(
        '-e', '--eta',
        type=float,
        help='Damping',
        default=0.99
    )
    args = parser.parse_args()
    
    with open(args.filename) as f:
        try:
            # parse yaml
            yml = yaml.safe_load(f)

            # draw nodes
            max_node = max(
                max([node["id"] for node in yml.get("nodes", [0])]),
                max([edge[0] for edge in yml.get("edges", [[0,0]])]),
                max([edge[1] for edge in yml.get("edges", [[0,0]])]) 
            )
            nodes = [Node(
                coords=(random.random(), random.random()),
                velocity=(0.0, 0.0),
                canvas_id=canvas.create_oval(0, 0, 0, 0, fill="red"),
                label_canvas_id=canvas.create_text(0, 0, text=str(i)),
                fixed=False
            ) for i in range(max_node + 1)]
            for node in yml.get("nodes", []): # override defaults
                nodes[node["id"]] = Node(
                    coords=(random.random(), random.random()),
                    velocity=(0.0, 0.0),
                    canvas_id=canvas.create_oval(0, 0, 0, 0, fill=node.get("color", "red")),
                    label_canvas_id=canvas.create_text(0, 0, text=node.get("name", str(node["id"]))),
                    fixed=node.get("fixed", False)
                )
                for sink in node.get("outgoing_edges", []):
                    lines.append(Line(
                        node_from=node["id"],
                        node_to=sink,
                        canvas_id=canvas.create_line(0, 0, 0, 0, arrow=tkinter.LAST),
                        strength=0.1
                    ))
                for source in node.get("incoming_edges", []):
                    lines.append(Line(
                        node_from=source,
                        node_to=node["id"],
                        canvas_id=canvas.create_line(0, 0, 0, 0, arrow=tkinter.LAST),
                        strength=0.1
                    ))

            # draw lines
            for edge in yml.get("edges", []):
                lines.append(Line(
                    node_from=edge[0],
                    node_to=edge[1],
                    canvas_id=canvas.create_line(0, 0, 0, 0, arrow=tkinter.LAST),
                    strength=0.1
                ))

            # begin canvas main loop
            root.after(1, move, 0.0)
            root.mainloop()
        except yaml.YAMLError as exc:
            print(exc)
