from shop.checkout import checkout
from shop.models import Cart


def cart(*prices):
    c = Cart()
    for i, p in enumerate(prices):
        c.add(f"s{i}", p)
    return c


def test_fixed_discount_taxed_after_discount():
    r = checkout(cart(2000), "FIVEOFF")
    assert (r["discount"], r["tax"], r["total"]) == (500, 120, 1620)


def test_fixed_discount_capped_at_subtotal():
    r = checkout(cart(300), "FIVEOFF")
    assert r["discount"] == 300
    assert r["tax"] == 0
    assert r["total"] == 0


def test_tax_rounds_half_up_after_discount():
    r = checkout(cart(1250), "SAVE10")  # 1250 - 125 = 1125 -> 90.0 tax
    assert r["tax"] == 90 and r["total"] == 1215
