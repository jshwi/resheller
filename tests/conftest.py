#!/usr/bin/env python3
from pytest import fixture

from src.client.build import Build


@fixture
def make(**kwargs):
    make_cls = Build(user=True)
    make_cls.obj = vars(make_cls)
    if kwargs:
        for key, value in kwargs.items():
            if key in make_cls.obj:
                make_cls.obj[key] = value
    return make_cls
