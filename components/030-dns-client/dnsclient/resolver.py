import random
from typing import List, Optional, Dict, Any
from .protocol import DNSPacket, DNSHeader, DNSQuestion, DNSType
from .transport import send_query
from .cache import DNSCache

ROOT_HINTS = [
    "198.41.0.4",  # a.root-servers.net
    "199.9.14.201",  # b.root-servers.net
    "192.33.4.12",  # c.root-servers.net
    "199.7.91.13",  # d.root-servers.net
    "192.203.230.10",  # e.root-servers.net
    "192.5.5.241",  # f.root-servers.net
    "192.112.36.4",  # g.root-servers.net
    "198.97.190.53",  # h.root-servers.net
    "192.36.148.17",  # i.root-servers.net
    "192.58.128.30",  # j.root-servers.net
    "193.0.14.129",  # k.root-servers.net
    "199.7.83.42",  # l.root-servers.net
    "202.12.27.33",  # m.root-servers.net
]


class ResolutionTrace:
    """Records the steps taken during DNS resolution."""

    def __init__(self) -> None:
        self.steps: List[Dict[str, Any]] = []

    def add_step(self, server: str, packet: DNSPacket) -> None:
        """Adds a resolution step to the trace."""
        self.steps.append({"server": server, "packet": packet})


class DNSResolver:
    """A recursive DNS resolver."""

    def __init__(self, cache: Optional[DNSCache] = None) -> None:
        self.cache = cache or DNSCache()

    def resolve(
        self,
        name: str,
        qtype: int = DNSType.A,
        trace: Optional[ResolutionTrace] = None,
        use_tcp: bool = False,
    ) -> DNSPacket:
        """Resolves a DNS query recursively."""

        # Check cache
        cached_answers = self.cache.get(name, qtype)
        if cached_answers:
            # Create a dummy packet with cached answers
            header = DNSHeader(
                id=random.getrandbits(16), qr=1, rd=1, ra=1, ancount=len(cached_answers)
            )
            question = DNSQuestion(name, qtype)
            return DNSPacket(header, [question], answers=cached_answers)

        # Handle PTR queries for IP addresses
        if qtype == DNSType.PTR:
            try:
                # Basic check for IPv4
                parts = name.split(".")
                if len(parts) == 4 and all(part.isdigit() for part in parts):
                    name = ".".join(reversed(parts)) + ".in-addr.arpa"
            except Exception:
                pass

        # Start recursion from root
        return self._resolve_recursive(name, qtype, ROOT_HINTS, trace, use_tcp)

    def _resolve_recursive(
        self,
        name: str,
        qtype: int,
        nameservers: List[str],
        trace: Optional[ResolutionTrace] = None,
        use_tcp: bool = False,
        depth: int = 0,
    ) -> DNSPacket:
        """Helper for recursive resolution."""
        if depth > 10:
            raise Exception("Recursion depth exceeded")

        # Select a random nameserver from the list
        server = random.choice(nameservers)

        header = DNSHeader(id=random.getrandbits(16), rd=0)
        question = DNSQuestion(name, qtype)
        packet = DNSPacket(header, [question])

        try:
            response = send_query(packet, server, use_tcp=use_tcp)
        except Exception as e:
            # Try other nameservers if one fails
            remaining_servers = [s for s in nameservers if s != server]
            if not remaining_servers:
                raise e
            return self._resolve_recursive(
                name, qtype, remaining_servers, trace, use_tcp, depth
            )

        if trace:
            trace.add_step(server, response)

        # Add records to cache
        for rr in response.answers + response.authorities + response.additionals:
            self.cache.add(rr)

        # If we have answers, return the response
        if response.answers:
            # Handle CNAME chasing
            cname_ans = [ans for ans in response.answers if ans.type == DNSType.CNAME]
            target_ans = [ans for ans in response.answers if ans.type == qtype]

            if not target_ans and cname_ans and qtype != DNSType.CNAME:
                # Follow CNAME
                return self.resolve(cname_ans[0].rdata, qtype, trace, use_tcp)
            return response

        # If we have referrals in authorities
        if response.authorities:
            ns_records = [rr for rr in response.authorities if rr.type == DNSType.NS]
            if ns_records:
                # Try to find glue records in additionals
                next_ns_ips = []
                for ns in ns_records:
                    ns_name = str(ns.rdata)
                    glue = [
                        rr
                        for rr in response.additionals
                        if rr.name.lower() == ns_name.lower()
                        and rr.type in (DNSType.A, DNSType.AAAA)
                    ]
                    for g in glue:
                        next_ns_ips.append(str(g.rdata))

                if next_ns_ips:
                    return self._resolve_recursive(
                        name, qtype, next_ns_ips, trace, use_tcp, depth + 1
                    )
                else:
                    # No glue records, must resolve NS names first
                    for ns in ns_records:
                        ns_name = str(ns.rdata)
                        try:
                            # Resolve the NS name to an IP
                            ns_packet = self.resolve(ns_name, DNSType.A, trace, use_tcp)
                            new_ips = [
                                str(ans.rdata)
                                for ans in ns_packet.answers
                                if ans.type == DNSType.A
                            ]
                            if new_ips:
                                return self._resolve_recursive(
                                    name, qtype, new_ips, trace, use_tcp, depth + 1
                                )
                        except Exception:
                            continue

        # If nothing works, return the response as is (might be NXDOMAIN or just no data)
        return response
