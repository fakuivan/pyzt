#!/usr/bin/env python3.9
from .misc import only_contains, subnet_at
from ipaddress import IPv6Network, IPv6Address
from base64 import b32encode

"""
Utility functions for configuring ZeroTier
"""

class NodeID(int):
    def __new__(cls, address: str) -> 'NodeID':
        if len(address) != 10 or not only_contains(
                address.lower(), set('0123456789abcdef')):
            raise ValueError(
                "Node ID must be a 10 digit hexadecimal number")
        return super().__new__(cls, int(address, 16))
    
    def __str__(self) -> str:
        return f"{self:010x}"

    def __repr__(self) -> str:
        return f"NodeID('{str(self)}')"


class NetworkID(int):
    def __new__(cls, address: str) -> 'NetworkID':
        if len(address) != 16 or not only_contains(
                address.lower(), set('0123456789abcdef')):
            raise ValueError(
                "Network ID must be a 16 digit hexadecimal number")
        return super().__new__(cls, int(address, 16))

    def __str__(self) -> str:
        return f"{self:016x}"

    def __repr__(self) -> str:
        return f"NetworkID('{str(self)}')"

# from https://github.com/zerotier/ZeroTierOne/blob/91b16310ea47a6de96edb488a61494f8ed8c139c/node/InetAddress.cpp#L427
def mk6plane(nwid: NetworkID) -> IPv6Network:
    """
    Given a ZeroTier node and network ID, return
    the subnet for the whole 6plane network
    """
    prefix = (nwid ^ (nwid >> 8*4)) & ((1 << 8*4) - 1)
    return IPv6Network(((0xfc << 8*15) +
                       (prefix << 8*11), 40))

def node_6plane_subnet(nwid: NetworkID, nid: NodeID
) -> tuple[IPv6Network, IPv6Network]:
    net = mk6plane(nwid)
    return net, subnet_at(net, 40, nid)

# from https://github.com/zerotier/ZeroTierOne/blob/b6b11dbf8242ff17c58f10f817d754da3f8c00eb/osdep/LinuxEthernetTap.cpp#L143-L159
def mkrfc4193(nwid: NetworkID) -> IPv6Network:
    """
    Given a ZeroTier node and network ID, return
    the subnet for the whole rfc4193 network
    """
    return IPv6Network(((0xfd << 8*15) +
                        (nwid << 8*7) +
                        (0x9993 << 8*5), 88))

# from https://github.com/zerotier/ZeroTierOne/blob/b6b11dbf8242ff17c58f10f817d754da3f8c00eb/osdep/LinuxEthernetTap.cpp#L143-L159
def ifname(nwid: NetworkID, trial: int = 0) -> str:
    """
    Given a ZeroTier network ID and a trial number, compute
    the linux interface name for the network adapter
    """
    nwid40 = (nwid ^ (nwid >> 8*3) + trial) & \
             ((1 << 8*5) - 1)
    return "zt" + b32encode(nwid40.to_bytes(5, "big")
        ).decode().lower()

