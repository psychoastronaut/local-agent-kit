from dataclasses import dataclass, field


@dataclass(frozen=True)
class Item:
    sku: str
    price_cents: int
    qty: int = 1


@dataclass
class Cart:
    items: list = field(default_factory=list)

    def add(self, sku: str, price_cents: int, qty: int = 1) -> None:
        self.items.append(Item(sku, price_cents, qty))

    @property
    def subtotal(self) -> int:
        return sum(i.price_cents * i.qty for i in self.items)
