# -*- coding: utf-8 -*-
# Patch: admin import from pasted text via LLM.
# Instructions are hardcoded from EGE 2027 demo. LLM does not touch them.

PATCH_NAME = "admin_import"
PATCH_DESCRIPTION = "Admin import: paste task data + key, LLM structures it, instructions hardcoded"


PY_NEW_CODE = r'''
TASK_INSTRUCTIONS = {
    "1": "\u0412\u044b \u0443\u0441\u043b\u044b\u0448\u0438\u0442\u0435 6 \u0432\u044b\u0441\u043a\u0430\u0437\u044b\u0432\u0430\u043d\u0438\u0439. \u0423\u0441\u0442\u0430\u043d\u043e\u0432\u0438\u0442\u0435 \u0441\u043e\u043e\u0442\u0432\u0435\u0442\u0441\u0442\u0432\u0438\u0435 \u043c\u0435\u0436\u0434\u0443 \u0432\u044b\u0441\u043a\u0430\u0437\u044b\u0432\u0430\u043d\u0438\u044f\u043c\u0438 \u043a\u0430\u0436\u0434\u043e\u0433\u043e \u0433\u043e\u0432\u043e\u0440\u044f\u0449\u0435\u0433\u043e \u0410\u2013F \u0438 \u0443\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043d\u0438\u044f\u043c\u0438, \u0434\u0430\u043d\u043d\u044b\u043c\u0438 \u0432 \u0441\u043f\u0438\u0441\u043a\u0435 1\u20137. \u0418\u0441\u043f\u043e\u043b\u044c\u0437\u0443\u0439\u0442\u0435 \u043a\u0430\u0436\u0434\u043e\u0435 \u0443\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043d\u0438\u0435, \u043e\u0431\u043e\u0437\u043d\u0430\u0447\u0435\u043d\u043d\u043e\u0435 \u0441\u043e\u043e\u0442\u0432\u0435\u0442\u0441\u0442\u0432\u0443\u044e\u0449\u0435\u0439 \u0446\u0438\u0444\u0440\u043e\u0439, \u0442\u043e\u043b\u044c\u043a\u043e \u043e\u0434\u0438\u043d \u0440\u0430\u0437. \u0412 \u0437\u0430\u0434\u0430\u043d\u0438\u0438 \u0435\u0441\u0442\u044c \u043e\u0434\u043d\u043e \u043b\u0438\u0448\u043d\u0435\u0435 \u0443\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043d\u0438\u0435. \u0412\u044b \u0443\u0441\u043b\u044b\u0448\u0438\u0442\u0435 \u0437\u0430\u043f\u0438\u0441\u044c \u0434\u0432\u0430\u0436\u0434\u044b. \u0417\u0430\u043d\u0435\u0441\u0438\u0442\u0435 \u0441\u0432\u043e\u0438 \u043e\u0442\u0432\u0435\u0442\u044b \u0432 \u0442\u0430\u0431\u043b\u0438\u0446\u0443.",
    "2": "\u0412\u044b \u0443\u0441\u043b\u044b\u0448\u0438\u0442\u0435 \u0434\u0438\u0430\u043b\u043e\u0433. \u041e\u043f\u0440\u0435\u0434\u0435\u043b\u0438\u0442\u0435, \u043a\u0430\u043a\u0438\u0435 \u0438\u0437 \u043f\u0440\u0438\u0432\u0435\u0434\u0451\u043d\u043d\u044b\u0445 \u0443\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043d\u0438\u0439 \u0410\u2013G \u0441\u043e\u043e\u0442\u0432\u0435\u0442\u0441\u0442\u0432\u0443\u044e\u0442 \u0441\u043e\u0434\u0435\u0440\u0436\u0430\u043d\u0438\u044e \u0442\u0435\u043a\u0441\u0442\u0430 (1 \u2013 True), \u043a\u0430\u043a\u0438\u0435 \u043d\u0435 \u0441\u043e\u043e\u0442\u0432\u0435\u0442\u0441\u0442\u0432\u0443\u044e\u0442 (2 \u2013 False) \u0438 \u043e \u0447\u0451\u043c \u0432 \u0442\u0435\u043a\u0441\u0442\u0435 \u043d\u0435 \u0441\u043a\u0430\u0437\u0430\u043d\u043e, \u0442\u043e \u0435\u0441\u0442\u044c \u043d\u0430 \u043e\u0441\u043d\u043e\u0432\u0430\u043d\u0438\u0438 \u0442\u0435\u043a\u0441\u0442\u0430 \u043d\u0435\u043b\u044c\u0437\u044f \u0434\u0430\u0442\u044c \u043d\u0438 \u043f\u043e\u043b\u043e\u0436\u0438\u0442\u0435\u043b\u044c\u043d\u043e\u0433\u043e, \u043d\u0438 \u043e\u0442\u0440\u0438\u0446\u0430\u0442\u0435\u043b\u044c\u043d\u043e\u0433\u043e \u043e\u0442\u0432\u0435\u0442\u0430 (3 \u2013 Not stated). \u0417\u0430\u043d\u0435\u0441\u0438\u0442\u0435 \u043d\u043e\u043c\u0435\u0440 \u0432\u044b\u0431\u0440\u0430\u043d\u043d\u043e\u0433\u043e \u0412\u0430\u043c\u0438 \u0432\u0430\u0440\u0438\u0430\u043d\u0442\u0430 \u043e\u0442\u0432\u0435\u0442\u0430 \u0432 \u0442\u0430\u0431\u043b\u0438\u0446\u0443. \u0412\u044b \u0443\u0441\u043b\u044b\u0448\u0438\u0442\u0435 \u0437\u0430\u043f\u0438\u0441\u044c \u0434\u0432\u0430\u0436\u0434\u044b.",
    "3-9": "\u0412\u044b \u0443\u0441\u043b\u044b\u0448\u0438\u0442\u0435 \u0438\u043d\u0442\u0435\u0440\u0432\u044c\u044e. \u0412 \u0437\u0430\u0434\u0430\u043d\u0438\u044f\u0445 3\u20139 \u0437\u0430\u043f\u0438\u0448\u0438\u0442\u0435 \u0432 \u043f\u043e\u043b\u0435 \u043e\u0442\u0432\u0435\u0442\u0430 \u0446\u0438\u0444\u0440\u0443 1, 2 \u0438\u043b\u0438 3, \u0441\u043e\u043e\u0442\u0432\u0435\u0442\u0441\u0442\u0432\u0443\u044e\u0449\u0443\u044e \u0432\u044b\u0431\u0440\u0430\u043d\u043d\u043e\u043c\u0443 \u0412\u0430\u043c\u0438 \u0432\u0430\u0440\u0438\u0430\u043d\u0442\u0443 \u043e\u0442\u0432\u0435\u0442\u0430. \u0412\u044b \u0443\u0441\u043b\u044b\u0448\u0438\u0442\u0435 \u0437\u0430\u043f\u0438\u0441\u044c \u0434\u0432\u0430\u0436\u0434\u044b.",
    "10": "\u0423\u0441\u0442\u0430\u043d\u043e\u0432\u0438\u0442\u0435 \u0441\u043e\u043e\u0442\u0432\u0435\u0442\u0441\u0442\u0432\u0438\u0435 \u043c\u0435\u0436\u0434\u0443 \u0442\u0435\u043a\u0441\u0442\u0430\u043c\u0438 A\u2013G \u0438 \u0437\u0430\u0433\u043e\u043b\u043e\u0432\u043a\u0430\u043c\u0438 1\u20138. \u0417\u0430\u043d\u0435\u0441\u0438\u0442\u0435 \u0441\u0432\u043e\u0438 \u043e\u0442\u0432\u0435\u0442\u044b \u0432 \u0442\u0430\u0431\u043b\u0438\u0446\u0443. \u0418\u0441\u043f\u043e\u043b\u044c\u0437\u0443\u0439\u0442\u0435 \u043a\u0430\u0436\u0434\u0443\u044e \u0446\u0438\u0444\u0440\u0443 \u0442\u043e\u043b\u044c\u043a\u043e \u043e\u0434\u0438\u043d \u0440\u0430\u0437. \u0412 \u0437\u0430\u0434\u0430\u043d\u0438\u0438 \u043e\u0434\u0438\u043d \u0437\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a \u043b\u0438\u0448\u043d\u0438\u0439.",
    "11": "\u041f\u0440\u043e\u0447\u0438\u0442\u0430\u0439\u0442\u0435 \u0442\u0435\u043a\u0441\u0442 \u0438 \u0437\u0430\u043f\u043e\u043b\u043d\u0438\u0442\u0435 \u043f\u0440\u043e\u043f\u0443\u0441\u043a\u0438 A\u2013F \u0447\u0430\u0441\u0442\u044f\u043c\u0438 \u043f\u0440\u0435\u0434\u043b\u043e\u0436\u0435\u043d\u0438\u0439, \u043e\u0431\u043e\u0437\u043d\u0430\u0447\u0435\u043d\u043d\u044b\u043c\u0438 \u0446\u0438\u0444\u0440\u0430\u043c\u0438 1\u20137. \u041e\u0434\u043d\u0430 \u0438\u0437 \u0447\u0430\u0441\u0442\u0435\u0439 \u0432 \u0441\u043f\u0438\u0441\u043a\u0435 1\u20137 \u043b\u0438\u0448\u043d\u044f\u044f. \u0417\u0430\u043d\u0435\u0441\u0438\u0442\u0435 \u0446\u0438\u0444\u0440\u044b, \u043e\u0431\u043e\u0437\u043d\u0430\u0447\u0430\u044e\u0449\u0438\u0435 \u0441\u043e\u043e\u0442\u0432\u0435\u0442\u0441\u0442\u0432\u0443\u044e\u0449\u0438\u0435 \u0447\u0430\u0441\u0442\u0438 \u043f\u0440\u0435\u0434\u043b\u043e\u0436\u0435\u043d\u0438\u0439, \u0432 \u0442\u0430\u0431\u043b\u0438\u0446\u0443.",
    "12-18": "\u041f\u0440\u043e\u0447\u0438\u0442\u0430\u0439\u0442\u0435 \u0442\u0435\u043a\u0441\u0442 \u0438 \u0432\u044b\u043f\u043e\u043b\u043d\u0438\u0442\u0435 \u0437\u0430\u0434\u0430\u043d\u0438\u044f 12\u201318. \u0412 \u043a\u0430\u0436\u0434\u043e\u043c \u0437\u0430\u0434\u0430\u043d\u0438\u0438 \u0437\u0430\u043f\u0438\u0448\u0438\u0442\u0435 \u0432 \u043f\u043e\u043b\u0435 \u043e\u0442\u0432\u0435\u0442\u0430 \u0446\u0438\u0444\u0440\u0443 1, 2, 3 \u0438\u043b\u0438 4, \u0441\u043e\u043e\u0442\u0432\u0435\u0442\u0441\u0442\u0432\u0443\u044e\u0449\u0443\u044e \u0432\u044b\u0431\u0440\u0430\u043d\u043d\u043e\u043c\u0443 \u0412\u0430\u043c\u0438 \u0432\u0430\u0440\u0438\u0430\u043d\u0442\u0443 \u043e\u0442\u0432\u0435\u0442\u0430.",
    "19-24": "\u041f\u0440\u043e\u0447\u0438\u0442\u0430\u0439\u0442\u0435 \u043f\u0440\u0438\u0432\u0435\u0434\u0451\u043d\u043d\u044b\u0439 \u043d\u0438\u0436\u0435 \u0442\u0435\u043a\u0441\u0442 / \u043f\u0440\u0438\u0432\u0435\u0434\u0451\u043d\u043d\u044b\u0435 \u043d\u0438\u0436\u0435 \u0442\u0435\u043a\u0441\u0442\u044b. \u041f\u0440\u0435\u043e\u0431\u0440\u0430\u0437\u0443\u0439\u0442\u0435, \u0435\u0441\u043b\u0438 \u043d\u0435\u043e\u0431\u0445\u043e\u0434\u0438\u043c\u043e, \u0441\u043b\u043e\u0432\u0430, \u043d\u0430\u043f\u0435\u0447\u0430\u0442\u0430\u043d\u043d\u044b\u0435 \u0437\u0430\u0433\u043b\u0430\u0432\u043d\u044b\u043c\u0438 \u0431\u0443\u043a\u0432\u0430\u043c\u0438 \u0432 \u043a\u043e\u043d\u0446\u0435 \u0441\u0442\u0440\u043e\u043a, \u043e\u0431\u043e\u0437\u043d\u0430\u0447\u0435\u043d\u043d\u044b\u0445 \u043d\u043e\u043c\u0435\u0440\u0430\u043c\u0438 19\u201324, \u0442\u0430\u043a, \u0447\u0442\u043e\u0431\u044b \u043e\u043d\u0438 \u0433\u0440\u0430\u043c\u043c\u0430\u0442\u0438\u0447\u0435\u0441\u043a\u0438 \u0441\u043e\u043e\u0442\u0432\u0435\u0442\u0441\u0442\u0432\u043e\u0432\u0430\u043b\u0438 \u0441\u043e\u0434\u0435\u0440\u0436\u0430\u043d\u0438\u044e \u0442\u0435\u043a\u0441\u0442\u043e\u0432.",
    "25-29": "\u041f\u0440\u043e\u0447\u0438\u0442\u0430\u0439\u0442\u0435 \u043f\u0440\u0438\u0432\u0435\u0434\u0451\u043d\u043d\u044b\u0439 \u043d\u0438\u0436\u0435 \u0442\u0435\u043a\u0441\u0442. \u041e\u0431\u0440\u0430\u0437\u0443\u0439\u0442\u0435 \u043e\u0442 \u0441\u043b\u043e\u0432, \u043d\u0430\u043f\u0435\u0447\u0430\u0442\u0430\u043d\u043d\u044b\u0445 \u0437\u0430\u0433\u043b\u0430\u0432\u043d\u044b\u043c\u0438 \u0431\u0443\u043a\u0432\u0430\u043c\u0438 \u0432 \u043a\u043e\u043d\u0446\u0435 \u0441\u0442\u0440\u043e\u043a, \u043e\u0431\u043e\u0437\u043d\u0430\u0447\u0435\u043d\u043d\u044b\u0445 \u043d\u043e\u043c\u0435\u0440\u0430\u043c\u0438 25\u201329, \u043e\u0434\u043d\u043e\u043a\u043e\u0440\u0435\u043d\u043d\u044b\u0435 \u0441\u043b\u043e\u0432\u0430.",
    "30-36": "\u041f\u0440\u043e\u0447\u0438\u0442\u0430\u0439\u0442\u0435 \u0442\u0435\u043a\u0441\u0442 \u0441 \u043f\u0440\u043e\u043f\u0443\u0441\u043a\u0430\u043c\u0438, \u043e\u0431\u043e\u0437\u043d\u0430\u0447\u0435\u043d\u043d\u044b\u043c\u0438 \u043d\u043e\u043c\u0435\u0440\u0430\u043c\u0438 30\u201336. \u0417\u0430\u043f\u0438\u0448\u0438\u0442\u0435 \u0432 \u043f\u043e\u043b\u0435 \u043e\u0442\u0432\u0435\u0442\u0430 \u0446\u0438\u0444\u0440\u0443 1, 2, 3 \u0438\u043b\u0438 4.",
}


IMPORT_PROMPT = """You parse Russian EGE English exam tasks. Return ONLY valid JSON. Do not invent content.

Task type: {task_type}

Expected JSON structure:
{structure}

Pasted task data (may include Russian instruction, task body, table, chart data):
{task_text}

Audio script with speaker genders (Name (M): text or Name (F): text):
{audio_text}

Answer key:
{key_text}

Rules:
1. Extract ALL content from the pasted task into the JSON structure. Do NOT fill the "instruction" field (it is added automatically).
2. English content stays English, Russian content stays Russian.
3. Task 1 scripts: [{"speaker": "A".."F", "text": "..."}]. No gender needed.
4. Task 2 dialogue_script and Task 3-9 interview_script: each entry {"speaker": "Name", "gender": "M" or "F", "text": "..."}.
   Gender from (M)/(F)/(m)/(f) mark after speaker name. If missing - guess by common name (Ben, Mike, Sophie, Anna etc.).
5. Task 38.1/38.2 survey_data.options from the pasted table/chart.
   Each option = {"option": "text", "percent": number_without_percent_sign}.
   task_text stays as the full instruction line + question + plan.
   plan = array of plan step strings from "Use the following plan:" section.
6. Task 37: task_text = full email task (From/To/Subject + body + Write an email...).
7. Tasks 19-29: items[].source_word = base word in CAPS.
   text must contain __19__ style markers where the gap is.
8. answer_key: numbers for 1-18 and 30-36; strings for 19-29. Skip if missing.
9. Never invent. If a field is impossible to extract, omit it.

Return ONLY JSON. No text outside."""


def _import_structure(task_type):
    table = {
        "1": '{"statements": [{"number": 1, "text": "..."}], "scripts": [{"speaker": "A", "text": "..."}], "answer_key": {"A": 3}, "extra_statement": 7}',
        "2": '{"statements": [{"letter": "A", "text": "..."}], "dialogue_script": [{"speaker": "Ben", "gender": "M", "text": "..."}], "answer_key": {"A": 1}}',
        "3-9": '{"questions": [{"number": 3, "question": "...", "options": {"1": "...", "2": "...", "3": "..."}}], "interview_script": [{"speaker": "Mike", "gender": "M", "text": "..."}], "answer_key": {"3": 1}}',
        "10": '{"headings": [{"number": 1, "text": "..."}], "texts": [{"letter": "A", "text": "..."}], "answer_key": {"A": 3}, "extra_heading": 8}',
        "11": '{"title": "...", "text": "Text with __1__ markers", "fragments": [{"number": 1, "text": "..."}], "answer_key": {"A": 3}, "extra_fragment": 7}',
        "12-18": '{"title": "...", "text": "Full reading text", "questions": [{"number": 12, "question": "...", "options": {"1": "...", "2": "...", "3": "...", "4": "..."}}], "answer_key": {"12": 1}}',
        "19-24": '{"title": "...", "text": "Full text with __19__ markers", "items": [{"number": 19, "source_word": "SITUATE"}], "answer_key": {"19": "situated"}}',
        "25-29": '{"title": "...", "text": "Full text", "items": [{"number": 25, "source_word": "CERTAIN"}], "answer_key": {"25": "certainly"}}',
        "30-36": '{"title": "...", "text": "Text with (30) ____ markers", "items": [{"number": 30, "options": {"1": "...", "2": "...", "3": "...", "4": "..."}}], "answer_key": {"30": 3}}',
        "37": '{"task_text": "Full email task text with From/To/Subject and instructions"}',
        "38.1": '{"task_text": "Full task text", "survey_data": {"question": "...", "options": [{"option": "...", "percent": 48}]}, "plan": ["make an opening statement...", "select and report 2-3 facts...", "make 1-2 comparisons...", "outline a problem...", "conclude..."]}',
        "38.2": '{"task_text": "Full task text", "survey_data": {"question": "...", "options": [{"option": "...", "percent": 30}]}, "plan": ["make an opening statement...", "select and report 2-3 facts...", "make 1-2 comparisons...", "outline a problem...", "conclude..."]}',
    }
    return table.get(task_type, "{}")


def admin_import_task(task_type, topic_letter, task_text, audio_text, key_text):
    structure = _import_structure(task_type)
    prompt = IMPORT_PROMPT
    prompt = prompt.replace("{task_type}", str(task_type))
    prompt = prompt.replace("{structure}", structure)
    prompt = prompt.replace("{task_text}", task_text or "(empty)")
    prompt = prompt.replace("{audio_text}", audio_text or "(empty)")
    prompt = prompt.replace("{key_text}", key_text or "(empty)")
    r = call_llm(prompt, retries=1)
    if "error" in r:
        return {"error": "LLM: " + str(r["error"])}
    if not isinstance(r, dict):
        return {"error": "LLM returned non-object"}
    if "task_data" in r and isinstance(r["task_data"], dict):
        task_data = r["task_data"]
    else:
        task_data = r
    if not task_data:
        return {"error": "Empty task_data from LLM"}
    task_data["instruction"] = TASK_INSTRUCTIONS.get(str(task_type), "")
    if "_bank_save_generated" not in globals():
        return {"error": "patch variant_builder required"}
    code = _bank_save_generated(task_type, topic_letter, task_data)
    if not code:
        return {"error": "Failed to save to bank"}
    return {"ok": True, "code": code, "task_data": task_data}


'''


