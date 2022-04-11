from ipaddress import IPv6Network
from typing import Iterator, Iterable, TypeVar
from functools import reduce

T = TypeVar("T")

def only_contains(seq: Iterable[T], allowed: set[T]) -> bool:
    return set(seq) <= allowed

def int_bits(number: int, bits: int) -> Iterator[int]:
    for i in reversed(range(bits)):
        yield number >> i & 0b1
    
def subnet_at(net: IPv6Network, prefix_diff: int, at: int) -> IPv6Network:
    return reduce(
        lambda net, bit: tuple(net.subnets())[bit],
        int_bits(at, prefix_diff),
        net
    )

