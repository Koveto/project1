import os, json

BST_MIN = 180
BST_MAX = 680
LEVEL_MIN = 1
LEVEL_MAX = 96

def bst_to_level(bst):
    # Linear scaling
    ratio = (bst - BST_MIN) / (BST_MAX - BST_MIN)
    level = int(ratio * (LEVEL_MAX - LEVEL_MIN)) + LEVEL_MIN

    # Clamp just in case
    return max(LEVEL_MIN, min(LEVEL_MAX, level))


def main():
    HERE = os.path.dirname(__file__)
    JSON_PATH = os.path.join(HERE, "smt_stats.json")

    # FIXED: use JSON_PATH here
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    for p in data["pokemon"]:
        bst = p["bst"]
        p["level"] = bst_to_level(bst)

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print("Levels added successfully.")


if __name__ == "__main__":
    main()
