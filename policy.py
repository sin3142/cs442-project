import ast
from charm.toolbox.pairinggroup import PairingGroup, GT, G1, G2, ZR, pair
from charm.toolbox.secretutil import SecretUtil


def generate_tree(policy_str: str):
    return ast.parse(policy_str, mode='eval').body


def get_attributes(policy_tree: ast.AST):
    """Perform a breadth-first search of the policy tree to get all attributes.

    Args:
        policy_tree (ast.AST): The policy tree.

    Returns:
        list: A list of all attributes in the policy tree.
    """
    attributes = list()
    queue = [policy_tree]
    while queue:
        node = queue.pop(0)
        if isinstance(node, ast.Str):
            attributes.append(node.s)
        elif isinstance(node, ast.BoolOp):
            queue.extend(node.values)
        else:
            raise ValueError("Unknown policy tree type")
    return attributes


def generate_shares(group, policy_tree: ast.AST, secret, dict: dict):
    if policy_tree is None:
        return None

    if isinstance(policy_tree, ast.Str):
        dict[policy_tree.s] = secret
        return None
    elif isinstance(policy_tree, ast.BoolOp):
        n = len(policy_tree.values)
        if isinstance(policy_tree.op, ast.Or):
            k = 1
        elif isinstance(policy_tree.op, ast.And):
            k = n
    else:
        raise ValueError("Unknown policy tree type")

    coefs = [secret] + [group.random() for _ in range(k-1)]
    shares = [sum([c * (i ** j) for j, c in enumerate(coefs)])
              for i in range(1, n+1)]
    for i in range(n):
        generate_shares(group, policy_tree.values[i], shares[i], dict)


def compute_coefs(group, policy_tree: ast.AST, coef, dict: dict):
    if policy_tree is None:
        return None

    if isinstance(policy_tree, ast.Str):
        dict[policy_tree.s] = coef
        return None
    elif isinstance(policy_tree, ast.BoolOp):
        if isinstance(policy_tree.op, ast.Or):
            coefs = lgi(group, [1])
            for i in range(len(policy_tree.values)):
                compute_coefs(
                    group, policy_tree.values[i], coef * coefs[1], dict)
        elif isinstance(policy_tree.op, ast.And):
            coefs = lgi(
                group, range(1, len(policy_tree.values)+1))
            for i in range(len(policy_tree.values)):
                compute_coefs(
                    group, policy_tree.values[i], coef * coefs[i+1], dict)
    else:
        raise ValueError("Unknown policy tree type")


def lgi(group, x):
    coefs = {}
    y = [group.init(ZR, i) for i in x]
    for i in y:
        c = 1
        for j in y:
            if i != j:
                c *= j / (j - i)
        coefs[int(i)] = c
    return coefs


def prune_tree(policy_tree: ast.AST, attributes: set):
    if policy_tree is None:
        return True, None

    if isinstance(policy_tree, ast.Str):
        if policy_tree.s in attributes:
            return True, policy_tree
        else:
            return False, None
    elif isinstance(policy_tree, ast.BoolOp):
        n = len(policy_tree.values)
        if isinstance(policy_tree.op, ast.Or):
            for i in range(n):
                satisfies, subtree = prune_tree(
                    policy_tree.values[i], attributes)
                if satisfies:
                    return True, subtree
            return False, None
        elif isinstance(policy_tree.op, ast.And):
            tree = ast.BoolOp(op=ast.And(), values=[])
            for i in range(n):
                satisfies, subtree = prune_tree(
                    policy_tree.values[i], attributes)
                if not satisfies:
                    return False, None
                tree.values.append(subtree)
            return True, tree
    else:
        raise ValueError("Unknown policy tree type")


def main():
    policy_tree = ast.parse("('A' or 'B') and 'C'", mode="eval").body
    attributes = {"A", "B", "C"}
    group = PairingGroup('SS512')
    secret = group.random(seed=0)
    matrix = {}
    generate_shares(group, policy_tree, secret, matrix)
    print(matrix)

    matrix = {}
    compute_coefs(group, policy_tree, 1, matrix)
    print(matrix)

    satisfies = prune_tree(policy_tree, attributes)
    print(satisfies[0], ast.dump(satisfies[1]))

    group = PairingGroup('SS512')
    secret = group.random(seed=0)
    util = SecretUtil(group)
    policy = util.createPolicy("A or B and C")
    matrix = util.calculateSharesDict(secret, policy)
    print(matrix)

    matrix = {}
    print(util.getCoefficients(policy))

    satisfies = util.prune(policy, ["A", "C"])
    print(satisfies)


if __name__ == "__main__":
    main()
