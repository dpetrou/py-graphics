"""Homework assignment for kindergarten, Jun 10, 2022.

Number of different icecreams that can be made from a variable
number of flavors and scoops.

A given icecream does not need to use all flavors. Two icecreams
are considered the same if the flavors they have are the same,
even if they have a different number of scoops for a given flavor.

Note: This definition of uniqueness, from the homework instructions,
does not match that of "n choose k" from standard combinatorics.
The code here, therefore, brute-forces the solution as a closed-form
representation wasn't immediately clear. In any case, coroutines are
used to reduce memory overhead.
"""

import pyglet
import argparse
import random
import math


def random_color():
    """Return an RGB triple.
    
    We set a minimum intensity to ensure visibility on black.
    """
    min_color = 50
    max_color = 255
    return (random.randrange(min_color, max_color),
            random.randrange(min_color, max_color),
            random.randrange(min_color, max_color))


def combos(depth, num_flavors, icecream):
    """A generator yielding icecreams of `depth` scoops of all
    possible combinations of `num_flavors` flavors."""
    assert depth >= 0
    if depth == 0:
        yield icecream
        return
    for i in range(num_flavors):
        icecream_copy = icecream[:]
        icecream_copy.append(i)
        yield from combos(depth - 1, num_flavors, icecream_copy)


def unique_icecreams(num_scoops, num_flavors):
    """A generator yielding unique icecreams of a given number
    of scoops and flavors."""
    num_total_combos = 0

    fprints = set()

    for icecream in combos(depth=num_scoops,
                           num_flavors=num_flavors,
                           icecream=[]):
        num_total_combos += 1
        fprint = frozenset(icecream)
        if fprint in fprints:
            continue
        yield icecream
        fprints.add(fprint)

    print(f"num_total_combos={num_total_combos}")


# TODO: Test when resizing window to aspect ratios both above and
# below 1.0.
def num_rows_and_cols(num_icecreams, aspect_ratio):
    """Return the minimum plus one number of rows and cols to fit a given
    number of icecreams. The additional row and col pads the rendering
    to ensure all icecreams are on screen."""
    num_rows = math.sqrt(num_icecreams / aspect_ratio)
    num_cols = num_rows * aspect_ratio
    num_rows = int(num_rows)
    num_cols = int(num_cols)
    # Due to edge effects, increase the number of rows until we're good.
    while (True):
        if num_rows * num_cols > num_icecreams:
            break
        num_rows += 1
    return (num_rows + 1, num_cols + 1)


def create_icecreams(icecreams, num_scoops, flavors, num_rows, num_cols, width,
                     height):
    """Create all the icecreams."""
    num_icecreams = len(icecreams)
    box_width = width / num_cols
    box_height = height / num_rows

    # We're stacking scoops one diameter away from each other.
    unit_vertical_slop = 2
    radius = min(box_width, box_height) / (num_scoops + unit_vertical_slop)

    circle_scoops = []
    icecream_idx = 0

    # We index row and col starting at 1 since the num rows and columns
    # includes padding.
    for row in range(1, num_rows):
        for col in range(1, num_cols):
            x_center = col * box_width
            y_center = row * box_height - (radius * num_scoops / 2)

            for flavor_index in icecreams[icecream_idx]:
                circle = pyglet.shapes.Circle(x=x_center,
                                              y=y_center,
                                              radius=radius,
                                              color=flavors[flavor_index])
                circle.opacity = 128
                circle_scoops.append(circle)
                y_center += radius

            icecream_idx += 1
            if (icecream_idx == num_icecreams):
                return circle_scoops


def main(argv):
    import os

    p = argparse.ArgumentParser(description="Work with graphics")
    p.add_argument("-f", "--num_flavors", type=int, default=5)
    p.add_argument("-s", "--num_scoops", type=int, default=2)
    args = p.parse_args(args=argv)

    num_flavors = args.num_flavors
    num_scoops = args.num_scoops

    if num_flavors < 1 or num_scoops < 1:
        print(
            "The number of flavors and number of scoops must be greater than 0"
        )
        return os.EX_USAGE

    # Materialize the generator into a list because need to know the total number
    # of icecreams to do layout.
    icecreams = list(
        unique_icecreams(num_scoops=num_scoops, num_flavors=num_flavors))
    num_icecreams = len(icecreams)
    print(f"num_icecreams={num_icecreams}")

    flavors = [random_color() for _ in range(num_flavors)]
    print(f"Flavors: {flavors}")

    window = pyglet.window.Window()

    aspect_ratio = window.width / window.height
    print(f"Aspect ratio: {aspect_ratio}")
    (num_rows, num_cols) = num_rows_and_cols(num_icecreams=num_icecreams,
                                             aspect_ratio=aspect_ratio)

    print(f"num_rows={num_rows}, num_cols={num_cols}")

    circle_scoops = create_icecreams(icecreams=icecreams,
                                     num_scoops=num_scoops,
                                     flavors=flavors,
                                     num_rows=num_rows,
                                     num_cols=num_cols,
                                     width=window.width,
                                     height=window.height)

    text = f"scoops={num_scoops}, flavors={num_flavors}, icecreams={num_icecreams}"

    label = pyglet.text.Label(text,
                          x=window.width//2, y=window.height - 10,
                          anchor_x='center', anchor_y='center')
    label.opacity = 200

    @window.event
    def on_draw():
        window.clear()
        for circle_scoop in circle_scoops:
            circle_scoop.draw()
        label.draw()

    pyglet.app.run()


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])