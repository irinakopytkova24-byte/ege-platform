# -*- coding: utf-8 -*-
# Patch: Russian UI + topic mode selector (one / random per task).
import re

PATCH_NAME = "variant_ru"
PATCH_DESCRIPTION = "Русский интерфейс + режим темы (одна / случайно для каждого задания)"

NEW_BUTTON = (
    '<button class="btn btn-ok" style="width:auto;padding:12px 24px;font-size:16px"'
    ' onclick="openBuildVariant()">Собрать вариант ЕГЭ</button>'
)

BUTTON_PATTERN = re.compile(
    r'<button class="btn btn-ok" style="width:auto;padding:12px 24px;font-size:16px"'
    r' onclick="openBuildVariant\(\)">.*?</button>',
    re.DOTALL
)

NEW_MODAL = '''<div class="modal-bg" id="buildVariantModal" onclick="if(event.target===this)closeBuildVariant()">
  <div class="modal" style="max-width:600px">
    <button class="close" onclick="closeBuildVariant()">×</button>
    <h3>Собрать вариант ЕГЭ</h3>
    <p style="color:#8b93c4;font-size:14px;line-height:1.6;margin-bottom:14px">
      Соберём все задания (1–36, 37 и одно 38). Займёт 5–7 минут. Не закрывай страницу.
    </p>
    <div class="f">
      <label>Задание 38 — выбери одно</label>
      <div style="display:flex;gap:20px;margin-top:6px;flex-wrap:wrap">
        <label style="display:flex;gap:8px;align-items:center;font-size:15px;color:#d0d5f5;cursor:pointer">
          <input type="radio" name="sb38" value="38.1" checked style="accent-color:#7b5cff;transform:scale(1.3)"> 38.1 (таблица)
        </label>
        <label style="display:flex;gap:8px;align-items:center;font-size:15px;color:#d0d5f5;cursor:pointer">
          <input type="radio" name="sb38" value="38.2" style="accent-color:#7b5cff;transform:scale(1.3)"> 38.2 (диаграмма)
        </label>
      </div>
    </div>
    <div class="f">
      <label>Режим темы</label>
      <div style="display:flex;gap:20px;margin-top:6px;flex-wrap:wrap">
        <label style="display:flex;gap:8px;align-items:center;font-size:15px;color:#d0d5f5;cursor:pointer">
          <input type="radio" name="sbMode" value="same" checked onchange="onSbModeChange()" style="accent-color:#7b5cff;transform:scale(1.3)"> Одна тема на весь вариант
        </label>
        <label style="display:flex;gap:8px;align-items:center;font-size:15px;color:#d0d5f5;cursor:pointer">
          <input type="radio" name="sbMode" value="random" onchange="onSbModeChange()" style="accent-color:#7b5cff;transform:scale(1.3)"> Случайно для каждого задания
        </label>
      </div>
    </div>
    <div class="f" id="sbTopicWrap">
      <label>Тема</label>
      <select id="sbTopic">__TOPIC_OPTIONS__</select>
    </div>
    <button class="btn btn-ok" id="sbStartBtn" onclick="buildStudentVariant()">Собрать вариант</button>
    <div id="sbProgress" style="display:none;margin-top:14px;padding:14px;background:rgba(123,92,255,.1);border-radius:10px">
      <div style="color:#c9b8ff;font-size:14px;font-weight:600;margin-bottom:8px" id="sbProgressText">Готовим…</div>
      <div style="background:rgba(5,6,15,.5);border-radius:6px;height:8px;overflow:hidden">
        <div id="sbProgressBar" style="height:100%;background:linear-gradient(90deg,#7b5cff,#00e5ff);width:0%;transition:width .3s"></div>
      </div>
    </div>
    <div id="sbError" class="er" style="display:none;margin-top:12px"></div>
  </div>
</div>

'''

MODAL_PATTERN = re.compile(
    r'<div class="modal-bg" id="buildVariantModal".*?(?=<div class="modal-bg" id="resultModal")',
    re.DOTALL
)

