import random
from primegenerators import get_generator


def generate_prime():

    prime_generator = get_generator()

    r = random.randint(100, 10000)
    prime_iter = prime_generator.primes_range(3, r)
    prime = 3

    while True:
        try:
            prime = next(prime_iter)
        except StopIteration:
            break

    return prime


def is_primative_root(n: int, p: int):
    try:
        return n ** ((p - 1) / 2) % p == p - 1
    except OverflowError:
        s = set()
        for i in range(1, p):
            s.add((n ** i) % p)

        return len(s) == p - 1


def find_primative_root(p: int) -> int:

    g = random.randint(10, p - 2)

    while not is_primative_root(g, p):
        g += 1

    return g


P = generate_prime()
G = find_primative_root(P)

a = random.randint(2, 1000)
b = random.randint(2, 1000)

A = (G ** a) % P
B = (G ** b) % P


As = (B ** a) % P
Bs = (A ** b) % P


assert As == Bs


print(P, G)
