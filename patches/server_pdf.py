# -*- coding: utf-8 -*-
# Patch: PDF via server-side reportlab.

PY_NEW = r'''
def _pdf_escape(s):
    from xml.sax.saxutils import escape as _e
    return _e(str(s or ""))

def _pdf_font():
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    import os as _os
    cands = [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/TTF/DejaVuSans.ttf',
    ]
    for p in cands:
        try:
            if _os.path.exists(p):
                pdfmetrics.registerFont(TTFont('MainFont', p))
                return 'MainFont'
        except Exception:
            pass
    return 'Helvetica'


def _render_task_pdf(task_type, task_data, with_answers=False):
    import io
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

    font = _pdf_font()
    st_title = ParagraphStyle('t', fontName=font, fontSize=15, leading=18, alignment=1, spaceAfter=8)
    st_inst = ParagraphStyle('i', fontName=font, fontSize=10, leading=13, textColor=colors.HexColor('#222222'), spaceAfter=6)
    st_text = ParagraphStyle('tx', fontName=font, fontSize=11, leading=14, spaceAfter=4)
    st_h = ParagraphStyle('h', fontName=font, fontSize=12, leading=15, spaceAfter=4)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=15*mm, rightMargin=15*mm,
                            topMargin=15*mm, bottomMargin=15*mm)
    story = []
    story.append(Paragraph(_pdf_escape('Задание ' + str(task_type)), st_title))

    ins = task_data.get('instruction', '')
    if ins:
        story.append(Paragraph(_pdf_escape(ins), st_inst))

    tbl_style = TableStyle([
        ('FONTNAME', (0,0), (-1,-1), font),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e8e8e8')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ])

    if task_type == '1':
        for s in task_data.get('statements', []) or []:
            story.append(Paragraph('<b>' + _pdf_escape(str(s.get('number')) + '.') + '</b> ' + _pdf_escape(s.get('text')), st_text))
        story.append(Spacer(1, 8))
        row1 = ['Говорящий'] + list('ABCDEF')
        row2 = ['Ответ'] + [''] * 6
        t = Table([row1, row2], colWidths=[80, 45, 45, 45, 45, 45, 45])
        t.setStyle(tbl_style)
        story.append(t)
    elif task_type == '2':
        for s in task_data.get('statements', []) or []:
            story.append(Paragraph('<b>' + _pdf_escape(str(s.get('letter')) + '.') + '</b> ' + _pdf_escape(s.get('text')), st_text))
        story.append(Spacer(1, 8))
        row1 = ['Утв.'] + list('ABCDEFG')
        row2 = ['Ответ'] + [''] * 7
        t = Table([row1, row2], colWidths=[60, 40, 40, 40, 40, 40, 40, 40])
        t.setStyle(tbl_style)
        story.append(t)
        story.append(Paragraph('1 – True, 2 – False, 3 – Not stated', st_text))
    elif task_type == '3-9':
        for q in task_data.get('questions', []) or []:
            story.append(Paragraph('<b>' + _pdf_escape(str(q.get('number')) + '.') + '</b> ' + _pdf_escape(q.get('question')), st_text))
            opts = q.get('options') or {}
            for k in ['1','2','3']:
                story.append(Paragraph(_pdf_escape(k + ') ' + str(opts.get(k, ''))), st_text))
    elif task_type == '10':
        for h in task_data.get('headings', []) or []:
            story.append(Paragraph('<b>' + _pdf_escape(str(h.get('number')) + '.') + '</b> ' + _pdf_escape(h.get('text')), st_text))
        story.append(Spacer(1, 8))
        for x in task_data.get('texts', []) or []:
            story.append(Paragraph('<b>' + _pdf_escape(x.get('letter')) + '.</b> ' + _pdf_escape(x.get('text')), st_text))
        story.append(Spacer(1, 8))
        row1 = list('ABCDEFG')
        row2 = [''] * 7
        t = Table([row1, row2], colWidths=[55]*7)
        t.setStyle(tbl_style)
        story.append(t)
    elif task_type == '11':
        if task_data.get('title'):
            story.append(Paragraph(_pdf_escape(task_data.get('title')), st_h))
        if task_data.get('text'):
            story.append(Paragraph(_pdf_escape(task_data.get('text')).replace('\n', '<br/>'), st_text))
        story.append(Spacer(1, 6))
        for f in task_data.get('fragments', []) or []:
            story.append(Paragraph('<b>' + _pdf_escape(str(f.get('number')) + '.') + '</b> ' + _pdf_escape(f.get('text')), st_text))
        story.append(Spacer(1, 8))
        row1 = list('ABCDEF')
        row2 = [''] * 6
        t = Table([row1, row2], colWidths=[60]*6)
        t.setStyle(tbl_style)
        story.append(t)
    elif task_type in ('12-18', '30-36'):
        if task_data.get('title'):
            story.append(Paragraph(_pdf_escape(task_data.get('title')), st_h))
        if task_data.get('text'):
            story.append(Paragraph(_pdf_escape(task_data.get('text')).replace('\n', '<br/>'), st_text))
        story.append(Spacer(1, 6))
        items = task_data.get('questions') or task_data.get('items') or []
        for it in items:
            num = it.get('number')
            q = it.get('question')
            if q:
                story.append(Paragraph('<b>' + _pdf_escape(str(num) + '.') + '</b> ' + _pdf_escape(q), st_text))
            else:
                story.append(Paragraph('<b>' + _pdf_escape(str(num) + '.') + '</b>', st_text))
            opts = it.get('options') or {}
            for k in ['1','2','3','4']:
                story.append(Paragraph(_pdf_escape(k + ') ' + str(opts.get(k, ''))), st_text))
    elif task_type in ('19-24', '25-29'):
        if task_data.get('title'):
            story.append(Paragraph(_pdf_escape(task_data.get('title')), st_h))
        if task_data.get('text'):
            story.append(Paragraph(_pdf_escape(task_data.get('text')).replace('\n', '<br/>'), st_text))
        story.append(Spacer(1, 8))
        for it in task_data.get('items', []) or []:
            story.append(Paragraph('<b>' + _pdf_escape(str(it.get('number')) + '.') + '</b> ' + _pdf_escape(it.get('source_word')) + ' — ____________________', st_text))
    elif task_type == '37':
        if task_data.get('task_text'):
            story.append(Paragraph(_pdf_escape(task_data.get('task_text')).replace('\n', '<br/>'), st_text))
        story.append(Spacer(1, 10))
        story.append(Paragraph('Ответ (100–140 слов):', st_h))
        for _ in range(20):
            story.append(Paragraph('_' * 100, st_text))
    elif task_type in ('38.1', '38.2'):
        if task_data.get('task_text'):
            story.append(Paragraph(_pdf_escape(task_data.get('task_text')).replace('\n', '<br/>'), st_text))
        sd = task_data.get('survey_data') or {}
        if sd.get('question'):
            story.append(Spacer(1, 6))
            story.append(Paragraph('<b>' + _pdf_escape(sd.get('question')) + '</b>', st_text))
        opts = sd.get('options') or []
        if opts:
            rows = [['Options', 'Number of respondents (%)']]
            for o in opts:
                rows.append([str(o.get('option','')), str(o.get('percent',''))])
            t = Table(rows, colWidths=[130, 60])
            t.setStyle(tbl_style)
            story.append(t)
        plan = task_data.get('plan') or []
        if plan:
            story.append(Spacer(1, 6))
            story.append(Paragraph('<b>Use the following plan:</b>', st_text))
            for p in plan:
                story.append(Paragraph('– ' + _pdf_escape(p), st_text))
        story.append(Spacer(1, 10))
        story.append(Paragraph('Ответ (200–250 слов):', st_h))
        for _ in range(24):
            story.append(Paragraph('_' * 100, st_text))

    if with_answers:
        story.append(PageBreak())
        story.append(Paragraph('ОТВЕТЫ', st_title))
        key = task_data.get('answer_key') or {}
        parts = []
        for k in key:
            parts.append(str(k) + '→' + str(key[k]))
        story.append(Paragraph(_pdf_escape('   '.join(parts)), st_text))
        exps = task_data.get('explanations') or {}
        if exps:
            story.append(Spacer(1, 8))
            story.append(Paragraph('Объяснения:', st_h))
            for k in exps:
                story.append(Paragraph('<b>' + _pdf_escape(str(k)) + ':</b> ' + _pdf_escape(exps[k]), st_text))

    doc.build(story)
    return buf.getvalue()

'''

