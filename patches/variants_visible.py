# -*- coding: utf-8 -*-
"""Патч: карточка 'Мои варианты' всегда видна залогиненному ученику."""

PATCH_NAME = "variants_visible"
PATCH_DESCRIPTION = "Не скрывать карточку 'Мои варианты', показывать подсказку если вариантов нет"

OLD_FUNC = r'''async function loadMyVariants(){
  if (!IS_LOGGED_IN) return;
  var card = document.getElementById('myVariantsCard');
  var box = document.getElementById('myVariants');
  try{
    var d = await fetch(window.location.pathname,{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({action:'variant_my_list', student_code: STUDENT_CODE})}).then(function(r){return r.json();});
    if (d.error || !d.variants || !d.variants.length) { card.style.display = 'none'; return; }
    card.style.display = 'block';'''

NEW_FUNC = r'''async function loadMyVariants(){
  if (!IS_LOGGED_IN) return;
  var card = document.getElementById('myVariantsCard');
  var box = document.getElementById('myVariants');
  card.style.display = 'block';
  try{
    var d = await fetch(window.location.pathname,{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({action:'variant_my_list', student_code: STUDENT_CODE})).then(function(r){return r.json();});
    if (d.error || !d.variants || !d.variants.length) {
      box.innerHTML = '<div class="mat-empty">У вас пока нет вариантов. Нажмите «🎯 Собрать полный вариант ЕГЭ» выше.</div>';
      _myVariantsCache = [];
      return;
    }'''

OLD_CATCH = r'''  }catch(e){ card.style.display = 'none'; }
}'''
NEW_CATCH = r'''  }catch(e){ box.innerHTML = '<div class="mat-empty">Ошибка загрузки</div>'; }
}'''


def is_applied(src):
    return "Нажмите «🎯 Собрать полный вариант ЕГЭ» выше." in src


def apply(src):
    if is_applied(src):
        return src

    if OLD_FUNC not in src:
        raise Exception("Не найден якорь: начало loadMyVariants")
    src = src.replace(OLD_FUNC, NEW_FUNC, 1)

    if OLD_CATCH not in src:
        raise Exception("Не найден якорь: catch в loadMyVariants")
    src = src.replace(OLD_CATCH, NEW_CATCH, 1)

    return src