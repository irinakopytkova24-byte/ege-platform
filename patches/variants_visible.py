# -*- coding: utf-8 -*-
# Patch: keep My Variants card visible for logged-in student.
# ASCII only.

PATCH_NAME = "variants_visible"
PATCH_DESCRIPTION = "Keep My Variants card visible, show hint if empty"

OLD_FUNC = '''async function loadMyVariants(){
  if (!IS_LOGGED_IN) return;
  var card = document.getElementById('myVariantsCard');
  var box = document.getElementById('myVariants');
  try{
    var d = await fetch(window.location.pathname,{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({action:'variant_my_list', student_code: STUDENT_CODE})}).then(function(r){return r.json();});
    if (d.error || !d.variants || !d.variants.length) { card.style.display = 'none'; return; }
    card.style.display = 'block';'''

NEW_FUNC = '''async function loadMyVariants(){
  if (!IS_LOGGED_IN) return;
  var card = document.getElementById('myVariantsCard');
  var box = document.getElementById('myVariants');
  card.style.display = 'block';
  try{
    var d = await fetch(window.location.pathname,{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({action:'variant_my_list', student_code: STUDENT_CODE})}).then(function(r){return r.json();});
    if (d.error || !d.variants || !d.variants.length) {
      box.innerHTML = 'No variants yet. Click Build full EGE variant above.';
      _myVariantsCache = [];
      return;
    }'''

OLD_CATCH = '''  }catch(e){ card.style.display = 'none'; }
}'''

NEW_CATCH = '''  }catch(e){ box.innerHTML = 'Load error'; }
}'''


def is_applied(src):
    return 'Click Build full EGE variant above.' in src


def apply(src):
    if is_applied(src):
        return src

    if OLD_FUNC not in src:
        raise Exception('anchor: loadMyVariants start')
    src = src.replace(OLD_FUNC, NEW_FUNC, 1)

    if OLD_CATCH not in src:
        raise Exception('anchor: catch in loadMyVariants')
    src = src.replace(OLD_CATCH, NEW_CATCH, 1)

    return src