ANCHOR_PY = 'def handler(event, context):'

ACTION = '''            if action == "pdf_download":
                _t = data.get("task_type") or ""
                _td = data.get("task_data") or {}
                _wa = bool(data.get("with_answers"))
                if not _t:
                    return _resp(400, {"error": "task_type required"})
                if not _td:
                    return _resp(400, {"error": "task_data required"})
                try:
                    import base64 as _b64
                    pdf_bytes = _render_task_pdf(_t, _td, _wa)
                    return _resp(200, {"ok": True, "pdf": _b64.b64encode(pdf_bytes).decode("ascii")})
                except Exception as _e:
                    import traceback as _tb
                    _tb.print_exc()
                    return _resp(500, {"error": str(_e)})

'''

ANCHOR_ACTION = '            if action == "variant_generate":'

JS_OVERRIDE = """
// SERVER_PDF_OVERRIDE
(function(){
  window._serverPdf = async function(taskType, taskData, withAnswers, filename){
    try {
      var res = await fetch(window.location.pathname, {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({action:'pdf_download', task_type: taskType, task_data: taskData, with_answers: !!withAnswers})
      });
      var d = await res.json();
      if (d.error) { alert('Ошибка: ' + d.error); return; }
      if (!d.pdf) { alert('Пустой PDF'); return; }
      var bin = atob(d.pdf);
      var bytes = new Uint8Array(bin.length);
      for (var i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
      var blob = new Blob([bytes], {type:'application/pdf'});
      var url = URL.createObjectURL(blob);
      var a = document.createElement('a');
      a.href = url;
      a.download = (filename || ('task_' + taskType)) + '.pdf';
      document.body.appendChild(a);
      a.click();
      setTimeout(function(){ document.body.removeChild(a); URL.revokeObjectURL(url); }, 1500);
    } catch(e) {
      alert('Ошибка: ' + e.message);
    }
  };

  window.downloadLoadedBankTask = function(withAnswers){
    if (!_loadedBankTask) { alert('Ничего не загружено'); return; }
    var t = _loadedBankTask.task_type;
    var name = 'Задание_' + t + (_loadedBankTask.code ? ('_' + _loadedBankTask.code) : '') + (withAnswers ? '_с_ответами' : '');
    window._serverPdf(t, _loadedBankTask, withAnswers, name);
  };

  window.downloadTaskPDF = function(){
    var d = window._taskData;
    if (!d) { alert('Задание не загружено'); return; }
    var t = (d._meta && d._meta.task_type) || d.task_type || '';
    window._serverPdf(t, d, false, 'Задание_' + t);
  };
})();
"""


def is_applied(src):
    return '_serverPdf' in src and 'pdf_download' in src


def apply(src):
    if is_applied(src):
        return src
    if '_render_task_pdf' not in src:
        if ANCHOR_PY not in src:
            raise Exception('anchor not found: def handler')
        src = src.replace(ANCHOR_PY, PY_NEW + '\n\n' + ANCHOR_PY, 1)
    if 'action == "pdf_download"' not in src:
        if ANCHOR_ACTION not in src:
            raise Exception('anchor not found: variant_generate action')
        src = src.replace(ANCHOR_ACTION, ACTION + ANCHOR_ACTION, 1)
    anchor = '\n</script>\n</body>\n</html>'
    if anchor not in src:
        raise Exception('anchor not found: closing script')
    src = src.replace(anchor, JS_OVERRIDE + anchor)
    return src
