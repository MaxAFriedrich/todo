from os import path


def build_tree(raw):
    import re

    regex = r"^#+\s+.*(?:\r?\n(?!#).*)*"
    result = {}
    matches = re.findall(regex, raw, re.MULTILINE)
    for match in matches:
        heading_text = re.search(r"#{1,}\s(.*)", match).group(1)
        result[heading_text] = match
    return result


def new_td(file_loc: str, fm: dict, raw: str, topic=None):
    if topic == None:
        import uuid

        topic = fm["current"] = str(uuid.uuid1())
    from yaml import safe_dump

    fm_str = safe_dump(fm)
    md = f"## {topic}\n\n- "
    with open(file_loc, "w") as file:
        file.write(f"---\n{fm_str}\n---\n{raw}\n{md}")
    return topic, md


def rem_td(file_loc: str, topic: str):
    return
    import re

    regex = r"^#+\s+" + topic + r".*(?:\r?\n(?!#).*)*"

    with open(file_loc, "r") as file:
        # with open(file_loc, "w") as out:
            print(re.sub(regex, "", file.read()))


def open_td(inp) -> str:
    import subprocess
    import tempfile
    from os import unlink

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as tmp_file:
        tmp_file.write(inp)
        tmp_file.flush()

        proc = subprocess.Popen(["lvim", tmp_file.name])
        proc.communicate()

        with open(tmp_file.name, "r") as f:
            content = f.read()

    unlink(tmp_file.name)

    return content


def save_td(old, new, file_loc):
    with open(file_loc, "r") as inp:
        txt = inp.read().replace(old, new)
    with open(file_loc, "w") as file:
        file.write(txt)


def get_config():
    from toml import load

    conf = load(path.expanduser("~/.config/todo/config.toml"))
    conf["file_loc"] = path.expanduser(conf["file_loc"])
    with open(conf["file_loc"], "r") as file:
        from yaml import safe_load

        raw = file.read()
        s = raw.find("---")
        e = raw.find("---", s + 3)
        fm = safe_load(raw[s + 3 : e].strip())
    return fm, conf, raw[e + 3 :]


def arg_parser():
    from argparse import ArgumentParser

    p = ArgumentParser()
    p.add_argument("cmd", help="new|n current|c topic|t blank|b remove|r")
    p.add_argument("-t", "--topic")
    return p.parse_args()


def main():

    args = arg_parser()
    fm, conf, raw = get_config()
    tree = build_tree(raw)
    topic = None
    if args.cmd in ["new", "n"]:
        topic, md = new_td(conf["file_loc"], fm, raw)
        tree[topic] = md
    elif args.cmd in ["current", "c"]:
        topic = fm["current"]
    elif args.cmd in ["topic", "t", "blank", "b"] and args.topic != None:
        topic = args.topic
        if args.cmd in ["blank", "b"]:
            topic, md = new_td(conf["file_loc"], fm, raw, topic=topic)
            tree[topic] = md
    elif args.cmd in ["remove", "r"] and args.topic != None:
        if fm["current"] == topic:
            topic = new_td(conf["file_loc"], fm, raw)
            save_td(tree[topic], open_td(tree[topic]), conf["file_loc"])
        rem_td(conf["file_loc"], args.topic)
        return
    else:
        print("Invalid args.")
        return
    if topic == None:
        print("Invalid topic.")
        return

    save_td(tree[topic], open_td(tree[topic]), conf["file_loc"])


if __name__ == "__main__":
    main()
