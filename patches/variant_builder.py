# -*- coding: utf-8 -*-
"""Патч: кнопка сборки варианта у ученика + банк-приоритет."""

PATCH_NAME = "variant_builder"
PATCH_DESCRIPTION = "Кнопка 'Собрать полный вариант ЕГЭ' у ученика + генерация из банка"

PY_NEW_FUNCS = r'''def _topic_letter_from_full(full):
    if not full or "Любая" in full or "любая" in full:
        return "any"
    for letter, t in TOPIC_MAP.items():
        if t.lower() in full.lower() or letter == full.strip():
            return letter
    return "any"


def _bank_save_generated(task_type, topic_letter, task_data, audio_b64=None):
    try:
        n = _bank_next_number(task_type, topic_letter)
        code = f"{task_type}-{topic_letter}-{n:03d}"
        meta = {
            "code": code, "task_type": task_type, "topic": topic_letter,
            "topic_full": TOPIC_MAP.get(topic_letter, ""),
            "instruction": task_data.get("instruction", ""),
            "has_audio": bool(audio_b64),
        }
        for k in ("statements", "scripts", "answer_key", "extra_statement",
                  "questions", "interview_script", "script", "headings", "texts",
                  "extra_heading", "fragments", "extra_fragment", "title", "text",
                  "items", "explanations", "dialogue_script", "task_text",
                  "survey_data", "plan"):
            if k in task_data:
                meta[k] = task_data[k]
        s3 = _s3()
        prefix = _bank_prefix(task_type, topic_letter)
        s3.put_object(Bucket=BUCKET_NAME, Key=f"{prefix}{code}.json",
                      Body=json.dumps(meta, ensure_ascii=False).encode("utf-8"),
                      ContentType="application/json")
        if audio_b64:
            mp3 = base64.b64decode(audio_b64)
            s3.put_object(Bucket=BUCKET_NAME, Key=f"{prefix}{code}.mp3",
                          Body=mp3, ContentType="audio/mpeg")
        print(f"[bank-save] {code}")
        return code
    except Exception as e:
        print(f"[bank-save] {type(e).__name__}: {e}")
        return None


def _bank_fetch_random(task_type, topic_letter=None):
    try:
        s3 = _s3()
        files = []
        if topic_letter and topic_letter != "any":
            files = [f for f in _bank_list_raw(task_type, topic_letter) if f.endswith(".json")]
        else:
            paginator = s3.get_paginator("list_objects_v2")
            prefix = f"tasks/{task_type}/"
            for page in paginator.paginate(Bucket=BUCKET_NAME, Prefix=prefix):
                for obj in page.get("Contents", []):
                    if obj["Key"].endswith(".json"):
                        files.append(obj["Key"])
        if not files:
            return None
        key = random.choice(files)
        obj = s3.get_object(Bucket=BUCKET_NAME, Key=key)
        meta = json.loads(obj["Body"].read().decode("utf-8"))
        mp3_key = key.replace(".json", ".mp3")
        try:
            mp3_obj = s3.get_object(Bucket=BUCKET_NAME, Key=mp3_key)
            meta["audio_b64"] = base64.b64encode(mp3_obj["Body"].read()).decode("utf-8")
        except Exception:
            pass
        return meta
    except Exception as e:
        print(f"[bank-fetch] {type(e).__name__}: {e}")
        return None


def generate_variant_prefer_bank(topic_config):
    RAW_PIPELINES = {
        "1": generate_task_1, "2": generate_task_2, "3-9": generate_task_3_9,
        "10": generate_task_10, "11": generate_task_11, "12-18": generate_task_12_18,
        "19-24": generate_task_19_24, "25-29": generate_task_25_29,
        "30-36": generate_task_30_36, "37": generate_task_37,
        "38.1": generate_task_38_1, "38.2": generate_task_38_2,
    }
    result, chosen_topics, sources, fresh_tests = {}, {}, {}, {}
    for tt in VARIANT_TASKS:
        raw = topic_config.get(tt) or "any"
        topic_full = _resolve_topic(raw)
        chosen_topics[tt] = topic_full
        topic_letter = "any" if raw in ("any", "random") else _topic_letter_from_full(raw)
        bank_item = _bank_fetch_random(tt, topic_letter if topic_letter != "any" else None)
        if bank_item:
            print(f"[variant] {tt}: из банка ({bank_item.get('code')})")
            result[tt] = bank_item
            sources[tt] = "bank"
            continue
        print(f"[variant] {tt}: из LLM")
        gen = RAW_PIPELINES[tt](topic_full)
        if isinstance(gen, dict) and "error" in gen:
            return {"error": f"Ошибка в задании {tt}: {gen['error']}"}
        result[tt] = gen
        sources[tt] = "llm"
        if tt not in ("37", "38.1", "38.2"):
            fresh_tests[tt] = gen
    if fresh_tests:
        try:
            _batch_explanations_for_variant(fresh_tests)
            for tt in fresh_tests:
                if fresh_tests[tt].get("explanations"):
                    result[tt]["explanations"] = fresh_tests[tt]["explanations"]
        except Exception as e:
            print(f"[variant-explanations] {e}")
    for tt in VARIANT_TASKS:
        if sources.get(tt) == "llm":
            raw = topic_config.get(tt) or "any"
            letter = "any" if raw in ("any", "random") else _topic_letter_from_full(raw)
            _bank_save_generated(tt, letter, result[tt])
    return {"ok": True, "tasks": result, "chosen_topics": chosen_topics, "sources": sources}


'''

