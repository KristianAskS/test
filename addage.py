import ast

import redis

from fetch import Employee

r = redis.Redis(host="localhost", port=6379, db=0)


def main():
    with open("result.txt", "rt") as file:
        contents = file.read()

    results = ast.literal_eval(contents)
    for name, contents in results.items():
        formatted_name = name.replace("-", " ")
        if (raw_info := r.get(formatted_name)) is None:
            continue

        teacher = Employee(**ast.literal_eval(raw_info.decode("utf-8")))

        teacher.predicted_age = int(results[name]["age"])
        r.set(formatted_name, teacher.__str__())


if __name__ == "__main__":
    main()
