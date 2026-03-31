import argparse
import sys
import time
from .protocol import DNSType
from .resolver import DNSResolver, ResolutionTrace


def format_rr(rr) -> str:
    """Formats a resource record for display."""
    type_name = DNSType.to_string(rr.type)
    return f"{rr.name:<30} {rr.ttl:<8} IN {type_name:<8} {rr.rdata}"


def print_packet(packet) -> None:
    """Prints a DNS packet in a format similar to dig."""
    if not packet.answers and not packet.authorities and not packet.additionals:
        print(";; Got answer:")
        print(
            f";; ->>HEADER<<- opcode: QUERY, status: {packet.header.rcode}, id: {packet.header.id}"
        )
        print(
            f";; flags: {' '.join(filter(None, ['qr' if packet.header.qr else '', 'aa' if packet.header.aa else '', 'tc' if packet.header.tc else '', 'rd' if packet.header.rd else '', 'ra' if packet.header.ra else '']))}; QUERY: {packet.header.qdcount}, ANSWER: {packet.header.ancount}, AUTHORITY: {packet.header.nscount}, ADDITIONAL: {packet.header.arcount}"
        )
        print()

    if packet.questions:
        print(";; QUESTION SECTION:")
        for q in packet.questions:
            print(f";{q.qname:<29} IN {DNSType.to_string(q.qtype)}")
        print()

    if packet.answers:
        print(";; ANSWER SECTION:")
        for rr in packet.answers:
            print(format_rr(rr))
        print()

    if packet.authorities:
        print(";; AUTHORITY SECTION:")
        for rr in packet.authorities:
            print(format_rr(rr))
        print()

    if packet.additionals:
        print(";; ADDITIONAL SECTION:")
        for rr in packet.additionals:
            print(format_rr(rr))
        print()


def main() -> None:
    """Main entry point for the DNS client CLI."""
    parser = argparse.ArgumentParser(description="DNS Client (from scratch)")
    parser.add_argument("domain", help="Domain name or IP address (for PTR)")
    parser.add_argument(
        "type", nargs="?", default="A", help="Record type (A, MX, TXT, etc.)"
    )
    parser.add_argument("--trace", action="store_true", help="Show resolution trace")
    parser.add_argument("--tcp", action="store_true", help="Use TCP instead of UDP")

    args = parser.parse_args()

    qtype = DNSType.from_string(args.type)
    if qtype == 0 and args.type.upper() != "A":
        print(f"Unknown record type: {args.type}")
        sys.exit(1)

    # If the domain is an IP and qtype is PTR, we're good.
    # The resolver handles IP to in-addr.arpa conversion if qtype is PTR.

    resolver = DNSResolver()
    trace = ResolutionTrace() if args.trace else None

    start_time = time.time()
    try:
        response = resolver.resolve(args.domain, qtype, trace=trace, use_tcp=args.tcp)
        end_time = time.time()

        if args.trace and trace:
            print(";; RESOLUTION TRACE:")
            for i, step in enumerate(trace.steps):
                print(f";; Step {i + 1}: Querying {step['server']}")
                # print_packet(step['packet']) # Can be too verbose
            print()

        print_packet(response)

        query_time = int((end_time - start_time) * 1000)
        print(f";; Query time: {query_time} msec")
        print(
            f";; SERVER: {trace.steps[-1]['server'] if trace and trace.steps else 'cached'}"
        )
        print(f";; WHEN: {time.ctime(start_time)}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