PY_ANCHOR = 'def handler(event, context):'
HANDLER_ANCHOR = '            if action == "variant_generate":'

HANDLER_INSERT = '''            if action == "import_task":
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


TAB_ANCHOR = 'data-tab="ratelimit"'
TAB_REPLACE = 'data-tab="import" onclick="switchTab(\'import\')">\U0001f4e5 \u0418\u043c\u043f\u043e\u0440\u0442</button>\n  <button class="tab" data-tab="ratelimit"'


PANE_ANCHOR = '<div class="tab-pane" id="pane-ratelimit">'

PANE_HTML = '''<div class="tab-pane" id="pane-import">
  <div class="panel">
    <h3>\U0001f4e5 \u0418\u043c\u043f\u043e\u0440\u0442 \u0437\u0430\u0434\u0430\u043d\u0438\u044f</h3>
    <p class="hint">\u0424\u043e\u0440\u043c\u0443\u043b\u0438\u0440\u043e\u0432\u043a\u0430 \u0437\u0430\u0434\u0430\u043d\u0438\u044f \u043f\u043e\u0434\u0441\u0442\u0430\u0432\u0438\u0442\u0441\u044f \u0430\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0447\u0435\u0441\u043a\u0438. \u0412\u0441\u0442\u0430\u0432\u044c \u0442\u043e\u043b\u044c\u043a\u043e \u0434\u0430\u043d\u043d\u044b\u0435 \u0438\u0437 PDF.</p>
    <div class="row">
      <div class="f"><label>\u0422\u0438\u043f</label>
        <select id="impType" onchange="impOnTypeChange()">
          <option value="1">1</option>
          <option value="2">2</option>
          <option value="3-9">3\u20139</option>
          <option value="10">10</option>
          <option value="11">11</option>
          <option value="12-18">12\u201318</option>
          <option value="19-24">19\u201324</option>
          <option value="25-29">25\u201329</option>
          <option value="30-36">30\u201336</option>
          <option value="37">37</option>
          <option value="38.1">38.1</option>
          <option value="38.2">38.2</option>
        </select>
      </div>
      <div class="f"><label>\u0422\u0435\u043c\u0430</label>
        <select id="impTopic">
          <option value="\u0410">\u0410</option><option value="\u0411">\u0411</option>
          <option value="\u0412">\u0412</option><option value="\u0413">\u0413</option>
          <option value="\u0414">\u0414</option><option value="\u0415">\u0415</option>
          <option value="\u0416">\u0416</option><option value="\u0417">\u0417</option>
          <option value="\u0418">\u0418</option><option value="\u041a">\u041a</option>
          <option value="\u041b">\u041b</option><option value="\u041c">\u041c</option>
          <option value="\u041d">\u041d</option><option value="\u041e">\u041e</option>
          <option value="\u041f">\u041f</option><option value="\u0420">\u0420</option>
          <option value="\u0421">\u0421</option>
        </select>
      </div>
    </div>
    <div class="f"><label>\u0414\u0430\u043d\u043d\u044b\u0435 \u0437\u0430\u0434\u0430\u043d\u0438\u044f (\u0432\u0441\u0442\u0430\u0432\u0438\u0442\u044c \u0438\u0437 PDF)</label>
      <textarea id="impText" style="min-height:220px"></textarea>
    </div>
    <div class="f" id="impAudioWrap" style="display:none">
      <label>\u0422\u0435\u043a\u0441\u0442 \u0434\u043b\u044f \u043e\u0437\u0432\u0443\u0447\u043a\u0438 (Name (M): / Name (F): / Speaker A:)</label>
      <textarea id="impAudio" style="min-height:180px"></textarea>
    </div>
    <div class="f"><label>\u041a\u043b\u044e\u0447 (\u043e\u0442\u0432\u0435\u0442\u044b)</label>
      <textarea id="impKey" style="min-height:70px"></textarea>
    </div>
    <button class="btn btn-ok" id="impBtn" onclick="importTask()">\U0001f50d \u0420\u0430\u0437\u043e\u0431\u0440\u0430\u0442\u044c \u0438 \u0441\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c</button>
    <div id="impRes" style="margin-top:12px"></div>
  </div>
