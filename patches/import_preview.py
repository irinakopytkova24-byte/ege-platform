# -*- coding: utf-8 -*-
# Patch: preview before saving imported task to bank.

PATCH_NAME = "import_preview"
PATCH_DESCRIPTION = "Preview imported task before saving, with Confirm/Cancel buttons"


# ==== PYTHON ====
OLD_TAIL = '''    task_data["instruction"] = TASK_INSTRUCTIONS.get(str(task_type), "")
    if "_bank_save_generated" not in globals():
        return {"error": "patch variant_builder required"}
    code = _bank_save_generated(task_type, topic_letter, task_data)
    if not code:
        return {"error": "Failed to save to bank"}
    return {"ok": True, "code": code, "task_data": task_data}
'''

NEW_TAIL = '''    task_data["instruction"] = TASK_INSTRUCTIONS.get(str(task_type), "")
    return {"ok": True, "task_data": task_data}


def admin_import_save(task_type, topic_letter, task_data):
    if not isinstance(task_data, dict) or not task_data:
        return {"error": "task_data is empty"}
    if "_bank_save_generated" not in globals():
        return {"error": "patch variant_builder required"}
    code = _bank_save_generated(task_type, topic_letter, task_data)
    if not code:
        return {"error": "Failed to save to bank"}
    return {"ok": True, "code": code}
'''


OLD_ACTION = '''            if action == "import_task":
                _t = data.get("task_type")
                _top = (data.get("topic_letter") or "").strip().upper()
                _txt = data.get("task_text") or ""
                _aud = data.get("audio_text") or ""
                _key = data.get("key_text") or ""
                if not _t or not _top:
                    return _resp(400, {"error": "task_type and topic_letter required"})
                if not _txt:
                    return _resp(400, {"error": "task_text is empty"})
                _r = admin_import_task(_t, _top, _txt, _aud, _key)
                return _resp(200 if "ok" in _r else 500, _r)
'''

NEW_ACTION = '''            if action == "import_preview":
                _t = data.get("task_type")
                _txt = data.get("task_text") or ""
                _aud = data.get("audio_text") or ""
                _key = data.get("key_text") or ""
                if not _t:
                    return _resp(400, {"error": "task_type required"})
                if not _txt:
                    return _resp(400, {"error": "task_text is empty"})
                _r = admin_import_task(_t, "", _txt, _aud, _key)
                return _resp(200 if "ok" in _r else 500, _r)

            if action == "import_save":
                _t = data.get("task_type")
                _top = (data.get("topic_letter") or "").strip().upper()
                _td = data.get("task_data") or {}
                if not _t or not _top:
                    return _resp(400, {"error": "task_type and topic_letter required"})
                _r = admin_import_save(_t, _top, _td)
                return _resp(200 if "ok" in _r else 500, _r)
'''


# ==== JS ====
OLD_BTN = 'onclick="importTask()">'

NEW_BTN = 'onclick="importPreviewStart()">'

JS_ANCHOR = 'function impOnTypeChange() {'

