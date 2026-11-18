The checkout total is wrong when a discount code is used. Tax must be charged on the
DISCOUNTED subtotal (not the pre-discount one), and a fixed-amount discount must never
push the total below zero (cap the discount at the subtotal).

`tests/test_checkout.py::test_percent_discount_taxed_after_discount` currently fails.
Find the root cause in the `shop` package, fix it, and run the test suite until it is green.
Do not change the tests.
