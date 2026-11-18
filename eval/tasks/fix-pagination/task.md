`tests/test_pager.py::test_exact_multiple_has_no_empty_last_page` fails. Find the cause
and fix it in the library code (not in the tests). While you are there, check that the
other page helpers behave correctly for the last page and for out-of-range pages
(an out-of-range page must return an empty list, never raise). Run the suite until green.
