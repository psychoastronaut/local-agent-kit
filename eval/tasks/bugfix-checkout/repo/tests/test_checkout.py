from shop.checkout import checkout
from shop.models import Cart


def make_cart(*prices):
    cart = Cart()
    for i, p in enumerate(prices):
        cart.add(f"sku{i}", p)
    return cart


def test_no_discount():
    r = checkout(make_cart(5000, 5000))
    assert r == {"subtotal": 10000, "discount": 0, "tax": 800, "total": 10800}


def test_unknown_code_is_ignored():
    assert checkout(make_cart(1000), "NOPE")["discount"] == 0


def test_percent_discount_taxed_after_discount():
    r = checkout(make_cart(10000), "SAVE10")
    assert r["discount"] == 1000
    assert r["tax"] == 720
    assert r["total"] == 9720
