#!/usr/bin/env python3.9
from .misc import only_contains, subnet_at
from ipaddress import IPv6Network, IPv6Address
from base64 import b32encode
from typing import Union

"""
Utility functions for configuring ZeroTier
"""


class FixedSizeHexUInt(int):
    hex_len: int = 0

    def __new__(cls, num: Union[str, int]) -> "FixedSizeHexUInt":
        value = num if isinstance(num, int) else int(num, 16)
        if not 0 <= value <= cls.max_value():
            raise ValueError(
                f"Value of {cls.__name__} must be between {cls(0)} and {cls(cls.max_value())}, got {value:x}"
            )
        return super().__new__(cls, value)

    @classmethod
    def max_value(cls) -> int:
        return int(16**cls.hex_len) - 1

    def __str__(self) -> str:
        return f"{self:0{self.__class__.hex_len}x}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{str(self)}')"


class NodeID(FixedSizeHexUInt):
    hex_len: int = 10


class NetworkID(FixedSizeHexUInt):
    hex_len: int = 16


# from https://github.com/zerotier/ZeroTierOne/blob/91b16310ea47a6de96edb488a61494f8ed8c139c/node/InetAddress.cpp#L427
def mk6plane(nwid: NetworkID) -> IPv6Network:
    """
    Given a ZeroTier node and network ID, return
    the subnet for the whole 6plane network
    """
    prefix = (nwid ^ (nwid >> 8 * 4)) & ((1 << 8 * 4) - 1)
    # fmt: off
    return IPv6Network((
        (0xFC << 8 * 15) + 
        (prefix << 8 * 11), 40)
    )
    # fmt: on


def node_6plane_subnet(
    nwid: NetworkID, nid: NodeID
) -> tuple[IPv6Network, IPv6Network]:
    net = mk6plane(nwid)
    return net, subnet_at(net, 40, nid)


# from https://github.com/zerotier/ZeroTierOne/blob/b6b11dbf8242ff17c58f10f817d754da3f8c00eb/osdep/LinuxEthernetTap.cpp#L143-L159
def mkrfc4193(nwid: NetworkID) -> IPv6Network:
    """
    Given a ZeroTier node and network ID, return
    the subnet for the whole rfc4193 network
    """
    # fmt: off
    return IPv6Network((
        (0xFD << 8 * 15) + 
        (nwid << 8 * 7) + 
        (0x9993 << 8 * 5), 88)
    )
    # fmt: on


# from https://github.com/zerotier/ZeroTierOne/blob/b6b11dbf8242ff17c58f10f817d754da3f8c00eb/osdep/LinuxEthernetTap.cpp#L143-L159
def ifname(nwid: NetworkID, trial: int = 0) -> str:
    """
    Given a ZeroTier network ID and a trial number, compute
    the linux interface name for the network adapter
    """
    # fmt: off
    nwid40 = (
        (nwid ^ (nwid >> 8 * 3) + trial) &
        ((1 << 8 * 5) - 1)
    )
    # fmt: on
    return (
        "zt" + b32encode(nwid40.to_bytes(5, "big")).decode().lower()
    )
