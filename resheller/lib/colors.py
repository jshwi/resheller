#!/usr/bin/env python3
from object_colors import Color


def colors() -> Color:
    return Color(
        ylw={"text": "yellow"},
        grn={"text": "green"},
        red={"text": "red"},
        b_grn={"text": "green", "effect": "bold"},
        b_red={"text": "red", "effect": "bold"},
        b_blu={"text": "blue", "effect": "bold"},
    )


color = colors()
