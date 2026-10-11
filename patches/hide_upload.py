# -*- coding: utf-8 -*-
# Patch: hide the "Upload" tab (was for task 1 only, now obsolete).
import re

PATCH_NAME = "hide_upload"
PATCH_DESCRIPTION = "Hide the old Upload tab and make Bank the default active tab"


def is_applied(src):
    return 'style="display:none" data-tab="upload"' in src


def apply(src):
    if is_applied(src):
        return src

    # 1. Hide Upload tab button, remove 'active' from it
    src = re.sub(
        r'<button class="tab active" data-tab="upload"',
        '<button class="tab" style="display:none" data-tab="upload"',
        src, count=1
    )

    # 2. Make Bank tab active
    src = re.sub(
        r'<button class="tab" data-tab="bank"',
        '<button class="tab active" data-tab="bank"',
        src, count=1
    )

    # 3. Hide Upload pane
    src = re.sub(
        r'<div class="tab-pane active" id="pane-upload">',
        '<div class="tab-pane" id="pane-upload" style="display:none">',
        src, count=1
    )

    # 4. Make Bank pane active
    src = re.sub(
        r'<div class="tab-pane" id="pane-bank">',
        '<div class="tab-pane active" id="pane-bank">',
        src, count=1
    )

    return src