JS_INSERT = '''var _impPreview = null;

async function importPreviewStart() {
  var t = document.getElementById('impType').value;
  var topic = document.getElementById('impTopic').value;
  var txt = document.getElementById('impText').value.trim();
  var aud = document.getElementById('impAudio').value.trim();
  var key = document.getElementById('impKey').value.trim();
  var res = document.getElementById('impRes');
  var btn = document.getElementById('impBtn');
  if (!txt) { res.className = 'res err'; res.textContent = '\\u041d\\u0443\\u0436\\u0435\\u043d \\u0442\\u0435\\u043a\\u0441\\u0442 \\u0437\\u0430\\u0434\\u0430\\u043d\\u0438\\u044f'; return; }
  res.className = 'res';
  res.textContent = '\\u0420\\u0430\\u0437\\u0431\\u0438\\u0440\\u0430\\u044e... 20-40 \\u0441\\u0435\\u043a.';
  btn.disabled = true;
  btn.textContent = '\\u23f3 \\u0418\\u0434\\u0451\\u0442 \\u0440\\u0430\\u0437\\u0431\\u043e\\u0440...';
  _impPreview = null;
  try {
    var d = await api({action:'import_preview', task_type:t, task_text:txt, audio_text:aud, key_text:key});
    if (d.error) {
      res.className = 'res err';
      res.textContent = '\\u041e\\u0448\\u0438\\u0431\\u043a\\u0430: ' + d.error;
      btn.disabled = false;
      btn.textContent = '\\U0001f50d \\u0420\\u0430\\u0437\\u043e\\u0431\\u0440\\u0430\\u0442\\u044c';
      return;
    }
    _impPreview = {task_type: t, topic: topic, task_data: d.task_data};
    renderImportPreview(d.task_data, t, topic);
    btn.disabled = false;
    btn.textContent = '\\U0001f50d \\u0420\\u0430\\u0437\\u043e\\u0431\\u0440\\u0430\\u0442\\u044c';
  } catch(e) {
    res.className = 'res err';
    res.textContent = '\\u041e\\u0448\\u0438\\u0431\\u043a\\u0430: ' + e.message;
    btn.disabled = false;
    btn.textContent = '\\U0001f50d \\u0420\\u0430\\u0437\\u043e\\u0431\\u0440\\u0430\\u0442\\u044c';
  }
}

async function importConfirmSave() {
  if (!_impPreview) { alert('\\u0421\\u043d\\u0430\\u0447\\u0430\\u043b\\u0430 \\u0440\\u0430\\u0437\\u043e\\u0431\\u0440\\u0430\\u0442\\u044c'); return; }
  var res = document.getElementById('impRes');
  var btn = document.getElementById('impConfirmBtn');
  if (btn) { btn.disabled = true; btn.textContent = '\\u23f3 \\u0421\\u043e\\u0445\\u0440\\u0430\\u043d\\u044f\\u044e...'; }
  try {
    var d = await api({action:'import_save', task_type:_impPreview.task_type, topic_letter:_impPreview.topic, task_data:_impPreview.task_data});
    if (d.error) { alert('\\u041e\\u0448\\u0438\\u0431\\u043a\\u0430: ' + d.error); if (btn) { btn.disabled = false; btn.textContent = '\\u2705 \\u0421\\u043e\\u0445\\u0440\\u0430\\u043d\\u0438\\u0442\\u044c \\u0432 \\u0431\\u0430\\u043d\\u043a'; } return; }
    _impPreview = null;
    res.className = 'res ok';
    res.innerHTML = '\\u2705 \\u0421\\u043e\\u0445\\u0440\\u0430\\u043d\\u0435\\u043d\\u043e! \\u041a\\u043e\\u0434: <code>' + esc(d.code) + '</code>';
    document.getElementById('impText').value = '';
    document.getElementById('impAudio').value = '';
    document.getElementById('impKey').value = '';
  } catch(e) {
    alert('\\u041e\\u0448\\u0438\\u0431\\u043a\\u0430: ' + e.message);
    if (btn) { btn.disabled = false; btn.textContent = '\\u2705 \\u0421\\u043e\\u0445\\u0440\\u0430\\u043d\\u0438\\u0442\\u044c \\u0432 \\u0431\\u0430\\u043d\\u043a'; }
  }
}

function importCancelPreview() {
  _impPreview = null;
  var res = document.getElementById('impRes');
  res.className = '';
  res.innerHTML = '';
}

function _impTabRow(letter, text) {
  return '<tr><td style="padding:6px 10px;color:#c9b8ff;font-weight:700;border:1px solid rgba(123,92,255,.2)">' + esc(letter) + '</td>'
       + '<td style="padding:6px 10px;border:1px solid rgba(123,92,255,.2)">' + esc(text) + '</td></tr>';
}

function renderImportPreview(td, t, topic) {
  var res = document.getElementById('impRes');
  var h = '';
  h += '<div class="panel" style="background:rgba(123,92,255,.08);border:1px solid rgba(123,92,255,.4);margin-top:14px">';
  h += '<h3 style="color:#c9b8ff;margin-bottom:10px">\\u041f\\u0440\\u0435\\u0434\\u043f\\u0440\\u043e\\u0441\\u043c\\u043e\\u0442\\u0440 \\u2014 \\u0437\\u0430\\u0434\\u0430\\u043d\\u0438\\u0435 ' + esc(t) + ' (' + esc(topic) + ')</h3>';

  if (td.instruction) {
    h += '<div style="background:rgba(5,6,15,.5);padding:12px;border-radius:8px;color:#d0d5f5;font-size:13px;line-height:1.6;margin-bottom:12px;font-style:italic">' + esc(td.instruction) + '</div>';
  }

  if (t === '1' || t === '2') {
    var items = td.statements || [];
    h += '<div style="color:#c9b8ff;font-weight:700;margin-bottom:6px">\\u0423\\u0442\\u0432\\u0435\\u0440\\u0436\\u0434\\u0435\\u043d\\u0438\\u044f (' + items.length + '):</div>';
    items.forEach(function(s){
      var lab = t === '1' ? s.number : s.letter;
      h += '<div style="color:#d0d5f5;font-size:13px;margin:3px 0"><b>' + esc(lab) + '.</b> ' + esc(s.text) + '</div>';
    });
    if (t === '1') {
      h += '<div style="color:#c9b8ff;font-weight:700;margin:10px 0 6px">\\u0421\\u043a\\u0440\\u0438\\u043f\\u0442\\u044b (\\u0433\\u043e\\u043b\\u043e\\u0441\\u0430 A-F):</div>';
      (td.scripts || []).forEach(function(s){
        h += '<div style="color:#d0d5f5;font-size:12px;margin:2px 0"><b>Speaker ' + esc(s.speaker) + ':</b> ' + esc(String(s.text).slice(0,80)) + '...</div>';
      });
    } else if (t === '2') {
      h += '<div style="color:#c9b8ff;font-weight:700;margin:10px 0 6px">\\u0414\\u0438\\u0430\\u043b\\u043e\\u0433 (' + (td.dialogue_script||[]).length + ' \\u0440\\u0435\\u043f\\u043b\\u0438\\u043a):</div>';
      (td.dialogue_script || []).slice(0,4).forEach(function(s){
        h += '<div style="color:#d0d5f5;font-size:12px;margin:2px 0"><b>' + esc(s.speaker) + ' (' + esc(s.gender||'?') + '):</b> ' + esc(String(s.text).slice(0,70)) + '...</div>';
      });
    }
  } else if (t === '3-9') {
    h += '<div style="color:#c9b8ff;font-weight:700;margin-bottom:6px">\\u0412\\u043e\\u043f\\u0440\\u043e\\u0441\\u044b (' + (td.questions||[]).length + '):</div>';
    (td.questions || []).forEach(function(q){
      h += '<div style="color:#d0d5f5;font-size:13px;margin:4px 0"><b>' + q.number + '.</b> ' + esc(q.question) + '</div>';
      ['1','2','3'].forEach(function(k){
        h += '<div style="color:#a0a8d0;font-size:12px;margin-left:14px">' + k + ') ' + esc(q.options[k]) + '</div>';
      });
    });
    h += '<div style="color:#c9b8ff;font-weight:700;margin:10px 0 6px">\\u0418\\u043d\\u0442\\u0435\\u0440\\u0432\\u044c\\u044e (' + (td.interview_script||[]).length + ' \\u0440\\u0435\\u043f\\u043b\\u0438\\u043a):</div>';
    (td.interview_script || []).slice(0,3).forEach(function(s){
      h += '<div style="color:#d0d5f5;font-size:12px;margin:2px 0"><b>' + esc(s.speaker) + ' (' + esc(s.gender||'?') + '):</b> ' + esc(String(s.text).slice(0,70)) + '...</div>';
    });
  } else if (t === '10') {
    h += '<div style="color:#c9b8ff;font-weight:700;margin-bottom:6px">\\u0417\\u0430\\u0433\\u043e\\u043b\\u043e\\u0432\\u043a\\u0438 (' + (td.headings||[]).length + '):</div>';
    (td.headings || []).forEach(function(x){
      h += '<div style="color:#d0d5f5;font-size:13px;margin:2px 0"><b>' + x.number + '.</b> ' + esc(x.text) + '</div>';
    });
    h += '<div style="color:#c9b8ff;font-weight:700;margin:10px 0 6px">\\u0422\\u0435\\u043a\\u0441\\u0442\\u044b (' + (td.texts||[]).length + '):</div>';
    (td.texts || []).forEach(function(x){
      h += '<div style="color:#d0d5f5;font-size:12px;margin:2px 0"><b>' + esc(x.letter) + '.</b> ' + esc(String(x.text).slice(0,80)) + '...</div>';
    });
  } else if (t === '11') {
    if (td.title) h += '<div style="color:#d0d5f5;font-size:13px;margin-bottom:6px"><b>' + esc(td.title) + '</b></div>';
    h += '<div style="color:#d0d5f5;font-size:12px;background:rgba(5,6,15,.5);padding:10px;border-radius:6px;max-height:200px;overflow-y:auto;white-space:pre-wrap">' + esc(td.text || '') + '</div>';
    h += '<div style="color:#c9b8ff;font-weight:700;margin:10px 0 6px">\\u0424\\u0440\\u0430\\u0433\\u043c\\u0435\\u043d\\u0442\\u044b:</div>';
    (td.fragments || []).forEach(function(x){
      h += '<div style="color:#d0d5f5;font-size:12px;margin:2px 0"><b>' + x.number + '.</b> ' + esc(x.text) + '</div>';
    });
  } else if (t === '12-18' || t === '30-36') {
    if (td.title) h += '<div style="color:#d0d5f5;font-size:13px;margin-bottom:6px"><b>' + esc(td.title) + '</b></div>';
    h += '<div style="color:#d0d5f5;font-size:12px;background:rgba(5,6,15,.5);padding:10px;border-radius:6px;max-height:180px;overflow-y:auto;white-space:pre-wrap">' + esc(td.text || '') + '</div>';
    if (t === '12-18') {
      h += '<div style="color:#c9b8ff;font-weight:700;margin:10px 0 6px">\\u0412\\u043e\\u043f\\u0440\\u043e\\u0441\\u044b:</div>';
      (td.questions || []).forEach(function(q){
        h += '<div style="color:#d0d5f5;font-size:13px;margin:4px 0"><b>' + q.number + '.</b> ' + esc(q.question) + '</div>';
      });
    } else {
      h += '<div style="color:#c9b8ff;font-weight:700;margin:10px 0 6px">\\u0417\\u0430\\u0434\\u0430\\u043d\\u0438\\u044f (' + (td.items||[]).length + '):</div>';
      (td.items || []).forEach(function(it){
        h += '<div style="color:#d0d5f5;font-size:12px;margin:2px 0"><b>' + it.number + '.</b> ' + (it.options ? esc([it.options['1'],it.options['2'],it.options['3'],it.options['4']].join(' / ')) : '') + '</div>';
      });
    }
  } else if (t === '19-24' || t === '25-29') {
    if (td.title) h += '<div style="color:#d0d5f5;font-size:13px;margin-bottom:6px"><b>' + esc(td.title) + '</b></div>';
    h += '<div style="color:#d0d5f5;font-size:12px;background:rgba(5,6,15,.5);padding:10px;border-radius:6px;max-height:180px;overflow-y:auto;white-space:pre-wrap">' + esc(td.text || '') + '</div>';
    h += '<div style="color:#c9b8ff;font-weight:700;margin:10px 0 6px">\\u0411\\u0430\\u0437\\u043e\\u0432\\u044b\\u0435 \\u0441\\u043b\\u043e\\u0432\\u0430:</div>';
    (td.items || []).forEach(function(it){
      h += '<div style="color:#d0d5f5;font-size:12px;margin:2px 0"><b>' + it.number + '.</b> <span style="font-family:monospace">' + esc(it.source_word) + '</span></div>';
    });
  } else if (t === '37' || t === '38.1' || t === '38.2') {
    h += '<div style="color:#d0d5f5;font-size:13px;background:rgba(5,6,15,.5);padding:14px;border-radius:8px;white-space:pre-wrap;line-height:1.7">' + esc(td.task_text || '') + '</div>';
    if (td.survey_data && td.survey_data.options) {
      h += '<div style="color:#c9b8ff;font-weight:700;margin:12px 0 6px">\\u0414\\u0430\\u043d\\u043d\\u044b\\u0435 \\u043e\\u043f\\u0440\\u043e\\u0441\\u0430:</div>';
      h += '<div style="color:#a0a8d0;font-size:12px;margin-bottom:6px">' + esc(td.survey_data.question || '') + '</div>';
      h += '<table style="width:100%;border-collapse:collapse;margin:6px 0">';
      h += '<tr><th style="padding:6px 10px;background:rgba(123,92,255,.15);border:1px solid rgba(123,92,255,.2);color:#c9b8ff;text-align:left">Options</th>';
      h += '<th style="padding:6px 10px;background:rgba(123,92,255,.15);border:1px solid rgba(123,92,255,.2);color:#c9b8ff;width:120px;text-align:center">%</th></tr>';
      (td.survey_data.options || []).forEach(function(o){
        h += '<tr><td style="padding:6px 10px;border:1px solid rgba(123,92,255,.2);color:#d0d5f5;font-size:13px">' + esc(o.option) + '</td>';
        h += '<td style="padding:6px 10px;border:1px solid rgba(123,92,255,.2);color:#d0d5f5;font-size:13px;text-align:center">' + esc(o.percent) + '</td></tr>';
      });
      h += '</table>';
    }
    if (td.plan && td.plan.length) {
      h += '<div style="color:#c9b8ff;font-weight:700;margin:12px 0 6px">\\u041f\\u043b\\u0430\\u043d:</div>';
      td.plan.forEach(function(p){ h += '<div style="color:#d0d5f5;font-size:12px;margin:2px 0;margin-left:10px">\\u2013 ' + esc(p) + '</div>'; });
    }
  }

  if (td.answer_key && Object.keys(td.answer_key).length) {
    h += '<div style="color:#c9b8ff;font-weight:700;margin:12px 0 6px">\\u041a\\u043b\\u044e\\u0447:</div>';
    h += '<div style="color:#00e5ff;font-family:monospace;font-size:13px;background:rgba(5,6,15,.5);padding:8px 12px;border-radius:6px">';
    var parts = [];
    Object.keys(td.answer_key).forEach(function(k){ parts.push(k + '\\u2192' + td.answer_key[k]); });
    h += parts.join('  ');
    h += '</div>';
  }

  h += '<details style="margin-top:12px"><summary style="cursor:pointer;color:#8b93c4;font-size:12px">\\u041f\\u043e\\u043a\\u0430\\u0437\\u0430\\u0442\\u044c JSON</summary>';
  h += '<pre style="color:#a0a8d0;font-size:11px;background:rgba(5,6,15,.5);padding:10px;border-radius:6px;max-height:300px;overflow:auto;margin-top:8px">' + esc(JSON.stringify(td, null, 2)) + '</pre></details>';

  h += '<div style="display:flex;gap:12px;margin-top:16px">';
  h += '<button class="btn btn-ok" id="impConfirmBtn" style="width:auto;padding:12px 24px" onclick="importConfirmSave()">\\u2705 \\u0421\\u043e\\u0445\\u0440\\u0430\\u043d\\u0438\\u0442\\u044c \\u0432 \\u0431\\u0430\\u043d\\u043a</button>';
  h += '<button class="btn btn-cancel" style="width:auto;padding:12px 24px" onclick="importCancelPreview()">\\u274c \\u041e\\u0442\\u043c\\u0435\\u043d\\u0438\\u0442\\u044c</button>';
  h += '</div>';

  h += '</div>';
  res.className = '';
  res.innerHTML = h;
}
'''


def is_applied(src):
    return 'importPreviewStart' in src and 'def admin_import_save' in src


def apply(src):
    if is_applied(src):
        return src

    if OLD_TAIL not in src:
        raise Exception('anchor not found: admin_import_task tail')
    src = src.replace(OLD_TAIL, NEW_TAIL, 1)

    if OLD_ACTION not in src:
        raise Exception('anchor not found: import_task action')
    src = src.replace(OLD_ACTION, NEW_ACTION, 1)

    if OLD_BTN not in src:
        raise Exception('anchor not found: import button onclick')
    src = src.replace(OLD_BTN, NEW_BTN, 1)

    if 'function importPreviewStart' not in src:
        if JS_ANCHOR not in src:
            raise Exception('anchor not found: impOnTypeChange')
        src = src.replace(JS_ANCHOR, JS_INSERT + '\n' + JS_ANCHOR, 1)

    return src
