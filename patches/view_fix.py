# -*- coding: utf-8 -*-
# Patch: hide Upload tab + full bank viewer + student-style import preview + PDF download.
import shutil, datetime

OVERRIDE = """
// VIEW_FIX_PATCH
(function(){
  // 1. hide Upload tab
  try {
    var btn = document.querySelector('[data-tab="upload"]');
    if (btn) btn.style.display = 'none';
    var pane = document.getElementById('pane-upload');
    if (pane) pane.style.display = 'none';
    var bankBtn = document.querySelector('[data-tab="bank"]');
    var bankPane = document.getElementById('pane-bank');
    if (bankBtn && bankPane) {
      var tabs = document.querySelectorAll('.tab');
      for (var i=0;i<tabs.length;i++) tabs[i].classList.remove('active');
      var panes = document.querySelectorAll('.tab-pane');
      for (var j=0;j<panes.length;j++) panes[j].classList.remove('active');
      bankBtn.classList.add('active');
      bankPane.classList.add('active');
    }
  } catch(e){ console.log('hide tab', e); }

  // 2. renderStudentView - renders task the way student sees it
  window._renderStudentView = function(t, d){
    var h = '';
    if (d.instruction) h += '<div style="font-style:italic;color:#555;margin-bottom:12px;line-height:1.5;font-size:13px">' + esc(d.instruction) + '</div>';
    if (t === '1'){
      (d.statements||[]).forEach(function(s){h += '<div style="margin:4px 0;color:#333"><b>' + s.number + '.</b> ' + esc(s.text) + '</div>';});
      h += '<table style="border-collapse:collapse;margin:12px 0">';
      h += '<tr><th style="border:1px solid #000;padding:6px 14px;background:#eee;color:#000">Говорящий</th>';
      'ABCDEF'.split('').forEach(function(k){h += '<th style="border:1px solid #000;padding:6px 14px;background:#eee;color:#000">' + k + '</th>';});
      h += '</tr><tr><td style="border:1px solid #000;padding:6px 14px;color:#000">Ответ</td>';
      'ABCDEF'.split('').forEach(function(){h += '<td style="border:1px solid #000;padding:6px 14px;min-width:36px">&nbsp;</td>';});
      h += '</tr></table>';
    } else if (t === '2'){
      (d.statements||[]).forEach(function(s){h += '<div style="margin:4px 0;color:#333"><b>' + esc(s.letter) + '.</b> ' + esc(s.text) + '</div>';});
      h += '<table style="border-collapse:collapse;margin:12px 0">';
      h += '<tr><th style="border:1px solid #000;padding:6px 14px;background:#eee;color:#000">Утв.</th>';
      'ABCDEFG'.split('').forEach(function(k){h += '<th style="border:1px solid #000;padding:6px 14px;background:#eee;color:#000">' + k + '</th>';});
      h += '</tr><tr><td style="border:1px solid #000;padding:6px 14px;color:#000">Ответ</td>';
      'ABCDEFG'.split('').forEach(function(){h += '<td style="border:1px solid #000;padding:6px 14px;min-width:36px">&nbsp;</td>';});
      h += '</tr></table>';
      h += '<div style="font-size:11px;color:#666">1 – True, 2 – False, 3 – Not stated</div>';
    } else if (t === '3-9'){
      (d.questions||[]).forEach(function(q){
        h += '<div style="margin:10px 0;color:#333"><b>' + q.number + '.</b> ' + esc(q.question) + '</div>';
        ['1','2','3'].forEach(function(k){h += '<div style="margin:2px 0 2px 20px;color:#444">' + k + ') ' + esc(q.options[k]) + '</div>';});
      });
    } else if (t === '10'){
      (d.headings||[]).forEach(function(x){h += '<div style="margin:2px 0;color:#333"><b>' + x.number + '.</b> ' + esc(x.text) + '</div>';});
      h += '<hr style="margin:12px 0;border:none;border-top:1px solid #999">';
      (d.texts||[]).forEach(function(x){h += '<div style="margin:10px 0;color:#333;line-height:1.5"><b>' + esc(x.letter) + '.</b> ' + esc(x.text) + '</div>';});
      h += '<table style="border-collapse:collapse;margin:12px 0">';
      h += '<tr>' + 'ABCDEFG'.split('').map(function(k){return '<th style="border:1px solid #000;padding:6px 14px;background:#eee;color:#000">' + k + '</th>';}).join('') + '</tr>';
      h += '<tr>' + 'ABCDEFG'.split('').map(function(){return '<td style="border:1px solid #000;padding:6px 14px;min-width:36px">&nbsp;</td>';}).join('') + '</tr></table>';
    } else if (t === '11'){
      if (d.title) h += '<div style="font-weight:700;margin-bottom:6px;color:#000">' + esc(d.title) + '</div>';
      if (d.text) h += '<div style="white-space:pre-wrap;line-height:1.6;margin-bottom:12px;color:#333">' + esc(d.text) + '</div>';
      (d.fragments||[]).forEach(function(f){h += '<div style="margin:2px 0;color:#333"><b>' + f.number + '.</b> ' + esc(f.text) + '</div>';});
      h += '<table style="border-collapse:collapse;margin:12px 0">';
      h += '<tr>' + 'ABCDEF'.split('').map(function(k){return '<th style="border:1px solid #000;padding:6px 14px;background:#eee;color:#000">' + k + '</th>';}).join('') + '</tr>';
      h += '<tr>' + 'ABCDEF'.split('').map(function(){return '<td style="border:1px solid #000;padding:6px 14px;min-width:36px">&nbsp;</td>';}).join('') + '</tr></table>';
    } else if (t === '12-18'){
      if (d.title) h += '<div style="font-weight:700;margin-bottom:6px;color:#000">' + esc(d.title) + '</div>';
      if (d.text) h += '<div style="white-space:pre-wrap;line-height:1.6;margin-bottom:12px;color:#333">' + esc(d.text) + '</div>';
      (d.questions||[]).forEach(function(q){
        h += '<div style="margin:10px 0;color:#333"><b>' + q.number + '.</b> ' + esc(q.question) + '</div>';
        ['1','2','3','4'].forEach(function(k){h += '<div style="margin:2px 0 2px 20px;color:#444">' + k + ') ' + esc(q.options[k]) + '</div>';});
      });
    } else if (t === '19-24' || t === '25-29'){
      if (d.title) h += '<div style="font-weight:700;margin-bottom:6px;color:#000">' + esc(d.title) + '</div>';
      if (d.text) h += '<div style="white-space:pre-wrap;line-height:1.8;color:#333">' + esc(d.text) + '</div>';
      h += '<hr style="margin:12px 0;border:none;border-top:1px solid #999">';
      (d.items||[]).forEach(function(it){
        h += '<div style="margin:6px 0;color:#333"><b>' + it.number + '.</b> <span style="font-family:monospace;letter-spacing:1px">' + esc(it.source_word) + '</span> -&gt; _________________</div>';
      });
    } else if (t === '30-36'){
      if (d.title) h += '<div style="font-weight:700;margin-bottom:6px;color:#000">' + esc(d.title) + '</div>';
      if (d.text) h += '<div style="white-space:pre-wrap;line-height:1.6;color:#333">' + esc(d.text) + '</div>';
      (d.items||[]).forEach(function(it){
        h += '<div style="margin:10px 0;color:#333"><b>' + it.number + '.</b></div>';
        ['1','2','3','4'].forEach(function(k){h += '<div style="margin:2px 0 2px 20px;color:#444">' + k + ') ' + esc(it.options[k]) + '</div>';});
      });
    } else if (t === '37'){
      if (d.task_text) h += '<div style="white-space:pre-wrap;line-height:1.6;color:#333;margin-bottom:12px">' + esc(d.task_text) + '</div>';
      h += '<div style="background:#f5f5f5;border:1px dashed #999;padding:14px;border-radius:6px;color:#666;font-style:italic;text-align:center;font-size:13px">Здесь у ученика будет окно для ввода ответа (90-154 слова) и кнопка «Отправить на проверку»</div>';
    } else if (t === '38.1' || t === '38.2'){
      if (d.task_text) h += '<div style="white-space:pre-wrap;line-height:1.6;color:#333;margin-bottom:12px">' + esc(d.task_text) + '</div>';
      if (d.survey_data && d.survey_data.options){
        if (d.survey_data.question) h += '<div style="text-align:center;font-weight:700;margin:12px 0 8px;color:#000">' + esc(d.survey_data.question) + '</div>';
        h += '<table style="border-collapse:collapse;margin:8px 0;width:100%">';
        h += '<tr><th style="border:1px solid #000;padding:6px 14px;background:#eee;color:#000;text-align:left">Options</th><th style="border:1px solid #000;padding:6px 14px;background:#eee;color:#000;width:100px;text-align:center">Number of respondents (%)</th></tr>';
        (d.survey_data.options||[]).forEach(function(o){h += '<tr><td style="border:1px solid #000;padding:6px 14px;color:#333">' + esc(o.option) + '</td><td style="border:1px solid #000;padding:6px 14px;color:#333;text-align:center">' + esc(o.percent) + '</td></tr>';});
        h += '</table>';
      }
      if (d.plan && d.plan.length){
        h += '<div style="font-weight:700;margin:12px 0 6px;color:#000">Use the following plan:</div>';
        d.plan.forEach(function(p){h += '<div style="margin:2px 0 2px 20px;color:#333">- ' + esc(p) + '</div>';});
      }
      h += '<div style="background:#f5f5f5;border:1px dashed #999;padding:14px;border-radius:6px;color:#666;font-style:italic;text-align:center;font-size:13px;margin-top:12px">Здесь у ученика будет окно для ввода ответа (200-250 слов) и кнопка «Отправить на проверку»</div>';
    }
    if (d.answer_key && Object.keys(d.answer_key).length){
      h += '<div style="margin-top:16px;padding:10px 14px;background:#fff8d8;border:1px solid #b8860b;border-radius:6px;color:#000"><b>Ключ (только для админа):</b><br>';
      var parts = [];
      Object.keys(d.answer_key).forEach(function(k){parts.push(k + '-' + d.answer_key[k]);});
      h += '<span style="font-family:monospace;color:#8b6508;font-weight:700;font-size:13px">' + parts.join('  ') + '</span></div>';
    }
    if (d.explanations && Object.keys(d.explanations).length){
      h += '<details style="margin-top:12px;background:#eef7ee;border:1px solid #4a8f4a;border-radius:6px;padding:10px;color:#000"><summary style="cursor:pointer;color:#2e6b2e;font-weight:700">Объяснения</summary><div style="margin-top:8px">';
      Object.keys(d.explanations).forEach(function(k){
        h += '<div style="margin:4px 0;font-size:13px"><b style="color:#2e6b2e">' + esc(k) + ':</b> ' + esc(d.explanations[k]) + '</div>';
      });
      h += '</div></details>';
    }
    return h;
  };

  // 3. Import preview: student-style
  window.renderImportPreview = function(td, t, topic){
    var res = document.getElementById('impRes');
    if (!res) return;
    var h = '';
    h += '<div class="panel" style="background:rgba(123,92,255,.08);border:1px solid rgba(123,92,255,.4);margin-top:14px">';
    h += '<h3 style="color:#c9b8ff;margin-bottom:10px">Предпросмотр: задание ' + esc(t) + ' (' + esc(topic) + ')</h3>';
    h += '<div style="background:#fff;color:#000;padding:20px;border-radius:8px;max-height:600px;overflow:auto;font-family:Times New Roman,serif;font-size:12pt;line-height:1.4">';
    h += window._renderStudentView(t, td);
    h += '</div>';
    h += '<div style="display:flex;gap:12px;margin-top:16px">';
    h += '<button class="btn btn-ok" style="width:auto;padding:12px 24px" onclick="importConfirmSave()">Сохранить в банк</button>';
    h += '<button class="btn btn-cancel" style="width:auto;padding:12px 24px" onclick="importCancelPreview()">Отменить</button>';
    h += '</div>';
    h += '<details style="margin-top:10px"><summary style="cursor:pointer;color:#8b93c4;font-size:12px">Показать JSON</summary><pre style="color:#a0a8d0;font-size:11px;background:rgba(5,6,15,.5);padding:10px;border-radius:6px;max-height:200px;overflow:auto;margin-top:8px">' + esc(JSON.stringify(td, null, 2)) + '</pre></details>';
    h += '</div>';
    res.className = '';
    res.innerHTML = h;
  };

  // 4. Bank viewer: full task
  window.openTask = async function(task_type, topic_letter, code){
    var v = document.getElementById('bankList');
    v.innerHTML = '<div class="res">Загружаю ' + esc(code) + '...</div>';
    try {
      var d = await api({action:'get_bank_task', task_type:task_type, topic_letter:topic_letter, code:code});
      if (d.error){ v.innerHTML = '<div class="res err">Ошибка: ' + esc(d.error) + '</div>'; return; }
      _loadedBankTask = d;
      _loadedBankTask.task_type = task_type;
      var h = '<div class="res ok" style="margin-top:12px">';
      h += '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px"><b style="font-family:monospace;font-size:16px">' + esc(d.code) + '</b><button class="btn btn-sm btn-outline" onclick="listBank()">Закрыть</button></div>';
      if (d.audio_b64){
        var bytes = b64ToBytes(d.audio_b64);
        var url = URL.createObjectURL(new Blob([bytes], {type:'audio/mpeg'}));
        h += '<audio controls src="' + url + '" style="width:100%;margin:8px 0"></audio>';
      }
      h += '<div style="background:#fff;color:#000;padding:20px;border-radius:8px;max-height:600px;overflow:auto;font-family:Times New Roman,serif;font-size:12pt;line-height:1.4;margin-top:12px">';
      h += window._renderStudentView(task_type, d);
      h += '</div>';
      h += '<div style="margin-top:14px;padding-top:14px;border-top:1px solid rgba(123,92,255,.2)"><b style="color:#c9b8ff">Скачать PDF:</b><br>';
      h += '<button class="btn btn-sm btn-outline" style="margin-right:8px;margin-top:8px" onclick="downloadLoadedBankTask(false)">Для ученика</button>';
      h += '<button class="btn btn-sm" style="margin-top:8px" onclick="downloadLoadedBankTask(true)">Для учителя</button></div>';
      h += '</div>';
      v.innerHTML = h;
    } catch(e){ v.innerHTML = '<div class="res err">Ошибка: ' + esc(e.message) + '</div>'; }
  };

  // 5. PDF via html2pdf
  window._loadHtml2PdfOnce = function(cb){
    if (typeof html2pdf !== 'undefined') { cb(true); return; }
    var urls = [
      'https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js',
      'https://cdn.jsdelivr.net/npm/html2pdf.js@0.10.1/dist/html2pdf.bundle.min.js'
    ];
    var i = 0;
    (function next(){
      if (i >= urls.length) { cb(false); return; }
      var s = document.createElement('script');
      s.src = urls[i++];
      s.onload = function(){ cb(typeof html2pdf !== 'undefined'); };
      s.onerror = next;
      document.head.appendChild(s);
    })();
  };

  window.openPrintWindow = function(bodyHtml, title){
    window._loadHtml2PdfOnce(function(ok){
      if (!ok) {
        var w = window.open('', '_blank');
        if (w) {
          var doc = '<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8"><title>' + esc(title) + '</title><style>' + (typeof PRINT_CSS !== 'undefined' ? PRINT_CSS : '') + '</style></head><body class="print-body"><div class="print-doc">' + bodyHtml + '</div><scr' + 'ipt>window.addEventListener("load",function(){setTimeout(function(){window.print();},500);});</scr' + 'ipt></body></html>';
          w.document.open(); w.document.write(doc); w.document.close();
        }
        return;
      }
      var c = document.createElement('div');
      c.className = 'print-doc';
      c.style.cssText = 'position:fixed;top:0;left:0;width:210mm;background:#fff;color:#000;z-index:99999;padding:20px;opacity:0;pointer-events:none;font-family:"Times New Roman",Times,serif;font-size:12pt;line-height:1.4';
      c.innerHTML = bodyHtml;
      document.body.appendChild(c);
      var safe = (title || 'document').replace(/[^A-Za-zА-Яа-я0-9_ -]+/g, '_').trim() || 'document';
      setTimeout(function(){
        var opt = {
          margin: [10,10,10,10],
          filename: safe + '.pdf',
          image: { type:'jpeg', quality:0.95 },
          html2canvas: { scale:2, useCORS:true, logging:false, backgroundColor:'#ffffff', scrollX:0, scrollY:0, windowWidth:794 },
          jsPDF: { unit:'mm', format:'a4', orientation:'portrait' },
          pagebreak: { mode:['css','legacy'] }
        };
        html2pdf().set(opt).from(c).output('datauristring').then(function(dataUri){
          if (c.parentNode) c.parentNode.removeChild(c);
          var a = document.createElement('a');
          a.href = dataUri;
          a.download = safe + '.pdf';
          document.body.appendChild(a);
          a.click();
          setTimeout(function(){ document.body.removeChild(a); }, 500);
        }).catch(function(err){
          if (c.parentNode) c.parentNode.removeChild(c);
          console.error('pdf err', err);
          alert('PDF: ' + (err && err.message ? err.message : err));
        });
      }, 400);
    });
  };
})();
"""


def is_applied(src):
    return '// VIEW_FIX_PATCH' in src


def apply(src):
    if is_applied(src):
        return src

    # remove previous override markers
    for marker in ('// FINAL_FIX_APPLIED', '// FIX_ALL_PATCH_APPLIED', '// PDF2_PATCH'):
        while marker in src:
            s = src.find(marker)
            e = src.find('</script>', s)
            if e < 0: break
            src = src[:s] + src[e:]

    anchor = "\n</script>\n</body>\n</html>"
    cnt = src.count(anchor)
    if cnt == 0:
        raise Exception("anchor not found: </script></body></html>")
    src = src.replace(anchor, OVERRIDE + anchor)
    print("[patch] injected into " + str(cnt) + " block(s)")
    return src
