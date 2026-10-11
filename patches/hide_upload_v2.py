# -*- coding: utf-8 -*-
# Patch: hide Upload tab via JS (robust, ignores attribute order).

PATCH_NAME = "hide_upload_v2"
PATCH_DESCRIPTION = "Hide Upload tab via JavaScript after page load"


JS_CODE = '''(function hideUploadTab(){
  try {
    var btn = document.querySelector('[data-tab="upload"]');
    if (btn) btn.style.display = 'none';
    var pane = document.getElementById('pane-upload');
    if (pane) pane.style.display = 'none';
    var bankBtn = document.querySelector('[data-tab="bank"]');
    var bankPane = document.getElementById('pane-bank');
    if (bankBtn && bankPane) {
      var tabs = document.querySelectorAll('.tab');
      for (var i = 0; i < tabs.length; i++) tabs[i].classList.remove('active');
      var panes = document.querySelectorAll('.tab-pane');
      for (var j = 0; j < panes.length; j++) panes[j].classList.remove('active');
      bankBtn.classList.add('active');
      bankPane.classList.add('active');
    }
  } catch(e) { console.log('hideUploadTab', e); }
})();
'''

ANCHOR = 'loadPending();\ninitVariantsTab();'


def is_applied(src):
    return 'hideUploadTab' in src


def apply(src):
    if is_applied(src):
        return src
    if ANCHOR not in src:
        raise Exception('anchor not found: loadPending init')
    src = src.replace(ANCHOR, JS_CODE + '\n' + ANCHOR, 1)
    return src
