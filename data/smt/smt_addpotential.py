import json
import random

def bst_to_range(bst):
    """Return (min_val, max_val) for potential based on BST."""
    if bst < 236:
        return -1, 1
    elif bst < 280:
        return -1, 2
    elif bst < 308:
        return -1, 3
    elif bst < 360:
        return -2, 4
    elif bst < 413:
        return -2, 5
    elif bst < 465:
        return -2, 6
    elif bst < 518:
        return -3, 7
    elif bst < 580:
        return -3, 8
    else:
        return -3, 9


def compute_potential(affinities, bst):
    """
    Given affinities list and bst, return a potential list.
    """
    min_val, max_val = bst_to_range(bst)
    potentials = []

    for affinity in affinities:
        if affinity == 0 or affinity == 1:
            potentials.append(0)
        elif affinity < 0:
            # negative potential only
            neg_values = [v for v in range(min_val, 0)]
            potentials.append(random.choice(neg_values))
        else:
            # positive potential only
            pos_values = [v for v in range(1, max_val + 1)]
            potentials.append(random.choice(pos_values))

    return potentials


def main():
    with open("data/smt/smt_stats.json", "r") as f:
        data = json.load(f)

    for entry in data["pokemon"]:
        affinities = entry["affinities"]
        bst = entry["bst"]

        entry["potential"] = compute_potential(affinities, bst)

    with open("smt_stats_new.json", "w") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    main()
