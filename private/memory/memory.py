from __future__ import annotations

from typing import Final


class Size:  # noqa: D101 – self‑documenting names
    __slots__ = ("size",)

    # IEC units (binary multiples)
    B:   Final[int] = 1
    KiB: Final[int] = B << 10
    MiB: Final[int] = KiB << 10
    GiB: Final[int] = MiB << 10
    TiB: Final[int] = GiB << 10
    PiB: Final[int] = TiB << 10
    EiB: Final[int] = PiB << 10

    # SI units (decimal multiples)
    KB: Final[int] = 1_000
    MB: Final[int] = 1_000_000
    GB: Final[int] = 1_000_000_000
    TB: Final[int] = 1_000_000_000_000
    PB: Final[int] = 1_000_000_000_000_000
    EB: Final[int] = 1_000_000_000_000_000_000

    def __init__(self, size: int) -> None:
        self.size: int = size

    def mul_int(self, n: int) -> "Size":
        return Size(self.size * n)

    def div_int(self, n: int) -> "Size":
        return Size(self.size // n)



    def to_int(self) -> int:
        return self.size



    def __str__(self) -> str:  # noqa: DunderStr
        return self.format_size()

    def format_size(self) -> str:
        """Return a compact *IEC* string – e.g. ``"1.23 GiB"``."""
        s = self.size
        if s >= self.EiB:
            return f"{s / self.EiB:.2f}EiB"
        if s >= self.PiB:
            return f"{s / self.PiB:.2f}PiB"
        if s >= self.TiB:
            return f"{s / self.TiB:.2f}TiB"
        if s >= self.GiB:
            return f"{s / self.GiB:.2f}GiB"
        if s >= self.MiB:
            return f"{s / self.MiB:.2f}MiB"
        if s >= self.KiB:
            return f"{s / self.KiB:.2f}KiB"
        return f"{s}B"


    @staticmethod
    def format_bytes(bytes_size: int) -> str:  # noqa: D401
        """Return an *SI* formatted string (KB/MB/GB)."""
        if bytes_size >= Size.GB:
            return f"{bytes_size // Size.GB} GB"
        if bytes_size >= Size.MB:
            return f"{bytes_size // Size.MB} MB"
        if bytes_size >= Size.KB:
            return f"{bytes_size // Size.KB} KB"
        return f"{bytes_size} Bytes"