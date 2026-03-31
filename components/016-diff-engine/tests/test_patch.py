import pytest
from diffengine.diff import get_line_diff
from diffengine.patch import apply_patch, apply_unified_patch
from diffengine.format import format_unified

def test_apply_patch():
    a = "line1\nline2\n"
    b = "line1\nline3\n"
    diff = get_line_diff(a, b)
    restored = apply_patch(a, diff)
    assert restored == b

def test_apply_unified_patch():
    a = "line1\nline2\n"
    b = "line1\nline3\n"
    diff = get_line_diff(a, b)
    patch = format_unified(diff)
    restored = apply_unified_patch(a, patch)
    assert restored == b

def test_apply_unified_patch_partial():
    # Test that applying a patch only affects the relevant part of the file
    source = "header\nline1\nline2\nfooter\n"
    target = "header\nline1_mod\nline2\nfooter\n"

    # We create a patch with a small hunk
    diff = get_line_diff(source, target)
    patch = format_unified(diff, context=0)

    # The patch should not include header/footer in the hunk content if context=0
    # but the line numbers should reflect their presence.
    restored = apply_unified_patch(source, patch)
    assert restored == target

def test_apply_patch_empty():
    a = ""
    b = ""
    diff = get_line_diff(a, b)
    restored = apply_patch(a, diff)
    assert restored == b
