# -*- coding: utf-8 -*-
# Fix: import_task alias + emoji fix in import buttons.

PATCH_NAME = "import_fix"
PATCH_DESCRIPTION = "Fix import_task action name + button text"


# Python: add alias so old button works
OLD_ACT = '''            if action == "import_preview":
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
'''

NEW_ACT = '''            if action == "import_task" or action == "import_preview":
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
'''


# JS fixes: replace broken emoji in button text
OLD_TEXT1 = '''btn.textContent = '\\U0001f50d \\u0420\\u0430\\u0437\\u043e\\u0431\\u0440\\u0430\\u0442\\u044c';'''
NEW_TEXT1 = '''btn.textContent = '\\u0420\\u0430\\u0437\\u043e\\u0431\\u0440\\u0430\\u0442\\u044c';'''

OLD_TEXT2 = '''btn.textContent = '\\U0001f50d \\u0420\\u0430\\u0437\\u043e\\u0431\\u0440\\u0430\\u0442\\u044c \\u0438 \\u0441\\u043e\\u0445\\u0440\\u0430\\u043d\\u0438\\u0442\\u044c';'''
NEW_TEXT2 = '''btn.textContent = '\\u0420\\u0430\\u0437\\u043e\\u0431\\u0440\\u0430\\u0442\\u044c \\u0438 \\u0441\\u043e\\u0445\\u0440\\u0430\\u043d\\u0438\\u0442\\u044c';'''

# HTML button fixes
OLD_HTML1 = 'onclick="importTask()">\U0001f50d'
NEW_HTML1 = 'onclick="importPreviewStart()">'

OLD_HTML2 = 'onclick="importPreviewStart()">\U0001f50d \u0420\u0430\u0437\u043e\u0431\u0440\u0430\u0442\u044c'
NEW_HTML2 = 'onclick="importPreviewStart()">\u0420\u0430\u0437\u043e\u0431\u0440\u0430\u0442\u044c'


def is_applied(src):
    return 'action == "import_task" or action == "import_preview"' in src


def apply(src):
    if is_applied(src):
        return src

    if OLD_ACT not in src:
        raise Exception("anchor not found: import_preview action")
    src = src.replace(OLD_ACT, NEW_ACT, 1)

    # Try to fix emoji in JS button text
    src = src.replace(OLD_TEXT1, NEW_TEXT1)
    src = src.replace(OLD_TEXT2, NEW_TEXT2)

    # Try to fix emoji in HTML button
    src = src.replace(OLD_HTML1, NEW_HTML1)
    src = src.replace(OLD_HTML2, NEW_HTML2)

    return src
