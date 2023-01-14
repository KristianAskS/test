#!/usr/local/bin/python
import ast
import concurrent.futures
from dataclasses import dataclass
from typing import List, Optional

import redis
import requests
from bs4 import BeautifulSoup

from misc import save_to_redis
from objects import Teacher

PIC_FOLDER = "./teachers"

BLACKLISTED_ROLES = ["sfo", "barneveileder", "vikar"]


def load_urls():
    with open("URLS.txt", "r") as f:
        lines = f.read().splitlines()
    final = []
    stack = []
    current_school = lines[0][1:]
    for line in lines:
        if line.startswith("#"):
            final.append((current_school, stack))
            stack = []
            current_school = line[1:]
        else:
            stack.append(line)

    final.append((current_school, stack))
    return list(filter(lambda x: len(x[1]) > 0, final))


def download_image(url: str, teacher: Teacher):
    r = requests.get(url)
    n = teacher.name.replace(" ", "-")
    with open(f"{PIC_FOLDER}/{n}.jpg", "wb") as f:
        f.write(r.content)
        print(f"Downloaded {teacher.name}")


def format_img_url(img_path: str, school_url: str) -> str:
    u = school_url.split("/")
    u.pop()
    u.append(img_path)
    return "/".join(u)


def download_images(e: List[Teacher]) -> None:
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(download_image, [t.img_url for t in e], e)


def parse_teachers(url: str, school_name: str) -> List[Teacher]:
    teachers = []
    try:
        r = requests.get(url).text
    except Exception:
        print(f"SKIPPED, {url}")
        return []
    soup = BeautifulSoup(r, "html.parser")

    for tr in soup.find_all("tr"):
        tds = tr.find_all("td")
        img_tag = tds[0].find("img")

        if img_tag is None:
            continue

        name = tds[1].find("strong").text
        img_url = format_img_url(img_tag["src"], url)
        if img_url == "":
            continue

        try:
            role = (
                tds[1]
                .find("br")
                .next_sibling.strip()
                .replace("\n", "")
                .replace("\t", "")
            )
            x = False
            for b_role in BLACKLISTED_ROLES:
                if b_role in role.lower():
                    x = True
            if x:
                continue
        except Exception:
            role = None

        teachers.append(
            Teacher(
                name=name.replace("  ", " "),
                img_url=img_url,
                role=role,
                school=school_name,
            )
        )
    return teachers


if __name__ == "__main__":
    for school, urls in load_urls():
        teachers = []
        for url in urls:
            teachers.extend(parse_teachers(url, school))
        save_to_redis(teachers)
        # download_images(teachers)
