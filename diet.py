#!/usr/bin/python3
from typing import NamedTuple, Tuple
from yaml import safe_load
from functools import lru_cache


class Traits(NamedTuple):
    body_odor:    int
    rebel:        int
    brutality:    int
    intelligence: int
    purity:       int


def add(old: Traits, other: Traits) -> Traits:
    return Traits(
        old.body_odor    + other.body_odor,
        old.rebel        + other.rebel,
        old.brutality    + other.brutality,
        old.intelligence + other.intelligence,
        old.purity       + other.purity
    )


class Server(NamedTuple):
    ''' Tracks stat thresholds for a given server '''
    bounds:    Traits
    primary:   str
    secondary: str
    size:      int = 40
    range:     int = 20


@lru_cache
def getType(traits: Traits, server: Server) -> str:
    other = server.bounds
    normals = []
    normals.append(traits.body_odor    - other.body_odor)
    normals.append(traits.rebel        - other.rebel)
    normals.append(traits.brutality    - other.brutality)
    normals.append(traits.intelligence - other.intelligence)
    normals.append(traits.purity       - other.purity)
    for i in normals:
        if i < 0 or i > server.range:
            return "noble"
    for i in normals:
        if i < 3 or i > (server.range - 3):
            return server.secondary
    return server.primary


servers = {
    "theta": Server(Traits(  0, -5, 10,  5, -5), "iron",   "poison", 30),
    "lamda": Server(Traits( 10,  0,  5,  5, -5), "bony",   "snakey"),
    "sigma": Server(Traits(  5,  5, -5, 10,  0), "aqua",   "milky"),
    "omega": Server(Traits(  0,  5, -5,  5, 10), "rocker", "woody"),
    }


class Food(NamedTuple):
    size: int
    traits: Traits


class Grunty(NamedTuple):
    size: int
    traits: Traits


@lru_cache
def eat(grunty: Grunty, food: Food) -> Grunty:
    return Grunty(grunty.size + food.size, add(grunty.traits, food.traits))


class Shelf(NamedTuple):
    name:     str
    total:    int
    consumed: int
    food:     Food


Pantry = Tuple[Shelf, Shelf, Shelf, Shelf, Shelf, Shelf, Shelf, Shelf, Shelf, Shelf, Shelf, Shelf, Shelf, Shelf, Shelf, Shelf]


def stock(counts) -> Pantry:
    return tuple([
        Shelf("golden_egg",     counts["golden_egg"],     0, Food(2, Traits( 0,  0,  0,  0,  0))),
        Shelf("grunt_mints",    counts["grunt_mints"],    0, Food(1, Traits( 0,  4, -4, -2, -1))),
        Shelf("twilight_onion", counts["twilight_onion"], 0, Food(1, Traits( 4,  3, -3,  0,  1))),
        Shelf("snaky_cactus",   counts["snaky_cactus"],   0, Food(1, Traits( 1,  5, -2, -1,  2))),
        Shelf("oh_no_melon",    counts["oh_no_melon"],    0, Food(1, Traits( 3,  1, -1,  1,  0))),
        Shelf("cordyceps",      counts["cordyceps"],      0, Food(1, Traits( 2,  2,  0,  2,  4))),
        Shelf("white_cherry",   counts["white_cherry"],   0, Food(1, Traits(-1,  0,  1,  3,  5))),
        Shelf("root_vegetable", counts["root_vegetable"], 0, Food(1, Traits(-2, -1,  2,  0,  3))),
        Shelf("la_pumpkin",     counts["la_pumpkin"],     0, Food(1, Traits(-3, -2,  3,  5,  0))),
        Shelf("mushroom",       counts["mushroom"],       0, Food(1, Traits(-4, -3,  0, -3, -3))),
        Shelf("mandragora",     counts["mandragora"],     0, Food(1, Traits( 5,  0,  4, -4, -4))),
        Shelf("piney_apple",    counts["piney_apple"],    0, Food(1, Traits( 0, -4,  5,  4, -2))),
        Shelf("immature_egg",   counts["immature_egg"],   0, Food(2, Traits(-3, -1,  3,  2,  1))),
        Shelf("bear_cat_egg",   counts["bear_cat_egg"],   0, Food(2, Traits(-1, -3,  1,  2,  3))),
        Shelf("invisible_egg",  counts["invisible_egg"],  0, Food(2, Traits( 3,  1,  0, -1, -3))),
        Shelf("bloody_egg",     counts["bloody_egg"],     0, Food(2, Traits( 1,  3,  0, -3, -1))),
    ])


@lru_cache
def consume(old: Pantry, food_name: str) -> Pantry:
    def map_shelf(shelf: Shelf) -> Shelf:
        if shelf.name == food_name:
            return Shelf(shelf.name, shelf.total, shelf.consumed + 1, shelf.food)
        else:
            return shelf
    return tuple(map(map_shelf, old))


def r(kid: Grunty, pantry: Pantry, server: Server, goal: str):
    if kid.size >= server.size:
        if getType(kid.traits, server) == goal:
            print(goal)
            for shelf in pantry:
                print(f'{shelf.name}\t{shelf.consumed}')
        return

    for shelf in pantry:
        if shelf.consumed < shelf.total:
            new_pantry = consume(pantry, shelf.name)
            new_kid = eat(kid, shelf.food)
            r(new_kid, new_pantry, server, goal)


if __name__ == "__main__":
    with open("config.yml") as cfgfile:
        config = safe_load(cfgfile)
        servername = config["server"].lower()
        if servername not in servers:
            print("Invalid server %s" % config["server"])
            exit(1)
        server = servers[servername]
        goal = config["goal"].lower()
        if goal not in [servers[x].primary for x in servers] + [servers[x].secondary for x in servers] + ["noble"]:
            print("Invalid grunty type %s" % config["goal"])
            exit(1)
    pantry = stock(config["food"])
    baby = Grunty(0, Traits(0, 0, 0, 0, 0))
    r(baby, pantry, server, goal)