JS_FUNCS = r'''function openBuildVariant() {
  document.getElementById('buildVariantModal').classList.add('show');
  document.getElementById('sbProgress').style.display = 'none';
  document.getElementById('sbError').style.display = 'none';
  var btn = document.getElementById('sbStartBtn');
  btn.disabled = false;
  btn.textContent = '🚀 Собрать вариант';
}
function closeBuildVariant() {
  document.getElementById('buildVariantModal').classList.remove('show');
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
  var topic = document.getElementById('sbTopic').value;
  var taskTypes = ["1","2","3-9","10","11","12-18","19-24","25-29","30-36","37", choice38];
  var total = taskTypes.length, tasks = {}, chosen = {};
  btn.disabled = true;
  btn.textContent = '⏳ Идёт генерация…';
  try {
    for (var i = 0; i < total; i++) {
      var tt = taskTypes[i];
      _sbUpdateProgress(Math.round(i * 90 / total), 'Генерирую задание ' + tt + ' (' + (i+1) + '/' + total + ')…');
      var payload = {action:'variant_generate', topic_config: {}};
      payload.topic_config[tt] = topic;
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
    _sbUpdateProgress(100, '✅ Готово!');
    await new Promise(function(r){ setTimeout(r, 600); });
    closeBuildVariant();
    loadMyVariants();
    alert('✅ Вариант собран! Открой его в разделе «Мои варианты».');
  } catch (e) {
    errEl.style.display = 'block';
    errEl.textContent = '💥 ' + e.message;
    btn.disabled = false;
    btn.textContent = '🚀 Собрать вариант';
  }
}
'''

CARD_OLD = '''    <div class="card" id="myVariantsCard" style="display:none">
      <h3>📦 Мои варианты</h3>
      <div id="myVariants"><div class="mat-empty">Загрузка…</div></div>
    </div>'''

CARD_NEW = '''    <div class="card" id="myVariantsCard" style="display:none">
      <h3>📦 Мои варианты</h3>
      <div style="margin-bottom:14px">
        <button class="btn btn-ok" style="width:auto;padding:12px 24px;font-size:16px" onclick="openBuildVariant()">🎯 Собрать полный вариант ЕГЭ</button>
      </div>
      <div id="myVariants"><div class="mat-empty">Загрузка…</div></div>
    </div>

    <div class="modal-bg" id="buildVariantModal" onclick="if(event.target===this)closeBuildVariant()">
      <div class="modal" style="max-width:600px">
        <button class="close" onclick="closeBuildVariant()">✕</button>
        <h3>🎯 Собрать полный вариант ЕГЭ</h3>
        <p style="color:#8b93c4;font-size:14px;line-height:1.6;margin-bottom:14px">Сгенерируем все задания (1–36, 37 и 38). Займёт 5–7 минут, не закрывай страницу.</p>
        <div class="f">
          <label>Задание 38 — выбери одно</label>
          <div style="display:flex;gap:20px;margin-top:6px">
            <label style="display:flex;gap:8px;align-items:center;font-size:15px;color:#d0d5f5;cursor:pointer">
              <input type="radio" name="sb38" value="38.1" checked style="accent-color:#7b5cff;transform:scale(1.3)"> 38.1 (таблица)
            </label>
            <label style="display:flex;gap:8px;align-items:center;font-size:15px;color:#d0d5f5;cursor:pointer">
              <input type="radio" name="sb38" value="38.2" style="accent-color:#7b5cff;transform:scale(1.3)"> 38.2 (диаграмма)
            </label>
          </div>
        </div>
        <div class="f">
          <label>Тема</label>
          <select id="sbTopic">__TOPIC_OPTIONS__</select>
        </div>
        <button class="btn btn-ok" id="sbStartBtn" onclick="buildStudentVariant()">🚀 Собрать вариант</button>
        <div id="sbProgress" style="display:none;margin-top:14px;padding:14px;background:rgba(123,92,255,.1);border-radius:10px">
          <div style="color:#c9b8ff;font-size:14px;font-weight:600;margin-bottom:8px" id="sbProgressText">Готовим…</div>
          <div style="background:rgba(5,6,15,.5);border-radius:6px;height:8px;overflow:hidden">
            <div id="sbProgressBar" style="height:100%;background:linear-gradient(90deg,#7b5cff,#00e5ff);width:0%;transition:width .3s"></div>
          </div>
        </div>
        <div id="sbError" class="er" style="display:none;margin-top:12px"></div>
      </div>
    </div>'''


def is_applied(src):
    return "def generate_variant_prefer_bank" in src and "openBuildVariant" in src


def apply(src):
    if is_applied(src):
        return src

    if "def generate_variant_prefer_bank" not in src:
        if "def generate_variant(topic_config):" not in src:
            raise Exception("Не найден якорь: def generate_variant(topic_config):")
        src = src.replace("def generate_variant(topic_config):",
                          PY_NEW_FUNCS + "def generate_variant(topic_config):", 1)

    if "r = generate_variant_prefer_bank(topic_config)" not in src:
        if "r = generate_variant(topic_config)" not in src:
            raise Exception("Не найден якорь: r = generate_variant(topic_config)")
        src = src.replace("r = generate_variant(topic_config)",
                          "r = generate_variant_prefer_bank(topic_config)", 1)

    if "openBuildVariant()" not in src:
        if CARD_OLD in src:
            src = src.replace(CARD_OLD, CARD_NEW, 1)
        else:
            raise Exception("Не найден якорь: карточка myVariantsCard")

    if "function openBuildVariant" not in src:
        if "async function loadMyVariants()" not in src:
            raise Exception("Не найден якорь: async function loadMyVariants()")
        src = src.replace("async function loadMyVariants()",
                          JS_FUNCS + "async function loadMyVariants()", 1)

    return src