</div>

'''


JS_ANCHOR = 'loadPending();\ninitVariantsTab();'

JS_CODE = '''function impOnTypeChange() {
  var t = document.getElementById('impType').value;
  var wrap = document.getElementById('impAudioWrap');
  if (wrap) wrap.style.display = (t === '1' || t === '2' || t === '3-9') ? 'block' : 'none';
}
async function importTask() {
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
  try {
    var d = await api({action:'import_task', task_type:t, topic_letter:topic, task_text:txt, audio_text:aud, key_text:key});
    if (d.error) {
      res.className = 'res err';
      res.textContent = '\\u041e\\u0448\\u0438\\u0431\\u043a\\u0430: ' + d.error;
      btn.disabled = false;
      btn.textContent = '\\U0001f50d \\u0420\\u0430\\u0437\\u043e\\u0431\\u0440\\u0430\\u0442\\u044c \\u0438 \\u0441\\u043e\\u0445\\u0440\\u0430\\u043d\\u0438\\u0442\\u044c';
      return;
    }
    res.className = 'res ok';
    res.innerHTML = '\\u2705 \\u0421\\u043e\\u0445\\u0440\\u0430\\u043d\\u0435\\u043d\\u043e! \\u041a\\u043e\\u0434: <code>' + esc(d.code) + '</code>';
    document.getElementById('impText').value = '';
    document.getElementById('impAudio').value = '';
    document.getElementById('impKey').value = '';
  } catch(e) {
    res.className = 'res err';
    res.textContent = '\\u041e\\u0448\\u0438\\u0431\\u043a\\u0430: ' + e.message;
  } finally {
    btn.disabled = false;
    btn.textContent = '\\U0001f50d \\u0420\\u0430\\u0437\\u043e\\u0431\\u0440\\u0430\\u0442\\u044c \\u0438 \\u0441\\u043e\\u0445\\u0440\\u0430\\u043d\\u0438\\u0442\\u044c';
  }
}
'''


def is_applied(src):
    return "TASK_INSTRUCTIONS" in src and "pane-import" in src


def apply(src):
    if is_applied(src):
        return src

    if "def admin_import_task" not in src:
        if PY_ANCHOR not in src:
            raise Exception("anchor not found: def handler")
        src = src.replace(PY_ANCHOR, PY_NEW_CODE + "\n\n" + PY_ANCHOR, 1)
    else:
        # already had previous version; replace old block
        import re as _re
        old = _re.search(r"IMPORT_PROMPT = .*?\n\n\ndef handler", src, _re.DOTALL)
        if old:
            src = src[:old.start()] + PY_NEW_CODE + "\n\ndef handler" + src[old.end():]

    if '"import_task"' not in src:
        if HANDLER_ANCHOR not in src:
            raise Exception("anchor not found: variant_generate action")
        src = src.replace(HANDLER_ANCHOR, HANDLER_INSERT + HANDLER_ANCHOR, 1)

    if 'data-tab="import"' not in src:
        if TAB_ANCHOR not in src:
            raise Exception("anchor not found: ratelimit tab")
        src = src.replace(TAB_ANCHOR, TAB_REPLACE, 1)

    if 'id="pane-import"' not in src:
        if PANE_ANCHOR not in src:
            raise Exception("anchor not found: ratelimit pane")
        src = src.replace(PANE_ANCHOR, PANE_HTML + PANE_ANCHOR, 1)

    if "function impOnTypeChange" not in src:
        if JS_ANCHOR not in src:
            raise Exception("anchor not found: loadPending init")
        src = src.replace(JS_ANCHOR, JS_CODE + "\n" + JS_ANCHOR, 1)

    return src