NEW_JS = '''function openBuildVariant() {
  document.getElementById('buildVariantModal').classList.add('show');
  document.getElementById('sbProgress').style.display = 'none';
  document.getElementById('sbError').style.display = 'none';
  var btn = document.getElementById('sbStartBtn');
  btn.disabled = false;
  btn.textContent = 'Собрать вариант';
  onSbModeChange();
}
function closeBuildVariant() {
  document.getElementById('buildVariantModal').classList.remove('show');
}
function onSbModeChange() {
  var mode = document.querySelector('input[name="sbMode"]:checked');
  var wrap = document.getElementById('sbTopicWrap');
  if (mode && wrap) {
    wrap.style.display = (mode.value === 'same') ? 'block' : 'none';
  }
}
function _sbUpdateProgress(pct, text) {
  document.getElementById('sbProgress').style.display = 'block';
  document.getElementById('sbProgressBar').style.width = pct + '%';
  document.getElementById('sbProgressText').textContent = text;
}
async function buildStudentVariant() {
  var btn = document.getElementById('sbStartBtn');
  var errEl = document.getElementById('sbError');
  errEl.style.display = 'none';
  var choice38 = document.querySelector('input[name="sb38"]:checked').value;
  var mode = document.querySelector('input[name="sbMode"]:checked').value;
  var topic = 'any';
  if (mode === 'same') {
    topic = document.getElementById('sbTopic').value;
  }
  var taskTypes = ["1","2","3-9","10","11","12-18","19-24","25-29","30-36","37", choice38];
  var total = taskTypes.length, tasks = {}, chosen = {};
  btn.disabled = true;
  btn.textContent = 'Идёт генерация…';
  try {
    for (var i = 0; i < total; i++) {
      var tt = taskTypes[i];
      _sbUpdateProgress(Math.round(i * 90 / total), 'Генерирую задание ' + tt + ' (' + (i+1) + '/' + total + ')…');
      var payload = {action:'variant_generate', topic_config: {}};
      if (mode === 'random') {
        payload.topic_config[tt] = 'random';
      } else {
        payload.topic_config[tt] = topic;
      }
      var g = await fetch(window.location.pathname, {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify(payload)
      }).then(function(r){ return r.json(); });
      if (g.error) throw new Error('Задание ' + tt + ': ' + g.error);
      tasks[tt] = g.tasks[tt];
      if (g.chosen_topics && g.chosen_topics[tt]) chosen[tt] = g.chosen_topics[tt];
    }
    _sbUpdateProgress(93, 'Сохраняю вариант…');
    var cr = await fetch(window.location.pathname, {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({action:'variant_create', tasks: tasks, topic_config: chosen})
    }).then(function(r){ return r.json(); });
    if (cr.error) throw new Error(cr.error);
    _sbUpdateProgress(97, 'Назначаю тебе…');
    var as = await fetch(window.location.pathname, {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({action:'variant_assign', id: cr.id, student_codes: [STUDENT_CODE]})
    }).then(function(r){ return r.json(); });
    if (as.error) throw new Error(as.error);
    _sbUpdateProgress(100, 'Готово!');
    await new Promise(function(r){ setTimeout(r, 600); });
    closeBuildVariant();
    loadMyVariants();
    alert('Вариант собран! Открой его в разделе «Мои варианты».');
  } catch (e) {
    errEl.style.display = 'block';
    errEl.textContent = 'Ошибка: ' + e.message;
    btn.disabled = false;
    btn.textContent = 'Собрать вариант';
  }
}
'''

JS_PATTERN = re.compile(
    r'function openBuildVariant\(\).*?(?=async function loadMyVariants)',
    re.DOTALL
)

MSG_OLD = 'No variants yet. Click Build full EGE variant above.'
MSG_NEW = 'У вас пока нет вариантов. Нажмите «Собрать вариант ЕГЭ» выше.'

ERR_OLD = "box.innerHTML = 'Load error';"
ERR_NEW = "box.innerHTML = 'Ошибка загрузки';"


def is_applied(src):
    return 'Собрать вариант ЕГЭ' in src and 'name="sbMode"' in src


def apply(src):
    if is_applied(src):
        return src

    if 'def generate_variant_prefer_bank' not in src:
        raise Exception('anchor: variant_builder not applied')

    if not BUTTON_PATTERN.search(src):
        raise Exception('anchor: build button')
    src = BUTTON_PATTERN.sub(lambda m: NEW_BUTTON, src, count=1)

    if not MODAL_PATTERN.search(src):
        raise Exception('anchor: buildVariantModal')
    src = MODAL_PATTERN.sub(lambda m: NEW_MODAL, src, count=1)

    if not JS_PATTERN.search(src):
        raise Exception('anchor: openBuildVariant JS')
    src = JS_PATTERN.sub(lambda m: NEW_JS, src, count=1)

    if MSG_OLD in src:
        src = src.replace(MSG_OLD, MSG_NEW, 1)
    if ERR_OLD in src:
        src = src.replace(ERR_OLD, ERR_NEW, 1)

    return src