import time
from typing import Dict, List, Optional, Tuple
from .protocol import DNSResourceRecord


class DNSCache:
    """A simple TTL-based cache for DNS records."""

    def __init__(self) -> None:
        # Key: (name, type), Value: List of (expiration_time, record)
        self._cache: Dict[Tuple[str, int], List[Tuple[float, DNSResourceRecord]]] = {}

    def get(self, name: str, type: int) -> Optional[List[DNSResourceRecord]]:
        """Retrieves cached records for a given name and type."""
        key = (name.lower(), type)
        if key not in self._cache:
            return None

        now = time.time()
        valid_records = []
        expired = False

        for expiration, record in self._cache[key]:
            if expiration > now:
                valid_records.append(record)
            else:
                expired = True

        if expired:
            # Clean up the cache for this key
            self._cache[key] = [
                (exp, rec) for exp, rec in self._cache[key] if exp > now
            ]
            if not self._cache[key]:
                del self._cache[key]
                return None

        return valid_records if valid_records else None

    def add(self, record: DNSResourceRecord) -> None:
        """Adds a DNS resource record to the cache."""
        if record.ttl == 0:
            return

        key = (record.name.lower(), record.type)
        expiration = time.time() + record.ttl

        if key not in self._cache:
            self._cache[key] = []

        # Check for duplicates
        duplicate = False
        for i, (exp, rec) in enumerate(self._cache[key]):
            if rec.rdata == record.rdata:
                self._cache[key][i] = (expiration, record)
                duplicate = True
                break

        if not duplicate:
            self._cache[key].append((expiration, record))

    def clear(self) -> None:
        """Clears the cache."""
        self._cache.clear()
