import ast
import random
from typing import List

import redis
from flask import Flask, jsonify, redirect, render_template, request

from misc import (fetch_teachers, get_filtered_teachers, get_teacher,
                  load_from_redis, save_to_redis)
from objects import Teacher

# login_manager = LoginManager()

with open("URLS.txt", "r") as f:
    SCHOOL_NAMES = [
        line[1:].lower() for line in f.read().splitlines() if line.startswith("#")
    ]


app = Flask(
    __name__,
    static_url_path="",
    static_folder="web/static",
    template_folder="web/templates",
)


def formatted_school_names():
    return [name.replace(" ", "-") for name in SCHOOL_NAMES]


@app.route("/", methods=["GET"])
def index():
    s_names = formatted_school_names()
    if (w := request.args.get("winner_id")) and (l := request.args.get("loser_id")):
        winner = get_teacher(w)
        loser = get_teacher(l)
        winner.won(loser)
        save_to_redis([winner, loser])

        e1, e2 = fetch_teachers()
        if e2.name == winner.name:
            e2 = e1

        if request.args.get("w_side") == "left":
            return render_template("index.html", e1=winner, e2=e2, school_names=s_names)
        else:
            return render_template("index.html", e1=e2, e2=winner, school_names=s_names)

    e1, e2 = fetch_teachers()
    return render_template("index.html", e1=e1, e2=e2, school_names=s_names)


@app.route("/leaderboard", methods=["GET"])
def leaderboard():
    teachers = sorted(load_from_redis(), key=lambda x: x.rating, reverse=True)[:13]
    return render_template(
        "leaderboard.html",
        employees=list(map(lambda x: (x[0] + 1, x[1]), enumerate(teachers))),
    )


@app.route("/leaderboard/<school_name>", methods=["GET"])
def school_leaderboard(school_name):
    school_names = [s.replace(" ", "-") for s in SCHOOL_NAMES]
    if school_name not in school_names:
        return "404"

    e = load_from_redis()
    teachers = [x for x in e if x.school.replace(" ", "-").lower() == school_name][:13]
    teachers.sort(key=lambda x: x.local_rating, reverse=True)
    return render_template(
        "schoolleaderboard.html",
        employees=list(map(lambda x: (x[0] + 1, x[1]), enumerate(teachers))),
        school_name=school_name,
    )


@app.route("/<school_name>", methods=["GET"])
def school_index(school_name):
    if (w := request.args.get("winner_id")) and (l := request.args.get("loser_id")):
        winner = get_teacher(w)
        loser = get_teacher(l)

        winner.won_local(loser)
        save_to_redis([winner, loser])

        formatted_school_name = school_name.replace("-", " ")
        filtered_teachers = get_filtered_teachers(formatted_school_name)

        e1, e2 = random.sample(filtered_teachers, 2)
        if e2.name == winner.name:

            e2 = e1
        if request.args.get("w_side") == "left":
            return render_template(
                "schoolindex.html", e1=winner, e2=e2, school_name=school_name
            )
        else:
            return render_template(
                "schoolindex.html", e1=e2, e2=winner, school_name=school_name
            )

    school_names = [s.replace(" ", "-") for s in SCHOOL_NAMES]
    if school_name not in school_names:
        return school_names
    formatted_school_name = school_name.replace("-", " ")
    filtered_teachers = get_filtered_teachers(formatted_school_name)
    e1, e2 = random.sample(filtered_teachers, 2)

    return render_template("schoolindex.html", e1=e1, e2=e2, school_name=school_name)


if __name__ == "__main__":
    app.run(debug=True)
