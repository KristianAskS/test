import ast
import random
from typing import List

import redis

from objects import Teacher

Redis = redis.Redis(host="localhost", port=6379, db=0)


def load_from_redis() -> List[Teacher]:
    teachers = []
    for key in Redis.keys():
        teacher = Redis.get(key).decode("utf-8")
        teachers.append(Teacher(**ast.literal_eval(teacher)))
    return teachers


def save_to_redis(e: List[Teacher]):
    for t in e:
        Redis.set(t.name, t.__str__())


def get_teacher(name: str) -> Teacher:
    return Teacher(**ast.literal_eval(Redis.get(name).decode("utf-8")))


def fetch_teachers():
    teachers = load_from_redis()
    return random.sample(teachers, 2)


def get_filtered_teachers(name):
    return list(
        filter(
            lambda x: x.school.lower() == name.lower(),
            load_from_redis(),
        )
    )
