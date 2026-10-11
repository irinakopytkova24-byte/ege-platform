# -*- coding: utf-8 -*-
# Patch: PDF download via html2pdf.js. Fixed version.

PATCH_NAME = "pdf_download"
PATCH_DESCRIPTION = "Save as PDF via html2pdf.js - direct download, no print dialog"


NEW_FUNC = r'''function _loadHtml2Pdf(cb){
  if (typeof html2pdf !== 'undefined') { cb(true); return; }
  var urls = [
    'https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js',
    'https://cdn.jsdelivr.net/npm/html2pdf.js@0.10.1/dist/html2pdf.bundle.min.js',
    'https://unpkg.com/html2pdf.js@0.10.1/dist/html2pdf.bundle.min.js'
  ];
  var i = 0;
  function tryNext(){
    if (i >= urls.length) { cb(false); return; }
    var s = document.createElement('script');
    s.src = urls[i++];
    s.onload = function(){ cb(typeof html2pdf !== 'undefined'); };
    s.onerror = function(){ tryNext(); };
    document.head.appendChild(s);
  }
  tryNext();
}

function openPrintWindow(bodyHtml, title){
  _loadHtml2Pdf(function(ok){
    if (!ok) {
      var w = window.open('', '_blank');
      if (!w) { alert('\u0420\u0430\u0437\u0440\u0435\u0448\u0438\u0442\u0435 \u0432\u0441\u043f\u043b\u044b\u0432\u0430\u044e\u0449\u0438\u0435 \u043e\u043a\u043d\u0430'); return; }
      var doc = '<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8"><title>' + esc(title) + '</title><style>' + PRINT_CSS + '</style></head><body class="print-body"><div class="print-doc">' + bodyHtml + '</div><scr'+'ipt>window.addEventListener("load",function(){setTimeout(function(){try{window.print();}catch(e){}},500);});</scr'+'ipt></body></html>';
      w.document.open(); w.document.write(doc); w.document.close();
      return;
    }
    var container = document.createElement('div');
    container.className = 'print-doc';
    container.style.cssText = 'position:absolute;left:-99999px;top:0;width:210mm;background:#fff;padding:0;font-family:"Times New Roman",Times,serif;color:#000;font-size:12pt;line-height:1.4';
    container.innerHTML = bodyHtml;
    document.body.appendChild(container);
    var styleEl = document.createElement('style');
    styleEl.textContent = PRINT_CSS;
    document.head.appendChild(styleEl);
    var safeTitle = (title || 'document').replace(/[^A-Za-z0-9_\-\u0400-\u04FF ]+/g, '_').trim() || 'document';
    var opt = {
      margin: [10, 10, 10, 10],
      filename: safeTitle + '.pdf',
      image: { type: 'jpeg', quality: 0.95 },
      html2canvas: { scale: 2, useCORS: true, letterRendering: true, logging: false, backgroundColor: '#ffffff' },
      jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' },
      pagebreak: { mode: ['css', 'legacy'] }
    };
    html2pdf().set(opt).from(container).save().then(function(){
      if (container.parentNode) container.parentNode.removeChild(container);
      if (styleEl.parentNode) styleEl.parentNode.removeChild(styleEl);
    }).catch(function(err){
      console.error('PDF error', err);
      alert('\u041e\u0448\u0438\u0431\u043a\u0430 PDF: ' + (err && err.message ? err.message : err));
      if (container.parentNode) container.parentNode.removeChild(container);
      if (styleEl.parentNode) styleEl.parentNode.removeChild(styleEl);
    });
  });
}'''


def is_applied(src):
    return '_loadHtml2Pdf' in src and 'html2pdf().set' in src


def _find_func(src):
    marker = 'function openPrintWindow(bodyHtml, title){'
    start = src.find(marker)
    if start < 0:
        return None
    depth = 0
    i = start
    seen_open = False
    while i < len(src):
        c = src[i]
        if c == '{':
            depth += 1
            seen_open = True
        elif c == '}':
            depth -= 1
            if seen_open and depth == 0:
                return (start, i + 1)
        i += 1
    return None


def apply(src):
    if is_applied(src):
        return src

    pos = _find_func(src)
    if not pos:
        raise Exception("anchor not found: openPrintWindow function")

    start, end = pos
    src = src[:start] + NEW_FUNC + src[end:]
    return src
