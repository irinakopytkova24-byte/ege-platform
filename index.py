import os
import json
import base64
import re
import random
import asyncio
import traceback
import time
import uuid
import hashlib
import requests

import boto3
from botocore.client import Config

from PROMPT_1_STATEMENTS import PROMPT_1_STATEMENTS
from PROMPT_1_MONOLOGUES import PROMPT_1_MONOLOGUES
from PROMPT_2_STATEMENTS import PROMPT_2_STATEMENTS
from PROMPT_2_DIALOGUE import PROMPT_2_DIALOGUE
from PROMPT_3_9_QUESTIONS import PROMPT_3_9_QUESTIONS
from PROMPT_3_9_SCRIPT import PROMPT_3_9_SCRIPT
from PROMPT_10_HEADERS import PROMPT_10_HEADERS
from PROMPT_10_TEXTS import PROMPT_10_TEXTS
from PROMPT_11_FRAGMENTS import PROMPT_11_FRAGMENTS
from PROMPT_11_TEXT import PROMPT_11_TEXT
from PROMPT_12_18_TEXT import PROMPT_12_18_TEXT
from PROMPT_12_18_QUESTION import PROMPT_12_18_QUESTIONS
from PROMPT_19_24_SCHEMA import PROMPT_19_24_SCHEMA
from PROMPT_19_24_TEXT import PROMPT_19_24_TEXT
from PROMPT_25_29_SCHEMA import PROMPT_25_29_SCHEMA
from PROMPT_25_29_TEXT import PROMPT_25_29_TEXT
from PROMPT_30_36_SCHEMA import PROMPT_30_36_SCHEMA
from PROMPT_30_36_TEXT import PROMPT_30_36_TEXT
from PROMPT_37_STIMULUS_SCHEMA import PROMPT_37_STIMULUS_SCHEMA
from PROMPT_37_EMAIL_GENERATION import PROMPT_37_EMAIL_GENERATION
from PROMPT_38_1_DATA_SCHEMA import PROMPT_38_1_DATA_SCHEMA
from PROMPT_38_1_TASK_GENERATION import PROMPT_38_1_TASK_GENERATION
from PROMPT_38_2_CHART_SCHEMA import PROMPT_38_2_CHART_SCHEMA
from PROMPT_38_2_CHART_GENERATION import PROMPT_38_2_CHART_GENERATION


PROXYAPI_URL = "https://api.proxyapi.ru/v1/chat/completions"
API_KEY      = os.getenv("PROXYAPI_KEY", "")
MODEL        = os.getenv("PROXYAPI_MODEL", "qwen/qwen3.6-plus")
MAX_TOKENS   = int(os.getenv("PROXYAPI_MAX_TOKENS", "20000"))
TEMPERATURE  = float(os.getenv("PROXYAPI_TEMPERATURE", "0.3"))

STORAGE_KEY_ID = os.getenv("STORAGE_KEY_ID", "")
STORAGE_SECRET = os.getenv("STORAGE_SECRET", "")
BUCKET_NAME    = os.getenv("STORAGE_BUCKET", "ege-tasks-bank")

ADMIN_SECRET = "k7Rq2Mn9XzT4wPv8LbJf6Hs3AeDy"

RATELIMIT_ENABLED      = True
RATELIMIT_MAX          = 5
RATELIMIT_SALT         = os.getenv("RATELIMIT_SALT", "ege-kosmodrom-2027-change-me")
RATELIMIT_IP_WHITELIST = set(os.getenv("RATELIMIT_IP_WHITELIST", "").split(",")) - {""}
RATELIMIT_CID_WHITELIST = set(os.getenv("RATELIMIT_CID_WHITELIST", "").split(",")) - {""}
RATELIMIT_AUDIT_LIMIT  = 200

TOPIC_MAP = {
    "А": "Повседневная жизнь семьи. Межличностные отношения",
    "Б": "Внешность и характеристика человека",
    "В": "Здоровый образ жизни и забота о здоровье",
    "Г": "Школьное образование, школьная жизнь",
    "Д": "Современный мир профессий",
    "Е": "Место иностранного языка в жизни",
    "Ж": "Молодёжь в современном обществе",
    "З": "Покупки: одежда, обувь, продукты",
    "И": "Роль спорта в современной жизни",
    "К": "Деловое общение",
    "Л": "Туризм. Виды отдыха. Экотуризм",
    "М": "Вселенная и человек. Природа. Экология",
    "Н": "Средства массовой информации",
    "О": "Технический прогресс. Интернет-безопасность",
    "П": "Проблемы современной цивилизации",
    "Р": "Родная страна и страны изучаемого языка",
    "С": "Выдающиеся люди родной страны и мира",
}

MONOLOGUE_VOICES = {
    "A": "en-GB-RyanNeural",  "B": "en-GB-SoniaNeural",
    "C": "en-GB-ThomasNeural", "D": "en-GB-LibbyNeural",
    "E": "en-GB-RyanNeural",  "F": "en-GB-SoniaNeural",
}
VOICE_M = "en-GB-RyanNeural"
VOICE_M2 = "en-GB-ThomasNeural"
VOICE_F = "en-GB-SoniaNeural"
VOICE_F2 = "en-GB-LibbyNeural"
VOICE_ANNOUNCER = "en-GB-ThomasNeural"
VOICE_RU_FEMALE = "ru-RU-SvetlanaNeural"

EN_NOW_START   = "Now we are ready to start."
EN_WAIT        = "You have 15 seconds to complete the task."
EN_HEAR_AGAIN  = "Now you will hear the text again."
EN_END_ALL     = "This is the end of the task. You now have 15 seconds to check your answers."

INTRO_RU = {
    "1": ("Сейчас вы будете выполнять задание один. Вы услышите шесть высказываний. "
          "Установите соответствие между высказываниями каждого говорящего, "
          "обозначенного буквами эй-эф, и утверждениями, данными в списке один – семь. "
          "Используйте каждое утверждение, обозначенное соответствующей цифрой, "
          "только один раз. В задании есть одно лишнее утверждение. "
          "Вы услышите запись дважды. Занесите свои ответы в таблицу. "
          "У вас есть двадцать секунд, чтобы ознакомиться с заданием."),
    "2": ("Сейчас вы будете выполнять задание два. Вы услышите диалог. "
          "Определите, какие из приведённых утверждений, обозначенных буквами эй-джи, "
          "соответствуют содержанию текста, это цифра один, тру; "
          "какие не соответствуют, это цифра два, фолс; "
          "и о чём в тексте не сказано, это цифра три, нот стейтед. "
          "Занесите номер выбранного вами варианта ответа в таблицу. "
          "Вы услышите запись дважды. У вас есть двадцать секунд, чтобы ознакомиться с заданием."),
    "3-9": ("Сейчас вы будете выполнять задания три – девять. Вы услышите интервью. "
            "В заданиях три – девять запишите в поле ответа цифру один, два или три, "
            "соответствующую выбранному вами варианту ответа. "
            "Вы услышите запись дважды. У вас есть пятьдесят секунд, чтобы ознакомиться с заданием."),
}
PAUSE_AFTER_INTRO    = {"1": 20, "2": 20, "3-9": 50}
PAUSE_BETWEEN_BLOCKS = 0.3
PAUSE_BEFORE_REPLAY  = 15

MALE_NAMES = {"ben","tom","mark","harry","daniel","alex","michael","john","peter",
    "ethan","oliver","liam","noah","james","william","lucas","jack","ryan","sam",
    "charlie","mike","david","robert","richard","thomas","george","presenter",
    "interviewer","host","mr","sir"}
FEMALE_NAMES = {"sophie","emma","kate","emily","sarah","olivia","chloe","lily","anna",
    "mia","amelia","isabella","ava","ella","grace","zoe","charlotte","jessica",
    "lucy","hannah","mary","jane","alice","laura","helen","ms","mrs","miss"}
CRITERIA_37 = {
    "task_type": "37",
    "max_total": 6,
    "rule_k1_zero": True,
    "criteria": [
        {"code": "К1", "name": "Решение коммуникативной задачи", "max": 2, "levels": {
            2: "Задание выполнено полностью: содержание отражает все аспекты, указанные в задании "
               "(даны полные и точные ответы на все вопросы, заданы правильно 3 вопроса по указанной теме); "
               "стилевое оформление речи выбрано правильно с учётом цели высказывания и адресата; "
               "соблюдены принятые в языке нормы вежливости. Допускается 1 неполный или неточный аспект.",
            1: "Задание выполнено не полностью: содержание отражает не все аспекты, указанные в задании "
               "(все случаи, не указанные в оценивании на 2 балла и 0 баллов).",
            0: "Задание не выполнено: 3 и более аспекта содержания отсутствуют, ИЛИ 6 аспектов раскрыты "
               "неполно/неточно, ИЛИ 1 аспект не раскрыт и 4–5 раскрыты неполно/неточно, ИЛИ 2 аспекта "
               "не раскрыты и 2–4 раскрыты неполно/неточно, ИЛИ ответ не соответствует требуемому объёму.",
        }},
        {"code": "К2", "name": "Организация текста", "max": 2, "levels": {
            2: "Высказывание логично, средства логической связи использованы правильно, текст верно "
               "разделён на абзацы; структурное оформление текста соответствует нормам, принятым в стране "
               "изучаемого языка (допускается 1 ошибка в организации текста).",
            1: "Имеются 2–3 ошибки в организации текста.",
            0: "Имеются 4 и более ошибки в организации текста.",
        }},
        {"code": "К3", "name": "Языковое оформление текста", "max": 2, "levels": {
            2: "Используемый словарный запас и грамматические структуры соответствуют базовому уровню "
               "сложности задания; орфографические и пунктуационные ошибки практически отсутствуют "
               "(допускаются 1–2 лексико-грамматические ошибки, И/ИЛИ 1–2 орфографические и пунктуационные).",
            1: "Словарный запас и грамматические структуры не полностью соответствуют базовому уровню: "
               "3–4 лексико-грамматические ошибки, И/ИЛИ 3–4 орфографические и пунктуационные ошибки.",
            0: "Словарный запас и грамматические структуры не соответствуют базовому уровню: "
               "5 и более лексико-грамматических ошибок, И/ИЛИ 5 и более орфографических и пунктуационных.",
        }},
    ],
}

CRITERIA_38 = {
    "task_type": "38",
    "max_total": 14,
    "rule_k1_zero": True,
    "criteria": [
        {"code": "К1", "name": "Решение коммуникативной задачи", "max": 3, "levels": {
            3: "Задание выполнено полностью: содержание отражает все аспекты, указанные в задании; "
               "стилевое оформление речи выбрано правильно (допускается 1 неполный/неточный аспект "
               "и 1 нарушение нейтрального стиля).",
            2: "Задание выполнено в основном: 1 аспект не раскрыт (остальные раскрыты полно), ИЛИ "
               "1 аспект не раскрыт и 1 раскрыт неполно/неточно, ИЛИ 2–3 аспекта раскрыты неполно/неточно; "
               "стилевое оформление в основном правильно (допускаются 2–3 нарушения нейтрального стиля).",
            1: "Задание выполнено не полностью: 1 аспект не раскрыт и 2–3 раскрыты неполно/неточно, ИЛИ "
               "2 аспекта не раскрыты (остальные раскрыты полно), ИЛИ 2 аспекта содержания не раскрыты "
               "и 1 раскрыт неполно/неточно, ИЛИ 4–5 аспектов раскрыты неполно/неточно; имеются ошибки "
               "в стилевом оформлении речи (допускаются 4 нарушения нейтрального стиля).",
            0: "Задание не выполнено: все случаи, не указанные в оценивании на 1, 2 и 3 балла, ИЛИ ответ "
               "не соответствует требуемому объёму, ИЛИ более 30% ответа имеет непродуктивный характер "
               "(текстуально совпадает с опубликованным источником), ИЛИ предложенный план ответа "
               "полностью не соблюдается, И/ИЛИ отсутствует деление на абзацы.",
        }},
        {"code": "К2", "name": "Организация текста", "max": 3, "levels": {
            3: "Высказывание логично; структура текста соответствует предложенному плану; текст "
               "правильно разделён на абзацы; средства логической связи использованы правильно.",
            2: "Высказывание логично; структура соответствует плану; текст разделён на абзацы; средства "
               "логической связи использованы (допускаются 1–3 ошибки).",
            1: "В высказывании имеются 4–5 ошибок в организации текста, И/ИЛИ отсутствует вступление "
               "или заключение.",
            0: "В высказывании имеются 6 и более ошибок в организации текста, И/ИЛИ отсутствует "
               "вступление и заключение, И/ИЛИ предложенный план ответа полностью не соблюдается, "
               "И/ИЛИ отсутствует деление на абзацы.",
        }},
        {"code": "К3", "name": "Лексика", "max": 3, "levels": {
            3: "Используемый словарный запас соответствует высокому уровню сложности задания; "
               "практически нет нарушений в использовании лексики (допускается 1 лексическая ошибка).",
            2: "Словарный запас соответствует высокому уровню сложности задания, однако имеются "
               "2–3 лексические ошибки, И/ИЛИ словарный запас ограничен, но лексика использована правильно.",
            1: "Словарный запас не вполне соответствует высокому уровню сложности задания; "
               "в тексте имеются 4 лексические ошибки.",
            0: "Словарный запас не соответствует высокому уровню сложности задания; "
               "в тексте имеются 5 и более лексических ошибок.",
        }},
        {"code": "К4", "name": "Грамматика", "max": 3, "levels": {
            3: "Используемые грамматические средства соответствуют высокому уровню сложности задания; "
               "нарушений практически нет (допускаются 1–2 неповторяющиеся грамматические ошибки).",
            2: "Грамматические средства соответствуют высокому уровню сложности задания, однако "
               "в тексте имеются 3–4 грамматические ошибки.",
            1: "Грамматические средства не вполне соответствуют высокому уровню сложности задания; "
               "в тексте имеются 5–7 грамматических ошибок.",
            0: "Грамматические средства не соответствуют высокому уровню сложности задания; "
               "имеются 8 и более грамматических ошибок.",
        }},
        {"code": "К5", "name": "Орфография и пунктуация", "max": 2, "levels": {
            2: "Орфографические ошибки практически отсутствуют. Текст разделён на предложения "
               "с правильным пунктуационным оформлением (допускается 1 орфографическая И/ИЛИ "
               "1 пунктуационная ошибка).",
            1: "В тексте имеются 2–4 орфографические И/ИЛИ пунктуационные ошибки.",
            0: "В тексте имеются 5 и более орфографических И/ИЛИ пунктуационных ошибок.",
        }},
    ],
}

CRITERIA_BY_TYPE = {"37": CRITERIA_37, "38.1": CRITERIA_38, "38.2": CRITERIA_38}

# ============================================================
# РАЗБАЛЛОВКА ВАРИАНТА (ФИПИ)
# ============================================================
VARIANT_TASKS = ["1", "2", "3-9", "10", "11", "12-18",
                 "19-24", "25-29", "30-36", "37", "38.1", "38.2"]

VARIANT_SCORING = {
    "1":     {"max": 2,  "per_element": True,  "letters": "ABCDEF"},
    "2":     {"max": 3,  "per_element": True,  "letters": "ABCDEFG"},
    "3-9":   {"max": 7,  "per_element": False, "numbers": [3,4,5,6,7,8,9]},
    "10":    {"max": 3,  "per_element": True,  "letters": "ABCDEFG"},
    "11":    {"max": 2,  "per_element": True,  "letters": "ABCDEF"},
    "12-18": {"max": 7,  "per_element": False, "numbers": [12,13,14,15,16,17,18]},
    "19-24": {"max": 6,  "per_element": False, "numbers": [19,20,21,22,23,24]},
    "25-29": {"max": 5,  "per_element": False, "numbers": [25,26,27,28,29]},
    "30-36": {"max": 7,  "per_element": False, "numbers": [30,31,32,33,34,35,36]},
    "37":    {"max": 6,  "per_element": False, "manual": True},
    "38.1":  {"max": 14, "per_element": False, "manual": True},
    "38.2":  {"max": 14, "per_element": False, "manual": True},
}


def variant_test_max(task_types):
    total = 0
    for t in task_types:
        cfg = VARIANT_SCORING.get(t)
        if cfg and not cfg.get("manual"):
            total += cfg["max"]
    return total


def variant_total_max(task_types):
    total = 0
    for t in task_types:
        cfg = VARIANT_SCORING.get(t)
        if cfg:
            total += cfg["max"]
    return total


def score_test_task(task_type, student_answer, answer_key):
    cfg = VARIANT_SCORING.get(task_type)
    if not cfg or cfg.get("manual"):
        return None
    max_score = cfg["max"]
    detail = {}
    correct_count = 0
    total_count = 0
    if cfg.get("per_element"):
        for pos in cfg["letters"]:
            total_count += 1
            given = str((student_answer or {}).get(pos, "") or "").strip().upper()
            correct = str((answer_key or {}).get(pos, "") or "").strip().upper()
            ok = given == correct and given != ""
            if ok:
                correct_count += 1
            detail[pos] = {"given": given, "correct": correct, "ok": ok}
        score = max(0, max_score - (total_count - correct_count))
        return {"score": score, "max": max_score,
                "correct": correct_count, "wrong": total_count - correct_count,
                "detail": detail, "per_element": True}
    else:
        for num in cfg["numbers"]:
            total_count += 1
            given = str((student_answer or {}).get(str(num), "") or "").strip().lower()
            correct = str((answer_key or {}).get(str(num), "") or "").strip().lower()
            ok = given == correct and given != ""
            if ok:
                correct_count += 1
            detail[str(num)] = {"given": given, "correct": correct, "ok": ok}
        return {"score": correct_count, "max": max_score,
                "correct": correct_count, "wrong": total_count - correct_count,
                "detail": detail, "per_element": False}


def checklist_for(task_type, task_data=None):
    if task_type == "37":
        return {
            "title": "Дополнительная схема оценивания задания 37 «Электронное письмо личного характера»",
            "volume": "90–154 слова",
            "k1": {"code": "К1", "name": "Решение коммуникативной задачи (Содержание)", "max": 2,
                   "aspects": [
                       "Аспект 1. Ответ на вопрос о том, какую книгу читает друг.",
                       "Аспект 2. Ответ на вопрос о том, какие книги любит читать друг.",
                       "Аспект 3. Ответ на вопрос о том, что автор пишет в своей книге.",
                       "Аспект 4. Три вопроса о любимом произведении друга.",
                       "Аспект 5. Нормы вежливости соблюдены.",
                       "Аспект 6. Стилевое оформление выбрано правильно.",
                   ]},
            "k2": {"code": "К2", "name": "Организация текста", "max": 2,
                   "items": ["Логичность", "Деление на абзацы", "Средства логической связи",
                             "Обращение на отдельной строке", "Завершающая фраза", "Подпись"]},
            "k3": {"code": "К3", "name": "Языковое оформление текста", "max": 2},
        }
    elif task_type in ("38.1", "38.2"):
        chart_word = "таблице" if task_type == "38.1" else "диаграмме"
        return {
            "title": "Дополнительная схема оценивания задания " + task_type,
            "volume": "180–275 слов",
            "k1": {"code": "К1", "name": "Решение коммуникативной задачи (Содержание)", "max": 3,
                   "aspects": [
                       "Аспект 1. Вступление соответствует предложенной теме.",
                       "Аспект 2. 2–3 факта из данных в " + chart_word + " приведены.",
                       "Аспект 3. 1–2 существенных сравнения даны и прокомментированы.",
                       "Аспект 4. Возможная проблема обозначена, и её решение предложено.",
                       "Аспект 5. В заключении мнение автора выражено и обосновано.",
                       "Аспект 6. Стилевое оформление выбрано правильно, нейтральный стиль.",
                   ]},
            "k2": {"code": "К2", "name": "Организация текста", "max": 3,
                   "items": ["Логичность", "Деление на абзацы", "Средства логической связи"]},
            "k3": {"code": "К3", "name": "Лексика", "max": 3},
            "k4": {"code": "К4", "name": "Грамматика", "max": 3},
            "k5": {"code": "К5", "name": "Орфография и пунктуация", "max": 2},
        }
    return None
def extract_json(text):
    if not text:
        raise ValueError("Пустой ответ модели")
    s = text.strip().lstrip('\ufeff').strip()
    s = re.sub(r"^```(?:json|JSON)?\s*\n?", "", s)
    s = re.sub(r"\n?\s*```\s*$", "", s).strip()
    s = re.sub(r"^(?:Json|JSON|json)\s*:\s*", "", s).strip()
    try:
        return json.loads(s)
    except Exception:
        pass
    start, end = s.find("{"), s.rfind("}")
    if start == -1 or end <= start:
        raise ValueError("Не найден JSON: " + s[:300])
    cand = s[start:end + 1]
    for t in [
        lambda x: x,
        lambda x: re.sub(r",(\s*[}\]])", r"\1", x),
        lambda x: re.sub(r",(\s*[}\]])", r"\1", x.replace("{{", "{").replace("}}", "}")),
    ]:
        try:
            return json.loads(t(cand))
        except Exception:
            pass
    try:
        import ast
        return ast.literal_eval(cand)
    except Exception:
        pass
    raise ValueError(f"JSON parse fail: {cand[:800]}")


def _cyrillic_ratio(text):
    if not text:
        return 0.0
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    return sum(1 for c in letters if '\u0400' <= c <= '\u04FF') / len(letters)


def _strip_braces(s):
    return s.replace("{{", "{").replace("}}", "}")


def _fill(prompt, **kwargs):
    for k, v in kwargs.items():
        prompt = prompt.replace("{" + k + "}", str(v))
    return _strip_braces(prompt)


def _collect_texts(task_type, result):
    texts = []
    def add(x):
        if isinstance(x, str):
            texts.append(x)
    if task_type == "1":
        for s in result.get("scripts", []): add(s.get("text"))
        for s in result.get("statements", []): add(s.get("text"))
    elif task_type in ("2", "3-9"):
        add(result.get("script"))
        for s in result.get("statements", []): add(s.get("text"))
        for q in result.get("questions", []):
            add(q.get("question"))
            for v in (q.get("options") or {}).values(): add(v)
    elif task_type == "10":
        for h in result.get("headings", []): add(h.get("text"))
        for t in result.get("texts", []): add(t.get("text"))
    elif task_type == "11":
        add(result.get("title")); add(result.get("text"))
        for f in result.get("fragments", []): add(f.get("text"))
    elif task_type == "12-18":
        add(result.get("title")); add(result.get("text"))
        for q in result.get("questions", []):
            add(q.get("question"))
            for v in (q.get("options") or {}).values(): add(v)
    elif task_type in ("19-24", "25-29"):
        add(result.get("title")); add(result.get("text"))
        for it in result.get("items", []): add(it.get("source_word"))
    elif task_type == "30-36":
        add(result.get("title")); add(result.get("text"))
        for it in result.get("items", []):
            for v in (it.get("options") or {}).values(): add(v)
    elif task_type == "37":
        add(result.get("task_text"))
    elif task_type in ("38.1", "38.2"):
        add(result.get("task_text"))
        sd = result.get("survey_data") or {}
        add(sd.get("question"))
        for o in sd.get("options", []): add(o.get("option"))
    return texts


def validate_general(task_type, result):
    if not isinstance(result, dict):
        return "Ответ не объект"
    if "error" in result:
        return result["error"]
    texts = _collect_texts(task_type, result)
    full = " ".join(t for t in texts if t)
    if not full.strip():
        return "Пустой контент"
    if _cyrillic_ratio(full) > 0.30:
        return "Текст на русском"
    if re.search(r'https?://|www\.', full) and task_type in ("1", "2", "3-9"):
        return "URL-мусор в тексте"
    return None


def call_llm(prompt, retries=1):
    if not API_KEY:
        return {"error": "Не задан PROXYAPI_KEY в переменных окружения"}
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": (
                "You are an EGE English exam generator. Return ONLY valid JSON. "
                "No markdown, no code blocks, no text outside JSON. "
                "Use SINGLE curly braces { } — NOT double {{ }}. "
                "All content texts MUST be in British English. No URLs."
            )},
            {"role": "user", "content": prompt},
        ],
    }
    if MODEL.startswith("openai/"):
        payload["max_completion_tokens"] = MAX_TOKENS
    else:
        payload["max_tokens"] = MAX_TOKENS
        payload["temperature"] = TEMPERATURE

    last_err = None
    for _ in range(retries):
        try:
            r = requests.post(PROXYAPI_URL, headers=headers, json=payload, timeout=240)
            if r.status_code != 200:
                last_err = f"HTTP {r.status_code}: {r.text[:300]}"
                continue
            data = r.json()
            choices = data.get("choices", [])
            if not choices:
                last_err = f"Пустой ответ: {json.dumps(data)[:300]}"
                continue
            msg = choices[0].get("message", {}) or {}
            content = msg.get("content") or msg.get("reasoning") or msg.get("reasoning_content")
            if not content:
                last_err = f"Пустой content: {json.dumps(data)[:400]}"
                print(f"[gen] {last_err}")
                continue
            print(f"[gen] content_len={len(content)}")
            return extract_json(content)
        except Exception as e:
            last_err = f"{type(e).__name__}: {e}"
            traceback.print_exc()
    return {"error": f"ProxyAPI: {last_err}"}


def _mp3_silence(seconds):
    try:
        import lameenc
    except ImportError:
        print("[silence] lameenc не установлен")
        return b""
    sr = 24000
    enc = lameenc.Encoder()
    enc.set_bit_rate(48); enc.set_in_sample_rate(sr)
    enc.set_channels(1); enc.set_quality(7)
    pcm = b"\x00\x00" * int(sr * seconds)
    try:
        return bytes(enc.encode(pcm) + enc.flush())
    except Exception as e:
        print(f"[silence] {e}")
        return b""


def _tts_clean(text):
    t = str(text)
    t = re.sub(r'\b(Mr|Mrs|Ms|Dr|Prof|St|Jr|Sr)\.', r'\1', t)
    t = re.sub(
        r'^((?:Hi|Hello|Hey|Oh|Well|Yeah|Yes|No|Okay|OK|Right|So|Ah|Hmm|Um|Er|Bye|Thanks|Thank you|Please)\s*),\s+',
        r'\1 ', t, flags=re.IGNORECASE)
    t = re.sub(
        r'\b(hi|hello|hey|oh|well|yeah|yes|no|okay|ok|right|so)\s*,\s+',
        r'\1 ', t, flags=re.IGNORECASE)
    t = re.sub(r'^([A-Z][a-z]+)\s*,\s+', r'\1 ', t)
    t = t.replace('...', ',')
    t = t.replace(' – ', ' ').replace(' — ', ' ')
    t = re.sub(r'\s{2,}', ' ', t)
    return t.strip()


async def _edge_synth(text, voice):
    import edge_tts
    try:
        c = edge_tts.Communicate(text, voice)
        audio = b""
        async for ch in c.stream():
            if ch["type"] == "audio":
                audio += ch["data"]
        return audio if audio else None
    except Exception as e:
        print(f"[Edge TTS] {voice}: {type(e).__name__}: {e}")
        return None


def _split_long(text, limit=2400):
    if len(text) <= limit:
        return [text]
    parts = re.split(r'(?<=[.!?])\s+', text)
    chunks, cur = [], ""
    for p in parts:
        if len(cur) + len(p) > limit - 200:
            if cur:
                chunks.append(cur.strip())
            cur = p
        else:
            cur += " " + p
    if cur:
        chunks.append(cur.strip())
    return chunks


def _guess_gender(name):
    low = (name or "").lower().strip()
    low = re.sub(r'[^a-z ]', '', low).strip()
    first = low.split()[0] if low else ""
    if first in FEMALE_NAMES:
        return "F"
    if first in MALE_NAMES:
        return "M"
    if first.endswith("a") or first.endswith("ie") or first.endswith("y"):
        return "F"
    return "M"


def _blocks_for_task(task_type, task_data):
    blocks = []
    if task_type == "1":
        for s in task_data.get("scripts", []):
            letter = (s.get("speaker") or "A").upper()
            blocks.append({"name": f"Speaker {letter}", "gender": None, "text": s.get("text", "")})
    elif task_type == "2":
        for e in task_data.get("dialogue_script", []):
            name = (e.get("speaker") or "").strip()
            blocks.append({"name": name, "gender": _guess_gender(name), "text": e.get("text", "")})
    elif task_type == "3-9":
        for e in task_data.get("interview_script", []):
            name = (e.get("speaker") or "").strip()
            blocks.append({"name": name, "gender": _guess_gender(name), "text": e.get("text", "")})
    return blocks


def _voice_for_block(blk, is_task1):
    if is_task1:
        m = re.match(r'^Speaker\s*([A-F])$', blk["name"], re.IGNORECASE)
        if m:
            return MONOLOGUE_VOICES.get(m.group(1).upper(), VOICE_M)
        return VOICE_M
    return VOICE_F if blk["gender"] == "F" else VOICE_M


async def _blocks_audio(blocks, is_task1):
    total = b""
    for i, blk in enumerate(blocks):
        text = (blk.get("text") or "").strip()
        if not text:
            continue
        if is_task1:
            m = re.match(r'^Speaker\s*([A-F])$', blk["name"], re.IGNORECASE)
            if m:
                a = await _edge_synth(f"Speaker {m.group(1).upper()}.", VOICE_ANNOUNCER)
                if a:
                    total += a
        if i > 0:
            total += _mp3_silence(PAUSE_BETWEEN_BLOCKS)
        voice = _voice_for_block(blk, is_task1)
        for chunk in _split_long(text):
            clean_chunk = _tts_clean(chunk)
            if not clean_chunk:
                continue
            a = await _edge_synth(clean_chunk, voice)
            if a:
                total += a
        await asyncio.sleep(0.05)
    return total


def synthesize_part1(task_type, task_data):
    blocks = _blocks_for_task(task_type, task_data)
    if not blocks:
        return {"error": "Нет блоков для озвучки"}
    is_task1 = (task_type == "1")
    intro_pause = PAUSE_AFTER_INTRO.get(task_type, 20)
    async def _run():
        out = b""
        intro = INTRO_RU.get(task_type, "")
        if intro:
            a = await _edge_synth(_tts_clean(intro), VOICE_RU_FEMALE)
            if a:
                out += a
        out += _mp3_silence(intro_pause)
        a = await _edge_synth(EN_NOW_START, VOICE_ANNOUNCER)
        if a:
            out += a
        out += await _blocks_audio(blocks, is_task1)
        a = await _edge_synth(EN_WAIT, VOICE_ANNOUNCER)
        if a:
            out += a
        out += _mp3_silence(PAUSE_BEFORE_REPLAY)
        return out
    try:
        audio = asyncio.run(_run())
    except Exception as e:
        traceback.print_exc()
        return {"error": f"{type(e).__name__}: {e}"}
    if not audio:
        return {"error": "Пустое аудио (part1)"}
    b64 = base64.b64encode(audio).decode("utf-8")
    if len(b64) > 3_400_000:
        return {"error": f"part1 слишком большой ({len(b64)})"}
    return {"audio": b64, "part": 1, "blocks": len(blocks)}


def synthesize_part2(task_type, task_data):
    blocks = _blocks_for_task(task_type, task_data)
    if not blocks:
        return {"error": "Нет блоков для озвучки"}
    is_task1 = (task_type == "1")
    async def _run():
        out = b""
        a = await _edge_synth(EN_HEAR_AGAIN, VOICE_ANNOUNCER)
        if a:
            out += a
        out += await _blocks_audio(blocks, is_task1)
        a = await _edge_synth(EN_END_ALL, VOICE_ANNOUNCER)
        if a:
            out += a
        return out
    try:
        audio = asyncio.run(_run())
    except Exception as e:
        traceback.print_exc()
        return {"error": f"{type(e).__name__}: {e}"}
    if not audio:
        return {"error": "Пустое аудио (part2)"}
    b64 = base64.b64encode(audio).decode("utf-8")
    if len(b64) > 3_400_000:
        return {"error": f"part2 слишком большой ({len(b64)})"}
    return {"audio": b64, "part": 2, "blocks": len(blocks)}


def _balance_choice_keys(questions, answer_key, num_options):
    if not questions:
        return questions, answer_key
    n = len(questions)
    base = [str(i) for i in range(1, num_options + 1)]
    slots = []
    while len(slots) < n:
        slots.extend(base)
    slots = slots[:n]
    random.shuffle(slots)
    new_questions, new_key = [], {}
    for i, q in enumerate(questions):
        num = str(q.get("number"))
        opts = dict(q.get("options") or {})
        correct_slot = str(answer_key.get(num, "1"))
        correct_text = opts.pop(correct_slot, None)
        if correct_text is None or len(opts) != num_options - 1:
            new_questions.append(q)
            new_key[num] = correct_slot
            continue
        remaining = list(opts.values())
        random.shuffle(remaining)
        target = slots[i]
        new_opts = {}
        rem_idx = 0
        for slot in [str(x) for x in range(1, num_options + 1)]:
            if slot == target:
                new_opts[slot] = correct_text
            else:
                new_opts[slot] = remaining[rem_idx]
                rem_idx += 1
        new_questions.append({"number": q["number"], "question": q["question"], "options": new_opts})
        new_key[num] = target
    return new_questions, new_key
def _s3():
    return boto3.client(
        "s3",
        endpoint_url="https://storage.yandexcloud.net",
        aws_access_key_id=STORAGE_KEY_ID,
        aws_secret_access_key=STORAGE_SECRET,
        config=Config(signature_version="s3v4"),
        region_name="ru-central1",
    )


def _new_id(prefix):
    return prefix + "-" + uuid.uuid4().hex[:8].upper()


def _parse_gemini_task1(text):
    clean = text.replace("—", "-").replace("–", "-")
    m_scripts_start = re.search(r'-{2,}\s*AUDIO\s*SCRIPTS?\s*-{2,}', clean, re.IGNORECASE)
    statements_part = clean[:m_scripts_start.start()] if m_scripts_start else clean
    statements = []
    seen = set()
    for line in statements_part.split("\n"):
        m = re.match(r'^\s*(\d)\s+(.+?)\s*$', line)
        if m:
            n = int(m.group(1))
            t = m.group(2).strip()
            if 1 <= n <= 7 and n not in seen and len(t) > 3:
                statements.append({"number": n, "text": t})
                seen.add(n)
    statements.sort(key=lambda x: x["number"])

    scripts = []
    m_end = re.search(r'-{2,}\s*ANSWER\s*KEY\s*-{2,}', clean, re.IGNORECASE)
    if m_scripts_start and m_end:
        body = clean[m_scripts_start.end():m_end.start()]
    elif m_scripts_start:
        body = clean[m_scripts_start.end():]
    else:
        body = ""
    parts = re.split(r'Speaker\s+([A-F])\s*:', body)
    for i in range(1, len(parts), 2):
        letter = parts[i]
        text_block = parts[i + 1] if i + 1 < len(parts) else ""
        text_block = re.split(r'-{2,}', text_block)[0].strip()
        if text_block:
            scripts.append({"speaker": letter, "text": text_block})

    answer_key = {}
    m = re.search(r'Ответ\s*:\s*(\d{6})', clean)
    if m:
        digits = m.group(1)
        for i, letter in enumerate("ABCDEF"):
            answer_key[letter] = int(digits[i])

    extra = None
    m = re.search(r'лишн\w*\s*[-—]\s*(\d)', clean, re.IGNORECASE)
    if m:
        extra = int(m.group(1))
    elif answer_key:
        used = set(answer_key.values())
        for n in range(1, 8):
            if n not in used:
                extra = n
                break

    return {"statements": statements, "scripts": scripts,
            "answer_key": answer_key, "extra_statement": extra}


def _bank_prefix(task_type, topic_letter):
    return f"tasks/{task_type}/{topic_letter}/"


def _bank_list_raw(task_type, topic_letter):
    s3 = _s3()
    prefix = _bank_prefix(task_type, topic_letter)
    result = []
    try:
        paginator = s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=BUCKET_NAME, Prefix=prefix):
            for obj in page.get("Contents", []):
                result.append(obj["Key"])
    except Exception as e:
        print(f"[bank] list error: {e}")
    return result


def _bank_next_number(task_type, topic_letter):
    files = _bank_list_raw(task_type, topic_letter)
    existing = set()
    for key in files:
        fname = key.split("/")[-1]
        m = re.match(r'.+-(\d{3,})\.json$', fname)
        if m:
            existing.add(int(m.group(1)))
    n = 1
    while n in existing:
        n += 1
    return n


def _bank_find_duplicate(task_type, topic_letter, parsed):
    if not parsed.get("scripts"):
        return None
    try:
        s3 = _s3()
        files = _bank_list_raw(task_type, topic_letter)
        first_script = parsed["scripts"][0]["text"][:100].lower().strip()
        for key in files:
            if key.endswith(".json"):
                try:
                    obj = s3.get_object(Bucket=BUCKET_NAME, Key=key)
                    meta = json.loads(obj["Body"].read().decode("utf-8"))
                    for s in meta.get("scripts", []):
                        if s.get("text", "")[:100].lower().strip() == first_script:
                            return meta.get("code")
                except Exception:
                    pass
    except Exception as e:
        print(f"[bank] dup check error: {e}")
    return None


def preview_task1(raw_text, topic_letter):
    parsed = _parse_gemini_task1(raw_text)
    if len(parsed["statements"]) != 7:
        return {"error": f"Найдено {len(parsed['statements'])} утверждений, нужно 7"}
    if len(parsed["scripts"]) != 6:
        return {"error": f"Найдено {len(parsed['scripts'])} монологов, нужно 6"}
    if len(parsed["answer_key"]) != 6:
        return {"error": "Не удалось распарсить ключ"}

    dup = _bank_find_duplicate("1", topic_letter, parsed)

    task_data = {
        "instruction": ("Вы услышите 6 высказываний. Установите соответствие между высказываниями "
                        "каждого говорящего А–F и утверждениями, данными в списке 1–7. Используйте "
                        "каждое утверждение, обозначенное соответствующей цифрой, только один раз. "
                        "В задании есть одно лишнее утверждение. Вы услышите запись дважды. "
                        "Занесите свои ответы в таблицу."),
        "statements": parsed["statements"],
        "scripts": parsed["scripts"],
        "answer_key": parsed["answer_key"],
        "extra_statement": parsed["extra_statement"],
    }

    print("[preview] озвучиваю часть 1")
    p1 = synthesize_part1("1", task_data)
    if "error" in p1:
        return {"error": f"TTS часть 1: {p1['error']}"}
    print("[preview] озвучиваю часть 2")
    p2 = synthesize_part2("1", task_data)
    if "error" in p2:
        return {"error": f"TTS часть 2: {p2['error']}"}

    mp3 = base64.b64decode(p1["audio"]) + base64.b64decode(p2["audio"])
    return {
        "task_data": task_data,
        "audio_b64": base64.b64encode(mp3).decode("utf-8"),
        "audio_size_kb": len(mp3) // 1024,
        "duplicate_of": dup,
        "summary": {
            "statements": len(parsed["statements"]),
            "scripts": len(parsed["scripts"]),
            "extra_statement": parsed["extra_statement"],
            "answer_key": parsed["answer_key"],
        }
    }


def save_previewed_task(task_type, topic_letter, task_data, audio_b64, force=False):
    if not force:
        dup = _bank_find_duplicate(task_type, topic_letter, task_data)
        if dup:
            return {"warning": f"Похожее задание уже есть: {dup}", "duplicate_of": dup}

    n = _bank_next_number(task_type, topic_letter)
    code = f"{task_type}-{topic_letter}-{n:03d}"
    mp3 = base64.b64decode(audio_b64) if audio_b64 else b""

    meta = {
        "code": code,
        "task_type": task_type,
        "topic": topic_letter,
        "topic_full": TOPIC_MAP.get(topic_letter, ""),
        "instruction": task_data.get("instruction", ""),
        "statements": task_data.get("statements", []),
        "scripts": task_data.get("scripts", []),
        "answer_key": task_data.get("answer_key", {}),
        "extra_statement": task_data.get("extra_statement", None),
        "explanations": task_data.get("explanations", {}),
        "has_audio": bool(mp3),
    }

    try:
        s3 = _s3()
        prefix = _bank_prefix(task_type, topic_letter)
        s3.put_object(Bucket=BUCKET_NAME, Key=f"{prefix}{code}.json",
                      Body=json.dumps(meta, ensure_ascii=False).encode("utf-8"),
                      ContentType="application/json")
        if mp3:
            s3.put_object(Bucket=BUCKET_NAME, Key=f"{prefix}{code}.mp3",
                          Body=mp3, ContentType="audio/mpeg")
    except Exception as e:
        traceback.print_exc()
        return {"error": f"Storage: {type(e).__name__}: {e}"}

    return {"ok": True, "code": code, "size_kb": len(mp3) // 1024}


def get_bank_task(task_type, topic_letter, code):
    try:
        s3 = _s3()
        prefix = _bank_prefix(task_type, topic_letter)
        obj = s3.get_object(Bucket=BUCKET_NAME, Key=f"{prefix}{code}.json")
        meta = json.loads(obj["Body"].read().decode("utf-8"))
        try:
            mp3_obj = s3.get_object(Bucket=BUCKET_NAME, Key=f"{prefix}{code}.mp3")
            mp3 = mp3_obj["Body"].read()
            meta["audio_b64"] = base64.b64encode(mp3).decode("utf-8")
            meta["audio_size_kb"] = len(mp3) // 1024
        except Exception:
            meta["audio_b64"] = None
            meta["audio_size_kb"] = 0
        return meta
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


def delete_bank_task(task_type, topic_letter, code):
    try:
        s3 = _s3()
        prefix = _bank_prefix(task_type, topic_letter)
        s3.delete_object(Bucket=BUCKET_NAME, Key=f"{prefix}{code}.json")
        try:
            s3.delete_object(Bucket=BUCKET_NAME, Key=f"{prefix}{code}.mp3")
        except Exception:
            pass
        return {"ok": True, "code": code}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


def list_bank(task_type=None, topic_letter=None):
    try:
        s3 = _s3()
        prefix = "tasks/"
        if task_type and topic_letter:
            prefix = _bank_prefix(task_type, topic_letter)
        result = []
        paginator = s3.get_paginator("list_objects_v2")
        keys = []
        for page in paginator.paginate(Bucket=BUCKET_NAME, Prefix=prefix):
            for obj in page.get("Contents", []):
                if obj["Key"].endswith(".json"):
                    keys.append(obj["Key"])
        for key in keys:
            try:
                obj = s3.get_object(Bucket=BUCKET_NAME, Key=key)
                meta = json.loads(obj["Body"].read().decode("utf-8"))
                result.append({
                    "code": meta.get("code", ""),
                    "task_type": meta.get("task_type", ""),
                    "topic": meta.get("topic", ""),
                    "topic_full": meta.get("topic_full", ""),
                    "has_audio": meta.get("has_audio", False),
                    "statements_count": len(meta.get("statements", [])),
                    "scripts_count": len(meta.get("scripts", [])),
                })
            except Exception:
                pass
        result.sort(key=lambda x: x.get("code", ""))
        return {"tasks": result, "count": len(result)}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


def fetch_from_bank(task_type, topic_letter):
    files = [f for f in _bank_list_raw(task_type, topic_letter) if f.endswith(".json")]
    if not files:
        return None
    try:
        s3 = _s3()
        key = random.choice(files)
        obj = s3.get_object(Bucket=BUCKET_NAME, Key=key)
        meta = json.loads(obj["Body"].read().decode("utf-8"))
        mp3_key = key.replace(".json", ".mp3")
        try:
            mp3_obj = s3.get_object(Bucket=BUCKET_NAME, Key=mp3_key)
            mp3_bytes = mp3_obj["Body"].read()
            meta["audio_b64"] = base64.b64encode(mp3_bytes).decode("utf-8")
        except Exception:
            meta["audio_b64"] = None
        return meta
    except Exception as e:
        print(f"[bank] fetch error: {e}")
        return None


STUDENT_TRANSLIT = {
    'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ё':'e','ж':'zh','з':'z',
    'и':'i','й':'y','к':'k','л':'l','м':'m','н':'n','о':'o','п':'p','р':'r',
    'с':'s','т':'t','у':'u','ф':'f','х':'h','ц':'ts','ч':'ch','ш':'sh',
    'щ':'sch','ъ':'','ы':'y','ь':'','э':'e','ю':'yu','я':'ya',
    'a':'a','b':'b','c':'c','d':'d','e':'e','f':'f','g':'g','h':'h','i':'i',
    'j':'j','k':'k','l':'l','m':'m','n':'n','o':'o','p':'p','q':'q','r':'r',
    's':'s','t':'t','u':'u','v':'v','w':'w','x':'x','y':'y','z':'z',
}


def _student_translit(word):
    latin = ""
    for c in (word or "").lower():
        if c in STUDENT_TRANSLIT:
            latin += STUDENT_TRANSLIT[c]
    return latin


def _student_code_from_name(surname, name):
    base = _student_translit(surname) or _student_translit(name) or "stud"
    base = base[:4].upper()
    suffix = "".join(random.choices("ABCDEF0123456789", k=4))
    return f"{base}-{suffix}"


def _student_create(surname, name):
    surname = (surname or "").strip()
    name = (name or "").strip()
    if not surname and not name:
        return {"error": "Введи хотя бы фамилию или имя"}
    s3 = _s3()
    code = None
    for _ in range(50):
        candidate = _student_code_from_name(surname, name)
        try:
            s3.head_object(Bucket=BUCKET_NAME, Key=f"students/{candidate}.json")
        except Exception:
            code = candidate
            break
    if not code:
        return {"error": "Не удалось сгенерировать уникальный код"}

    now = int(time.time())
    meta = {
        "code": code, "surname": surname, "name": name,
        "created_at": now, "updated_at": now,
    }
    try:
        s3.put_object(
            Bucket=BUCKET_NAME, Key=f"students/{code}.json",
            Body=json.dumps(meta, ensure_ascii=False).encode("utf-8"),
            ContentType="application/json",
        )
    except Exception as e:
        return {"error": f"Storage: {type(e).__name__}: {e}"}
    return {"ok": True, **meta}


def _student_list():
    try:
        s3 = _s3()
        paginator = s3.get_paginator("list_objects_v2")
        result = []
        for page in paginator.paginate(Bucket=BUCKET_NAME, Prefix="students/"):
            for obj in page.get("Contents", []):
                if obj["Key"].endswith(".json"):
                    try:
                        o = s3.get_object(Bucket=BUCKET_NAME, Key=obj["Key"])
                        meta = json.loads(o["Body"].read().decode("utf-8"))
                        result.append({
                            "code": meta.get("code", ""),
                            "surname": meta.get("surname", ""),
                            "name": meta.get("name", ""),
                            "created_at": meta.get("created_at", 0),
                            "updated_at": meta.get("updated_at", meta.get("created_at", 0)),
                        })
                    except Exception:
                        pass
        result.sort(key=lambda x: (x.get("surname", ""), x.get("name", "")))
        return {"students": result, "count": len(result)}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


def _student_get(code):
    try:
        s3 = _s3()
        o = s3.get_object(Bucket=BUCKET_NAME, Key=f"students/{code}.json")
        return json.loads(o["Body"].read().decode("utf-8"))
    except Exception:
        return None


def _student_update(code, surname, name):
    code = (code or "").strip()
    if not code:
        return {"error": "Нет кода"}
    existing = _student_get(code)
    if not existing:
        return {"error": "Ученик не найден"}
    surname = (surname or "").strip()
    name = (name or "").strip()
    if not surname and not name:
        return {"error": "Введи хотя бы фамилию или имя"}
    existing["surname"] = surname
    existing["name"] = name
    existing["updated_at"] = int(time.time())
    try:
        s3 = _s3()
        s3.put_object(
            Bucket=BUCKET_NAME, Key=f"students/{code}.json",
            Body=json.dumps(existing, ensure_ascii=False).encode("utf-8"),
            ContentType="application/json",
        )
    except Exception as e:
        return {"error": f"Storage: {type(e).__name__}: {e}"}
    return {"ok": True, **existing}


def _student_delete(code):
    try:
        s3 = _s3()
        s3.delete_object(Bucket=BUCKET_NAME, Key=f"students/{code}.json")
        return {"ok": True}
    except Exception as e:
        return {"error": str(e)}
WRITING_TYPES = ("37", "38.1", "38.2")


def _submission_key(student_code, submission_id):
    return f"submissions/{student_code}/{submission_id}.json"


def _submission_save_draft(student_code, task_type, task_data,
                           assignment_id=None, bank_code=None, answer_text=""):
    if not student_code:
        return {"error": "Нет student_code"}
    if task_type not in WRITING_TYPES:
        return {"error": "Черновики только для 37, 38.1, 38.2"}

    s3 = _s3()
    existing_id = None
    try:
        paginator = s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=BUCKET_NAME,
                                       Prefix=f"submissions/{student_code}/"):
            for obj in page.get("Contents", []):
                if not obj["Key"].endswith(".json"):
                    continue
                try:
                    o = s3.get_object(Bucket=BUCKET_NAME, Key=obj["Key"])
                    meta = json.loads(o["Body"].read().decode("utf-8"))
                    if (meta.get("status") == "draft"
                            and meta.get("task_type") == task_type
                            and meta.get("assignment_id") == assignment_id):
                        existing_id = meta.get("id")
                        break
                except Exception:
                    pass
            if existing_id:
                break
    except Exception as e:
        print(f"[submission] list error: {e}")

    now = int(time.time())
    if existing_id:
        meta = _submission_get(student_code, existing_id) or {}
        meta["answer_text"] = answer_text
        meta["task_data"] = task_data or meta.get("task_data")
        meta["updated_at"] = now
        sid = existing_id
    else:
        sid = _new_id("SUB")
        meta = {
            "id": sid,
            "student_code": student_code,
            "task_type": task_type,
            "assignment_id": assignment_id,
            "bank_code": bank_code,
            "task_data": task_data,
            "answer_text": answer_text,
            "status": "draft",
            "created_at": now,
            "updated_at": now,
            "submitted_at": None,
            "review": None,
        }

    try:
        s3.put_object(Bucket=BUCKET_NAME, Key=_submission_key(student_code, sid),
                      Body=json.dumps(meta, ensure_ascii=False).encode("utf-8"),
                      ContentType="application/json")
    except Exception as e:
        return {"error": f"Storage: {type(e).__name__}: {e}"}
    return {"ok": True, "id": sid, "updated_at": now}


def _submission_submit(student_code, submission_id, answer_text):
    if not student_code or not submission_id:
        return {"error": "Нужны student_code и submission_id"}
    meta = _submission_get(student_code, submission_id)
    if not meta:
        return {"error": "Работа не найдена"}
    if meta.get("status") == "reviewed":
        return {"error": "Уже проверено, пересдача не поддерживается"}

    txt = (answer_text or meta.get("answer_text", "")).strip()
    if not txt:
        return {"error": "Пустой ответ"}

    meta["answer_text"] = txt
    meta["status"] = "submitted"
    meta["submitted_at"] = int(time.time())
    meta["updated_at"] = meta["submitted_at"]

    try:
        s3 = _s3()
        s3.put_object(Bucket=BUCKET_NAME, Key=_submission_key(student_code, submission_id),
                      Body=json.dumps(meta, ensure_ascii=False).encode("utf-8"),
                      ContentType="application/json")
    except Exception as e:
        return {"error": f"Storage: {type(e).__name__}: {e}"}
    return {"ok": True, "id": submission_id}


def _submission_get(student_code, submission_id):
    try:
        s3 = _s3()
        o = s3.get_object(Bucket=BUCKET_NAME,
                          Key=_submission_key(student_code, submission_id))
        return json.loads(o["Body"].read().decode("utf-8"))
    except Exception:
        return None


def _submission_list(student_code):
    try:
        s3 = _s3()
        result = []
        paginator = s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=BUCKET_NAME,
                                       Prefix=f"submissions/{student_code}/"):
            for obj in page.get("Contents", []):
                if not obj["Key"].endswith(".json"):
                    continue
                try:
                    o = s3.get_object(Bucket=BUCKET_NAME, Key=obj["Key"])
                    meta = json.loads(o["Body"].read().decode("utf-8"))
                    result.append({
                        "id": meta.get("id"),
                        "task_type": meta.get("task_type"),
                        "status": meta.get("status"),
                        "created_at": meta.get("created_at", 0),
                        "updated_at": meta.get("updated_at", 0),
                        "submitted_at": meta.get("submitted_at"),
                        "total": (meta.get("review") or {}).get("total"),
                        "max_total": CRITERIA_BY_TYPE.get(meta.get("task_type"), {}).get("max_total", 0),
                    })
                except Exception:
                    pass
        result.sort(key=lambda x: x.get("created_at", 0), reverse=True)
        return {"submissions": result, "count": len(result)}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


def _submission_list_pending():
    try:
        s3 = _s3()
        result = []
        paginator = s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=BUCKET_NAME, Prefix="submissions/"):
            for obj in page.get("Contents", []):
                if not obj["Key"].endswith(".json"):
                    continue
                try:
                    o = s3.get_object(Bucket=BUCKET_NAME, Key=obj["Key"])
                    meta = json.loads(o["Body"].read().decode("utf-8"))
                    if meta.get("status") != "submitted":
                        continue
                    st = _student_get(meta.get("student_code")) or {}
                    result.append({
                        "id": meta.get("id"),
                        "student_code": meta.get("student_code"),
                        "student_name": ((st.get("surname", "") + " " +
                                          st.get("name", "")).strip()
                                         or meta.get("student_code")),
                        "task_type": meta.get("task_type"),
                        "submitted_at": meta.get("submitted_at"),
                    })
                except Exception:
                    pass
        result.sort(key=lambda x: x.get("submitted_at") or 0)
        return {"submissions": result, "count": len(result)}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


def _submission_review(student_code, submission_id, scores, comment):
    if not student_code or not submission_id:
        return {"error": "Нужны student_code и submission_id"}
    meta = _submission_get(student_code, submission_id)
    if not meta:
        return {"error": "Работа не найдена"}
    if meta.get("status") != "submitted":
        return {"error": "Можно проверять только работы со статусом submitted"}

    crit = CRITERIA_BY_TYPE.get(meta.get("task_type"))
    if not crit:
        return {"error": "Неизвестный тип задания"}

    clean = {}
    for c in crit["criteria"]:
        code = c["code"]
        raw = (scores or {}).get(code, 0)
        try:
            v = int(raw)
        except Exception:
            v = 0
        if v < 0:
            v = 0
        if v > c["max"]:
            v = c["max"]
        clean[code] = v

    if crit.get("rule_k1_zero") and clean.get("К1", 0) == 0:
        for code in clean:
            clean[code] = 0

    total = sum(clean.values())
    meta["review"] = {
        "scores": clean,
        "total": total,
        "max_total": crit["max_total"],
        "comment": (comment or "").strip(),
        "reviewed_at": int(time.time()),
    }
    meta["status"] = "reviewed"
    meta["updated_at"] = meta["review"]["reviewed_at"]

    try:
        s3 = _s3()
        s3.put_object(Bucket=BUCKET_NAME, Key=_submission_key(student_code, submission_id),
                      Body=json.dumps(meta, ensure_ascii=False).encode("utf-8"),
                      ContentType="application/json")
    except Exception as e:
        return {"error": f"Storage: {type(e).__name__}: {e}"}
    return {"ok": True, "id": submission_id, "total": total}


def _submission_stats():
    try:
        s3 = _s3()
        per_student = {}
        paginator = s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=BUCKET_NAME, Prefix="submissions/"):
            for obj in page.get("Contents", []):
                if not obj["Key"].endswith(".json"):
                    continue
                try:
                    o = s3.get_object(Bucket=BUCKET_NAME, Key=obj["Key"])
                    m = json.loads(o["Body"].read().decode("utf-8"))
                except Exception:
                    continue
                sc = m.get("student_code")
                if not sc:
                    continue
                if sc not in per_student:
                    per_student[sc] = {"total": 0, "max": 0, "count": 0,
                                       "pending": 0, "by_type": {}}
                entry = per_student[sc]
                if m.get("status") == "submitted":
                    entry["pending"] += 1
                if m.get("status") == "reviewed":
                    rv = m.get("review") or {}
                    entry["total"] += rv.get("total", 0)
                    entry["max"] += rv.get("max_total", 0)
                    entry["count"] += 1
                    t = m.get("task_type")
                    entry["by_type"][t] = entry["by_type"].get(t, 0) + 1

        # Дополнительно — варианты
        var_by_student = {}
        for page in paginator.paginate(Bucket=BUCKET_NAME, Prefix="variant_submissions/"):
            for obj in page.get("Contents", []):
                if not obj["Key"].endswith(".json"):
                    continue
                try:
                    o = s3.get_object(Bucket=BUCKET_NAME, Key=obj["Key"])
                    m = json.loads(o["Body"].read().decode("utf-8"))
                except Exception:
                    continue
                sc = m.get("student_code")
                if not sc:
                    continue
                if sc not in var_by_student:
                    var_by_student[sc] = {"total": 0, "max": 0, "count": 0, "pending": 0}
                e = var_by_student[sc]
                e["total"] += m.get("total_score", 0)
                e["max"] += m.get("total_max", 0)
                e["count"] += 1
                if m.get("status") == "submitted":
                    e["pending"] += 1

        students = (_student_list() or {}).get("students", [])
        smap = {s["code"]: s for s in students}
        all_codes = set(per_student.keys()) | set(var_by_student.keys())
        result = []
        for sc in all_codes:
            st = smap.get(sc, {})
            e = per_student.get(sc, {"total": 0, "max": 0, "count": 0, "pending": 0, "by_type": {}})
            ve = var_by_student.get(sc, {"total": 0, "max": 0, "count": 0, "pending": 0})
            result.append({
                "student_code": sc,
                "student_name": ((st.get("surname", "") + " " + st.get("name", "")).strip()
                                 or sc),
                "total": e["total"] + ve["total"],
                "max": e["max"] + ve["max"],
                "count": e["count"] + ve["count"],
                "pending": e["pending"] + ve["pending"],
                "by_type": e["by_type"],
                "variants_count": ve["count"],
                "variants_total": ve["total"],
                "variants_max": ve["max"],
            })
        result.sort(key=lambda x: x["student_name"])
        g_total = sum(x["total"] for x in result)
        g_max = sum(x["max"] for x in result)
        g_count = sum(x["count"] for x in result)
        g_pending = sum(x["pending"] for x in result)
        return {"students": result, "count": len(result),
                "global": {"total": g_total, "max": g_max,
                           "count": g_count, "pending": g_pending}}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}
MATERIAL_MAX_BYTES = 7 * 1024 * 1024


def _material_ext_from_type(t):
    return {"pdf": "pdf", "image": "png", "text": "txt"}.get(t, "bin")


def _material_guess_type(filename, content_type, url=None):
    if url:
        return "link"
    fn = (filename or "").lower()
    if fn.endswith(".pdf"):
        return "pdf"
    if fn.endswith((".png", ".jpg", ".jpeg", ".gif", ".webp")):
        return "image"
    if fn.endswith((".txt", ".docx", ".doc", ".md")):
        return "text"
    if content_type:
        if "pdf" in content_type:
            return "pdf"
        if content_type.startswith("image/"):
            return "image"
        if "text" in content_type:
            return "text"
    return "text"


def _materials_index_key():
    return "materials/_index.json"


def _materials_get_index():
    try:
        s3 = _s3()
        o = s3.get_object(Bucket=BUCKET_NAME, Key=_materials_index_key())
        return json.loads(o["Body"].read().decode("utf-8"))
    except Exception:
        return {"items": []}


def _materials_put_index(idx):
    s3 = _s3()
    s3.put_object(Bucket=BUCKET_NAME, Key=_materials_index_key(),
                  Body=json.dumps(idx, ensure_ascii=False).encode("utf-8"),
                  ContentType="application/json")


def _materials_list():
    idx = _materials_get_index()
    items = sorted(idx.get("items", []), key=lambda x: x.get("order", 0))
    return {"materials": items, "count": len(items)}


def _materials_add(title, file_b64=None, filename=None, content_type=None, url=None):
    title = (title or "").strip()
    if not title:
        return {"error": "Нужно название"}

    mid = _new_id("MAT")
    mtype = _material_guess_type(filename, content_type, url=url)

    if mtype == "link":
        if not url or not url.strip():
            return {"error": "Для ссылки нужен URL"}
        if not re.match(r'^https?://', url.strip(), re.IGNORECASE):
            return {"error": "URL должен начинаться с http(s)://"}
    else:
        if not file_b64:
            return {"error": "Нужен файл"}
        try:
            data = base64.b64decode(file_b64)
        except Exception:
            return {"error": "Не удалось декодировать файл"}
        if len(data) > MATERIAL_MAX_BYTES:
            return {"error": f"Файл больше {MATERIAL_MAX_BYTES // 1024 // 1024} МБ"}

    idx = _materials_get_index()
    order = max([m.get("order", 0) for m in idx.get("items", [])] or [0]) + 10

    meta = {
        "id": mid,
        "title": title,
        "type": mtype,
        "order": order,
        "created_at": int(time.time()),
    }
    if mtype == "link":
        meta["url"] = url.strip()
    else:
        meta["filename"] = filename or f"{mid}.{_material_ext_from_type(mtype)}"
        meta["size"] = len(data)
        meta["content_type"] = content_type or "application/octet-stream"

    s3 = _s3()
    try:
        if mtype != "link":
            s3.put_object(Bucket=BUCKET_NAME,
                          Key=f"materials/{mid}.{_material_ext_from_type(mtype)}",
                          Body=data,
                          ContentType=meta["content_type"])
        idx.setdefault("items", []).append(meta)
        _materials_put_index(idx)
    except Exception as e:
        return {"error": f"Storage: {type(e).__name__}: {e}"}
    return {"ok": True, "id": mid}


def _materials_get_file(mid):
    idx = _materials_get_index()
    meta = next((m for m in idx.get("items", []) if m.get("id") == mid), None)
    if not meta:
        return {"error": "Не найдено"}
    if meta.get("type") == "link":
        return {"url": meta.get("url")}
    try:
        s3 = _s3()
        ext = _material_ext_from_type(meta.get("type"))
        o = s3.get_object(Bucket=BUCKET_NAME, Key=f"materials/{mid}.{ext}")
        data = o["Body"].read()
        return {"file_b64": base64.b64encode(data).decode("utf-8"),
                "content_type": meta.get("content_type", "application/octet-stream"),
                "filename": meta.get("filename", f"{mid}.{ext}")}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


def _materials_delete(mid):
    idx = _materials_get_index()
    meta = next((m for m in idx.get("items", []) if m.get("id") == mid), None)
    if not meta:
        return {"error": "Не найдено"}
    try:
        s3 = _s3()
        if meta.get("type") != "link":
            ext = _material_ext_from_type(meta.get("type"))
            try:
                s3.delete_object(Bucket=BUCKET_NAME, Key=f"materials/{mid}.{ext}")
            except Exception:
                pass
        idx["items"] = [m for m in idx.get("items", []) if m.get("id") != mid]
        _materials_put_index(idx)
    except Exception as e:
        return {"error": f"Storage: {type(e).__name__}: {e}"}
    return {"ok": True, "id": mid}


def _materials_move(mid, direction):
    idx = _materials_get_index()
    items = sorted(idx.get("items", []), key=lambda x: x.get("order", 0))
    pos = next((i for i, m in enumerate(items) if m.get("id") == mid), None)
    if pos is None:
        return {"error": "Не найдено"}
    if direction == "up" and pos > 0:
        items[pos - 1], items[pos] = items[pos], items[pos - 1]
    elif direction == "down" and pos < len(items) - 1:
        items[pos + 1], items[pos] = items[pos], items[pos + 1]
    else:
        return {"ok": True, "id": mid, "note": "некуда двигать"}
    for i, m in enumerate(items):
        m["order"] = (i + 1) * 10
    idx["items"] = items
    _materials_put_index(idx)
    return {"ok": True, "id": mid}


def _assignment_key(aid):
    return f"assignments/{aid}.json"


def _assignment_create(student_code, task_type, task_data=None,
                       bank_code=None, note=""):
    if not student_code:
        return {"error": "Нужен student_code"}
    if task_type not in ("1", "2", "3-9", "10", "11", "12-18",
                         "19-24", "25-29", "30-36", "37", "38.1", "38.2"):
        return {"error": "Плохой task_type"}
    if not task_data and not bank_code:
        return {"error": "Нужны task_data или bank_code"}

    aid = _new_id("ASN")
    meta = {
        "id": aid,
        "student_code": student_code,
        "task_type": task_type,
        "task_data": task_data,
        "bank_code": bank_code,
        "note": (note or "").strip(),
        "created_at": int(time.time()),
    }
    try:
        s3 = _s3()
        s3.put_object(Bucket=BUCKET_NAME, Key=_assignment_key(aid),
                      Body=json.dumps(meta, ensure_ascii=False).encode("utf-8"),
                      ContentType="application/json")
    except Exception as e:
        return {"error": f"Storage: {type(e).__name__}: {e}"}
    return {"ok": True, "id": aid}


def _assignment_list(student_code=None):
    try:
        s3 = _s3()
        result = []
        paginator = s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=BUCKET_NAME, Prefix="assignments/"):
            for obj in page.get("Contents", []):
                if not obj["Key"].endswith(".json"):
                    continue
                try:
                    o = s3.get_object(Bucket=BUCKET_NAME, Key=obj["Key"])
                    m = json.loads(o["Body"].read().decode("utf-8"))
                    if student_code and m.get("student_code") != student_code:
                        continue
                    result.append({
                        "id": m.get("id"),
                        "student_code": m.get("student_code"),
                        "task_type": m.get("task_type"),
                        "bank_code": m.get("bank_code"),
                        "note": m.get("note", ""),
                        "created_at": m.get("created_at", 0),
                    })
                except Exception:
                    pass
        result.sort(key=lambda x: x.get("created_at", 0), reverse=True)
        return {"assignments": result, "count": len(result)}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


def _assignment_get(aid):
    try:
        s3 = _s3()
        o = s3.get_object(Bucket=BUCKET_NAME, Key=_assignment_key(aid))
        return json.loads(o["Body"].read().decode("utf-8"))
    except Exception:
        return None


def _assignment_delete(aid):
    try:
        s3 = _s3()
        s3.delete_object(Bucket=BUCKET_NAME, Key=_assignment_key(aid))
        return {"ok": True, "id": aid}
    except Exception as e:
        return {"error": str(e)}
# ============================================================
# ВАРИАНТЫ
# ============================================================
def _variant_meta_key(vid):
    return f"variants/{vid}/meta.json"


def _variant_data_key(vid):
    return f"variants/{vid}/data.json"


def _variant_assigned_key(vid):
    return f"variants/{vid}/assigned.json"


def _variant_next_code():
    try:
        s3 = _s3()
        existing = set()
        paginator = s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=BUCKET_NAME, Prefix="variants/"):
            for obj in page.get("Contents", []):
                k = obj["Key"]
                m = re.match(r'variants/V-(\d+)/meta\.json$', k)
                if m:
                    existing.add(int(m.group(1)))
        n = 1
        while n in existing:
            n += 1
        return f"V-{n:03d}"
    except Exception:
        return "V-" + uuid.uuid4().hex[:6].upper()


def _resolve_topic(topic):
    if not topic or topic == "any":
        return "Любая (по выбору модели)"
    if topic == "random":
        letter = random.choice(list(TOPIC_MAP.keys()))
        return TOPIC_MAP[letter]
    for letter, full in TOPIC_MAP.items():
        if full.lower() in topic.lower() or letter == topic.strip():
            return full
    return topic


def generate_variant(topic_config):
    RAW_PIPELINES = {
        "1": generate_task_1, "2": generate_task_2, "3-9": generate_task_3_9,
        "10": generate_task_10, "11": generate_task_11, "12-18": generate_task_12_18,
        "19-24": generate_task_19_24, "25-29": generate_task_25_29,
        "30-36": generate_task_30_36, "37": generate_task_37,
        "38.1": generate_task_38_1, "38.2": generate_task_38_2,
    }
    result = {}
    chosen_topics = {}
    for tt in VARIANT_TASKS:
        raw = topic_config.get(tt) or "any"
        topic = _resolve_topic(raw)
        chosen_topics[tt] = topic
        print(f"[variant] генерирую задание {tt} (тема: {topic})")
        gen = RAW_PIPELINES[tt](topic)
        if isinstance(gen, dict) and "error" in gen:
            return {"error": f"Ошибка в задании {tt}: {gen['error']}"}
        result[tt] = gen

    print("[variant] генерирую объяснения батчем…")
    _batch_explanations_for_variant(result)

    return {"ok": True, "tasks": result, "chosen_topics": chosen_topics}


def _batch_explanations_for_variant(tasks):
    test_types = [t for t in ["1","2","3-9","10","11","12-18","19-24","25-29","30-36"] if t in tasks]
    if not test_types:
        return
    chunks = []
    for tt in test_types:
        chunks.append(f"===== TASK TYPE {tt} =====")
        chunks.append(_task_content_for_explanations(tt, tasks[tt]))
        chunks.append("")
    body = "\n".join(chunks)

    prompt = (
        "You are an EGE English exam expert. Below are several tasks. For EACH task, "
        "briefly explain (1-2 sentences in RUSSIAN) why each correct answer is correct. "
        "Reference the script or text.\n\n"
        "Return ONLY valid JSON: {\"task_type\": {\"key\": \"explanation\", ...}, ...}\n"
        "Keys inside each task_type:\n"
        "- 1: A..F\n- 2: A..G\n- 3-9: 3..9\n- 10: A..G\n- 11: A..F\n"
        "- 12-18: 12..18\n- 19-24: 19..24\n- 25-29: 25..29\n- 30-36: 30..36\n\n"
        "Keep explanations SHORT and concrete.\n\n"
        + body
    )
    r = call_llm(prompt, retries=1)
    if "error" in r:
        print(f"[variant-explanations] {r['error']}")
        return
    for tt in test_types:
        exps = r.get(tt) or {}
        if isinstance(exps, dict) and exps:
            clean = {str(k): v.strip() for k, v in exps.items() if isinstance(v, str) and v.strip()}
            if clean:
                tasks[tt]["explanations"] = clean


def _variant_create(tasks_data, topic_config):
    vid = "V-" + uuid.uuid4().hex[:8].upper()
    code = _variant_next_code()
    now = int(time.time())
    task_types = [t for t in VARIANT_TASKS if t in tasks_data]
    meta = {
        "id": vid,
        "code": code,
        "created_at": now,
        "task_types": task_types,
        "topic_config": topic_config,
        "test_max": variant_test_max(task_types),
        "total_max": variant_total_max(task_types),
    }
    try:
        s3 = _s3()
        s3.put_object(Bucket=BUCKET_NAME, Key=_variant_meta_key(vid),
                      Body=json.dumps(meta, ensure_ascii=False).encode("utf-8"),
                      ContentType="application/json")
        s3.put_object(Bucket=BUCKET_NAME, Key=_variant_data_key(vid),
                      Body=json.dumps(tasks_data, ensure_ascii=False).encode("utf-8"),
                      ContentType="application/json")
        s3.put_object(Bucket=BUCKET_NAME, Key=_variant_assigned_key(vid),
                      Body=json.dumps({"students": []}, ensure_ascii=False).encode("utf-8"),
                      ContentType="application/json")
    except Exception as e:
        return {"error": f"Storage: {type(e).__name__}: {e}"}
    return {"ok": True, "id": vid, "code": code}


def _variant_get(vid):
    try:
        s3 = _s3()
        m = s3.get_object(Bucket=BUCKET_NAME, Key=_variant_meta_key(vid))
        meta = json.loads(m["Body"].read().decode("utf-8"))
        d = s3.get_object(Bucket=BUCKET_NAME, Key=_variant_data_key(vid))
        meta["data"] = json.loads(d["Body"].read().decode("utf-8"))
        try:
            a = s3.get_object(Bucket=BUCKET_NAME, Key=_variant_assigned_key(vid))
            meta["assigned"] = json.loads(a["Body"].read().decode("utf-8")).get("students", [])
        except Exception:
            meta["assigned"] = []
        return meta
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


def _variant_list():
    try:
        s3 = _s3()
        result = []
        paginator = s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=BUCKET_NAME, Prefix="variants/"):
            for obj in page.get("Contents", []):
                k = obj["Key"]
                if not k.endswith("/meta.json"):
                    continue
                try:
                    o = s3.get_object(Bucket=BUCKET_NAME, Key=k)
                    m = json.loads(o["Body"].read().decode("utf-8"))
                    result.append({
                        "id": m.get("id"),
                        "code": m.get("code"),
                        "created_at": m.get("created_at", 0),
                        "task_types": m.get("task_types", []),
                        "total_max": m.get("total_max", 0),
                        "test_max": m.get("test_max", 0),
                    })
                except Exception:
                    pass
        result.sort(key=lambda x: x.get("created_at", 0), reverse=True)
        return {"variants": result, "count": len(result)}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


def _variant_assign(vid, student_codes):
    if isinstance(student_codes, str):
        student_codes = [student_codes]
    try:
        s3 = _s3()
        try:
            a = s3.get_object(Bucket=BUCKET_NAME, Key=_variant_assigned_key(vid))
            data = json.loads(a["Body"].read().decode("utf-8"))
        except Exception:
            data = {"students": []}
        for sc in student_codes:
            if sc and sc not in data["students"]:
                data["students"].append(sc)
        s3.put_object(Bucket=BUCKET_NAME, Key=_variant_assigned_key(vid),
                      Body=json.dumps(data, ensure_ascii=False).encode("utf-8"),
                      ContentType="application/json")
        return {"ok": True, "assigned": data["students"]}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


def _variant_delete(vid):
    try:
        s3 = _s3()
        for suffix in ("meta.json", "data.json", "assigned.json"):
            try:
                s3.delete_object(Bucket=BUCKET_NAME, Key=f"variants/{vid}/{suffix}")
            except Exception:
                pass
        return {"ok": True}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


def _variant_list_for_student(student_code):
    try:
        s3 = _s3()
        result = []
        paginator = s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=BUCKET_NAME, Prefix="variants/"):
            for obj in page.get("Contents", []):
                k = obj["Key"]
                if not k.endswith("/assigned.json"):
                    continue
                try:
                    o = s3.get_object(Bucket=BUCKET_NAME, Key=k)
                    data = json.loads(o["Body"].read().decode("utf-8"))
                    if student_code in data.get("students", []):
                        vid = k.split("/")[1]
                        try:
                            mo = s3.get_object(Bucket=BUCKET_NAME, Key=_variant_meta_key(vid))
                            meta = json.loads(mo["Body"].read().decode("utf-8"))
                            result.append(meta)
                        except Exception:
                            pass
                except Exception:
                    pass
        result.sort(key=lambda x: x.get("created_at", 0), reverse=True)
        return result
    except Exception:
        return []


def _variant_submission_key(student_code, vid):
    return f"variant_submissions/{student_code}/{vid}.json"


def _variant_submit(student_code, vid, answers):
    if not student_code or not vid:
        return {"error": "Нужны student_code и variant_id"}
    v = _variant_get(vid)
    if "error" in v:
        return v
    data = v.get("data", {})
    scores = {}
    total_score = 0
    total_max = 0
    test_score = 0
    test_max = 0
    manual_pending = []
    has_manual = False

    for task_type, task_data in data.items():
        cfg = VARIANT_SCORING.get(task_type)
        if not cfg:
            continue
        if cfg.get("manual"):
            has_manual = True
            ans_obj = answers.get(task_type) or {}
            txt = ans_obj.get("text", "") if isinstance(ans_obj, dict) else ""
            scores[task_type] = {
                "score": None,
                "max": cfg["max"],
                "manual": True,
                "pending": True,
                "student_answer": txt,
            }
            manual_pending.append(task_type)
            total_max += cfg["max"]
        else:
            key = task_data.get("answer_key", {})
            student_ans = answers.get(task_type, {})
            r = score_test_task(task_type, student_ans, key)
            if r:
                r["student_answer"] = student_ans
                scores[task_type] = r
                total_score += r["score"]
                total_max += r["max"]
                test_score += r["score"]
                test_max += r["max"]

    now = int(time.time())
    sub = {
        "student_code": student_code,
        "variant_id": vid,
        "variant_code": v.get("code"),
        "answers": answers,
        "scores": scores,
        "total_score": total_score,
        "total_max": total_max,
        "test_score": test_score,
        "test_max": test_max,
        "manual_pending": manual_pending,
        "status": "submitted" if has_manual else "reviewed",
        "submitted_at": now,
        "updated_at": now,
    }
    try:
        s3 = _s3()
        s3.put_object(Bucket=BUCKET_NAME,
                      Key=_variant_submission_key(student_code, vid),
                      Body=json.dumps(sub, ensure_ascii=False).encode("utf-8"),
                      ContentType="application/json")
    except Exception as e:
        return {"error": f"Storage: {type(e).__name__}: {e}"}
    return {"ok": True, "submission": sub}


def _variant_get_submission(student_code, vid):
    try:
        s3 = _s3()
        o = s3.get_object(Bucket=BUCKET_NAME,
                          Key=_variant_submission_key(student_code, vid))
        return json.loads(o["Body"].read().decode("utf-8"))
    except Exception:
        return None


def _variant_review_manual(student_code, vid, task_type, scores, comment):
    sub = _variant_get_submission(student_code, vid)
    if not sub:
        return {"error": "Работа не найдена"}
    if task_type not in ("37", "38.1", "38.2"):
        return {"error": "Ручная проверка только для 37/38"}

    crit = CRITERIA_BY_TYPE.get(task_type)
    if not crit:
        return {"error": "Нет критериев"}

    clean = {}
    for c in crit["criteria"]:
        code = c["code"]
        raw = (scores or {}).get(code, 0)
        try:
            val = int(raw)
        except Exception:
            val = 0
        if val < 0:
            val = 0
        if val > c["max"]:
            val = c["max"]
        clean[code] = val
    if crit.get("rule_k1_zero") and clean.get("К1", 0) == 0:
        for code in clean:
            clean[code] = 0
    total = sum(clean.values())

    scores_map = sub.setdefault("scores", {})
    entry = scores_map.get(task_type) or {}
    entry["score"] = total
    entry["max"] = crit["max_total"]
    entry["manual"] = True
    entry["pending"] = False
    entry["review"] = {
        "scores": clean,
        "total": total,
        "max_total": crit["max_total"],
        "comment": (comment or "").strip(),
        "reviewed_at": int(time.time()),
    }
    scores_map[task_type] = entry

    total_score = 0
    total_max = 0
    test_score = 0
    test_max = 0
    manual_pending = []
    for tt, e in scores_map.items():
        cfg = VARIANT_SCORING.get(tt)
        if not cfg:
            continue
        if cfg.get("manual"):
            total_max += cfg["max"]
            if e.get("pending"):
                manual_pending.append(tt)
            else:
                total_score += int(e.get("score") or 0)
        else:
            total_max += cfg["max"]
            total_score += int(e.get("score") or 0)
            test_score += int(e.get("score") or 0)
            test_max += cfg["max"]

    sub["total_score"] = total_score
    sub["total_max"] = total_max
    sub["test_score"] = test_score
    sub["test_max"] = test_max
    sub["manual_pending"] = manual_pending
    sub["status"] = "submitted" if manual_pending else "reviewed"
    sub["updated_at"] = int(time.time())

    try:
        s3 = _s3()
        s3.put_object(Bucket=BUCKET_NAME,
                      Key=_variant_submission_key(student_code, vid),
                      Body=json.dumps(sub, ensure_ascii=False).encode("utf-8"),
                      ContentType="application/json")
    except Exception as e:
        return {"error": f"Storage: {type(e).__name__}: {e}"}
    return {"ok": True, "score": total, "max": crit["max_total"]}


def _variant_list_submissions(student_code):
    try:
        s3 = _s3()
        result = []
        paginator = s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=BUCKET_NAME,
                                       Prefix=f"variant_submissions/{student_code}/"):
            for obj in page.get("Contents", []):
                if not obj["Key"].endswith(".json"):
                    continue
                try:
                    o = s3.get_object(Bucket=BUCKET_NAME, Key=obj["Key"])
                    m = json.loads(o["Body"].read().decode("utf-8"))
                    result.append(m)
                except Exception:
                    pass
        result.sort(key=lambda x: x.get("submitted_at") or 0, reverse=True)
        return result
    except Exception:
        return []


def _variant_list_pending_manual():
    try:
        s3 = _s3()
        result = []
        paginator = s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=BUCKET_NAME, Prefix="variant_submissions/"):
            for obj in page.get("Contents", []):
                if not obj["Key"].endswith(".json"):
                    continue
                try:
                    o = s3.get_object(Bucket=BUCKET_NAME, Key=obj["Key"])
                    m = json.loads(o["Body"].read().decode("utf-8"))
                    if m.get("status") != "submitted":
                        continue
                    for tt in m.get("manual_pending", []):
                        sc = m.get("student_code")
                        st = _student_get(sc) or {}
                        result.append({
                            "kind": "variant",
                            "variant_id": m.get("variant_id"),
                            "variant_code": m.get("variant_code"),
                            "student_code": sc,
                            "student_name": ((st.get("surname", "") + " " +
                                              st.get("name", "")).strip() or sc),
                            "task_type": tt,
                            "submitted_at": m.get("submitted_at"),
                        })
                except Exception:
                    pass
        result.sort(key=lambda x: x.get("submitted_at") or 0)
        return result
    except Exception:
        return []
def _rl_hash(s):
    return hashlib.sha256((RATELIMIT_SALT + "|" + str(s)).encode("utf-8")).hexdigest()[:24]


def _rl_key_ip(ip):
    return f"ratelimit/ip_{_rl_hash(ip)}.json"


def _rl_key_cid(cid):
    return f"ratelimit/cid_{_rl_hash(cid)}.json"


def _rl_read(key):
    try:
        s3 = _s3()
        o = s3.get_object(Bucket=BUCKET_NAME, Key=key)
        return json.loads(o["Body"].read().decode("utf-8"))
    except Exception:
        return None


def _rl_write(key, data):
    try:
        s3 = _s3()
        s3.put_object(Bucket=BUCKET_NAME, Key=key,
                      Body=json.dumps(data, ensure_ascii=False).encode("utf-8"),
                      ContentType="application/json")
    except Exception as e:
        print(f"[ratelimit] write error: {e}")


def _rl_audit(event, ip_hash=None, cid_hash=None, used_ip=0, used_cid=0, note=""):
    try:
        key = "ratelimit/_audit.json"
        s3 = _s3()
        try:
            o = s3.get_object(Bucket=BUCKET_NAME, Key=key)
            log = json.loads(o["Body"].read().decode("utf-8"))
        except Exception:
            log = {"events": []}
        log.setdefault("events", []).append({
            "ts": int(time.time()),
            "event": event,
            "ip_hash": ip_hash,
            "cid_hash": cid_hash,
            "used_ip": used_ip,
            "used_cid": used_cid,
            "note": note,
        })
        log["events"] = log["events"][-RATELIMIT_AUDIT_LIMIT:]
        s3.put_object(Bucket=BUCKET_NAME, Key=key,
                      Body=json.dumps(log, ensure_ascii=False).encode("utf-8"),
                      ContentType="application/json")
    except Exception as e:
        print(f"[ratelimit] audit error: {e}")


def _extract_ip(event):
    try:
        rc = event.get("requestContext") or {}
        ident = rc.get("identity") or {}
        ip = ident.get("sourceIp")
        if ip:
            return ip
    except Exception:
        pass
    headers = event.get("headers") or {}
    for k, v in headers.items():
        if k.lower() == "x-forwarded-for" and v:
            return v.split(",")[0].strip()
    return "unknown"


def _cid_valid(cid):
    if not cid:
        return False
    return bool(re.match(r'^[a-f0-9\-]{16,64}$', str(cid).lower()))


def _ratelimit_check(ip, cid):
    if not RATELIMIT_ENABLED:
        return {"allowed": True, "used": 0, "left": RATELIMIT_MAX,
                "reason": "disabled", "ip_hash": None, "cid_hash": None}
    if ip in RATELIMIT_IP_WHITELIST:
        return {"allowed": True, "used": 0, "left": RATELIMIT_MAX,
                "reason": "ip_whitelist", "ip_hash": None, "cid_hash": None}
    ip_hash = _rl_hash(ip) if ip and ip != "unknown" else None
    cid_hash = _rl_hash(cid) if _cid_valid(cid) else None
    if cid_hash and cid_hash in RATELIMIT_CID_WHITELIST:
        return {"allowed": True, "used": 0, "left": RATELIMIT_MAX,
                "reason": "cid_whitelist", "ip_hash": ip_hash, "cid_hash": cid_hash}
    used_ip = 0
    used_cid = 0
    if ip_hash:
        rec = _rl_read(_rl_key_ip(ip_hash)) or {}
        used_ip = int(rec.get("used", 0))
    if cid_hash:
        rec = _rl_read(_rl_key_cid(cid_hash)) or {}
        used_cid = int(rec.get("used", 0))
    used = max(used_ip, used_cid)
    left = max(0, RATELIMIT_MAX - used)
    allowed = used < RATELIMIT_MAX
    reason = "ok" if allowed else "limit_exceeded"
    return {"allowed": allowed, "used": used, "left": left,
            "reason": reason, "ip_hash": ip_hash, "cid_hash": cid_hash}


def _ratelimit_increment(ip_hash, cid_hash):
    if not RATELIMIT_ENABLED:
        return
    now = int(time.time())
    if ip_hash:
        key = _rl_key_ip(ip_hash)
        rec = _rl_read(key) or {"used": 0, "first_seen": now}
        rec["used"] = int(rec.get("used", 0)) + 1
        rec["last_seen"] = now
        _rl_write(key, rec)
    if cid_hash:
        key = _rl_key_cid(cid_hash)
        rec = _rl_read(key) or {"used": 0, "first_seen": now}
        rec["used"] = int(rec.get("used", 0)) + 1
        rec["last_seen"] = now
        _rl_write(key, rec)


def _ratelimit_admin_list():
    try:
        s3 = _s3()
        result = []
        paginator = s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=BUCKET_NAME, Prefix="ratelimit/"):
            for obj in page.get("Contents", []):
                k = obj["Key"]
                if not k.endswith(".json") or k.endswith("_audit.json"):
                    continue
                try:
                    o = s3.get_object(Bucket=BUCKET_NAME, Key=k)
                    rec = json.loads(o["Body"].read().decode("utf-8"))
                    kind = "ip" if "/ip_" in k else "cid" if "/cid_" in k else "?"
                    h = k.split("_", 1)[1].replace(".json", "") if "_" in k else k
                    result.append({
                        "key": k, "kind": kind, "hash": h,
                        "used": int(rec.get("used", 0)),
                        "first_seen": rec.get("first_seen", 0),
                        "last_seen": rec.get("last_seen", 0),
                    })
                except Exception:
                    pass
        result.sort(key=lambda x: x.get("last_seen", 0), reverse=True)
        return {"records": result, "count": len(result)}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


def _ratelimit_admin_reset(key):
    try:
        s3 = _s3()
        if key == "all":
            paginator = s3.get_paginator("list_objects_v2")
            to_del = []
            for page in paginator.paginate(Bucket=BUCKET_NAME, Prefix="ratelimit/"):
                for obj in page.get("Contents", []):
                    k = obj["Key"]
                    if k.endswith(".json") and not k.endswith("_audit.json"):
                        to_del.append(k)
            for k in to_del:
                try:
                    s3.delete_object(Bucket=BUCKET_NAME, Key=k)
                except Exception:
                    pass
            return {"ok": True, "deleted": len(to_del)}
        s3.delete_object(Bucket=BUCKET_NAME, Key=key)
        return {"ok": True, "deleted": 1}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


def _ratelimit_admin_audit():
    try:
        s3 = _s3()
        o = s3.get_object(Bucket=BUCKET_NAME, Key="ratelimit/_audit.json")
        log = json.loads(o["Body"].read().decode("utf-8"))
        events = log.get("events", [])
        events = list(reversed(events[-RATELIMIT_AUDIT_LIMIT:]))
        return {"events": events, "count": len(events)}
    except Exception:
        return {"events": [], "count": 0}
 # ============================================================
# ГЕНЕРАЦИЯ ОБЪЯСНЕНИЙ К ЗАДАНИЯМ 1–36
# ============================================================
EXPLANATION_PROMPT = """You are an EGE English exam expert. For each task below, briefly explain (1-2 sentences in RUSSIAN) why the correct answer is correct. Reference the audio script or text.

Return ONLY valid JSON in this exact format:
{"explanations": {"<key>": "<explanation>", ...}}

Task type: {task_type}

{content}

For task 1: keys A..F
For task 2: keys A..G
For task 3-9: keys 3..9
For task 10: keys A..G
For task 11: keys A..F
For task 12-18: keys 12..18
For task 19-24: keys 19..24
For task 25-29: keys 25..29
For task 30-36: keys 30..36

Keep explanations SHORT and concrete. Mention the key phrase from the text/script."""


def _task_content_for_explanations(task_type, task_data):
    parts = []
    if task_type == "1":
        parts.append("STATEMENTS:")
        for s in task_data.get("statements", []):
            parts.append(f"  {s.get('number')}. {s.get('text','')}")
        parts.append("\nSPEAKERS (audio scripts):")
        for s in task_data.get("scripts", []):
            parts.append(f"  Speaker {s.get('speaker')}: {s.get('text','')}")
        parts.append(f"\nCORRECT ANSWERS: {json.dumps(task_data.get('answer_key',{}), ensure_ascii=False)}")
        parts.append(f"EXTRA (unused) STATEMENT: {task_data.get('extra_statement','')}")
    elif task_type == "2":
        parts.append("STATEMENTS:")
        for s in task_data.get("statements", []):
            parts.append(f"  {s.get('letter')}. {s.get('text','')}")
        parts.append("\nDIALOGUE:")
        for e in task_data.get("dialogue_script", []):
            parts.append(f"  {e.get('speaker')}: {e.get('text','')}")
        parts.append(f"\nCORRECT ANSWERS (1=True, 2=False, 3=Not stated): {json.dumps(task_data.get('answer_key',{}), ensure_ascii=False)}")
    elif task_type == "3-9":
        parts.append("QUESTIONS:")
        for q in task_data.get("questions", []):
            parts.append(f"  {q.get('number')}. {q.get('question','')}")
            for k, v in (q.get("options") or {}).items():
                parts.append(f"     {k}) {v}")
        parts.append("\nINTERVIEW:")
        for e in task_data.get("interview_script", []):
            parts.append(f"  {e.get('speaker')}: {e.get('text','')}")
        parts.append(f"\nCORRECT ANSWERS: {json.dumps(task_data.get('answer_key',{}), ensure_ascii=False)}")
    elif task_type == "10":
        parts.append("HEADINGS:")
        for h in task_data.get("headings", []):
            parts.append(f"  {h.get('number')}. {h.get('text','')}")
        parts.append("\nTEXTS:")
        for t in task_data.get("texts", []):
            parts.append(f"  {t.get('letter')}. {t.get('text','')}")
        parts.append(f"\nCORRECT ANSWERS: {json.dumps(task_data.get('answer_key',{}), ensure_ascii=False)}")
        parts.append(f"EXTRA (unused) HEADING: {task_data.get('extra_heading','')}")
    elif task_type == "11":
        parts.append("TEXT WITH GAPS:")
        parts.append(task_data.get("text", ""))
        parts.append("\nFRAGMENTS:")
        for f in task_data.get("fragments", []):
            parts.append(f"  {f.get('number')}. {f.get('text','')}")
        parts.append(f"\nCORRECT ANSWERS: {json.dumps(task_data.get('answer_key',{}), ensure_ascii=False)}")
        parts.append(f"EXTRA (unused) FRAGMENT: {task_data.get('extra_fragment','')}")
    elif task_type == "12-18":
        parts.append(f"TITLE: {task_data.get('title','')}")
        parts.append(f"\nTEXT:\n{task_data.get('text','')}")
        parts.append("\nQUESTIONS:")
        for q in task_data.get("questions", []):
            parts.append(f"  {q.get('number')}. {q.get('question','')}")
            for k, v in (q.get("options") or {}).items():
                parts.append(f"     {k}) {v}")
        parts.append(f"\nCORRECT ANSWERS: {json.dumps(task_data.get('answer_key',{}), ensure_ascii=False)}")
    elif task_type in ("19-24", "25-29"):
        parts.append(f"TITLE: {task_data.get('title','')}")
        parts.append(f"\nTEXT:\n{task_data.get('text','')}")
        parts.append("\nBASE WORDS:")
        for it in task_data.get("items", []):
            parts.append(f"  {it.get('number')}. {it.get('source_word','')}")
        parts.append(f"\nCORRECT ANSWERS: {json.dumps(task_data.get('answer_key',{}), ensure_ascii=False)}")
    elif task_type == "30-36":
        parts.append(f"TITLE: {task_data.get('title','')}")
        parts.append(f"\nTEXT:\n{task_data.get('text','')}")
        parts.append("\nITEMS:")
        for it in task_data.get("items", []):
            parts.append(f"  {it.get('number')}:")
            for k, v in (it.get("options") or {}).items():
                parts.append(f"     {k}) {v}")
        parts.append(f"\nCORRECT ANSWERS: {json.dumps(task_data.get('answer_key',{}), ensure_ascii=False)}")
    return "\n".join(parts)


def generate_explanations(task_type, task_data):
    if task_type in ("37", "38.1", "38.2"):
        return None
    content = _task_content_for_explanations(task_type, task_data)
    if not content.strip():
        return None
    prompt = EXPLANATION_PROMPT.replace("{task_type}", task_type).replace("{content}", content)
    r = call_llm(prompt, retries=1)
    if "error" in r:
        print(f"[explanations] {task_type}: {r['error']}")
        return None
    exps = r.get("explanations") or {}
    if not isinstance(exps, dict) or not exps:
        return None
    clean = {}
    for k, v in exps.items():
        if isinstance(v, str) and v.strip():
            clean[str(k)] = v.strip()
    return clean if clean else None


def _attach_explanations(task_type, task_data):
    if not isinstance(task_data, dict) or "error" in task_data:
        return task_data
    if task_type in ("37", "38.1", "38.2"):
        return task_data
    if task_data.get("explanations"):
        return task_data
    exps = generate_explanations(task_type, task_data)
    if exps:
        task_data["explanations"] = exps
    return task_data


def generate_task_1(topic):
    p1 = _fill(PROMPT_1_STATEMENTS, TOPIC=topic, TOPIC_LIST="", LEVEL="B1")
    r1 = call_llm(p1)
    if "error" in r1:
        return r1
    statements = r1.get("statements", [])
    if len(statements) != 7:
        return {"error": f"Утверждений {len(statements)}, ожидалось 7"}
    p2 = _fill(PROMPT_1_MONOLOGUES, TOPIC=topic, STATEMENTS=json.dumps(statements, ensure_ascii=False))
    r2 = call_llm(p2)
    if "error" in r2:
        return r2
    scripts = r2.get("scripts", [])
    if len(scripts) != 6:
        return {"error": f"Монологов {len(scripts)}, ожидалось 6"}
    return {
        "instruction": ("Вы услышите 6 высказываний. Установите соответствие между высказываниями "
                        "каждого говорящего А–F и утверждениями, данными в списке 1–7. Используйте "
                        "каждое утверждение, обозначенное соответствующей цифрой, только один раз. "
                        "В задании есть одно лишнее утверждение. Вы услышите запись дважды. "
                        "Занесите свои ответы в таблицу."),
        "statements": statements, "scripts": scripts,
        "answer_key": r2.get("answer_key", {}),
        "extra_statement": r2.get("extra_statement", 0),
    }


def generate_task_2(topic):
    p1 = _fill(PROMPT_2_STATEMENTS, TOPIC=topic)
    r1 = call_llm(p1)
    if "error" in r1:
        return r1
    st_raw = r1.get("statements", [])
    sp1 = r1.get("speaker_1_name", "").strip() or "Harry"
    sp2 = r1.get("speaker_2_name", "").strip() or "Chloe"
    if len(st_raw) != 7:
        return {"error": f"Утверждений {len(st_raw)}, ожидалось 7"}
    p2 = _fill(PROMPT_2_DIALOGUE, TOPIC=topic,
               SPEAKER_1=sp1, SPEAKER_2=sp2,
               STATEMENTS=json.dumps(st_raw, ensure_ascii=False))
    r2 = call_llm(p2)
    if "error" in r2:
        return r2
    dialogue = r2.get("dialogue_script", [])
    if not dialogue:
        return {"error": "Диалог не сгенерирован"}
    return {
        "instruction": ("Вы услышите диалог. Определите, какие из приведённых утверждений А–G "
                        "соответствуют содержанию текста (1 – True), какие не соответствуют "
                        "(2 – False) и о чём в тексте не сказано (3 – Not stated). "
                        "Занесите номер выбранного Вами варианта ответа в таблицу. Вы услышите запись дважды."),
        "statements": [{"letter": s["letter"], "text": s["text"]} for s in st_raw],
        "answer_key": {s["letter"]: s.get("target_answer", 1) for s in st_raw},
        "dialogue_script": dialogue,
        "script": "\n".join(f"{e['speaker']}: {e['text']}" for e in dialogue),
    }


def generate_task_3_9(topic):
    p1 = _fill(PROMPT_3_9_QUESTIONS, TOPIC=topic)
    r1 = call_llm(p1)
    if "error" in r1:
        return r1
    q_raw = r1.get("questions", [])
    if len(q_raw) != 7:
        return {"error": f"Вопросов {len(q_raw)}, ожидалось 7"}
    p2 = _fill(PROMPT_3_9_SCRIPT, TOPIC=topic, QUESTIONS=json.dumps(q_raw, ensure_ascii=False))
    r2 = call_llm(p2)
    if "error" in r2:
        return r2
    script = r2.get("interview_script", [])
    if not script:
        return {"error": "Интервью не сгенерировано"}
    questions, answer_key = [], {}
    for q in q_raw:
        num = q.get("id") or q.get("number")
        opts_arr = q.get("options", [])
        opts = ({"1": opts_arr[0], "2": opts_arr[1], "3": opts_arr[2]}
                if isinstance(opts_arr, list) else opts_arr)
        questions.append({"number": num, "question": q["question"], "options": opts})
        answer_key[str(num)] = str(q.get("correct"))
    questions, answer_key = _balance_choice_keys(questions, answer_key, 3)
    return {
        "instruction": ("Вы услышите интервью. В заданиях 3–9 запишите в поле ответа цифру 1, 2 или 3, "
                        "соответствующую выбранному Вами варианту ответа. Вы услышите запись дважды."),
        "questions": questions, "answer_key": answer_key,
        "interview_script": script,
        "script": "\n".join(f"{e['speaker']}: {e['text']}" for e in script),
    }


def generate_task_10(topic):
    p1 = _fill(PROMPT_10_HEADERS, TOPIC=topic)
    r1 = call_llm(p1)
    if "error" in r1:
        return r1
    headers = r1.get("headers", [])
    if len(headers) != 8:
        return {"error": f"Заголовков {len(headers)}, ожидалось 8"}
    headers_json = json.dumps(headers, ensure_ascii=False)
    p2 = _fill(PROMPT_10_TEXTS, TOPIC=topic,
               COMMON_SUBJECT=r1.get("common_subject", ""),
               HEADERS_LIST=headers_json)
    r2 = call_llm(p2)
    if "error" in r2:
        return r2
    texts = r2.get("texts", [])
    if len(texts) != 7:
        return {"error": f"Текстов {len(texts)}, ожидалось 7"}
    return {
        "instruction": ("Установите соответствие между текстами A–G и заголовками 1–8. "
                        "Занесите свои ответы в таблицу. Используйте каждую цифру только один раз. "
                        "В задании один заголовок лишний."),
        "headings": headers,
        "texts": [{"letter": t["letter"], "text": t["text"]} for t in texts],
        "answer_key": r2.get("answer_key", {}),
        "extra_heading": r2.get("extra_header_number", 0),
    }


def generate_task_11(topic):
    p1 = _fill(PROMPT_11_FRAGMENTS, TOPIC=topic)
    r1 = call_llm(p1)
    if "error" in r1:
        return r1
    fragments = r1.get("fragments", [])
    if len(fragments) != 7:
        return {"error": f"Фрагментов {len(fragments)}, ожидалось 7"}
    frag_json = json.dumps(fragments, ensure_ascii=False)
    p2 = _fill(PROMPT_11_TEXT, TOPIC=topic, FRAGMENTS_LIST=frag_json)
    r2 = call_llm(p2)
    if "error" in r2:
        return r2
    return {
        "instruction": ("Прочитайте текст и заполните пропуски A–F частями предложений, "
                        "обозначенными цифрами 1–7. Одна из частей в списке 1–7 лишняя. "
                        "Занесите цифры, обозначающие соответствующие части предложений, в таблицу."),
        "title": r2.get("title", ""),
        "text": r2.get("text_with_gaps", ""),
        "fragments": [{"number": f["number"], "text": f["text"]} for f in fragments],
        "answer_key": r2.get("answer_key", {}),
        "extra_fragment": r2.get("extra_fragment_number", 0),
    }


def generate_task_12_18(topic):
    base_prompt = _fill(PROMPT_12_18_TEXT, TOPIC=topic)
    r = call_llm(base_prompt)
    if "error" in r:
        return r
    paras = r.get("paragraphs", [])
    title = r.get("title", "")
    text_plain = "\n\n".join(pp.get("text", "") for pp in paras)
    text_marked = "\n\n".join(f"[Paragraph {p['number']}] {p['text']}" for p in paras)
    p2 = _fill(PROMPT_12_18_QUESTIONS, GENERATED_TEXT=text_marked)
    r2 = call_llm(p2)
    if "error" in r2:
        return r2
    q_raw = r2.get("questions", [])
    if len(q_raw) != 7:
        return {"error": f"Вопросов {len(q_raw)}, ожидалось 7"}
    questions, answer_key = [], {}
    for q in q_raw:
        num = q.get("id") or q.get("number")
        opts_arr = q.get("options", [])
        opts = ({"1": opts_arr[0], "2": opts_arr[1], "3": opts_arr[2], "4": opts_arr[3]}
                if isinstance(opts_arr, list) else opts_arr)
        questions.append({"number": num, "question": q["question"], "options": opts})
        answer_key[str(num)] = str(q.get("correct"))
    questions, answer_key = _balance_choice_keys(questions, answer_key, 4)
    return {
        "instruction": ("Прочитайте текст и выполните задания 12–18. В каждом задании запишите "
                        "в поле ответа цифру 1, 2, 3 или 4, соответствующую выбранному Вами "
                        "варианту ответа."),
        "title": title, "text": text_plain,
        "questions": questions, "answer_key": answer_key,
    }


def _grammar_items(schema):
    return [{"number": t["id"], "source_word": t.get("base_word", "")}
            for t in schema.get("tasks", [])]


def _grammar_key(schema):
    return {str(t["id"]): (t.get("target_form") or t.get("target_word") or "")
            for t in schema.get("tasks", [])}


def _fix_gaps(text):
    text = re.sub(r'___\s*\((\d+)\)', r'__\1__', text)
    text = re.sub(r'\(\s*(\d+)\s*\)\s*___', r'__\1__', text)
    text = re.sub(r'___\s*(\d+)', r'__\1__', text)
    return text


def _strip_base_words_from_text(text, base_words):
    for w in base_words:
        if not w:
            continue
        text = re.sub(r'\s+' + re.escape(w) + r'\b', '', text)
    return text


def generate_task_19_24(topic):
    p1 = _fill(PROMPT_19_24_SCHEMA, TOPIC=topic)
    r1 = call_llm(p1)
    if "error" in r1:
        return r1
    schema = r1
    if len(schema.get("tasks", [])) != 6:
        return {"error": "Схема неполная"}
    fmt = schema.get("chosen_format", "format_1")
    matrix = {"chosen_format": fmt, "tasks": [
        {"id": t.get("id"), "base_word": t.get("base_word"),
         "part_of_speech": t.get("part_of_speech"), "target_form": t.get("target_form")}
        for t in schema["tasks"]]}
    base_words = [t.get("base_word", "") for t in schema["tasks"]]
    p2 = _fill(PROMPT_19_24_TEXT, TOPIC=topic, CHOSEN_FORMAT=fmt,
               GRAMMAR_MATRIX=json.dumps(matrix, ensure_ascii=False))
    r2 = call_llm(p2)
    if "error" in r2:
        return r2
    if fmt == "format_2":
        t1 = r2.get("text_1_content", "")
        t2 = r2.get("text_2_content", "")
        text = f"**{r2.get('text_1_title','')}**\n\n{t1}\n\n**{r2.get('text_2_title','')}**\n\n{t2}"
        title = r2.get("text_1_title", "")
    else:
        text = r2.get("text_1_content", "")
        title = r2.get("text_1_title", "")
    text = _fix_gaps(text)
    text = _strip_base_words_from_text(text, base_words)
    return {
        "instruction": ("Прочитайте приведённый ниже текст / приведённые ниже тексты. "
                        "Преобразуйте, если необходимо, слова, напечатанные заглавными буквами "
                        "в конце строк, обозначенных номерами 19–24, так, чтобы они грамматически "
                        "соответствовали содержанию текстов."),
        "title": title, "text": text,
        "items": _grammar_items(schema), "answer_key": _grammar_key(schema),
    }


def generate_task_25_29(topic):
    p1 = _fill(PROMPT_25_29_SCHEMA, TOPIC=topic)
    r1 = call_llm(p1)
    if "error" in r1:
        return r1
    schema = r1
    if len(schema.get("tasks", [])) != 5:
        return {"error": "Схема неполная"}
    base_words = [t.get("base_word", "") for t in schema["tasks"]]
    p2 = _fill(PROMPT_25_29_TEXT, TOPIC=topic,
               WORD_BUILDING_MATRIX=json.dumps(schema, ensure_ascii=False))
    r2 = call_llm(p2)
    if "error" in r2:
        return r2
    text = _fix_gaps(r2.get("text_content", ""))
    text = _strip_base_words_from_text(text, base_words)
    return {
        "instruction": ("Прочитайте приведённый ниже текст. Образуйте от слов, напечатанных "
                        "заглавными буквами в конце строк, обозначенных номерами 25–29, "
                        "однокоренные слова."),
        "title": r2.get("title", ""), "text": text,
        "items": _grammar_items(schema), "answer_key": _grammar_key(schema),
    }


def generate_task_30_36(topic):
    p1 = _fill(PROMPT_30_36_SCHEMA, TOPIC=topic)
    r1 = call_llm(p1)
    if "error" in r1:
        return r1
    schema = r1
    if len(schema.get("tasks", [])) != 7:
        return {"error": "Схема неполная"}
    p2 = _fill(PROMPT_30_36_TEXT, TOPIC=topic,
               LEXICAL_MATRIX=json.dumps(schema, ensure_ascii=False))
    r2 = call_llm(p2)
    if "error" in r2:
        return r2
    items, answer_key = [], {}
    for t in schema["tasks"]:
        opts_arr = t.get("options", [])
        opts = ({"1": opts_arr[0], "2": opts_arr[1], "3": opts_arr[2], "4": opts_arr[3]}
                if isinstance(opts_arr, list) else opts_arr)
        items.append({"number": t["id"], "options": opts})
        answer_key[str(t["id"])] = str(t.get("correct"))
    pseudo = [{"number": it["number"], "question": "", "options": it["options"]} for it in items]
    pseudo, answer_key = _balance_choice_keys(pseudo, answer_key, 4)
    for it, pq in zip(items, pseudo):
        it["options"] = pq["options"]
    return {
        "instruction": ("Прочитайте текст с пропусками, обозначенными номерами 30–36. "
                        "Запишите в поле ответа цифру 1, 2, 3 или 4."),
        "title": r2.get("title", ""),
        "text": _fix_gaps(r2.get("text_content", "")),
        "items": items, "answer_key": answer_key,
    }


def generate_task_37(topic):
    p1 = _fill(PROMPT_37_STIMULUS_SCHEMA, TOPIC=topic)
    r1 = call_llm(p1)
    if "error" in r1:
        return r1
    schema = r1
    p2 = _fill(PROMPT_37_EMAIL_GENERATION, TOPIC=topic,
               STIMULUS_SCHEMA=json.dumps(schema, ensure_ascii=False),
               SENDER_NAME=schema.get("sender_name", "Alex"),
               SUBJECT_LINE=schema.get("subject_line", "Hi"),
               PERSONAL_NEWS=schema.get("personal_news", ""),
               NEWS_TOPIC_FOR_INSTRUCTION=schema.get("news_topic_for_instruction", ""))
    r2 = call_llm(p2)
    if "error" in r2:
        return r2
    return {"task_text": r2.get("formatted_task", "")}


def generate_task_38_1(topic):
    p1 = _fill(PROMPT_38_1_DATA_SCHEMA, TOPIC=topic)
    r1 = call_llm(p1)
    if "error" in r1:
        return r1
    schema = r1
    p2 = _fill(PROMPT_38_1_TASK_GENERATION, TOPIC=topic,
               SURVEY_SCHEMA=json.dumps(schema, ensure_ascii=False),
               PROJECT_SUBJECT=schema.get("project_subject", ""),
               SURVEY_AUDIENCE=schema.get("survey_audience", ""),
               SURVEY_QUESTION=schema.get("survey_question", ""),
               PLAN_STEP_4_ADAPTATION=schema.get("plan_step_4_adaptation", ""),
               PLAN_STEP_5_ADAPTATION=schema.get("plan_step_5_adaptation", ""))
    r2 = call_llm(p2)
    if "error" in r2:
        return r2
    task_text = r2.get("formatted_task") or r2.get("task_text") or ""
    HEADER = ("Choose only ONE of the two given tasks (38.1 or 38.2), indicate its number "
              "in ANSWER SHEET NO. 2 and complete it according to the plan. In your answer "
              "to task 38, write numerals in digits.")
    if not task_text.strip():
        task_text = (HEADER + "\n\n[38.1]\n\n"
                     f"Imagine that you are doing a project on {schema.get('project_subject','')} in Zetland. "
                     f"You have found some data on the subject – the results of a survey conducted among "
                     f"{schema.get('survey_audience','')} (see the table below).\n"
                     "Comment on the survey data and give your opinion on the subject of the project.")
    elif "Choose only ONE" not in task_text:
        task_text = HEADER + "\n\n" + task_text
    survey_data = {
        "question": schema.get("survey_question", ""),
        "options": [{"option": x["option"], "percent": x["percentage"]}
                    for x in schema.get("table_data", [])],
    }
    plan = [
        "make an opening statement on the subject of the project;",
        "select and report 2–3 facts;",
        "make 1–2 comparisons where relevant and give your comments;",
        (schema.get("plan_step_4_adaptation", "").rstrip(";. ") + ";"),
        (schema.get("plan_step_5_adaptation", "").rstrip(";. ") + "."),
    ]
    return {"task_text": task_text, "survey_data": survey_data, "plan": plan}


def generate_task_38_2(topic):
    p1 = _fill(PROMPT_38_2_CHART_SCHEMA, TOPIC=topic)
    r1 = call_llm(p1)
    if "error" in r1:
        return r1
    schema = r1
    p2 = _fill(PROMPT_38_2_CHART_GENERATION, TOPIC=topic,
               CHART_SCHEMA=json.dumps(schema, ensure_ascii=False),
               PROJECT_SUBJECT=schema.get("project_subject", ""),
               SURVEY_AUDIENCE=schema.get("survey_audience", ""),
               SURVEY_QUESTION=schema.get("survey_question", ""),
               PLAN_STEP_4_ADAPTATION=schema.get("plan_step_4_adaptation", ""),
               PLAN_STEP_5_ADAPTATION=schema.get("plan_step_5_adaptation", ""))
    r2 = call_llm(p2)
    if "error" in r2:
        return r2
    task_text = r2.get("formatted_task") or r2.get("task_text") or ""
    HEADER = ("Choose only ONE of the two given tasks (38.1 or 38.2), indicate its number "
              "in ANSWER SHEET NO. 2 and complete it according to the plan. In your answer "
              "to task 38, write numerals in digits.")
    if not task_text.strip():
        task_text = (HEADER + "\n\n[38.2]\n\n"
                     f"Imagine that you are doing a project on {schema.get('project_subject','')} in Zetland. "
                     f"You have found some data on the subject – the results of a survey conducted among "
                     f"{schema.get('survey_audience','')} (see the pie chart below).\n"
                     "Comment on the survey data and give your opinion on the subject of the project.")
    elif "Choose only ONE" not in task_text:
        task_text = HEADER + "\n\n" + task_text
    survey_data = {
        "question": schema.get("survey_question", ""),
        "options": [{"option": x["label"], "percent": x["percentage"]}
                    for x in schema.get("chart_segments", [])],
    }
    plan = [
        "make an opening statement on the subject of the project;",
        "select and report 2–3 facts;",
        "make 1–2 comparisons where relevant and give your comments;",
        (schema.get("plan_step_4_adaptation", "").rstrip(";. ") + ";"),
        (schema.get("plan_step_5_adaptation", "").rstrip(";. ") + "."),
    ]
    return {"task_text": task_text, "survey_data": survey_data, "plan": plan}


def _pipeline_with_explanations(task_type, gen_func):
    def wrapped(topic):
        data = gen_func(topic)
        return _attach_explanations(task_type, data)
    return wrapped


PIPELINES = {
    "1":     _pipeline_with_explanations("1", generate_task_1),
    "2":     _pipeline_with_explanations("2", generate_task_2),
    "3-9":   _pipeline_with_explanations("3-9", generate_task_3_9),
    "10":    _pipeline_with_explanations("10", generate_task_10),
    "11":    _pipeline_with_explanations("11", generate_task_11),
    "12-18": _pipeline_with_explanations("12-18", generate_task_12_18),
    "19-24": _pipeline_with_explanations("19-24", generate_task_19_24),
    "25-29": _pipeline_with_explanations("25-29", generate_task_25_29),
    "30-36": _pipeline_with_explanations("30-36", generate_task_30_36),
    "37":    generate_task_37,
    "38.1":  generate_task_38_1,
    "38.2":  generate_task_38_2,
}


def _resp(status, payload):
    return {"statusCode": status, "headers": {
        "Content-Type": "application/json; charset=utf-8",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
    }, "body": json.dumps(payload, ensure_ascii=False)}


def _read_body(event):
    body = event.get("body") or ""
    if event.get("isBase64Encoded"):
        try:
            body = base64.b64decode(body).decode("utf-8")
        except Exception:
            pass
    return body
def handler(event, context):
    method = event.get("httpMethod", "GET")
    qs = event.get("queryStringParameters") or {}

    if method == "OPTIONS":
        return _resp(200, {})

    if method == "POST":
        try:
            data = json.loads(_read_body(event))
            action = data.get("action")

            if action == "fetch":
                task_type = data.get("task_type")
                topic = data.get("topic", "any")
                student_code = (data.get("student_code") or "").strip() or None
                client_id = (data.get("client_id") or "").strip() or None

                if not task_type or task_type not in PIPELINES:
                    return _resp(400, {"error": "Неверный task_type"})

                is_admin = (data.get("ref") == ADMIN_SECRET)
                if is_admin:
                    logged_in = True
                else:
                    logged_in = False
                    if student_code:
                        st = _student_get(student_code)
                        if st:
                            logged_in = True
                        else:
                            student_code = None

                rl_info = None
                ip = _extract_ip(event)
                if not logged_in:
                    check = _ratelimit_check(ip, client_id)
                    rl_info = {
                        "used": check["used"], "left": check["left"],
                        "max": RATELIMIT_MAX, "enabled": RATELIMIT_ENABLED,
                    }
                    if not check["allowed"]:
                        _rl_audit("blocked", check["ip_hash"], check["cid_hash"],
                                  check["used"], check["used"], note=f"ip={ip}")
                        return _resp(429, {
                            "error": "Лимит бесплатных попыток исчерпан. "
                                     "Получите код доступа у учителя.",
                            "ratelimit": rl_info, "code_required": True,
                        })

                topic_letter = None
                for letter, full in TOPIC_MAP.items():
                    if full.lower() in topic.lower() or letter == topic.strip():
                        topic_letter = letter
                        break

                assignment_id = (data.get("assignment_id") or "").strip() or None
                if assignment_id:
                    a = _assignment_get(assignment_id)
                    if a and a.get("task_data"):
                        a["_meta"] = {"task_type": a.get("task_type"),
                                      "topic": topic, "source": "assignment",
                                      "assignment_id": assignment_id}
                        return _resp(200, {"task_data": a, "ratelimit": rl_info})

                task_data = None
                if topic_letter:
                    bank_item = fetch_from_bank(task_type, topic_letter)
                    if bank_item:
                        print(f"[bank] выдали из банка: {bank_item['code']}")
                        bank_item["_meta"] = {"task_type": task_type, "topic": topic,
                                              "source": "bank", "code": bank_item["code"]}
                        task_data = bank_item

                if not task_data:
                    print(f"[bank] банк пуст, генерируем через LLM")
                    result = PIPELINES[task_type](topic)
                    if isinstance(result, dict) and "error" in result:
                        return _resp(500, {"error": result["error"], "ratelimit": rl_info})
                    v_err = validate_general(task_type, result)
                    if v_err is not None:
                        return _resp(500, {"error": v_err, "ratelimit": rl_info})
                    result["_meta"] = {"task_type": task_type, "topic": topic, "source": "llm"}
                    task_data = result

                if not logged_in and rl_info is not None:
                    check = _ratelimit_check(ip, client_id)
                    _ratelimit_increment(check["ip_hash"], check["cid_hash"])
                    new_used = check["used"] + 1
                    rl_info = {
                        "used": new_used,
                        "left": max(0, RATELIMIT_MAX - new_used),
                        "max": RATELIMIT_MAX, "enabled": RATELIMIT_ENABLED,
                    }
                    _rl_audit("granted", check["ip_hash"], check["cid_hash"],
                              new_used, new_used, note=f"ip={ip}")

                return _resp(200, {"task_data": task_data, "ratelimit": rl_info})

            if action == "preview":
                task_type = data.get("task_type", "1")
                topic_letter = data.get("topic_letter", "").strip().upper()
                raw_text = data.get("text", "").strip()
                if not raw_text:
                    return _resp(400, {"error": "Пустой текст"})
                if not topic_letter or topic_letter not in TOPIC_MAP:
                    return _resp(400, {"error": f"Тема '{topic_letter}' не найдена"})
                if task_type != "1":
                    return _resp(400, {"error": "Пока только тип 1"})
                r = preview_task1(raw_text, topic_letter)
                if "error" in r:
                    return _resp(500, r)
                return _resp(200, r)

            if action == "save_previewed":
                task_type = data.get("task_type", "1")
                topic_letter = data.get("topic_letter", "").strip().upper()
                task_data = data.get("task_data") or {}
                audio_b64 = data.get("audio_b64") or ""
                force = bool(data.get("force"))
                if not task_data:
                    return _resp(400, {"error": "Нет task_data"})
                r = save_previewed_task(task_type, topic_letter, task_data, audio_b64, force=force)
                if "error" in r:
                    return _resp(500, r)
                return _resp(200, r)

            if action == "list_bank":
                r = list_bank(data.get("task_type"), data.get("topic_letter"))
                return _resp(200, r)

            if action == "get_bank_task":
                code = (data.get("code") or "").strip()
                task_type = data.get("task_type", "1")
                topic_letter = data.get("topic_letter", "").strip().upper()
                if not code or not topic_letter:
                    return _resp(400, {"error": "Нужны code и topic_letter"})
                r = get_bank_task(task_type, topic_letter, code)
                if "error" in r:
                    return _resp(500, r)
                return _resp(200, r)

            if action == "delete_bank_task":
                code = (data.get("code") or "").strip()
                task_type = data.get("task_type", "1")
                topic_letter = data.get("topic_letter", "").strip().upper()
                if not code or not topic_letter:
                    return _resp(400, {"error": "Нужны code и topic_letter"})
                r = delete_bank_task(task_type, topic_letter, code)
                if "error" in r:
                    return _resp(500, r)
                return _resp(200, r)

            if action == "list_students":
                return _resp(200, _student_list())

            if action == "get_student":
                code = (data.get("code") or "").strip()
                if not code:
                    return _resp(400, {"error": "Нужен code"})
                s = _student_get(code)
                if not s:
                    return _resp(404, {"error": "Не найден"})
                return _resp(200, s)

            if action == "create_student":
                r = _student_create((data.get("surname") or "").strip(),
                                    (data.get("name") or "").strip())
                if "error" in r:
                    return _resp(500, r)
                return _resp(200, r)

            if action == "update_student":
                r = _student_update((data.get("code") or "").strip(),
                                    (data.get("surname") or "").strip(),
                                    (data.get("name") or "").strip())
                if "error" in r:
                    return _resp(500, r)
                return _resp(200, r)

            if action == "delete_student":
                code = (data.get("code") or "").strip()
                if not code:
                    return _resp(400, {"error": "Нужен code"})
                r = _student_delete(code)
                if "error" in r:
                    return _resp(500, r)
                return _resp(200, r)

            if action == "tts":
                task_type = data.get("task_type")
                task_data = data.get("task_data") or {}
                part = int(data.get("part", 1))
                if task_type not in ("1", "2", "3-9"):
                    return _resp(400, {"error": "TTS только для 1, 2, 3-9"})
                result = (synthesize_part1(task_type, task_data) if part == 1
                          else synthesize_part2(task_type, task_data))
                if "error" in result:
                    return _resp(500, {"error": result["error"]})
                return _resp(200, result)

            if action == "save_draft":
                r = _submission_save_draft(
                    data.get("student_code"), data.get("task_type"),
                    data.get("task_data"), data.get("assignment_id"),
                    data.get("bank_code"), data.get("answer_text", ""))
                return _resp(200 if "ok" in r else 500, r)

            if action == "submit_work":
                r = _submission_submit(data.get("student_code"),
                                       data.get("submission_id"),
                                       data.get("answer_text", ""))
                return _resp(200 if "ok" in r else 500, r)

            if action == "my_submissions":
                return _resp(200, _submission_list(data.get("student_code")))

            if action == "get_submission":
                r = _submission_get(data.get("student_code"),
                                    data.get("submission_id"))
                if not r:
                    return _resp(404, {"error": "Не найдено"})
                return _resp(200, r)

            if action == "list_pending":
                return _resp(200, _submission_list_pending())

            if action == "review_submission":
                r = _submission_review(data.get("student_code"),
                                       data.get("submission_id"),
                                       data.get("scores") or {},
                                       data.get("comment", ""))
                return _resp(200 if "ok" in r else 500, r)

            if action == "stats":
                return _resp(200, _submission_stats())

            if action == "get_criteria":
                tt = data.get("task_type")
                c = CRITERIA_BY_TYPE.get(tt)
                if not c:
                    return _resp(400, {"error": "Нет критериев для " + str(tt)})
                return _resp(200, {"criteria": c, "checklist": checklist_for(tt)})

            if action == "materials_list":
                return _resp(200, _materials_list())

            if action == "materials_add":
                r = _materials_add(data.get("title"),
                                   data.get("file_b64"),
                                   data.get("filename"),
                                   data.get("content_type"),
                                   data.get("url"))
                return _resp(200 if "ok" in r else 500, r)

            if action == "materials_get":
                r = _materials_get_file(data.get("id"))
                return _resp(200 if "error" not in r else 500, r)

            if action == "materials_delete":
                r = _materials_delete(data.get("id"))
                return _resp(200 if "ok" in r else 500, r)

            if action == "materials_move":
                r = _materials_move(data.get("id"), data.get("direction"))
                return _resp(200 if "ok" in r else 500, r)

            if action == "assignment_create":
                r = _assignment_create(data.get("student_code"),
                                       data.get("task_type"),
                                       data.get("task_data"),
                                       data.get("bank_code"),
                                       data.get("note", ""))
                return _resp(200 if "ok" in r else 500, r)

            if action == "assignment_list":
                return _resp(200, _assignment_list(data.get("student_code")))

            if action == "assignment_get":
                a = _assignment_get(data.get("id"))
                if not a:
                    return _resp(404, {"error": "Не найдено"})
                return _resp(200, a)

            if action == "assignment_delete":
                r = _assignment_delete(data.get("id"))
                return _resp(200 if "ok" in r else 500, r)

            if action == "ratelimit_list":
                return _resp(200, _ratelimit_admin_list())

            if action == "ratelimit_reset":
                return _resp(200, _ratelimit_admin_reset(data.get("key")))

            if action == "ratelimit_audit":
                return _resp(200, _ratelimit_admin_audit())

            if action == "ratelimit_info":
                return _resp(200, {"enabled": RATELIMIT_ENABLED,
                                   "max": RATELIMIT_MAX})

            # ---------------- ВАРИАНТЫ ----------------
            if action == "variant_generate":
                topic_config = data.get("topic_config") or {}
                r = generate_variant(topic_config)
                if "error" in r:
                    return _resp(500, r)
                return _resp(200, r)

            if action == "variant_create":
                tasks_data = data.get("tasks") or {}
                topic_config = data.get("topic_config") or {}
                if not tasks_data:
                    return _resp(400, {"error": "Нет заданий"})
                r = _variant_create(tasks_data, topic_config)
                return _resp(200 if "ok" in r else 500, r)

            if action == "variant_list":
                return _resp(200, _variant_list())

            if action == "variant_get":
                v = _variant_get(data.get("id"))
                if "error" in v:
                    return _resp(404, v)
                return _resp(200, v)

            if action == "variant_delete":
                r = _variant_delete(data.get("id"))
                return _resp(200 if "ok" in r else 500, r)

            if action == "variant_assign":
                r = _variant_assign(data.get("id"), data.get("student_codes") or [])
                return _resp(200 if "ok" in r else 500, r)

            if action == "variant_my_list":
                sc = data.get("student_code")
                if not sc:
                    return _resp(400, {"error": "Нужен student_code"})
                variants = _variant_list_for_student(sc)
                submissions = _variant_list_submissions(sc)
                sub_by_vid = {s["variant_id"]: s for s in submissions}
                out = []
                for v in variants:
                    entry = dict(v)
                    entry["submission"] = sub_by_vid.get(v["id"])
                    out.append(entry)
                return _resp(200, {"variants": out})

            if action == "variant_get_full":
                v = _variant_get(data.get("id"))
                if "error" in v:
                    return _resp(404, v)
                sub = None
                sc = data.get("student_code")
                if sc:
                    sub = _variant_get_submission(sc, v["id"])
                return _resp(200, {"variant": v, "submission": sub})

            if action == "variant_submit":
                r = _variant_submit(data.get("student_code"),
                                    data.get("variant_id"),
                                    data.get("answers") or {})
                if "error" in r:
                    return _resp(500, r)
                return _resp(200, r)

            if action == "variant_get_submission":
                sub = _variant_get_submission(data.get("student_code"),
                                              data.get("variant_id"))
                if not sub:
                    return _resp(404, {"error": "Не найдено"})
                return _resp(200, sub)

            if action == "variant_pending_reviews":
                return _resp(200, {"pending": _variant_list_pending_manual()})

            if action == "variant_review_manual":
                r = _variant_review_manual(data.get("student_code"),
                                           data.get("variant_id"),
                                           data.get("task_type"),
                                           data.get("scores") or {},
                                           data.get("comment", ""))
                return _resp(200 if "ok" in r else 500, r)

            return _resp(400, {"error": f"Неизвестное действие: {action}"})
        except Exception as e:
            traceback.print_exc()
            return _resp(500, {"error": f"{type(e).__name__}: {e}"})

    # ============================================================
    # GET
    # ============================================================
    if qs.get("ref") and qs["ref"] == ADMIN_SECRET:
        return {"statusCode": 200,
                "headers": {"Content-Type": "text/html; charset=utf-8"},
                "body": ADMIN_HTML}

    if qs.get("code"):
        student = _student_get(qs["code"])
        if student:
            surname = student.get("surname", "")
            name = student.get("name", "")
            full_name = (surname + " " + name).strip() or "Ученик"
            student_code = student.get("code", "")
            student_bar = (
                f'<div style="text-align:center;padding:20px 0 10px">'
                f'<div style="font-size:17px;color:#8b93c4;margin-bottom:6px">👤 '
                f'<b style="color:#00e5ff;font-size:20px">{full_name}</b></div>'
                f'<div style="font-family:monospace;font-size:15px;color:#c9b8ff;'
                f'padding:5px 14px;background:rgba(123,92,255,.15);border-radius:8px;'
                f'display:inline-block;margin-bottom:12px">Код: {student_code}</div>'
                f'<div style="font-size:16px">'
                f'<a href="javascript:openProfile()" style="color:#c9b8ff;text-decoration:none;'
                f'margin-right:20px;font-weight:600">⚙ Профиль</a>'
                f'<a href="javascript:logout()" style="color:#7b5cff;text-decoration:none;'
                f'font-weight:600">🚪 Выйти</a>'
                f'</div>'
                f'</div>'
            )
            html = MAIN_HTML.replace('<div class="hero">',
                                     student_bar + '<div class="hero">', 1)
            html = html.replace(
                '<div class="card" id="myWorksCard" style="display:none">',
                '<div class="card" id="myWorksCard">', 1)
            html = html.replace(
                '<div class="card" id="myAssignmentsCard" style="display:none">',
                '<div class="card" id="myAssignmentsCard">', 1)
            html = html.replace(
                '<div class="card" id="myVariantsCard" style="display:none">',
                '<div class="card" id="myVariantsCard">', 1)

            sc_js = json.dumps(student_code)
            nm_js = json.dumps(full_name)
            profile_js = (
                "<script>"
                "window._studentCode=" + sc_js + ";"
                "window._studentName=" + nm_js + ";"
                "function logout(){window.location.href=window.location.pathname;}"
                "function openProfile(){"
                "  var code=window._studentCode;"
                "  fetch(window.location.pathname,{method:'POST',headers:{'Content-Type':'application/json'},"
                "    body:JSON.stringify({action:'get_student',code:code})})"
                "  .then(function(r){return r.json()}).then(function(s){"
                "    if(s.error){alert('Ошибка: '+s.error);return;}"
                "    alert('Ваш код доступа: ' + s.code + '. Сохраните его — по нему вы входите в личный кабинет.');"
                "    var sn=prompt('Фамилия:', s.surname || '');"
                "    if(sn===null)return;"
                "    var nm=prompt('Имя:', s.name || '');"
                "    if(nm===null)return;"
                "    fetch(window.location.pathname,{method:'POST',headers:{'Content-Type':'application/json'},"
                "      body:JSON.stringify({action:'update_student',code:code,surname:sn,name:nm})})"
                "    .then(function(r){return r.json()}).then(function(res){"
                "      if(res.error){alert('Ошибка: '+res.error);return;}"
                "      location.reload();"
                "    });"
                "  });"
                "}"
                "</script>"
            )
            html = html.replace('<script>', profile_js + '<script>', 1)
            return {"statusCode": 200,
                    "headers": {"Content-Type": "text/html; charset=utf-8"},
                    "body": html}
        else:
            return {"statusCode": 404,
                    "headers": {"Content-Type": "text/html; charset=utf-8"},
                    "body": '<html><body style="background:#05060f;color:#ff8ba8;'
                            'font-family:sans-serif;padding:40px;text-align:center">'
                            '<h1>Код не найден</h1>'
                            '<p style="color:#8b93c4">Проверь ссылку или попроси новый код у учителя.</p>'
                            '</body></html>'}

    return {"statusCode": 200,
            "headers": {"Content-Type": "text/html; charset=utf-8"},
            "body": MAIN_HTML}
MAIN_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🚀 Космодром ЕГЭ</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#05060f;--purple:#7b5cff;--pink:#ff5cf0;--cyan:#00e5ff;--text:#e8ecff;--dim:#8b93c4;--ok:#2ecc71;--warn:#f39c12;--err:#e74c3c}
html,body{min-height:100%;background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif}
#s1,#s2,#s3{position:fixed;inset:0;pointer-events:none;z-index:0}
#s1{background:radial-gradient(2px 2px at 20px 30px,#fff,transparent),radial-gradient(1px 1px at 90px 40px,#fff,transparent);background-repeat:repeat;background-size:300px 300px;animation:d 120s linear infinite}
#s2{background:radial-gradient(2px 2px at 130px 30px,#ffe9a8,transparent);background-repeat:repeat;background-size:200px 200px;animation:d 80s linear infinite reverse;opacity:.7}
#s3{background:radial-gradient(2px 2px at 80px 50px,#7b5cff,transparent);background-repeat:repeat;background-size:400px 400px;animation:d 160s linear infinite;opacity:.5}
@keyframes d{from{background-position:0 0}to{background-position:1000px 1000px}}
.neb{position:fixed;inset:0;pointer-events:none;z-index:0;background:radial-gradient(circle at 15% 20%,rgba(123,92,255,.18) 0,transparent 40%),radial-gradient(circle at 85% 70%,rgba(255,92,240,.14) 0,transparent 45%),radial-gradient(circle at 50% 100%,rgba(0,229,255,.10) 0,transparent 50%)}
.layout{position:relative;z-index:2;max-width:1500px;margin:0 auto;padding:32px 20px 80px;display:grid;grid-template-columns:1fr;gap:24px}
@media (min-width:1200px){.layout{grid-template-columns:340px minmax(0,1fr) 340px}}
.sidebar{position:relative}
@media (min-width:1200px){.sidebar{position:sticky;top:24px;align-self:start;max-height:calc(100vh - 48px);overflow-y:auto}}
.side-card{background:rgba(20,25,60,.55);border:1px solid rgba(123,92,255,.35);border-radius:20px;padding:28px;backdrop-filter:blur(20px);margin-bottom:18px}
.side-card h4{font-size:19px;text-transform:uppercase;letter-spacing:1.5px;color:var(--cyan);margin-bottom:20px;font-weight:700}
.mat-item{display:flex;gap:14px;align-items:flex-start;padding:16px 18px;margin:8px 0;background:rgba(5,6,15,.4);border-radius:12px;cursor:pointer;transition:background .15s;font-size:16px;line-height:1.5;color:#d0d5f5;text-decoration:none}
.mat-item:hover{background:rgba(123,92,255,.15)}
.mat-item .ic{font-size:26px;flex-shrink:0}
.mat-empty{font-size:15px;color:var(--dim);font-style:italic;padding:14px 0;line-height:1.6}
.hero{text-align:center;margin-bottom:28px}
.badge{display:inline-block;padding:8px 20px;border-radius:100px;font-size:13px;letter-spacing:2px;background:rgba(123,92,255,.15);border:1px solid rgba(123,92,255,.35);color:var(--cyan);margin-bottom:18px;text-transform:uppercase}
h1{font-size:clamp(28px,4.5vw,48px);font-weight:800;line-height:1.1;background:linear-gradient(135deg,#fff 0%,#c9b8ff 40%,#00e5ff 100%);-webkit-background-clip:text;background-clip:text;color:transparent;margin-bottom:16px}
.slogan{font-size:clamp(15px,1.8vw,18px);color:var(--dim);line-height:1.5;max-width:640px;margin:0 auto}
.panel{background:rgba(20,25,60,.55);border:1px solid rgba(123,92,255,.35);border-radius:20px;padding:28px;backdrop-filter:blur(20px);box-shadow:0 8px 40px rgba(0,0,0,.5)}
.f{margin-bottom:18px}
.f label{display:block;font-size:13px;text-transform:uppercase;letter-spacing:1.5px;color:var(--dim);margin-bottom:10px;font-weight:600}
.f select{width:100%;padding:14px 16px;background:rgba(5,6,15,.7);border:1px solid rgba(123,92,255,.25);border-radius:12px;color:var(--text);font-size:16px}
.f select:focus{outline:none;border-color:var(--purple);box-shadow:0 0 0 3px rgba(123,92,255,.2)}
.f select option{background:#0d1030;color:var(--text)}
.btn{width:100%;padding:18px 28px;margin-top:6px;border:none;border-radius:14px;font-size:17px;font-weight:700;cursor:pointer;background:linear-gradient(135deg,#7b5cff,#ff5cf0);color:#fff;box-shadow:0 8px 30px rgba(123,92,255,.5);transition:transform .15s}
.btn:hover:not(:disabled){transform:translateY(-2px)}
.btn:disabled{opacity:.6;cursor:wait}
.btn-sm{padding:10px 16px;font-size:14px;width:auto;margin-top:0}
.btn-ok{background:linear-gradient(135deg,#2ecc71,#27ae60);box-shadow:0 8px 30px rgba(46,204,113,.4)}
.btn-outline{background:transparent;border:1px solid rgba(123,92,255,.5);color:#c9b8ff;box-shadow:none}
.btn-outline:hover:not(:disabled){background:rgba(123,92,255,.15)}
.btn-danger{background:linear-gradient(135deg,#e74c3c,#c0392b);box-shadow:none}
#r{margin-top:22px}
.ld{text-align:center;padding:60px 20px;color:var(--dim)}
.ld .rk{font-size:56px;display:inline-block;animation:l 1.4s ease-in-out infinite}
@keyframes l{0%,100%{transform:translateY(0) rotate(-45deg)}50%{transform:translateY(-16px) rotate(-45deg)}}
.card{background:rgba(20,25,60,.55);border:1px solid rgba(123,92,255,.35);border-radius:20px;padding:28px;margin-top:22px;backdrop-filter:blur(20px);box-shadow:0 8px 40px rgba(0,0,0,.4)}
.card h3{margin-bottom:18px;font-size:22px;background:linear-gradient(135deg,#c9b8ff,#00e5ff);-webkit-background-clip:text;background-clip:text;color:transparent}
.tt{color:#d0d5f5;line-height:1.7;margin-bottom:16px;white-space:pre-wrap;font-size:16px}
.sc{background:rgba(5,6,15,.5);padding:16px;border-radius:12px;margin:10px 0;border-left:3px solid var(--purple);color:#c8cdf0;font-size:15px;line-height:1.7;white-space:pre-wrap}
.rw{display:flex;align-items:flex-start;gap:12px;margin:10px 0;flex-wrap:wrap;color:#d0d5f5;font-size:16px}
.op{display:flex;align-items:center;gap:10px;cursor:pointer;font-size:16px;color:#c8cdf0;padding:12px 16px;border-radius:10px;border:1px solid rgba(123,92,255,.15);margin:6px 0}
.op:hover{background:rgba(123,92,255,.12)}
.op input{accent-color:var(--purple);width:auto;transform:scale(1.3)}
.op.correct{background:rgba(46,204,113,.2);border-color:#2ecc71;color:#a8f0c0}
.op.wrong{background:rgba(231,76,60,.2);border-color:#e74c3c;color:#ffb3ab}
.ip{padding:12px 16px;background:rgba(5,6,15,.7);color:var(--text);border:1px solid rgba(123,92,255,.3);border-radius:10px;font-size:16px;width:200px}
.ip:focus{outline:none;border-color:var(--cyan)}
.ip.correct{border-color:#2ecc71;background:rgba(46,204,113,.15)}
.ip.wrong{border-color:#e74c3c;background:rgba(231,76,60,.15)}
.er{color:#ff8ba8;background:rgba(255,92,150,.1);border:1px solid rgba(255,92,150,.3);padding:18px;border-radius:12px;margin:16px 0;font-size:16px;word-break:break-word;line-height:1.6}
.tb{border-collapse:collapse;width:100%;margin:14px 0;background:rgba(5,6,15,.5);border-radius:10px;overflow:hidden}
.tb th,.tb td{border:1px solid rgba(123,92,255,.2);padding:14px 16px;text-align:left;color:#d0d5f5;font-size:16px}
.tb th{background:rgba(123,92,255,.15);font-weight:600;color:#c9b8ff}
.pi{width:300px;height:300px;border-radius:50%;margin:24px auto;box-shadow:0 0 60px rgba(123,92,255,.4)}
.lg{display:flex;flex-wrap:wrap;gap:14px;justify-content:center;margin-top:18px;font-size:15px;color:#c8cdf0}
.lg .i{display:flex;align-items:center;gap:8px}
.lg .c{width:18px;height:18px;border-radius:4px;display:inline-block}
.pl{margin:10px 0 10px 10px;color:#d0d5f5;line-height:1.8;font-size:16px}
.hr{border:none;border-top:1px solid rgba(123,92,255,.2);margin:22px 0}
.info{font-size:14px;color:var(--dim);margin-top:8px}
audio{display:none}
.gap-line{display:flex;align-items:center;gap:14px;margin:10px 0;background:rgba(5,6,15,.35);padding:12px 16px;border-radius:10px}
.gap-label{color:#c9b8ff;font-weight:700;font-family:monospace;min-width:80px;font-size:16px}
.gap-input{padding:12px 16px;background:rgba(5,6,15,.7);color:var(--text);border:1px solid rgba(123,92,255,.3);border-radius:10px;font-size:16px;flex:1;max-width:320px}
.gap-base{color:#7b5cff;font-family:monospace;font-weight:700;letter-spacing:1px;font-size:15px}
details{margin-top:14px;background:rgba(5,6,15,.5);border-radius:12px;border:1px solid rgba(123,92,255,.2);padding:16px}
details summary{cursor:pointer;color:#c9b8ff;font-weight:600;font-size:15px;padding:6px 0;user-select:none;list-style:none}
details summary::-webkit-details-marker{display:none}
details summary::before{content:'📄 ';margin-right:8px}
details[open] summary::before{content:'📖 '}
details .script-body{margin-top:12px;color:#c8cdf0;font-size:15px;line-height:1.8}
details .script-line{margin:8px 0;padding:10px 14px;background:rgba(5,6,15,.35);border-radius:8px;border-left:3px solid rgba(123,92,255,.4)}
details .script-monologue{margin:12px 0;padding:14px;background:rgba(5,6,15,.35);border-radius:10px}
details .script-speaker{color:#00e5ff;font-weight:600;margin-right:8px}
.rl-bar{text-align:center;font-size:14px;color:var(--dim);margin-top:12px}
.rl-bar b{color:var(--cyan)}
.rl-bar.warn b{color:var(--warn)}
.rl-bar.err b{color:var(--err)}
.sub-item{display:flex;gap:16px;align-items:center;padding:20px 22px;margin:12px 0;background:rgba(5,6,15,.4);border-radius:14px;border-left:4px solid var(--purple);flex-wrap:wrap;font-size:16px;color:#d0d5f5}
.sub-item.status-draft{border-left-color:#8b93c4}
.sub-item.status-submitted{border-left-color:var(--warn)}
.sub-item.status-reviewed{border-left-color:var(--ok)}
.sub-item.status-not_started{border-left-color:var(--purple)}
.sub-info{flex:1;min-width:220px}
.sub-title{font-weight:700;color:#c9b8ff;font-size:18px}
.sub-date{font-size:13px;color:#8b93c4;margin-top:5px}
.sub-score{font-size:26px;font-weight:800;color:var(--ok);font-family:monospace}
.sub-score.pending{color:var(--warn);font-size:14px;font-family:inherit;font-weight:600}
.badge-status{display:inline-block;padding:4px 10px;border-radius:8px;font-size:12px;font-weight:600;letter-spacing:.5px;text-transform:uppercase;margin-left:8px}
.badge-status.draft{background:rgba(139,147,196,.2);color:#b0b6d8}
.badge-status.submitted{background:rgba(243,156,18,.2);color:#fbd88b}
.badge-status.reviewed{background:rgba(46,204,113,.2);color:#a8f0c0}
.badge-status.not_started{background:rgba(123,92,255,.2);color:#c9b8ff}
.as-item{display:flex;gap:16px;align-items:center;padding:20px 22px;margin:12px 0;background:rgba(123,92,255,.08);border-radius:14px;border-left:4px solid var(--cyan);flex-wrap:wrap;font-size:16px;color:#d0d5f5}
.as-info{flex:1;min-width:220px}
.as-title{font-weight:700;color:#c9b8ff;font-size:18px}
.as-note{font-size:14px;color:#f39c12;margin-top:6px}
.as-date{font-size:13px;color:#8b93c4;margin-top:6px}
.modal-bg{position:fixed;inset:0;background:rgba(0,0,0,.7);z-index:1000;display:none;align-items:center;justify-content:center;padding:20px}
.modal-bg.show{display:flex}
.modal{background:#0d1030;border:1px solid rgba(123,92,255,.4);border-radius:20px;max-width:820px;width:100%;max-height:90vh;overflow-y:auto;padding:28px}
.modal h3{margin-bottom:16px;color:#c9b8ff;font-size:22px}
.modal .close{float:right;background:none;border:none;color:var(--dim);font-size:24px;cursor:pointer;line-height:1}
.modal .close:hover{color:#fff}
.crit-row{display:flex;justify-content:space-between;padding:14px 18px;margin:8px 0;background:rgba(5,6,15,.4);border-radius:10px;font-size:16px}
.crit-row .code{color:var(--cyan);font-weight:700;font-family:monospace;min-width:44px}
.crit-row .name{flex:1;color:#c8cdf0;margin-right:12px}
.crit-row .score{font-weight:800;font-family:monospace;font-size:18px}
.comment-box{background:rgba(46,204,113,.08);border:1px solid rgba(46,204,113,.3);border-radius:12px;padding:18px;margin-top:16px;color:#c8cdf0;font-size:15px;line-height:1.7;white-space:pre-wrap}
.comment-label{font-size:13px;text-transform:uppercase;letter-spacing:1px;color:var(--ok);font-weight:700;margin-bottom:8px}
.draft-hint{font-size:14px;color:var(--warn);text-align:right;margin-top:10px;min-height:18px}
.writing-area textarea{width:100%;min-height:340px;padding:18px;background:rgba(5,6,15,.7);color:var(--text);border:1px solid rgba(123,92,255,.3);border-radius:12px;font-family:Georgia,serif;font-size:17px;line-height:1.8;resize:vertical}
.writing-area textarea:focus{outline:none;border-color:var(--cyan);box-shadow:0 0 0 3px rgba(0,229,255,.15)}
.submit-bar{display:flex;gap:14px;align-items:center;margin-top:16px;flex-wrap:wrap}
.submit-bar .btn{width:auto;flex:1;min-width:220px;margin:0}
.submit-bar .info{flex-basis:100%;text-align:center;margin:0}
.inst{font-style:italic;color:#a0a8d0;margin-bottom:8px}
.vnav{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:14px}
.vnav button{padding:8px 12px;font-size:13px;background:rgba(123,92,255,.1);border:1px solid rgba(123,92,255,.3);color:#c9b8ff;border-radius:8px;cursor:pointer}
.vnav button:hover{background:rgba(123,92,255,.25)}
.vsection{margin-top:14px;padding-top:14px;border-top:1px solid rgba(123,92,255,.2)}
.vsection h4{color:#c9b8ff;margin-bottom:10px;font-size:16px}
@media print{.no-print{display:none!important}body.print-body{padding:0}}
.print-body{background:#fff;padding:20px;margin:0}
@page{size:A4;margin:15mm 12mm}
.print-doc{font-family:'Times New Roman',Times,serif;color:#000;font-size:12pt;line-height:1.4}
.print-doc h1{font-size:17pt;text-align:center;margin:0 0 12pt 0}
.print-doc h2{font-size:14pt;margin:16pt 0 6pt 0;padding-bottom:3pt;border-bottom:1.5pt solid #000}
.print-doc h3{font-size:12.5pt;margin:10pt 0 5pt 0}
.print-doc .meta{text-align:center;color:#444;font-size:10pt;margin-bottom:14pt}
.print-doc .inst{font-style:italic;color:#222;margin:8pt 0;text-align:justify}
.print-doc .tt{white-space:pre-wrap;margin:8pt 0;text-align:justify}
.print-doc .q{margin:8pt 0;text-align:justify}
.print-doc .op{margin:3pt 0 3pt 18pt}
.print-doc table{width:100%;border-collapse:collapse;margin:10pt 0}
.print-doc th,.print-doc td{border:1pt solid #000;padding:5pt 8pt;font-size:11pt;vertical-align:middle}
.print-doc th{background:#e8e8e8;text-align:center;font-weight:bold}
.print-doc .script{background:#f5f5f5;border:1pt solid #ccc;padding:8pt 12pt;margin:10pt 0;font-size:10.5pt}
.print-doc .answers{background:#fff8d8;border:1.5pt solid #b8860b;padding:10pt 14pt;margin:12pt 0}
.print-doc .answers h3{color:#8b6508;margin-top:0}
.print-doc .page-break{page-break-after:always;height:0}
</style>
</head>
<body>
<div id="s1"></div><div id="s2"></div><div id="s3"></div>
<div class="neb"></div>
<div class="layout">
  <aside class="sidebar" id="leftSidebar">
    <div class="side-card">
      <h4>📚 Полезное</h4>
      <div id="materialsLeft"><div class="mat-empty">Загрузка…</div></div>
    </div>
  </aside>

  <main>
    <div class="hero">
      <span class="badge">🛸 ORBITAL TASK ARCHIVE</span>
      <h1>Космодром ЕГЭ</h1>
      <p class="slogan">🌌 Сотни готовых миссий на борту. Пройдёшь все — квантовый генератор синтезирует новые. ⚡</p>
    </div>

    <div class="card" id="myVariantsCard" style="display:none">
      <h3>📦 Мои варианты</h3>
      <div id="myVariants"><div class="mat-empty">Загрузка…</div></div>
    </div>

    <div class="card" id="myAssignmentsCard" style="display:none">
      <h3>📌 Мои назначения от учителя</h3>
      <div id="myAssignments"><div class="mat-empty">Загрузка…</div></div>
    </div>

    <div class="panel">
      <div class="f"><label>🛸 Тип задания</label>
        <select id="tt">
          <optgroup label="🎧 Аудирование">
            <option value="1">Задание 1 — Соотнесение A–F</option>
            <option value="2">Задание 2 — True/False/Not Stated</option>
            <option value="3-9">Задания 3–9 — Интервью</option>
          </optgroup>
          <optgroup label="📖 Чтение">
            <option value="10">Задание 10 — Заголовки</option>
            <option value="11">Задание 11 — Пропуски A–F</option>
            <option value="12-18">Задания 12–18 — Множ. выбор</option>
          </optgroup>
          <optgroup label="⚗️ Грамматика и лексика">
            <option value="19-24">Задания 19–24 — Грамматика</option>
            <option value="25-29">Задания 25–29 — Словообразование</option>
            <option value="30-36">Задания 30–36 — Лексика</option>
          </optgroup>
          <optgroup label="✍️ Письменная речь (ручная проверка)">
            <option value="37">Задание 37 — Email</option>
            <option value="38.1">Задание 38.1 — Эссе (таблица)</option>
            <option value="38.2">Задание 38.2 — Эссе (диаграмма)</option>
          </optgroup>
        </select>
      </div>
      <div class="f"><label>🌍 Тема</label>
        <select id="tp">__TOPIC_OPTIONS__</select>
      </div>
      <button class="btn" onclick="gen()" id="bt">🚀 Запустить задание</button>
      <div class="rl-bar" id="rlBar"></div>
      <div class="info">Озвучка: Edge TTS. Генерация: Qwen (ProxyAPI).</div>
    </div>
    <div id="r"></div>

    <div class="card" id="myWorksCard" style="display:none">
      <h3>📝 Мои работы (37, 38.1, 38.2)</h3>
      <div id="myWorks"><div class="mat-empty">Загрузка…</div></div>
    </div>
  </main>

  <aside class="sidebar" id="rightSidebar">
    <div class="side-card">
      <h4>📊 Статистика</h4>
      <div id="studentStats"><div class="mat-empty">Загрузка…</div></div>
    </div>
  </aside>
</div>

<div class="modal-bg" id="resultModal" onclick="if(event.target===this)closeResultModal()">
  <div class="modal" id="resultModalBody"></div>
</div>

<script>
function esc(s){return String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;')}
function b64ToBytes(b64){const bin=atob(b64),bytes=new Uint8Array(bin.length);for(let i=0;i<bin.length;i++)bytes[i]=bin.charCodeAt(i);return bytes;}
function fmtDate(ts){if(!ts)return '';const d=new Date(ts*1000);return d.toLocaleString('ru-RU',{day:'2-digit',month:'2-digit',year:'2-digit',hour:'2-digit',minute:'2-digit'});}
const PIE=['#7b5cff','#ff5cf0','#00e5ff','#2ecc71','#f39c12','#e74c3c'];

const PRINT_CSS = "@page{size:A4;margin:15mm 12mm}*{box-sizing:border-box}"
 + "body.print-body{background:#fff;padding:20px;margin:0;font-family:'Times New Roman',Times,serif;color:#000}"
 + ".print-doc{font-size:12pt;line-height:1.4}"
 + ".print-doc h1{font-size:17pt;text-align:center;margin:0 0 12pt 0}"
 + ".print-doc h2{font-size:14pt;margin:16pt 0 6pt 0;padding-bottom:3pt;border-bottom:1.5pt solid #000}"
 + ".print-doc h3{font-size:12.5pt;margin:10pt 0 5pt 0}"
 + ".print-doc .meta{text-align:center;color:#444;font-size:10pt;margin-bottom:14pt}"
 + ".print-doc .inst{font-style:italic;color:#222;margin:8pt 0;text-align:justify}"
 + ".print-doc .tt{white-space:pre-wrap;margin:8pt 0;text-align:justify}"
 + ".print-doc .q{margin:8pt 0;text-align:justify}"
 + ".print-doc .op{margin:3pt 0 3pt 18pt}"
 + ".print-doc table{width:100%;border-collapse:collapse;margin:10pt 0}"
 + ".print-doc th,.print-doc td{border:1pt solid #000;padding:5pt 8pt;font-size:11pt;vertical-align:middle}"
 + ".print-doc th{background:#e8e8e8;text-align:center;font-weight:bold}"
 + ".print-doc .script{background:#f5f5f5;border:1pt solid #ccc;padding:8pt 12pt;margin:10pt 0;font-size:10.5pt}"
 + ".print-doc .answers{background:#fff8d8;border:1.5pt solid #b8860b;padding:10pt 14pt;margin:12pt 0}"
 + ".print-doc .answers h3{color:#8b6508;margin-top:0}"
 + ".print-doc .page-break{page-break-after:always;height:0}"
 + "@media print{.no-print{display:none!important}body.print-body{padding:0}}";

function renderTaskForPrint(t, d, opts){
  opts = opts || {};
  const withAnswers = !!opts.withAnswers;
  let h = '';
  if(d.instruction) h += '<div class="inst">'+esc(d.instruction)+'</div>';
  if(t==='1'){
    (d.statements||[]).forEach(function(s){h+='<div class="q"><b>'+s.number+'.</b> '+esc(s.text)+'</div>';});
    h+='<table><tr><th>Говорящий</th>'+'ABCDEF'.split('').map(function(k){return '<th>'+k+'</th>';}).join('')+'</tr>';
    h+='<tr><td>Ответ</td>'+'ABCDEF'.split('').map(function(){return '<td style="height:22pt"></td>';}).join('')+'</tr></table>';
    if(withAnswers&&d.answer_key){
      h+='<div class="answers"><h3>Ответы</h3><div style="font-family:monospace;font-size:14pt">'+'ABCDEF'.split('').map(function(k){return k+'→'+(d.answer_key[k]||'?');}).join('  ')+'</div>';
      if(d.extra_statement) h+='<div>Лишнее утверждение: '+d.extra_statement+'</div>';
      h+='</div>';
      if(d.explanations){h+=renderExplanationsBlock(d.explanations,'ABCDEF');}
    }
  } else if(t==='2'){
    (d.statements||[]).forEach(function(s){h+='<div class="q"><b>'+esc(s.letter)+'.</b> '+esc(s.text)+'</div>';});
    h+='<table><tr><th>Утв.</th>'+'ABCDEFG'.split('').map(function(k){return '<th>'+k+'</th>';}).join('')+'</tr>';
    h+='<tr><td>Ответ</td>'+'ABCDEFG'.split('').map(function(){return '<td style="height:22pt"></td>';}).join('')+'</tr></table>';
    h+='<div style="font-size:10pt">1 – True, 2 – False, 3 – Not stated</div>';
    if(withAnswers&&d.answer_key){
      h+='<div class="answers"><h3>Ответы</h3><div style="font-family:monospace;font-size:14pt">'+'ABCDEFG'.split('').map(function(k){return k+'→'+(d.answer_key[k]||'?');}).join('  ')+'</div></div>';
      if(d.explanations){h+=renderExplanationsBlock(d.explanations,'ABCDEFG');}
    }
  } else if(t==='3-9'){
    (d.questions||[]).forEach(function(q){
      h+='<div class="q"><b>'+q.number+'.</b> '+esc(q.question)+'</div>';
      ['1','2','3'].forEach(function(k){h+='<div class="op">'+k+') '+esc(q.options[k])+'</div>';});
    });
    if(withAnswers&&d.answer_key){
      h+='<div class="answers"><h3>Ответы</h3><div style="font-family:monospace;font-size:14pt">'+Object.keys(d.answer_key).map(function(k){return k+'→'+d.answer_key[k];}).join('  ')+'</div></div>';
      if(d.explanations){h+=renderExplanationsBlock(d.explanations,['3','4','5','6','7','8','9']);}
    }
  } else if(t==='10'){
    (d.headings||[]).forEach(function(x){h+='<div class="q"><b>'+x.number+'.</b> '+esc(x.text)+'</div>';});
    h+='<h3>Тексты</h3>';
    (d.texts||[]).forEach(function(x){h+='<div class="q"><b>'+esc(x.letter)+'.</b> '+esc(x.text)+'</div>';});
    h+='<table><tr>'+'ABCDEFG'.split('').map(function(k){return '<th>'+k+'</th>';}).join('')+'</tr>';
    h+='<tr>'+'ABCDEFG'.split('').map(function(){return '<td style="height:22pt"></td>';}).join('')+'</tr></table>';
    if(withAnswers&&d.answer_key){
      h+='<div class="answers"><h3>Ответы</h3><div style="font-family:monospace;font-size:14pt">'+'ABCDEFG'.split('').map(function(k){return k+'→'+(d.answer_key[k]||'?');}).join('  ')+'</div></div>';
      if(d.explanations){h+=renderExplanationsBlock(d.explanations,'ABCDEFG');}
    }
  } else if(t==='11'){
    if(d.title) h+='<h3>'+esc(d.title)+'</h3>';
    if(d.text) h+='<div class="tt">'+esc(d.text)+'</div>';
    h+='<h3>Фрагменты</h3>';
    (d.fragments||[]).forEach(function(f){h+='<div class="q"><b>'+f.number+'.</b> '+esc(f.text)+'</div>';});
    h+='<table><tr>'+'ABCDEF'.split('').map(function(k){return '<th>'+k+'</th>';}).join('')+'</tr>';
    h+='<tr>'+'ABCDEF'.split('').map(function(){return '<td style="height:22pt"></td>';}).join('')+'</tr></table>';
    if(withAnswers&&d.answer_key){
      h+='<div class="answers"><h3>Ответы</h3><div style="font-family:monospace;font-size:14pt">'+'ABCDEF'.split('').map(function(k){return k+'→'+(d.answer_key[k]||'?');}).join('  ')+'</div></div>';
      if(d.explanations){h+=renderExplanationsBlock(d.explanations,'ABCDEF');}
    }
  } else if(t==='12-18'){
    if(d.title) h+='<h3>'+esc(d.title)+'</h3>';
    if(d.text) h+='<div class="tt">'+esc(d.text)+'</div>';
    (d.questions||[]).forEach(function(q){
      h+='<div class="q"><b>'+q.number+'.</b> '+esc(q.question)+'</div>';
      ['1','2','3','4'].forEach(function(k){h+='<div class="op">'+k+') '+esc(q.options[k])+'</div>';});
    });
    if(withAnswers&&d.answer_key){
      h+='<div class="answers"><h3>Ответы</h3><div style="font-family:monospace;font-size:14pt">'+Object.keys(d.answer_key).map(function(k){return k+'→'+d.answer_key[k];}).join('  ')+'</div></div>';
      if(d.explanations){h+=renderExplanationsBlock(d.explanations,['12','13','14','15','16','17','18']);}
    }
  } else if(t==='19-24'||t==='25-29'){
    if(d.title) h+='<h3>'+esc(d.title)+'</h3>';
    if(d.text){
      var tx = String(d.text).replace(/__(\d{2})__/g, function(_,n){return '___('+n+')___';});
      h+='<div class="tt">'+esc(tx)+'</div>';
    }
    (d.items||[]).forEach(function(it){
      h+='<div class="q"><b>'+it.number+'.</b> <span style="font-family:monospace;letter-spacing:1pt">'+esc(it.source_word)+'</span> — <span style="display:inline-block;border-bottom:1pt solid #000;min-width:120pt">&nbsp;</span></div>';
    });
    if(withAnswers&&d.answer_key){
      h+='<div class="answers"><h3>Ответы</h3><div style="font-family:monospace;font-size:13pt">'+Object.keys(d.answer_key).map(function(k){return k+'→'+d.answer_key[k];}).join('  ')+'</div></div>';
      if(d.explanations){
        var ord = (t==='19-24')?['19','20','21','22','23','24']:['25','26','27','28','29'];
        h+=renderExplanationsBlock(d.explanations,ord);
      }
    }
  } else if(t==='30-36'){
    if(d.title) h+='<h3>'+esc(d.title)+'</h3>';
    if(d.text){
      var tx2 = String(d.text).replace(/__(\d{2})__/g, function(_,n){return '('+n+') ____';});
      h+='<div class="tt">'+esc(tx2)+'</div>';
    }
    (d.items||[]).forEach(function(it){
      h+='<div class="q"><b>'+it.number+'.</b></div>';
      ['1','2','3','4'].forEach(function(k){h+='<div class="op">'+k+') '+esc(it.options[k])+'</div>';});
    });
    if(withAnswers&&d.answer_key){
      h+='<div class="answers"><h3>Ответы</h3><div style="font-family:monospace;font-size:14pt">'+Object.keys(d.answer_key).map(function(k){return k+'→'+d.answer_key[k];}).join('  ')+'</div></div>';
      if(d.explanations){h+=renderExplanationsBlock(d.explanations,['30','31','32','33','34','35','36']);}
    }
  } else if(t==='37'){
    if(d.task_text) h+='<div class="tt">'+esc(d.task_text)+'</div>';
    h+='<h3 style="margin-top:14pt">Answer sheet</h3>';
    for(var i=0;i<22;i++) h+='<div style="border-bottom:1pt dotted #888;height:22pt"></div>';
  } else if(t==='38.1'||t==='38.2'){
    if(d.task_text) h+='<div class="tt">'+esc(d.task_text)+'</div>';
    var sd = d.survey_data || {};
    if(sd.question) h+='<p style="text-align:center;font-weight:bold">The survey question: &laquo;'+esc(String(sd.question).replace(/^"+|"+$/g,''))+'&raquo;</p>';
    if(t==='38.1'){
      h+='<table><tr><th>Options</th><th>Number of respondents (%)</th></tr>';
      (sd.options||[]).forEach(function(o){h+='<tr><td>'+esc(o.option)+'</td><td style="text-align:center">'+esc(o.percent)+'</td></tr>';});
      h+='</table>';
    } else {
      h+='<table><tr><th>Segment</th><th>%</th></tr>';
      (sd.options||[]).forEach(function(o){h+='<tr><td>'+esc(o.option)+'</td><td style="text-align:center">'+esc(o.percent)+'</td></tr>';});
      h+='</table>';
    }
    h+='<p style="margin-top:12pt"><b>Write 200–250 words.</b></p>';
    h+='<p><b>Use the following plan:</b></p>';
    (d.plan||[]).forEach(function(p){h+='<div style="margin-left:18pt">– '+esc(p)+'</div>';});
    h+='<h3 style="margin-top:14pt">Answer sheet</h3>';
    for(var j=0;j<22;j++) h+='<div style="border-bottom:1pt dotted #888;height:22pt"></div>';
  }
  return h;
}

function renderExplanationsBlock(exps, keysOrder){
  if(!exps || !keysOrder || !keysOrder.length) return '';
  var shown = keysOrder.filter(function(k){return exps[k];});
  if(!shown.length) return '';
  var h = '<div style="margin-top:14pt;padding:10pt 14pt;background:#eef7ee;border:1.5pt solid #4a8f4a;border-radius:6px">';
  h += '<h3 style="color:#2e6b2e;margin:0 0 8pt 0">💡 Объяснения</h3>';
  shown.forEach(function(k){
    h += '<div style="margin:6pt 0;font-size:11pt;line-height:1.5"><b style="color:#2e6b2e">'+esc(k)+':</b> '+esc(exps[k])+'</div>';
  });
  h += '</div>';
  return h;
}

function openPrintWindow(bodyHtml, title){
  var w = window.open('', '_blank');
  if(!w){alert('Разрешите всплывающие окна');return;}
  var doc = '<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8"><title>'+esc(title)+'</title>'
    +'<style>'+PRINT_CSS+'</style></head><body class="print-body">'
    +'<div class="no-print" style="position:fixed;top:12px;right:12px;z-index:999">'
    +'<button onclick="window.print()" style="padding:10px 18px;font-size:14px;cursor:pointer;background:#7b5cff;color:#fff;border:none;border-radius:8px;font-weight:600">🖨 Сохранить как PDF</button>'
    +'</div>'
    +'<div class="print-doc">'+bodyHtml+'</div>'
    +'<scr'+'ipt>window.addEventListener("load",function(){setTimeout(function(){try{window.print();}catch(e){}},500);});</scr'+'ipt>'
    +'</body></html>';
  w.document.open(); w.document.write(doc); w.document.close();
}

function downloadTaskPDF(){
  var d = window._taskData;
  if(!d){alert('Задание не загружено');return;}
  var t = (d._meta && d._meta.task_type) || d.task_type || '';
  var body = '<h1>Задание '+esc(t)+'</h1>';
  body += renderTaskForPrint(t, d, {withAnswers:false});
  openPrintWindow(body, 'Задание '+t);
}

function getClientId(){
  var cid = null;
  try { cid = localStorage.getItem('ege_client_id'); } catch(e){}
  if (!cid) {
    cid = (crypto.randomUUID ? crypto.randomUUID().replace(/-/g,'') : (Date.now().toString(16)+Math.random().toString(16).slice(2))).toLowerCase();
    cid = cid.slice(0,32);
    try { localStorage.setItem('ege_client_id', cid); } catch(e){}
  }
  return cid;
}
function setCookie(name, value, days){
  try { var exp = new Date(Date.now() + (days||365)*864e5).toUTCString();
    document.cookie = name + '=' + encodeURIComponent(value) + '; expires=' + exp + '; path=/; SameSite=Lax';
  } catch(e){}
}
function getCookie(name){
  try { var m = document.cookie.match(new RegExp('(?:^|; )' + name.replace(/([.$?*|{}()\[\]\\\/\+^])/g,'\\$1') + '=([^;]*)'));
    return m ? decodeURIComponent(m[1]) : null;
  } catch(e){ return null; }
}
(function initClientId(){
  var cid = getCookie('ege_client_id') || getClientId();
  setCookie('ege_client_id', cid, 365);
  try { localStorage.setItem('ege_client_id', cid); } catch(e){}
})();

var STUDENT_CODE = window._studentCode || null;
var IS_LOGGED_IN = !!STUDENT_CODE;

function materialIcon(type){return {pdf:'📄', image:'🖼', text:'📝', link:'🔗'}[type] || '📎';}
async function loadMaterials(){
  const box = document.getElementById('materialsLeft');
  try{
    const r = await fetch(window.location.pathname,{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({action:'materials_list'})});
    const d = await r.json();
    if (d.error || !d.materials || !d.materials.length) {
      box.innerHTML = '<div class="mat-empty">Пока ничего не добавлено</div>'; return;
    }
    box.innerHTML = d.materials.map(function(m){
      return '<a class="mat-item" href="javascript:void(0)" onclick="openMaterial(\\''+esc(m.id)+'\\')">'
        + '<span class="ic">'+materialIcon(m.type)+'</span>'
        + '<span>'+esc(m.title)+'</span></a>';
    }).join('');
  }catch(e){ box.innerHTML = '<div class="mat-empty">Ошибка загрузки</div>'; }
}
async function openMaterial(id){
  try{
    const r = await fetch(window.location.pathname,{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({action:'materials_get', id: id})});
    const d = await r.json();
    if (d.error) { alert('Ошибка: '+d.error); return; }
    if (d.url) { window.open(d.url, '_blank'); return; }
    if (d.file_b64) {
      const bytes = b64ToBytes(d.file_b64);
      const url = URL.createObjectURL(new Blob([bytes], {type: d.content_type || 'application/octet-stream'}));
      window.open(url, '_blank');
      setTimeout(function(){ URL.revokeObjectURL(url); }, 60000);
    }
  }catch(e){ alert('Ошибка: '+e.message); }
}

async function loadMyStats(){
  const box = document.getElementById('studentStats');
  if (!IS_LOGGED_IN) { box.innerHTML = '<div class="mat-empty">Войдите, чтобы видеть статистику</div>'; return; }
  try{
    const r = await fetch(window.location.pathname,{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({action:'stats'})});
    const d = await r.json();
    if (d.error) { box.innerHTML = '<div class="mat-empty">Ошибка</div>'; return; }
    const me = (d.students||[]).find(function(x){return x.student_code === STUDENT_CODE;});
    if (!me) { box.innerHTML = '<div class="mat-empty">Пока нет проверенных работ</div>'; return; }
    box.innerHTML =
      '<div style="font-size:15px;color:#c8cdf0;line-height:2">'
      + 'Проверено работ: <b style="color:#00e5ff;font-size:17px">'+me.count+'</b><br>'
      + 'На проверке: <b style="color:#f39c12;font-size:17px">'+(me.pending||0)+'</b><br>'
      + 'Всего баллов: <b style="color:#2ecc71;font-size:19px">'+me.total+' / '+me.max+'</b>'
      + '</div>';
  }catch(e){ box.innerHTML = '<div class="mat-empty">Ошибка</div>'; }
}

async function loadMyWorks(){
  if (!IS_LOGGED_IN) return;
  const card = document.getElementById('myWorksCard');
  const box = document.getElementById('myWorks');
  card.style.display = 'block';
  try{
    const r = await fetch(window.location.pathname,{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({action:'my_submissions', student_code: STUDENT_CODE})});
    const d = await r.json();
    if (d.error || !d.submissions || !d.submissions.length) {
      box.innerHTML = '<div class="mat-empty">У вас пока нет работ по 37 / 38.1 / 38.2</div>'; return;
    }
    box.innerHTML = d.submissions.map(function(s){
      const statusText = {draft:'Черновик', submitted:'На проверке', reviewed:'Проверено'}[s.status] || s.status;
      let scoreHtml = '';
      if (s.status === 'reviewed' && s.total != null) scoreHtml = '<div class="sub-score">'+s.total+' / '+s.max_total+'</div>';
      else if (s.status === 'submitted') scoreHtml = '<div class="sub-score pending">⏳ на проверке</div>';
      else scoreHtml = '<div class="sub-score pending">—</div>';
      return '<div class="sub-item status-'+esc(s.status)+'">'
        + '<div class="sub-info">'
        + '<div class="sub-title">Задание '+esc(s.task_type)+' '
        + '<span class="badge-status '+esc(s.status)+'">'+statusText+'</span></div>'
        + '<div class="sub-date">обновлено: '+esc(fmtDate(s.updated_at))+'</div>'
        + '</div>' + scoreHtml
        + '<button class="btn btn-sm" onclick="openSubmission(\\''+esc(s.id)+'\\')">👁 Открыть</button>'
        + '</div>';
    }).join('');
  }catch(e){ box.innerHTML = '<div class="mat-empty">Ошибка загрузки</div>'; }
}

async function openSubmission(sid){
  try{
    const r = await fetch(window.location.pathname,{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({action:'get_submission', student_code: STUDENT_CODE, submission_id: sid})});
    const d = await r.json();
    if (d.error) { alert('Ошибка: '+d.error); return; }
    renderSubmissionModal(d);
  }catch(e){ alert('Ошибка: '+e.message); }
}

async function renderSubmissionModal(sub){
  const crit = await fetch(window.location.pathname,{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({action:'get_criteria', task_type: sub.task_type})}).then(x=>x.json());

  let h = '<button class="close" onclick="closeResultModal()">✕</button>';
  h += '<h3>Задание '+esc(sub.task_type)+' — '+esc({draft:'Черновик',submitted:'На проверке',reviewed:'Проверено'}[sub.status])+'</h3>';

  if (sub.task_data && sub.task_data.task_text) {
    h += '<details><summary>Условие задания</summary><div style="margin-top:10px;color:#c8cdf0;font-size:15px;line-height:1.7;white-space:pre-wrap">'+esc(sub.task_data.task_text)+'</div></details>';
  }
  h += '<div style="margin-top:18px"><div class="comment-label">Ваш ответ</div>'
    + '<div style="background:rgba(5,6,15,.5);padding:16px;border-radius:12px;color:#d0d5f5;font-size:15px;line-height:1.7;white-space:pre-wrap;font-family:Georgia,serif">'
    + esc(sub.answer_text || '(пусто)') + '</div></div>';

  if (sub.status === 'reviewed' && sub.review) {
    const rv = sub.review;
    h += '<div style="margin-top:20px"><div class="comment-label" style="color:#2ecc71">Результат проверки</div>';
    const criteria = (crit.criteria && crit.criteria.criteria) || [];
    criteria.forEach(function(c){
      const sc = (rv.scores || {})[c.code] || 0;
      h += '<div class="crit-row"><span class="code">'+esc(c.code)+'</span>'
        + '<span class="name">'+esc(c.name)+'</span>'
        + '<span class="score" style="color:'+(sc>0?'#2ecc71':'#e74c3c')+'">'+sc+' / '+c.max+'</span></div>';
    });
    h += '<div style="text-align:right;font-size:24px;font-weight:800;font-family:monospace;color:#2ecc71;margin-top:14px">ИТОГО: ' + rv.total + ' / ' + rv.max_total + '</div>';
    if (rv.comment) h += '<div class="comment-box"><div class="comment-label">💬 Комментарий учителя</div>'+esc(rv.comment)+'</div>';
    h += '</div>';
  } else if (sub.status === 'submitted') {
    h += '<div class="comment-box" style="background:rgba(243,156,18,.1);border-color:rgba(243,156,18,.3);color:#fbd88b">⏳ Работа отправлена на проверку.</div>';
  }
  document.getElementById('resultModalBody').innerHTML = h;
  document.getElementById('resultModal').classList.add('show');
}
function closeResultModal(){document.getElementById('resultModal').classList.remove('show');}

async function loadMyAssignments(){
  if (!IS_LOGGED_IN) return;
  const card = document.getElementById('myAssignmentsCard');
  const box  = document.getElementById('myAssignments');
  try{
    const r = await fetch(window.location.pathname,{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({action:'assignment_list', student_code: STUDENT_CODE})});
    const d = await r.json();
    if (d.error || !d.assignments || !d.assignments.length) { card.style.display = 'none'; return; }
    card.style.display = 'block';
    box.innerHTML = d.assignments.map(function(a){
      return '<div class="as-item"><div class="as-info">'
        + '<div class="as-title">Задание '+esc(a.task_type)+'</div>'
        + (a.note ? '<div class="as-note">📌 '+esc(a.note)+'</div>' : '')
        + '<div class="as-date">от '+esc(fmtDate(a.created_at))+'</div></div>'
        + '<button class="btn btn-sm btn-ok" onclick="openAssignment(\\''+esc(a.id)+'\\',\\''+esc(a.task_type)+'\\')">▶ Открыть</button></div>';
    }).join('');
  }catch(e){ card.style.display = 'none'; }
}

async function openAssignment(aid, task_type){
  const sel = document.getElementById('tt');
  let found = false;
  for (let i=0; i<sel.options.length; i++){ if (sel.options[i].value === task_type){ found = true; break; } }
  if (!found) { const opt = document.createElement('option'); opt.value = task_type; opt.textContent = 'Назначение: '+task_type; sel.appendChild(opt); }
  sel.value = task_type;
  await gen({assignment_id: aid});
}

// ============================================================
// ВАРИАНТЫ — ученик
// ============================================================
const V_TASK_LABELS_S = {"1":"1","2":"2","3-9":"3–9","10":"10","11":"11","12-18":"12–18",
  "19-24":"19–24","25-29":"25–29","30-36":"30–36","37":"37","38.1":"38.1","38.2":"38.2"};
const V_TASK_MAX = {"1":2,"2":3,"3-9":7,"10":3,"11":2,"12-18":7,"19-24":6,"25-29":5,
  "30-36":7,"37":6,"38.1":14,"38.2":14};
let _myVariantsCache = null;
let _activeVariant = null;

async function loadMyVariants(){
  if (!IS_LOGGED_IN) return;
  var card = document.getElementById('myVariantsCard');
  var box = document.getElementById('myVariants');
  try{
    var d = await fetch(window.location.pathname,{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({action:'variant_my_list', student_code: STUDENT_CODE})}).then(function(r){return r.json();});
    if (d.error || !d.variants || !d.variants.length) { card.style.display = 'none'; return; }
    card.style.display = 'block';
    _myVariantsCache = d.variants;
    box.innerHTML = d.variants.map(function(v, i){
      var sub = v.submission;
      var status = 'not_started', statusText = 'Не начат';
      var scoreHtml = '<div class="sub-score pending">—</div>';
      if (sub){
        if (sub.status === 'submitted'){
          status = 'submitted'; statusText = 'На проверке';
          scoreHtml = '<div class="sub-score pending">⏳ '+sub.total_score+' / '+sub.total_max+'</div>';
        } else if (sub.status === 'reviewed'){
          status = 'reviewed'; statusText = 'Проверено';
          scoreHtml = '<div class="sub-score">'+sub.total_score+' / '+sub.total_max+'</div>';
        }
      }
      return '<div class="sub-item status-'+status+'">'
        + '<div class="sub-info">'
        + '<div class="sub-title">Вариант '+esc(v.code)+' '
        + '<span class="badge-status '+status+'">'+statusText+'</span></div>'
        + '<div class="sub-date">'+v.task_types.length+' заданий · макс. '+v.total_max+' баллов</div>'
        + '</div>' + scoreHtml
        + '<button class="btn btn-sm" onclick="openVariant('+i+')">▶ Открыть</button>'
        + '</div>';
    }).join('');
  }catch(e){ card.style.display = 'none'; }
}

async function openVariant(idx){
  var v = _myVariantsCache[idx];
  if (!v) return;
  var d = await fetch(window.location.pathname,{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({action:'variant_get_full', id:v.id, student_code: STUDENT_CODE})}).then(function(r){return r.json();});
  if (d.error) { alert(d.error); return; }
  _activeVariant = {variant:d.variant, submission:d.submission, answers:(d.submission && d.submission.answers) || {}};
  renderVariantSolver();
}

function scrollToVTask(i){
  var el = document.getElementById('vTask_'+i);
  if (el) el.scrollIntoView({behavior:'smooth'});
}

function renderVariantSolver(){
  var r = document.getElementById('r');
  var v = _activeVariant.variant;
  var sub = _activeVariant.submission;
  var tasks = v.data;
  var h = '<div class="card"><h3>📦 Вариант '+esc(v.code)+'</h3>';
  h += '<div class="info" style="margin-bottom:12px">Максимум: <b style="color:#00e5ff">'+v.total_max+'</b> баллов. Заданий: <b>'+v.task_types.length+'</b>.</div>';

  if (sub && (sub.status === 'submitted' || sub.status === 'reviewed')){
    h += renderVariantResult(sub, v);
    h += '</div>';
    r.innerHTML = h;
    if (sub.status === 'submitted') {
      var info = document.createElement('div');
      info.className = 'comment-box';
      info.style.cssText = 'background:rgba(243,156,18,.1);border-color:rgba(243,156,18,.3);color:#fbd88b;margin-top:12px';
      info.textContent = '⏳ Вариант отправлен на проверку. Тест оценён, письмо ожидает учителя.';
      r.insertBefore(info, r.firstChild);
    }
    return;
  }

  h += '<button class="btn btn-outline" style="width:auto;margin-bottom:14px" onclick="variantDownloadPDFFromServer(\\''+esc(v.id)+'\\')">📄 Скачать PDF (без ответов)</button>';
  var nav = '<div class="vnav">';
  v.task_types.forEach(function(t, i){
    nav += '<button onclick="scrollToVTask('+i+')">'+V_TASK_LABELS_S[t]+'</button>';
  });
  nav += '</div>';
  h += nav;

  v.task_types.forEach(function(t, i){
    h += '<div class="vsection" id="vTask_'+i+'">';
    h += '<h4>Задание '+esc(V_TASK_LABELS_S[t])+' (макс. '+V_TASK_MAX[t]+')</h4>';
    h += renderVariantTaskInput(t, tasks[t]);
    h += '</div>';
  });

  h += '<div style="margin-top:20px"><button class="btn btn-ok" onclick="submitVariant()">📤 Отправить вариант на проверку</button></div>';
  h += '<div id="vSubmitInfo" class="info" style="text-align:center"></div>';
  h += '</div>';
  r.innerHTML = h;
  v.task_types.forEach(function(t){ initVariantTaskInput(t, tasks[t]); });
}

function renderVariantTaskInput(t, d){
  var h = '';
  if (d.instruction) h += '<div class="inst">'+esc(d.instruction)+'</div>';
  if (t === '1'){
    (d.statements||[]).forEach(function(s){h += '<div class="rw"><b>'+s.number+'.</b> '+esc(s.text)+'</div>';});
    h += '<table class="tb"><tr><th>Говорящий</th>'+'ABCDEF'.split('').map(function(k){return '<th>'+k+'</th>';}).join('')+'</tr>';
    h += '<tr><td>Ответ</td>'+'ABCDEF'.split('').map(function(k){return '<td><input class="ip" style="width:60px" maxlength="1" id="vin_1_'+k+'"></td>';}).join('')+'</tr></table>';
  } else if (t === '2'){
    (d.statements||[]).forEach(function(s){h += '<div class="rw"><b>'+esc(s.letter)+'.</b> '+esc(s.text)+'</div>';});
    h += '<table class="tb"><tr><th>Утв.</th>'+'ABCDEFG'.split('').map(function(k){return '<th>'+k+'</th>';}).join('')+'</tr>';
    h += '<tr><td>Ответ</td>'+'ABCDEFG'.split('').map(function(k){return '<td><input class="ip" style="width:60px" maxlength="1" id="vin_2_'+k+'"></td>';}).join('')+'</tr></table>';
    h += '<div class="info">1 – True, 2 – False, 3 – Not stated</div>';
  } else if (t === '3-9'){
    (d.questions||[]).forEach(function(q){
      h += '<div class="rw"><b>'+q.number+'.</b> '+esc(q.question)+'</div>';
      ['1','2','3'].forEach(function(k){h += '<label class="op"><input type="radio" name="vin_'+q.number+'" value="'+k+'">'+k+') '+esc(q.options[k])+'</label>';});
    });
  } else if (t === '10'){
    (d.headings||[]).forEach(function(x){h += '<div class="rw"><b>'+x.number+'.</b> '+esc(x.text)+'</div>';});
    h += '<div class="hr"></div>';
    (d.texts||[]).forEach(function(x){h += '<div class="sc"><b>'+esc(x.letter)+'.</b> '+esc(x.text)+'</div>';});
    h += '<table class="tb"><tr>'+'ABCDEFG'.split('').map(function(k){return '<th>'+k+'</th>';}).join('')+'</tr>';
    h += '<tr>'+'ABCDEFG'.split('').map(function(k){return '<td><input class="ip" style="width:60px" maxlength="1" id="vin_10_'+k+'"></td>';}).join('')+'</tr></table>';
  } else if (t === '11'){
    if (d.title) h += '<div class="tt"><b>'+esc(d.title)+'</b></div>';
    if (d.text) h += '<div class="tt">'+esc(d.text)+'</div>';
    h += '<h4 style="margin-top:10px">Фрагменты</h4>';
    (d.fragments||[]).forEach(function(f){h += '<div class="rw"><b>'+f.number+'.</b> '+esc(f.text)+'</div>';});
    h += '<table class="tb"><tr>'+'ABCDEF'.split('').map(function(k){return '<th>'+k+'</th>';}).join('')+'</tr>';
    h += '<tr>'+'ABCDEF'.split('').map(function(k){return '<td><input class="ip" style="width:60px" maxlength="1" id="vin_11_'+k+'"></td>';}).join('')+'</tr></table>';
  } else if (t === '12-18'){
    if (d.title) h += '<div class="tt"><b>'+esc(d.title)+'</b></div>';
    if (d.text) h += '<div class="tt">'+esc(d.text)+'</div>';
    (d.questions||[]).forEach(function(q){
      h += '<div class="rw"><b>'+q.number+'.</b> '+esc(q.question)+'</div>';
      ['1','2','3','4'].forEach(function(k){h += '<label class="op"><input type="radio" name="vin_'+q.number+'" value="'+k+'">'+k+') '+esc(q.options[k])+'</label>';});
    });
  } else if (t === '19-24' || t === '25-29'){
    if (d.title) h += '<div class="tt"><b>'+esc(d.title)+'</b></div>';
    if (d.text){
      var parts = String(d.text).split(/(__\d{2}__)/g);
      var idx = {};
      (d.items||[]).forEach(function(it){idx[it.number]=it.source_word;});
      h += '<div class="tt">';
      parts.forEach(function(p){
        var m = p.match(/^__(\d{2})__$/);
        if (m){
          h += '<div class="gap-line"><span class="gap-label">'+m[1]+'</span><input class="gap-input" id="vin_'+m[1]+'" placeholder="ваш ответ"><span class="gap-base">'+esc(idx[parseInt(m[1])]||'')+'</span></div>';
        } else h += esc(p);
      });
      h += '</div>';
    }
  } else if (t === '30-36'){
    if (d.title) h += '<div class="tt"><b>'+esc(d.title)+'</b></div>';
    if (d.text) h += '<div class="tt">'+esc(d.text)+'</div>';
    (d.items||[]).forEach(function(item){
      h += '<div class="rw"><b>'+item.number+'</b></div>';
      ['1','2','3','4'].forEach(function(k){h += '<label class="op"><input type="radio" name="vin_'+item.number+'" value="'+k+'">'+k+') '+esc(item.options[k])+'</label>';});
    });
  } else if (t === '37'){
    if (d.task_text) h += '<div class="tt">'+esc(d.task_text)+'</div>';
    var prev = (_activeVariant.answers['37'] || {}).text || '';
    h += '<div class="writing-area"><div class="comment-label" style="color:#c9b8ff;margin:10px 0 6px">✍️ Ваш ответ (90–154 слова)</div>';
    h += '<textarea id="vin_37_text" style="min-height:240px">'+esc(prev)+'</textarea></div>';
  } else if (t === '38.1' || t === '38.2'){
    if (d.task_text) h += '<div class="tt">'+esc(d.task_text)+'</div>';
    var sd = d.survey_data || {};
    if (sd.question) h += '<p style="text-align:center;font-weight:bold">The survey question: &laquo;'+esc(String(sd.question).replace(/^"+|"+$/g,''))+'&raquo;</p>';
    if (t === '38.1'){
      h += '<table class="tb"><tr><th>Options</th><th>Number of respondents (%)</th></tr>';
      (sd.options||[]).forEach(function(o){h += '<tr><td>'+esc(o.option)+'</td><td style="text-align:center">'+esc(o.percent)+'</td></tr>';});
      h += '</table>';
    } else {
      var opts2 = sd.options || [], grad = [], st2 = 0;
      opts2.forEach(function(o,i){var e = st2 + (Number(o.percent)/100)*360; grad.push(PIE[i%PIE.length]+' '+st2+'deg '+e+'deg'); st2 = e;});
      if (grad.length) h += '<div class="pi" style="background:conic-gradient('+grad.join(',')+')"></div>';
      h += '<div class="lg">';
      opts2.forEach(function(o,i){
        var lbl = (o.option && String(o.option).trim()) ? o.option : ('Segment '+(i+1));
        h += '<div class="i"><span class="c" style="background:'+PIE[i%PIE.length]+'"></span>'+esc(lbl)+' — '+esc(o.percent)+'%</div>';
      });
      h += '</div>';
    }
    h += '<p style="margin-top:14px"><b>Write 200–250 words.</b></p>';
    h += '<p><b>Use the following plan:</b></p>';
    (d.plan||[]).forEach(function(p){h += '<div class="pl">– '+esc(p)+'</div>';});
    var prev2 = (_activeVariant.answers[t] || {}).text || '';
    h += '<div class="writing-area"><div class="comment-label" style="color:#c9b8ff;margin:14px 0 6px">✍️ Ваш ответ (200–250 слов)</div>';
    h += '<textarea id="vin_'+t+'_text" style="min-height:280px">'+esc(prev2)+'</textarea></div>';
  }
  return h;
}

function initVariantTaskInput(t, d){
  var saved = _activeVariant.answers || {};
  if (t === '1'){ 'ABCDEF'.split('').forEach(function(k){var el = document.getElementById('vin_1_'+k); if (el && saved['1'] && saved['1'][k]) el.value = saved['1'][k];});}
  else if (t === '2'){ 'ABCDEFG'.split('').forEach(function(k){var el = document.getElementById('vin_2_'+k); if (el && saved['2'] && saved['2'][k]) el.value = saved['2'][k];});}
  else if (t === '3-9'){ (d.questions||[]).forEach(function(q){var v = saved['3-9'] && saved['3-9'][String(q.number)]; if (v){var el = document.querySelector('input[name="vin_'+q.number+'"][value="'+v+'"]'); if (el) el.checked = true;}});}
  else if (t === '10'){ 'ABCDEFG'.split('').forEach(function(k){var el = document.getElementById('vin_10_'+k); if (el && saved['10'] && saved['10'][k]) el.value = saved['10'][k];});}
  else if (t === '11'){ 'ABCDEF'.split('').forEach(function(k){var el = document.getElementById('vin_11_'+k); if (el && saved['11'] && saved['11'][k]) el.value = saved['11'][k];});}
  else if (t === '12-18'){ (d.questions||[]).forEach(function(q){var v = saved['12-18'] && saved['12-18'][String(q.number)]; if (v){var el = document.querySelector('input[name="vin_'+q.number+'"][value="'+v+'"]'); if (el) el.checked = true;}});}
  else if (t === '19-24' || t === '25-29'){ (d.items||[]).forEach(function(it){var el = document.getElementById('vin_'+it.number); if (el && saved[t] && saved[t][String(it.number)]) el.value = saved[t][String(it.number)];});}
  else if (t === '30-36'){ (d.items||[]).forEach(function(item){var v = saved['30-36'] && saved['30-36'][String(item.number)]; if (v){var el = document.querySelector('input[name="vin_'+item.number+'"][value="'+v+'"]'); if (el) el.checked = true;}});}
}

function collectVariantAnswers(){
  var v = _activeVariant.variant;
  var tasks = v.data;
  var answers = {};
  v.task_types.forEach(function(t){
    var d = tasks[t];
    if (t === '1'){ answers['1'] = {}; 'ABCDEF'.split('').forEach(function(k){var el = document.getElementById('vin_1_'+k); answers['1'][k] = el ? (el.value || '').trim().toUpperCase() : '';});}
    else if (t === '2'){ answers['2'] = {}; 'ABCDEFG'.split('').forEach(function(k){var el = document.getElementById('vin_2_'+k); answers['2'][k] = el ? (el.value || '').trim().toUpperCase() : '';});}
    else if (t === '3-9'){ answers['3-9'] = {}; (d.questions||[]).forEach(function(q){var el = document.querySelector('input[name="vin_'+q.number+'"]:checked'); answers['3-9'][String(q.number)] = el ? el.value : '';});}
    else if (t === '10'){ answers['10'] = {}; 'ABCDEFG'.split('').forEach(function(k){var el = document.getElementById('vin_10_'+k); answers['10'][k] = el ? (el.value || '').trim().toUpperCase() : '';});}
    else if (t === '11'){ answers['11'] = {}; 'ABCDEF'.split('').forEach(function(k){var el = document.getElementById('vin_11_'+k); answers['11'][k] = el ? (el.value || '').trim().toUpperCase() : '';});}
    else if (t === '12-18'){ answers['12-18'] = {}; (d.questions||[]).forEach(function(q){var el = document.querySelector('input[name="vin_'+q.number+'"]:checked'); answers['12-18'][String(q.number)] = el ? el.value : '';});}
    else if (t === '19-24' || t === '25-29'){ answers[t] = {}; (d.items||[]).forEach(function(it){var el = document.getElementById('vin_'+it.number); answers[t][String(it.number)] = el ? (el.value || '').trim() : '';});}
    else if (t === '30-36'){ answers['30-36'] = {}; (d.items||[]).forEach(function(item){var el = document.querySelector('input[name="vin_'+item.number+'"]:checked'); answers['30-36'][String(item.number)] = el ? el.value : '';});}
    else if (t === '37'){ var ta = document.getElementById('vin_37_text'); answers['37'] = {text: ta ? ta.value : ''};}
    else if (t === '38.1' || t === '38.2'){ var ta2 = document.getElementById('vin_'+t+'_text'); answers[t] = {text: ta2 ? ta2.value : ''};}
  });
  return answers;
}

async function submitVariant(){
  if (!_activeVariant) return;
  var answers = collectVariantAnswers();
  if (!confirm('Отправить вариант? После этого редактирование будет недоступно.')) return;
  var info = document.getElementById('vSubmitInfo');
  if (info) info.textContent = '📤 Отправляю…';
  var d = await fetch(window.location.pathname,{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({action:'variant_submit', student_code:STUDENT_CODE,
      variant_id:_activeVariant.variant.id, answers:answers})}).then(function(r){return r.json();});
  if (d.error){ if (info) info.textContent = '💥 '+d.error; return; }
  _activeVariant.submission = d.submission;
  _activeVariant.answers = d.submission.answers;
  renderVariantSolver();
  loadMyVariants();
  loadMyStats();
}

async function variantDownloadPDFFromServer(vid){
  var d = await fetch(window.location.pathname,{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({action:'variant_get_full', id:vid, student_code: STUDENT_CODE})}).then(function(r){return r.json();});
  if (d.error){ alert(d.error); return; }
  var v = d.variant;
  var body = '<h1>Вариант '+esc(v.code)+'</h1>';
  body += '<div class="meta">Письменная часть ЕГЭ по английскому языку</div>';
  var first = true;
  ['1','2','3-9','10','11','12-18','19-24','25-29','30-36','37','38.1','38.2'].forEach(function(t){
    if (!v.data[t]) return;
    if (!first) body += '<div class="page-break"></div>';
    first = false;
    body += '<h2>Задание '+esc(t)+'</h2>';
    body += renderTaskForPrint(t, v.data[t], {withAnswers:false});
  });
  body += '<div class="page-break"></div>';
  body += '<h2>Бланк ответов</h2>';
  body += '<div style="border-bottom:1pt dotted #888;height:22pt;margin:8pt 0"></div>'.repeat(40);
  openPrintWindow(body, 'Вариант '+v.code);
}

function renderVariantResult(sub, v){
  var h = '<div style="margin-top:16px;padding:16px;background:rgba(46,204,113,.08);border:1px solid rgba(46,204,113,.3);border-radius:12px">';
  h += '<div style="font-size:20px;font-weight:800;color:#2ecc71;font-family:monospace;text-align:center;margin-bottom:6px">'
    + 'ИТОГО: '+sub.total_score+' / '+sub.total_max+'</div>';
  h += '<div style="text-align:center;color:#8b93c4;font-size:13px">Тест: '+sub.test_score+' / '+sub.test_max;
  if (sub.manual_pending && sub.manual_pending.length){
    h += ' · Письмо: ⏳ ожидает проверки ('+sub.manual_pending.join(', ')+')';
  }
  h += '</div></div>';
  h += '<h4 style="margin-top:18px;color:#c9b8ff">📋 Разбор по заданиям</h4>';
  v.task_types.forEach(function(t){
    var sc = sub.scores[t];
    if (!sc) return;
    var icon, color;
    if (sc.manual && sc.pending){ icon = '⏳'; color = '#f39c12'; }
    else if (sc.manual) { icon = '📝'; color = '#2ecc71'; }
    else if (sc.score === sc.max) { icon = '✅'; color = '#2ecc71'; }
    else if (sc.score === 0) { icon = '❌'; color = '#e74c3c'; }
    else { icon = '⚠'; color = '#f39c12'; }
    h += '<details style="margin-top:10px;background:rgba(5,6,15,.4);border-radius:10px;padding:12px;border-left:4px solid '+color+'">';
    h += '<summary style="cursor:pointer;font-weight:700;color:'+color+'">'+icon+' Задание '+esc(t);
    if (sc.manual && sc.pending){ h += ' — на проверке'; }
    else { h += ' — '+sc.score+' / '+sc.max; }
    h += '</summary>';
    if (sc.manual && sc.pending){
      h += '<div style="margin-top:10px;color:#fbd88b">Работа отправлена учителю. Как только он проверит, баллы обновятся автоматически.</div>';
    } else if (sc.manual && sc.review){
      var rv = sc.review;
      h += '<div style="margin-top:10px">';
      Object.keys(rv.scores || {}).forEach(function(code){
        h += '<div style="display:flex;justify-content:space-between;padding:6px 10px;margin:4px 0;background:rgba(5,6,15,.5);border-radius:6px;font-size:13px">'
          + '<span style="color:#00e5ff;font-family:monospace">'+esc(code)+'</span>'
          + '<span style="color:#c8cdf0">'+rv.scores[code]+'</span></div>';
      });
      if (rv.comment) h += '<div style="margin-top:10px;padding:10px;background:rgba(46,204,113,.08);border-radius:8px;color:#c8cdf0;font-size:13px;white-space:pre-wrap">💬 '+esc(rv.comment)+'</div>';
      h += '</div>';
    } else if (sc.detail){
      var exps = (v.data[t] && v.data[t].explanations) || {};
      Object.keys(sc.detail).forEach(function(key){
        var it = sc.detail[key];
        var mark = it.ok ? '✅' : '❌';
        var c = it.ok ? '#2ecc71' : '#e74c3c';
        h += '<div style="padding:8px 10px;margin:6px 0;background:rgba(5,6,15,.5);border-radius:6px;font-size:13px;border-left:3px solid '+c+'">';
        h += '<div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px">'
          + '<span style="color:#c8cdf0">'+esc(key)+'</span>'
          + '<span style="color:#8b93c4">ваш: <b style="color:'+c+'">'+esc(it.given || '—')+'</b> · верно: <b style="color:#2ecc71">'+esc(it.correct || '—')+'</b> '+mark+'</span>'
          + '</div>';
        if (exps[key]) h += '<div style="margin-top:6px;padding:8px 10px;background:rgba(123,92,255,.08);border-radius:6px;color:#c8cdf0;font-size:12.5px;line-height:1.6">💡 '+esc(exps[key])+'</div>';
        h += '</div>';
      });
    }
    h += '</details>';
  });
  return h;
}

async function gen(opts){
  opts = opts || {};
  const b=document.getElementById('bt'),r=document.getElementById('r');
  const rlBar = document.getElementById('rlBar');
  b.disabled=true;b.textContent='🛰 Сканируем орбитальный архив…';
  r.innerHTML='<div class="ld"><div class="rk">🚀</div><div style="margin-top:18px;font-size:16px">Проверяем базу данных…</div></div>';
  const task_type = document.getElementById('tt').value;
  setTimeout(function(){ if(b.disabled) b.textContent='🛰 Архив пуст, включаю синтез…'; }, 1500);
  try{
    const payload = {action:'fetch', task_type: task_type, topic: document.getElementById('tp').value, client_id: getClientId()};
    if (IS_LOGGED_IN) payload.student_code = STUDENT_CODE;
    if (opts.assignment_id) payload.assignment_id = opts.assignment_id;
    const res = await fetch(window.location.pathname, {method:'POST',headers:{'Content-Type':'application/json'},
      body: JSON.stringify(payload)});
    const d = await res.json();
    if (d.ratelimit) updateRlBar(d.ratelimit);
    if (d.error) {
      r.innerHTML='<div class="er">💥 '+esc(d.error)+(d.code_required?'<br><br>Обратитесь к учителю за кодом доступа.':'')+'</div>';
      return;
    }
    if (!d.task_data) { r.innerHTML='<div class="er">Нет task_data</div>'; return; }
    const td = d.task_data;
    if (td.audio_b64) {
      const bytes = b64ToBytes(td.audio_b64);
      const url = URL.createObjectURL(new Blob([bytes], {type:'audio/mpeg'}));
      window._audioUrl = url;
      render(td);
      const btn = document.getElementById('playBtn');
      if (btn) { btn.disabled = false; btn.textContent = '▶ Прослушать задание'; }
      const st = document.getElementById('audioStatus');
      if (st && td._meta && td._meta.code) st.innerHTML = '✅ Из архива (' + esc(td._meta.code) + ')';
      return;
    }
    render(td);
    if (['1','2','3-9'].indexOf(task_type) !== -1) {
      const statusEl = document.getElementById('audioStatus');
      if (statusEl) statusEl.textContent = '🎙 Озвучиваем часть 1/2…';
      try {
        const t1 = await fetch(window.location.pathname, {method:'POST',headers:{'Content-Type':'application/json'},
          body: JSON.stringify({action:'tts', task_type, task_data: td, part: 1})}).then(x=>x.json());
        if (t1.error) { if (statusEl) statusEl.textContent = '⚠ '+t1.error; return; }
        if (statusEl) statusEl.textContent = '🎙 Озвучиваем часть 2/2…';
        const t2 = await fetch(window.location.pathname, {method:'POST',headers:{'Content-Type':'application/json'},
          body: JSON.stringify({action:'tts', task_type, task_data: td, part: 2})}).then(x=>x.json());
        if (t2.error) { if (statusEl) statusEl.textContent = '⚠ '+t2.error; return; }
        const b1 = b64ToBytes(t1.audio), b2 = b64ToBytes(t2.audio);
        const comb = new Uint8Array(b1.length + b2.length);
        comb.set(b1, 0); comb.set(b2, b1.length);
        const url = URL.createObjectURL(new Blob([comb], {type:'audio/mpeg'}));
        window._audioUrl = url;
        const sizeMB = (comb.length / 1024 / 1024).toFixed(1);
        const btn = document.getElementById('playBtn');
        if (btn) { btn.disabled = false; btn.textContent = '▶ Прослушать задание'; }
        if (statusEl) statusEl.innerHTML = '✅ Аудио готово (' + sizeMB + ' МБ).';
      } catch(e) { if (statusEl) statusEl.textContent = '⚠ '+e.message; }
    }
  }catch(e){ r.innerHTML='<div class="er">💥 '+esc(e.message)+'</div>'; }
  finally{ b.disabled=false; b.textContent='🚀 Запустить задание'; }
}

function updateRlBar(rl){
  const bar = document.getElementById('rlBar');
  if (!rl || !rl.enabled || IS_LOGGED_IN) { bar.textContent=''; return; }
  const cls = rl.left === 0 ? 'err' : (rl.left <= 1 ? 'warn' : '');
  bar.className = 'rl-bar ' + cls;
  bar.innerHTML = 'Осталось бесплатных попыток: <b>' + rl.left + ' / ' + rl.max + '</b>';
}

let _playing=false,_audioEl=null;
function playFull(){
  if(_playing||!window._audioUrl)return;
  _playing=true;
  const btn=document.getElementById('playBtn'),st=document.getElementById('audioStatus');
  btn.disabled=true;btn.textContent='🔊 Воспроизведение...';
  if(st)st.textContent='🎧 Слушаем...';
  if(!_audioEl)_audioEl=new Audio();
  _audioEl.src=window._audioUrl;
  _audioEl.onended=function(){_playing=false;btn.disabled=false;btn.textContent='▶ Прослушать заново';if(st)st.textContent='✅ Готово';};
  _audioEl.play().catch(function(e){_playing=false;btn.disabled=false;btn.textContent='▶ Прослушать задание';if(st)st.textContent='⚠ '+e.message;});
}

function render(d){
  window._key=d.answer_key||{};
  window._taskData = d;
  const r=document.getElementById('r');
  const t=d._meta?d._meta.task_type:'';
  const src = d._meta && d._meta.source === 'bank' ? ' <span style="font-size:12px;color:#8b93c4">['+esc(d._meta.code)+']</span>' : '';
  let h='<div class="card"><h3>Задание '+esc(t)+src+'</h3>';
  h+='<button class="btn btn-outline btn-sm" style="margin-bottom:14px;padding:8px 14px" onclick="downloadTaskPDF()">📄 Скачать PDF (без ответов)</button>';
  if(d.instruction)h+='<div class="tt" style="font-style:italic;color:#a0a8d0">'+esc(d.instruction)+'</div>';
  if(['1','2','3-9'].indexOf(t)!==-1){
    h+='<button class="btn btn-ok" id="playBtn" onclick="playFull()" disabled>⌛ Готовим аудио…</button>';
    h+='<div id="audioStatus" class="info" style="text-align:center;margin-top:10px"></div>';
  }
  if(t==='1'){
    (d.statements||[]).forEach(function(s){h+='<div class="rw"><b>'+s.number+'.</b> <span>'+esc(s.text)+'</span></div>';});
    h+='<table class="tb"><tr><th>Говорящий</th>';
    'ABCDEF'.split('').forEach(function(k){h+='<th>'+k+'</th>';});
    h+='</tr><tr><td>Утверждение</td>';
    'ABCDEF'.split('').forEach(function(k){h+='<td><input class="ip" style="width:60px" id="ans_'+k+'" maxlength="1"></td>';});
    h+='</tr></table><button class="btn btn-ok" onclick="checkLettersABCDEF()">✅ Проверить</button><div id="fb"></div>';
  }
  else if(t==='2'){
    (d.statements||[]).forEach(function(s){h+='<div class="rw"><b>'+esc(s.letter)+'.</b> <span>'+esc(s.text)+'</span></div>';});
    h+='<table class="tb"><tr><th>Утв.</th>';
    'ABCDEFG'.split('').forEach(function(k){h+='<th>'+k+'</th>';});
    h+='</tr><tr><td>Ответ</td>';
    'ABCDEFG'.split('').forEach(function(k){h+='<td><input class="ip" style="width:60px" id="ans_'+k+'" maxlength="1"></td>';});
    h+='</tr></table><button class="btn btn-ok" onclick="checkLettersABCDEFG()">✅ Проверить</button><div id="fb"></div>';
  }
  else if(t==='3-9'){
    (d.questions||[]).forEach(function(q){
      h+='<div class="rw"><b>'+q.number+'.</b> <span>'+esc(q.question)+'</span></div>';
      ['1','2','3'].forEach(function(k){h+='<label class="op"><input type="radio" name="q_'+q.number+'" value="'+k+'">'+k+') '+esc(q.options[k])+'</label>';});
    });
    h+='<button class="btn btn-ok" onclick="checkRadio()">✅ Проверить</button><div id="fb"></div>';
  }
  else if(t==='10'){
    (d.headings||[]).forEach(function(x){h+='<div class="rw"><b>'+x.number+'.</b> <span>'+esc(x.text)+'</span></div>';});
    h+='<div class="hr"></div>';
    (d.texts||[]).forEach(function(x){h+='<div class="sc"><b>'+esc(x.letter)+'.</b> '+esc(x.text)+'</div>';});
    h+='<table class="tb"><tr>';'ABCDEFG'.split('').forEach(function(k){h+='<th>'+k+'</th>';});h+='</tr><tr>';
    'ABCDEFG'.split('').forEach(function(k){h+='<td><input class="ip" style="width:60px" id="ans_'+k+'" maxlength="1"></td>';});
    h+='</tr></table><button class="btn btn-ok" onclick="checkLettersABCDEFG()">✅ Проверить</button><div id="fb"></div>';
  }
  else if(t==='11'){
    if(d.title)h+='<div class="tt"><b>'+esc(d.title)+'</b></div>';
    if(d.text)h+='<div class="tt">'+esc(d.text)+'</div>';
    h+='<div class="hr"></div><b>Фрагменты:</b>';
    (d.fragments||[]).forEach(function(f){h+='<div class="rw"><b>'+f.number+'.</b> <span>'+esc(f.text)+'</span></div>';});
    h+='<table class="tb"><tr>';'ABCDEF'.split('').forEach(function(k){h+='<th>'+k+'</th>';});h+='</tr><tr>';
    'ABCDEF'.split('').forEach(function(k){h+='<td><input class="ip" style="width:60px" id="ans_'+k+'" maxlength="1"></td>';});
    h+='</tr></table><button class="btn btn-ok" onclick="checkLettersABCDEF()">✅ Проверить</button><div id="fb"></div>';
  }
  else if(t==='12-18'){
    if(d.title)h+='<div class="tt"><b>'+esc(d.title)+'</b></div>';
    if(d.text)h+='<div class="tt">'+esc(d.text)+'</div>';
    h+='<div class="hr"></div>';
    (d.questions||[]).forEach(function(q){
      h+='<div class="rw"><b>'+q.number+'.</b> <span>'+esc(q.question)+'</span></div>';
      ['1','2','3','4'].forEach(function(k){h+='<label class="op"><input type="radio" name="q_'+q.number+'" value="'+k+'">'+k+') '+esc(q.options[k])+'</label>';});
    });
    h+='<button class="btn btn-ok" onclick="checkRadio()">✅ Проверить</button><div id="fb"></div>';
  }
  else if(t==='19-24'||t==='25-29'){
    if(d.title)h+='<div class="tt"><b>'+esc(d.title)+'</b></div>';
    if(d.text){
      const parts=d.text.split(/(__\\d{2}__)/g);
      const items=d.items||[], idx={};
      items.forEach(function(it){idx[it.number]=it.source_word;});
      h+='<div class="tt">';
      parts.forEach(function(p){
        const m=p.match(/^__(\\d{2})__$/);
        if(m)h+='<div class="gap-line"><span class="gap-label">'+m[1]+'</span> <input class="gap-input" id="ans_'+m[1]+'" placeholder="ваш ответ"> <span class="gap-base">'+esc(idx[parseInt(m[1])]||'')+'</span></div>';
        else h+=esc(p);
      });
      h+='</div>';
    }
    const nums=(d.items||[]).map(function(x){return String(x.number);});
    h+='<button class="btn btn-ok" onclick="checkNums('+JSON.stringify(nums)+')">✅ Проверить</button><div id="fb"></div>';
  }
  else if(t==='30-36'){
    if(d.title)h+='<div class="tt"><b>'+esc(d.title)+'</b></div>';
    if(d.text)h+='<div class="tt">'+esc(d.text)+'</div>';
    h+='<div class="hr"></div>';
    (d.items||[]).forEach(function(item){
      h+='<div class="rw"><b>'+item.number+'</b></div>';
      ['1','2','3','4'].forEach(function(k){h+='<label class="op"><input type="radio" name="q_'+item.number+'" value="'+k+'">'+k+') '+esc(item.options[k])+'</label>';});
    });
    h+='<button class="btn btn-ok" onclick="checkRadio()">✅ Проверить</button><div id="fb"></div>';
  }
  else if(t==='37' || t==='38.1' || t==='38.2'){
    renderWritingTask(h, d, t);
    return;
  }
  h+='</div>';
  r.innerHTML=h;
}

async function renderWritingTask(initialH, d, t){
  const r = document.getElementById('r');
  let h = initialH;
  if (t === '37') {
    if (d.task_text) h += '<div class="tt">'+esc(d.task_text)+'</div>';
  } else if (t === '38.1') {
    if (d.task_text) h += '<div class="tt">'+esc(d.task_text)+'</div>';
    const sd = d.survey_data || {};
    if (sd.question) { const q = String(sd.question).replace(/^"+|"+$/g,'').trim();
      h += '<p style="text-align:center;font-weight:bold;margin:18px 0 10px;font-size:16px">The survey question: "'+esc(q)+'"</p>'; }
    h += '<table class="tb"><tr><th>Options</th><th>Number of respondents (%)</th></tr>';
    (sd.options||[]).forEach(function(o){h += '<tr><td>'+esc(o.option)+'</td><td>'+esc(o.percent)+'</td></tr>';});
    h += '</table>';
    h += '<p style="margin-top:20px;font-size:16px"><b>Write 200–250 words.</b></p>';
    h += '<p style="font-size:16px"><b>Use the following plan:</b></p>';
    (d.plan||[]).forEach(function(p){h += '<div class="pl">– '+esc(p)+'</div>';});
  } else if (t === '38.2') {
    if (d.task_text) h += '<div class="tt">'+esc(d.task_text)+'</div>';
    const sd = d.survey_data || {}, opts = sd.options || [];
    if (sd.question) { const q = String(sd.question).replace(/^"+|"+$/g,'').trim();
      h += '<p style="text-align:center;font-weight:bold;margin:18px 0 10px;font-size:16px">The survey question: "'+esc(q)+'"</p>'; }
    let grad = [], st = 0;
    opts.forEach(function(o,i){const e = st + (Number(o.percent)/100)*360; grad.push(PIE[i%PIE.length]+' '+st+'deg '+e+'deg'); st = e;});
    if (grad.length) h += '<div class="pi" style="background:conic-gradient('+grad.join(',')+')"></div>';
    h += '<div class="lg">';
    opts.forEach(function(o,i){
      const lbl = (o.option && String(o.option).trim()) ? o.option : ('Segment '+(i+1));
      h += '<div class="i"><span class="c" style="background:'+PIE[i%PIE.length]+'"></span>'+esc(lbl)+' — '+esc(o.percent)+'%</div>';
    });
    h += '</div>';
    h += '<p style="margin-top:20px;font-size:16px"><b>Write 200–250 words.</b></p>';
    h += '<p style="font-size:16px"><b>Use the following plan:</b></p>';
    (d.plan||[]).forEach(function(p){h += '<div class="pl">– '+esc(p)+'</div>';});
  }
  if (!IS_LOGGED_IN) {
    h += '<div class="er" style="margin-top:18px">✍️ Чтобы писать и отправлять на проверку, войдите по коду от учителя.</div></div>';
    r.innerHTML = h; return;
  }
  h += '<div class="writing-area" style="margin-top:18px">'
    + '<div class="comment-label" style="color:#c9b8ff;margin-bottom:10px">✍️ Ваш ответ</div>'
    + '<textarea id="answerText" placeholder="Начните писать здесь... Черновик сохраняется автоматически."></textarea>'
    + '<div class="draft-hint" id="draftHint"></div>'
    + '<div class="submit-bar"><button class="btn btn-ok" id="submitBtn" onclick="submitWork()">📤 Отправить на проверку</button></div>'
    + '<div class="info" id="submitInfo"></div></div>';
  h += '</div>';
  r.innerHTML = h;
  try{
    const subR = await fetch(window.location.pathname,{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({action:'my_submissions', student_code: STUDENT_CODE})});
    const sd = await subR.json();
    const existingDraft = (sd.submissions||[]).find(function(x){return x.task_type === t && x.status === 'draft';});
    if (existingDraft) {
      const full = await fetch(window.location.pathname,{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({action:'get_submission', student_code: STUDENT_CODE, submission_id: existingDraft.id})}).then(x=>x.json());
      if (full && full.answer_text) {
        document.getElementById('answerText').value = full.answer_text;
        window._submissionId = existingDraft.id;
        document.getElementById('draftHint').textContent = '✅ Загружен сохранённый черновик';
      }
    }
  }catch(e){}
  const ta = document.getElementById('answerText');
  let saveTimer = null;
  ta.addEventListener('input', function(){
    if (saveTimer) clearTimeout(saveTimer);
    document.getElementById('draftHint').textContent = '⌛ сохраняем…';
    saveTimer = setTimeout(function(){ saveDraft(); }, 2500);
  });
}

async function saveDraft(){
  if (!IS_LOGGED_IN) return;
  const ta = document.getElementById('answerText');
  if (!ta) return;
  const txt = ta.value;
  const d = window._taskData || {};
  const t = d._meta ? d._meta.task_type : null;
  if (!t) return;
  try{
    const r = await fetch(window.location.pathname,{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({action:'save_draft', student_code: STUDENT_CODE, task_type: t,
        task_data: d, assignment_id: (d._meta && d._meta.assignment_id) || null,
        bank_code: (d._meta && d._meta.code) || null, answer_text: txt})});
    const res = await r.json();
    if (res.ok) {
      window._submissionId = res.id;
      document.getElementById('draftHint').textContent = '✅ Черновик сохранён ('+new Date().toLocaleTimeString('ru-RU',{hour:'2-digit',minute:'2-digit'})+')';
    }
  }catch(e){ document.getElementById('draftHint').textContent = '⚠ Не удалось сохранить'; }
}

async function submitWork(){
  if (!IS_LOGGED_IN) return;
  const ta = document.getElementById('answerText');
  const txt = (ta.value || '').trim();
  if (!txt) { alert('Пустой ответ'); return; }
  if (!confirm('Отправить работу на проверку?')) return;
  const d = window._taskData || {};
  const t = d._meta ? d._meta.task_type : null;
  if (!t) return;
  await saveDraft();
  const sid = window._submissionId;
  if (!sid) { alert('Не удалось создать работу'); return; }
  try{
    const r = await fetch(window.location.pathname,{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({action:'submit_work', student_code: STUDENT_CODE, submission_id: sid, answer_text: txt})});
    const res = await r.json();
    if (res.error) { alert('Ошибка: '+res.error); return; }
    document.getElementById('submitInfo').innerHTML = '✅ Работа отправлена на проверку.';
    document.getElementById('submitBtn').disabled = true;
    document.getElementById('submitBtn').textContent = '⏳ На проверке';
    ta.disabled = true;
    loadMyWorks(); loadMyStats();
  }catch(e){ alert('Ошибка: '+e.message); }
}

function markInput(id,correct){
  const el=document.getElementById('ans_'+id);
  if(!el)return false;
  const v=(el.value||'').trim().toUpperCase(),c=String(correct).toUpperCase();
  el.classList.remove('correct','wrong');
  if(v===c){el.classList.add('correct');return true}
  el.classList.add('wrong');return false;
}
function checkLettersABCDEF(){ checkLetters('ABCDEF'); }
function checkLettersABCDEFG(){ checkLetters('ABCDEFG'); }

function _explanationsHTML(keys){
  var d = window._taskData || {};
  var exps = d.explanations || {};
  if (!exps || !Object.keys(exps).length) return '';
  var order = keys && keys.length ? keys : Object.keys(exps);
  var shown = order.filter(function(k){return exps[k];});
  if (!shown.length) return '';
  var h = '<details style="margin-top:14px;background:rgba(46,204,113,.08);border:1px solid rgba(46,204,113,.3);border-radius:10px;padding:12px">';
  h += '<summary style="cursor:pointer;color:#2ecc71;font-weight:700;font-size:15px">💡 Объяснения (почему так)</summary>';
  h += '<div style="margin-top:10px">';
  shown.forEach(function(k){
    h += '<div style="padding:8px 12px;margin:6px 0;background:rgba(5,6,15,.4);border-radius:8px;border-left:3px solid #2ecc71;color:#c8cdf0;font-size:13px;line-height:1.6">'
      + '<b style="color:#2ecc71;font-family:monospace">'+esc(k)+':</b> '+esc(exps[k])+'</div>';
  });
  h += '</div></details>';
  return h;
}

function checkLetters(letters){
  const key=window._key||{};
  let ok=0;
  letters.split('').forEach(function(k){ if(markInput(k,key[k]||'?')) ok++; });
  let fb = '<div class="tt"><b>Результат: '+ok+'/'+letters.length+'</b></div>';
  fb += _explanationsHTML(letters.split(''));
  document.getElementById('fb').innerHTML = fb;
}
function checkRadio(){
  const key=window._key||{};
  let ok=0,tot=0;
  Object.keys(key).forEach(function(n){
    const opts=document.querySelectorAll('input[name="q_'+n+'"]');
    if(!opts.length)return;
    tot++;
    opts.forEach(function(o){o.parentElement.classList.remove('correct','wrong');});
    opts.forEach(function(o){if(o.value==String(key[n]))o.parentElement.classList.add('correct');if(o.checked&&o.value!=String(key[n]))o.parentElement.classList.add('wrong');});
    const sel=document.querySelector('input[name="q_'+n+'"]:checked');
    if(sel&&sel.value==String(key[n]))ok++;
  });
  let fb = '<div class="tt"><b>Результат: '+ok+'/'+tot+'</b></div>';
  fb += _explanationsHTML(Object.keys(key));
  document.getElementById('fb').innerHTML = fb;
}
function checkNums(nums){
  const key=window._key||{};
  let ok=0,tot=0;
  nums.forEach(function(n){
    if(key[n]==null)return; tot++;
    const el=document.getElementById('ans_'+n); if(!el)return;
    const v=(el.value||'').trim().toLowerCase(), cc=String(key[n]).toLowerCase();
    el.classList.remove('correct','wrong');
    if(v===cc||cc.split(' / ').map(function(x){return x.trim();}).indexOf(v)>=0){el.classList.add('correct');ok++}
    else el.classList.add('wrong');
  });
  let fb = '<div class="tt"><b>Результат: '+ok+'/'+tot+'</b></div>';
  fb += _explanationsHTML(nums);
  document.getElementById('fb').innerHTML = fb;
}

loadMaterials();
if (IS_LOGGED_IN) {
  loadMyWorks();
  loadMyStats();
  loadMyAssignments();
  loadMyVariants();
}
</script>
</body>
</html>"""
ADMIN_HTML = r"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>⚙ Админка — Космодром ЕГЭ</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#05060f;--purple:#7b5cff;--cyan:#00e5ff;--text:#e8ecff;--dim:#8b93c4;--ok:#2ecc71;--warn:#f39c12;--err:#e74c3c;--card:rgba(20,25,60,.55)}
html,body{min-height:100%;background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif}
.wrap{max-width:1200px;margin:0 auto;padding:32px 20px 80px}
h1{font-size:28px;margin-bottom:6px;background:linear-gradient(135deg,#fff,#c9b8ff,#00e5ff);-webkit-background-clip:text;background-clip:text;color:transparent}
.sub{color:var(--dim);font-size:14px;margin-bottom:20px}
.tabs{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:20px;padding:6px;background:rgba(20,25,60,.5);border:1px solid rgba(123,92,255,.3);border-radius:14px;position:sticky;top:12px;z-index:50;backdrop-filter:blur(14px)}
.tab{padding:10px 16px;border-radius:10px;font-size:14px;font-weight:600;cursor:pointer;border:none;background:transparent;color:var(--dim);transition:all .15s;position:relative}
.tab:hover{color:var(--text);background:rgba(123,92,255,.1)}
.tab.active{background:linear-gradient(135deg,#7b5cff,#ff5cf0);color:#fff;box-shadow:0 4px 16px rgba(123,92,255,.45)}
.tab .cnt{display:inline-block;margin-left:6px;padding:1px 8px;border-radius:20px;font-size:11px;background:rgba(255,255,255,.2)}
.tab.active .cnt{background:rgba(0,0,0,.3)}
.tab-pane{display:none}
.tab-pane.active{display:block;animation:fade .2s}
@keyframes fade{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}
.panel{background:var(--card);border:1px solid rgba(123,92,255,.35);border-radius:18px;padding:22px;backdrop-filter:blur(20px);margin-bottom:18px}
.panel h3{font-size:16px;color:#c9b8ff;margin-bottom:14px}
.f{margin-bottom:14px}
.f label{display:block;font-size:12px;text-transform:uppercase;letter-spacing:1.2px;color:var(--dim);margin-bottom:6px;font-weight:600}
select,textarea,input[type=text],input[type=url]{padding:10px 12px;background:rgba(5,6,15,.7);border:1px solid rgba(123,92,255,.25);border-radius:10px;color:var(--text);font-size:14px;font-family:inherit;width:100%}
textarea{min-height:280px;resize:vertical;line-height:1.6;font-family:'SF Mono',Consolas,monospace;font-size:13px}
input:focus,textarea:focus,select:focus{outline:none;border-color:var(--purple);box-shadow:0 0 0 3px rgba(123,92,255,.2)}
select option{background:#0d1030;color:var(--text)}
.row{display:flex;gap:12px;align-items:flex-start;flex-wrap:wrap}
.row>div{flex:1;min-width:180px}
.btn{padding:12px 20px;border:none;border-radius:12px;font-size:14px;font-weight:700;cursor:pointer;background:linear-gradient(135deg,#7b5cff,#ff5cf0);color:#fff;box-shadow:0 6px 20px rgba(123,92,255,.4);transition:transform .15s;width:100%}
.btn:hover:not(:disabled){transform:translateY(-2px)}
.btn:disabled{opacity:.6;cursor:wait}
.btn-sm{padding:7px 12px;font-size:12px;width:auto;margin:0;box-shadow:none}
.btn-ok{background:linear-gradient(135deg,#2ecc71,#27ae60);box-shadow:0 6px 20px rgba(46,204,113,.4)}
.btn-cancel{background:linear-gradient(135deg,#555,#333);box-shadow:none}
.btn-danger{background:linear-gradient(135deg,#e74c3c,#c0392b);box-shadow:none}
.btn-outline{background:transparent;border:1px solid rgba(123,92,255,.4);color:var(--text);box-shadow:none}
.btn-outline:hover:not(:disabled){background:rgba(123,92,255,.15)}
.res{margin-top:14px;padding:14px 16px;border-radius:12px;font-size:14px;line-height:1.7;word-break:break-word}
.res.ok{background:rgba(46,204,113,.15);border:1px solid rgba(46,204,113,.4);color:#a8f0c0}
.res.err{background:rgba(231,76,60,.15);border:1px solid rgba(231,76,60,.4);color:#ffb3ab}
.res.warn{background:rgba(243,156,18,.15);border:1px solid rgba(243,156,18,.4);color:#fbd88b}
.res code{background:rgba(5,6,15,.6);padding:3px 8px;border-radius:6px;font-family:monospace;color:var(--cyan);font-weight:700;font-size:14px}
.hr{border:none;border-top:1px solid rgba(123,92,255,.2);margin:20px 0}
.hint{font-size:12px;color:var(--dim);margin-top:6px;line-height:1.6}
.list-item{display:flex;gap:10px;align-items:center;padding:12px 14px;margin:6px 0;background:rgba(5,6,15,.4);border-radius:10px;border-left:3px solid rgba(123,92,255,.5);flex-wrap:wrap;font-size:14px;color:#d0d5f5}
.list-item.ok{border-left-color:var(--ok)}
.list-item.warn{border-left-color:var(--warn)}
.list-item.err{border-left-color:var(--err)}
.list-item .info{flex:1;min-width:200px}
.list-item .code{font-family:monospace;color:#c9b8ff;font-weight:700}
.list-item .meta{font-size:12px;color:#8b93c4;margin-top:3px}
.empty{font-size:13px;color:var(--dim);font-style:italic;padding:12px 0;text-align:center}
.preview-summary{padding:12px 16px;border-radius:10px;background:rgba(5,6,15,.4);border-left:3px solid var(--cyan);margin:12px 0;font-size:13px;line-height:1.8;color:#c8cdf0}
.preview-summary b{color:var(--cyan)}
.audio-box{margin:14px 0}
.audio-box audio{width:100%;border-radius:10px;background:#0d1030;padding:4px}
.task-preview{margin-top:14px;padding:18px;background:rgba(5,6,15,.4);border-radius:12px;border:1px solid rgba(123,92,255,.2)}
.modal-bg{position:fixed;inset:0;background:rgba(0,0,0,.75);z-index:1000;display:none;align-items:flex-start;justify-content:center;padding:24px;overflow-y:auto}
.modal-bg.show{display:flex}
.modal{background:#0d1030;border:1px solid rgba(123,92,255,.4);border-radius:20px;max-width:960px;width:100%;padding:24px;margin:auto}
.modal h3{margin-bottom:14px;color:#c9b8ff;font-size:19px}
.modal .close{float:right;background:none;border:none;color:var(--dim);font-size:22px;cursor:pointer;line-height:1}
.modal .close:hover{color:#fff}
@media print{.no-print{display:none!important}body.print-body{padding:0}}
.print-body{background:#fff;padding:20px;margin:0}
@page{size:A4;margin:15mm 12mm}
.print-doc{font-family:'Times New Roman',Times,serif;color:#000;font-size:12pt;line-height:1.4}
.print-doc h1{font-size:17pt;text-align:center;margin:0 0 12pt 0}
.print-doc h2{font-size:14pt;margin:16pt 0 6pt 0;padding-bottom:3pt;border-bottom:1.5pt solid #000}
.print-doc h3{font-size:12.5pt;margin:10pt 0 5pt 0}
.print-doc .meta{text-align:center;color:#444;font-size:10pt;margin-bottom:14pt}
.print-doc .inst{font-style:italic;color:#222;margin:8pt 0;text-align:justify}
.print-doc .tt{white-space:pre-wrap;margin:8pt 0;text-align:justify}
.print-doc .q{margin:8pt 0;text-align:justify}
.print-doc .op{margin:3pt 0 3pt 18pt}
.print-doc table{width:100%;border-collapse:collapse;margin:10pt 0}
.print-doc th,.print-doc td{border:1pt solid #000;padding:5pt 8pt;font-size:11pt;vertical-align:middle}
.print-doc th{background:#e8e8e8;text-align:center;font-weight:bold}
.print-doc .script{background:#f5f5f5;border:1pt solid #ccc;padding:8pt 12pt;margin:10pt 0;font-size:10.5pt}
.print-doc .answers{background:#fff8d8;border:1.5pt solid #b8860b;padding:10pt 14pt;margin:12pt 0}
.print-doc .answers h3{color:#8b6508;margin-top:0}
.print-doc .page-break{page-break-after:always;height:0}
</style>
</head>
<body>
<div class="wrap">
<h1>⚙ Админка — Космодром ЕГЭ</h1>
<p class="sub">Задания, ученики, варианты, проверка работ, материалы, статистика.</p>

<div class="tabs">
  <button class="tab active" data-tab="upload" onclick="switchTab('upload')">📥 Загрузка</button>
  <button class="tab" data-tab="bank" onclick="switchTab('bank')">🏦 Банк</button>
  <button class="tab" data-tab="variants" onclick="switchTab('variants')">📦 Варианты</button>
  <button class="tab" data-tab="students" onclick="switchTab('students')">👥 Ученики</button>
  <button class="tab" data-tab="review" onclick="switchTab('review')">✅ Проверка<span class="cnt" id="pendingCnt" style="display:none">0</span></button>
  <button class="tab" data-tab="materials" onclick="switchTab('materials')">📎 Материалы</button>
  <button class="tab" data-tab="assignments" onclick="switchTab('assignments')">🎯 Назначения</button>
  <button class="tab" data-tab="stats" onclick="switchTab('stats')">📊 Статистика</button>
  <button class="tab" data-tab="ratelimit" onclick="switchTab('ratelimit')">🚦 Лимиты</button>
</div>

<div class="tab-pane active" id="pane-upload">
  <div class="panel">
    <h3>📥 Загрузить задание 1 (из текста Gemini)</h3>
    <div class="row">
      <div class="f"><label>Тип</label><select id="upTaskType"><option value="1" selected>Задание 1</option></select></div>
      <div class="f"><label>Тема</label><select id="upTopic">
        <option value="А">А. Семья</option><option value="Б">Б. Внешность</option><option value="В">В. ЗОЖ</option>
        <option value="Г">Г. Школа</option><option value="Д">Д. Профессии</option><option value="Е">Е. Иностр. язык</option>
        <option value="Ж">Ж. Молодёжь</option><option value="З">З. Покупки</option><option value="И">И. Спорт</option>
        <option value="К">К. Деловое</option><option value="Л">Л. Туризм</option><option value="М">М. Природа</option>
        <option value="Н">Н. СМИ</option><option value="О">О. Техпрогресс</option><option value="П">П. Проблемы</option>
        <option value="Р">Р. Родная страна</option><option value="С">С. Выдающиеся</option>
      </select></div>
    </div>
    <div class="f"><label>Текст</label>
      <textarea id="upText" placeholder="Вы услышите 6 высказываний...
1 ...
---AUDIO SCRIPTS---
Speaker A: ...
---ANSWER KEY---
Ответ: 246315
Лишнее — 4"></textarea>
    </div>
    <button class="btn" id="upBtnPreview" onclick="doPreview()">🔍 Предпросмотр (с озвучкой)</button>
    <div id="upPreviewRes"></div>
    <div id="upPreviewArea"></div>
  </div>
</div>

<div class="tab-pane" id="pane-bank">
  <div class="panel">
    <h3>🏦 Банк заданий</h3>
    <div class="row">
      <div class="f"><label>Тип</label><select id="bankFilterType">
        <option value="">Все типы</option>
        <option value="1">1</option><option value="2">2</option><option value="3-9">3–9</option>
        <option value="10">10</option><option value="11">11</option><option value="12-18">12–18</option>
        <option value="19-24">19–24</option><option value="25-29">25–29</option><option value="30-36">30–36</option>
        <option value="37">37</option><option value="38.1">38.1</option><option value="38.2">38.2</option>
      </select></div>
      <div class="f"><label>Тема</label><select id="bankFilterTopic">
        <option value="">Все темы</option>
        <option value="А">А</option><option value="Б">Б</option><option value="В">В</option><option value="Г">Г</option>
        <option value="Д">Д</option><option value="Е">Е</option><option value="Ж">Ж</option><option value="З">З</option>
        <option value="И">И</option><option value="К">К</option><option value="Л">Л</option><option value="М">М</option>
        <option value="Н">Н</option><option value="О">О</option><option value="П">П</option><option value="Р">Р</option>
        <option value="С">С</option>
      </select></div>
      <div class="f"><label>&nbsp;</label><button class="btn btn-outline" onclick="listBank()">📚 Обновить</button></div>
    </div>
    <div id="bankRes"></div>
    <div id="bankList"></div>
  </div>
</div>

<div class="tab-pane" id="pane-variants">
  <div class="panel">
    <h3>📦 Собрать полный вариант (1–38)</h3>
    <div class="row">
      <div class="f">
        <label>Режим тем</label>
        <select id="vMode" onchange="onVModeChange()">
          <option value="same">Одна тема на весь вариант</option>
          <option value="per_task">Своя тема для каждого задания</option>
          <option value="random">🎲 Случайно для всего варианта</option>
        </select>
      </div>
      <div class="f" id="vSameWrap">
        <label>Тема для всего варианта</label>
        <select id="vTopic">
          <option value="any">🎲 Любая</option>
          <option value="А. Повседневная жизнь семьи. Межличностные отношения">А. Семья</option>
          <option value="Б. Внешность и характеристика человека">Б. Внешность</option>
          <option value="В. Здоровый образ жизни и забота о здоровье">В. ЗОЖ</option>
          <option value="Г. Школьное образование, школьная жизнь">Г. Школа</option>
          <option value="Д. Современный мир профессий">Д. Профессии</option>
          <option value="Е. Место иностранного языка в жизни">Е. Иностранный язык</option>
          <option value="Ж. Молодёжь в современном обществе">Ж. Молодёжь</option>
          <option value="З. Покупки: одежда, обувь, продукты">З. Покупки</option>
          <option value="И. Роль спорта в современной жизни">И. Спорт</option>
          <option value="К. Деловое общение">К. Деловое</option>
          <option value="Л. Туризм. Виды отдыха. Экотуризм">Л. Туризм</option>
          <option value="М. Вселенная и человек. Природа. Экология">М. Природа</option>
          <option value="Н. Средства массовой информации">Н. СМИ</option>
          <option value="О. Технический прогресс. Интернет-безопасность">О. Техпрогресс</option>
          <option value="П. Проблемы современной цивилизации">П. Проблемы</option>
          <option value="Р. Родная страна и страны изучаемого языка">Р. Родная страна</option>
          <option value="С. Выдающиеся люди родной страны и мира">С. Выдающиеся</option>
        </select>
      </div>
    </div>
    <div id="vPerTaskWrap" style="display:none">
      <label style="display:block;font-size:12px;color:#8b93c4;margin-bottom:8px;text-transform:uppercase">Тема для каждого задания</label>
      <div id="vPerTaskTable"></div>
    </div>
    <div style="margin:10px 0">
      <label style="display:block;font-size:12px;color:#8b93c4;margin-bottom:6px">Что включать в вариант</label>
      <div id="vIncludeList" style="display:flex;flex-wrap:wrap;gap:14px;font-size:14px;color:#d0d5f5"></div>
    </div>
    <button class="btn" id="vGenBtn" onclick="variantGenerate()">🎲 Сгенерировать вариант</button>
    <div id="vRes"></div>
    <div id="vArea"></div>
  </div>
  <div class="panel">
    <h3>Сохранённые варианты</h3>
    <button class="btn btn-outline" style="max-width:200px" onclick="loadVariantsList()">🔄 Обновить</button>
    <div id="vList" style="margin-top:12px"><div class="empty">Загрузка…</div></div>
  </div>
</div>

<div class="tab-pane" id="pane-students">
  <div class="panel">
    <h3>👥 Создать ученика</h3>
    <div class="row">
      <div><input id="stSurname" placeholder="Фамилия"></div>
      <div><input id="stName" placeholder="Имя"></div>
      <div style="flex:0 0 auto"><button class="btn" style="width:auto" onclick="createStudent()">+ Добавить</button></div>
    </div>
    <div class="hint">Код генерируется автоматически.</div>
    <div id="stRes"></div>
  </div>
  <div class="panel"><h3>Все ученики</h3><div id="stList"><div class="empty">Загрузка…</div></div></div>
</div>

<div class="tab-pane" id="pane-review">
  <div class="panel">
    <h3>✅ Очередь на проверку</h3>
    <button class="btn btn-outline" onclick="loadPending()" style="max-width:200px">🔄 Обновить</button>
    <div id="pendingRes" style="margin-top:12px"></div>
    <div id="pendingList"></div>
  </div>
</div>

<div class="tab-pane" id="pane-materials">
  <div class="panel">
    <h3>📎 Добавить материал</h3>
    <div class="f"><label>Название</label><input type="text" id="matTitle" placeholder="Например: Критерии ФИПИ — письмо"></div>
    <div class="row">
      <div class="f"><label>Файл (до 7 МБ)</label><input type="file" id="matFile"></div>
      <div class="f"><label>…или ссылка</label><input type="url" id="matUrl" placeholder="https://..."></div>
    </div>
    <button class="btn btn-ok" style="margin-top:12px" onclick="uploadMaterial()">+ Добавить</button>
    <div id="matRes"></div>
  </div>
  <div class="panel"><h3>Список материалов</h3><div id="matList"><div class="empty">Загрузка…</div></div></div>
</div>

<div class="tab-pane" id="pane-assignments">
  <div class="panel">
    <h3>🎯 Назначить задание ученику</h3>
    <div class="row">
      <div class="f"><label>Ученик</label><select id="asStudent"><option value="">— выбери —</option></select></div>
      <div class="f"><label>Тип</label><select id="asTaskType" onchange="onAsTypeChange()">
        <option value="1">1</option><option value="2">2</option><option value="3-9">3–9</option>
        <option value="10">10</option><option value="11">11</option><option value="12-18">12–18</option>
        <option value="19-24">19–24</option><option value="25-29">25–29</option><option value="30-36">30–36</option>
        <option value="37">37</option><option value="38.1">38.1</option><option value="38.2">38.2</option>
      </select></div>
      <div class="f"><label>Источник</label><select id="asSource" onchange="onAsSourceChange()">
        <option value="bank">🏦 Из банка</option>
        <option value="generate">🤖 Сгенерировать сейчас</option>
      </select></div>
    </div>
    <div class="f" id="asBankWrap">
      <label>Код задания из банка</label>
      <input type="text" id="asBankCode" placeholder="Например: 1-А-001">
    </div>
    <div class="f" id="asGenWrap" style="display:none">
      <label>Тема (для генерации)</label>
      <select id="asTopic">
        <option value="any">Любая</option>
        <option value="А. Повседневная жизнь семьи. Межличностные отношения">А</option>
        <option value="Б. Внешность и характеристика человека">Б</option>
        <option value="В. Здоровый образ жизни и забота о здоровье">В</option>
        <option value="Г. Школьное образование, школьная жизнь">Г</option>
        <option value="Д. Современный мир профессий">Д</option>
        <option value="Е. Место иностранного языка в жизни">Е</option>
        <option value="Ж. Молодёжь в современном обществе">Ж</option>
        <option value="З. Покупки: одежда, обувь, продукты">З</option>
        <option value="И. Роль спорта в современной жизни">И</option>
        <option value="К. Деловое общение">К</option>
        <option value="Л. Туризм. Виды отдыха. Экотуризм">Л</option>
        <option value="М. Вселенная и человек. Природа. Экология">М</option>
        <option value="Н. Средства массовой информации">Н</option>
        <option value="О. Технический прогресс. Интернет-безопасность">О</option>
        <option value="П. Проблемы современной цивилизации">П</option>
        <option value="Р. Родная страна и страны изучаемого языка">Р</option>
        <option value="С. Выдающиеся люди родной страны и мира">С</option>
      </select>
    </div>
    <div class="f"><label>Заметка (необязательно)</label><input type="text" id="asNote" placeholder="Например: срочно"></div>
    <button class="btn" onclick="createAssignment()">🎯 Назначить</button>
    <div id="asRes"></div>
  </div>
  <div class="panel"><h3>Активные назначения</h3><div id="asList"><div class="empty">Загрузка…</div></div></div>
</div>

<div class="tab-pane" id="pane-stats">
  <div class="panel"><h3>📊 Общая сводка</h3><div id="statsGlobal"><div class="empty">Загрузка…</div></div></div>
  <div class="panel"><h3>📈 По ученикам</h3><div id="statsTable"><div class="empty">Загрузка…</div></div></div>
</div>

<div class="tab-pane" id="pane-ratelimit">
  <div class="panel">
    <h3>🚦 Лимиты</h3>
    <p class="hint" style="margin-bottom:12px">Максимум бесплатных попыток: <b id="rlMax">5</b>.</p>
    <button class="btn btn-outline" onclick="loadRatelimit()" style="max-width:200px">🔄 Обновить</button>
    <button class="btn btn-danger" onclick="resetAllRl()" style="max-width:240px;margin-left:8px">🗑 Сбросить ВСЕ</button>
    <div id="rlRes" style="margin-top:12px"></div>
    <div id="rlList"></div>
  </div>
  <div class="panel">
    <h3>📜 Аудит</h3>
    <button class="btn btn-outline" onclick="loadAudit()" style="max-width:200px">📜 Загрузить</button>
    <div id="auditList"></div>
  </div>
</div>

</div>

<div class="modal-bg" id="adminModal" onclick="if(event.target===this)closeAdminModal()">
  <div class="modal" id="adminModalBody"></div>
</div>

<script>
function esc(s){return String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;')}
function b64ToBytes(b64){const bin=atob(b64),bytes=new Uint8Array(bin.length);for(var i=0;i<bin.length;i++)bytes[i]=bin.charCodeAt(i);return bytes;}
function fmtDate(ts){if(!ts)return '';var d=new Date(ts*1000);return d.toLocaleString('ru-RU',{day:'2-digit',month:'2-digit',year:'2-digit',hour:'2-digit',minute:'2-digit'});}
function api(payload){
  return fetch(window.location.pathname,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)})
    .then(function(r){return r.json()});
}

const PRINT_CSS = "@page{size:A4;margin:15mm 12mm}*{box-sizing:border-box}"
 + "body.print-body{background:#fff;padding:20px;margin:0;font-family:'Times New Roman',Times,serif;color:#000}"
 + ".print-doc{font-size:12pt;line-height:1.4}"
 + ".print-doc h1{font-size:17pt;text-align:center;margin:0 0 12pt 0}"
 + ".print-doc h2{font-size:14pt;margin:16pt 0 6pt 0;padding-bottom:3pt;border-bottom:1.5pt solid #000}"
 + ".print-doc h3{font-size:12.5pt;margin:10pt 0 5pt 0}"
 + ".print-doc .meta{text-align:center;color:#444;font-size:10pt;margin-bottom:14pt}"
 + ".print-doc .inst{font-style:italic;color:#222;margin:8pt 0;text-align:justify}"
 + ".print-doc .tt{white-space:pre-wrap;margin:8pt 0;text-align:justify}"
 + ".print-doc .q{margin:8pt 0;text-align:justify}"
 + ".print-doc .op{margin:3pt 0 3pt 18pt}"
 + ".print-doc table{width:100%;border-collapse:collapse;margin:10pt 0}"
 + ".print-doc th,.print-doc td{border:1pt solid #000;padding:5pt 8pt;font-size:11pt;vertical-align:middle}"
 + ".print-doc th{background:#e8e8e8;text-align:center;font-weight:bold}"
 + ".print-doc .script{background:#f5f5f5;border:1pt solid #ccc;padding:8pt 12pt;margin:10pt 0;font-size:10.5pt}"
 + ".print-doc .answers{background:#fff8d8;border:1.5pt solid #b8860b;padding:10pt 14pt;margin:12pt 0}"
 + ".print-doc .answers h3{color:#8b6508;margin-top:0}"
 + ".print-doc .page-break{page-break-after:always;height:0}"
 + "@media print{.no-print{display:none!important}body.print-body{padding:0}}";

function renderExplanationsBlock(exps, keysOrder){
  if(!exps || !keysOrder || !keysOrder.length) return '';
  var shown = keysOrder.filter(function(k){return exps[k];});
  if(!shown.length) return '';
  var h = '<div style="margin-top:14pt;padding:10pt 14pt;background:#eef7ee;border:1.5pt solid #4a8f4a;border-radius:6px">';
  h += '<h3 style="color:#2e6b2e;margin:0 0 8pt 0">💡 Объяснения</h3>';
  shown.forEach(function(k){
    h += '<div style="margin:6pt 0;font-size:11pt;line-height:1.5"><b style="color:#2e6b2e">'+esc(k)+':</b> '+esc(exps[k])+'</div>';
  });
  h += '</div>';
  return h;
}

function renderTaskForPrint(t, d, opts){
  opts = opts || {};
  const withAnswers = !!opts.withAnswers;
  let h = '';
  if(d.instruction) h += '<div class="inst">'+esc(d.instruction)+'</div>';
  if(t==='1'){
    (d.statements||[]).forEach(function(s){h+='<div class="q"><b>'+s.number+'.</b> '+esc(s.text)+'</div>';});
    h+='<table><tr><th>Говорящий</th>'+'ABCDEF'.split('').map(function(k){return '<th>'+k+'</th>';}).join('')+'</tr>';
    h+='<tr><td>Ответ</td>'+'ABCDEF'.split('').map(function(){return '<td style="height:22pt"></td>';}).join('')+'</tr></table>';
    if(withAnswers&&d.answer_key){
      h+='<div class="answers"><h3>Ответы</h3><div style="font-family:monospace;font-size:14pt">'+'ABCDEF'.split('').map(function(k){return k+'→'+(d.answer_key[k]||'?');}).join('  ')+'</div>';
      if(d.extra_statement) h+='<div>Лишнее утверждение: '+d.extra_statement+'</div>';
      h+='</div>';
      if(d.explanations){h+=renderExplanationsBlock(d.explanations,'ABCDEF');}
    }
  } else if(t==='2'){
    (d.statements||[]).forEach(function(s){h+='<div class="q"><b>'+esc(s.letter)+'.</b> '+esc(s.text)+'</div>';});
    h+='<table><tr><th>Утв.</th>'+'ABCDEFG'.split('').map(function(k){return '<th>'+k+'</th>';}).join('')+'</tr>';
    h+='<tr><td>Ответ</td>'+'ABCDEFG'.split('').map(function(){return '<td style="height:22pt"></td>';}).join('')+'</tr></table>';
    h+='<div style="font-size:10pt">1 – True, 2 – False, 3 – Not stated</div>';
    if(withAnswers&&d.answer_key){
      h+='<div class="answers"><h3>Ответы</h3><div style="font-family:monospace;font-size:14pt">'+'ABCDEFG'.split('').map(function(k){return k+'→'+(d.answer_key[k]||'?');}).join('  ')+'</div></div>';
      if(d.explanations){h+=renderExplanationsBlock(d.explanations,'ABCDEFG');}
    }
  } else if(t==='3-9'){
    (d.questions||[]).forEach(function(q){
      h+='<div class="q"><b>'+q.number+'.</b> '+esc(q.question)+'</div>';
      ['1','2','3'].forEach(function(k){h+='<div class="op">'+k+') '+esc(q.options[k])+'</div>';});
    });
    if(withAnswers&&d.answer_key){
      h+='<div class="answers"><h3>Ответы</h3><div style="font-family:monospace;font-size:14pt">'+Object.keys(d.answer_key).map(function(k){return k+'→'+d.answer_key[k];}).join('  ')+'</div></div>';
      if(d.explanations){h+=renderExplanationsBlock(d.explanations,['3','4','5','6','7','8','9']);}
    }
  } else if(t==='10'){
    (d.headings||[]).forEach(function(x){h+='<div class="q"><b>'+x.number+'.</b> '+esc(x.text)+'</div>';});
    h+='<h3>Тексты</h3>';
    (d.texts||[]).forEach(function(x){h+='<div class="q"><b>'+esc(x.letter)+'.</b> '+esc(x.text)+'</div>';});
    h+='<table><tr>'+'ABCDEFG'.split('').map(function(k){return '<th>'+k+'</th>';}).join('')+'</tr>';
    h+='<tr>'+'ABCDEFG'.split('').map(function(){return '<td style="height:22pt"></td>';}).join('')+'</tr></table>';
    if(withAnswers&&d.answer_key){
      h+='<div class="answers"><h3>Ответы</h3><div style="font-family:monospace;font-size:14pt">'+'ABCDEFG'.split('').map(function(k){return k+'→'+(d.answer_key[k]||'?');}).join('  ')+'</div></div>';
      if(d.explanations){h+=renderExplanationsBlock(d.explanations,'ABCDEFG');}
    }
  } else if(t==='11'){
    if(d.title) h+='<h3>'+esc(d.title)+'</h3>';
    if(d.text) h+='<div class="tt">'+esc(d.text)+'</div>';
    h+='<h3>Фрагменты</h3>';
    (d.fragments||[]).forEach(function(f){h+='<div class="q"><b>'+f.number+'.</b> '+esc(f.text)+'</div>';});
    h+='<table><tr>'+'ABCDEF'.split('').map(function(k){return '<th>'+k+'</th>';}).join('')+'</tr>';
    h+='<tr>'+'ABCDEF'.split('').map(function(){return '<td style="height:22pt"></td>';}).join('')+'</tr></table>';
    if(withAnswers&&d.answer_key){
      h+='<div class="answers"><h3>Ответы</h3><div style="font-family:monospace;font-size:14pt">'+'ABCDEF'.split('').map(function(k){return k+'→'+(d.answer_key[k]||'?');}).join('  ')+'</div></div>';
      if(d.explanations){h+=renderExplanationsBlock(d.explanations,'ABCDEF');}
    }
  } else if(t==='12-18'){
    if(d.title) h+='<h3>'+esc(d.title)+'</h3>';
    if(d.text) h+='<div class="tt">'+esc(d.text)+'</div>';
    (d.questions||[]).forEach(function(q){
      h+='<div class="q"><b>'+q.number+'.</b> '+esc(q.question)+'</div>';
      ['1','2','3','4'].forEach(function(k){h+='<div class="op">'+k+') '+esc(q.options[k])+'</div>';});
    });
    if(withAnswers&&d.answer_key){
      h+='<div class="answers"><h3>Ответы</h3><div style="font-family:monospace;font-size:14pt">'+Object.keys(d.answer_key).map(function(k){return k+'→'+d.answer_key[k];}).join('  ')+'</div></div>';
      if(d.explanations){h+=renderExplanationsBlock(d.explanations,['12','13','14','15','16','17','18']);}
    }
  } else if(t==='19-24'||t==='25-29'){
    if(d.title) h+='<h3>'+esc(d.title)+'</h3>';
    if(d.text){
      var tx = String(d.text).replace(/__(\d{2})__/g, function(_,n){return '___('+n+')___';});
      h+='<div class="tt">'+esc(tx)+'</div>';
    }
    (d.items||[]).forEach(function(it){
      h+='<div class="q"><b>'+it.number+'.</b> <span style="font-family:monospace;letter-spacing:1pt">'+esc(it.source_word)+'</span> — <span style="display:inline-block;border-bottom:1pt solid #000;min-width:120pt">&nbsp;</span></div>';
    });
    if(withAnswers&&d.answer_key){
      h+='<div class="answers"><h3>Ответы</h3><div style="font-family:monospace;font-size:13pt">'+Object.keys(d.answer_key).map(function(k){return k+'→'+d.answer_key[k];}).join('  ')+'</div></div>';
      if(d.explanations){
        var ord = (t==='19-24')?['19','20','21','22','23','24']:['25','26','27','28','29'];
        h+=renderExplanationsBlock(d.explanations,ord);
      }
    }
  } else if(t==='30-36'){
    if(d.title) h+='<h3>'+esc(d.title)+'</h3>';
    if(d.text){
      var tx2 = String(d.text).replace(/__(\d{2})__/g, function(_,n){return '('+n+') ____';});
      h+='<div class="tt">'+esc(tx2)+'</div>';
    }
    (d.items||[]).forEach(function(it){
      h+='<div class="q"><b>'+it.number+'.</b></div>';
      ['1','2','3','4'].forEach(function(k){h+='<div class="op">'+k+') '+esc(it.options[k])+'</div>';});
    });
    if(withAnswers&&d.answer_key){
      h+='<div class="answers"><h3>Ответы</h3><div style="font-family:monospace;font-size:14pt">'+Object.keys(d.answer_key).map(function(k){return k+'→'+d.answer_key[k];}).join('  ')+'</div></div>';
      if(d.explanations){h+=renderExplanationsBlock(d.explanations,['30','31','32','33','34','35','36']);}
    }
  } else if(t==='37'){
    if(d.task_text) h+='<div class="tt">'+esc(d.task_text)+'</div>';
    h+='<h3 style="margin-top:14pt">Answer sheet</h3>';
    for(var i=0;i<22;i++) h+='<div style="border-bottom:1pt dotted #888;height:22pt"></div>';
  } else if(t==='38.1'||t==='38.2'){
    if(d.task_text) h+='<div class="tt">'+esc(d.task_text)+'</div>';
    var sd = d.survey_data || {};
    if(sd.question) h+='<p style="text-align:center;font-weight:bold">The survey question: &laquo;'+esc(String(sd.question).replace(/^"+|"+$/g,''))+'&raquo;</p>';
    if(t==='38.1'){
      h+='<table><tr><th>Options</th><th>Number of respondents (%)</th></tr>';
      (sd.options||[]).forEach(function(o){h+='<tr><td>'+esc(o.option)+'</td><td style="text-align:center">'+esc(o.percent)+'</td></tr>';});
      h+='</table>';
    } else {
      h+='<table><tr><th>Segment</th><th>%</th></tr>';
      (sd.options||[]).forEach(function(o){h+='<tr><td>'+esc(o.option)+'</td><td style="text-align:center">'+esc(o.percent)+'</td></tr>';});
      h+='</table>';
    }
    h+='<p style="margin-top:12pt"><b>Write 200–250 words.</b></p>';
    h+='<p><b>Use the following plan:</b></p>';
    (d.plan||[]).forEach(function(p){h+='<div style="margin-left:18pt">– '+esc(p)+'</div>';});
    h+='<h3 style="margin-top:14pt">Answer sheet</h3>';
    for(var j=0;j<22;j++) h+='<div style="border-bottom:1pt dotted #888;height:22pt"></div>';
  }
  return h;
}

function openPrintWindow(bodyHtml, title){
  var w = window.open('', '_blank');
  if(!w){alert('Разрешите всплывающие окна');return;}
  var doc = '<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8"><title>'+esc(title)+'</title>'
    +'<style>'+PRINT_CSS+'</style></head><body class="print-body">'
    +'<div class="no-print" style="position:fixed;top:12px;right:12px;z-index:999">'
    +'<button onclick="window.print()" style="padding:10px 18px;font-size:14px;cursor:pointer;background:#7b5cff;color:#fff;border:none;border-radius:8px;font-weight:600">🖨 Сохранить как PDF</button>'
    +'</div>'
    +'<div class="print-doc">'+bodyHtml+'</div>'
    +'<scr'+'ipt>window.addEventListener("load",function(){setTimeout(function(){try{window.print();}catch(e){}},500);});</scr'+'ipt>'
    +'</body></html>';
  w.document.open(); w.document.write(doc); w.document.close();
}

var _preview=null, _bankData=[], _students=[], _pendingList=[], _materials=[], _reviewCrit=null, _reviewSub=null;
var _loadedBankTask = null;

function switchTab(name){
  document.querySelectorAll('.tab').forEach(function(t){t.classList.toggle('active', t.getAttribute('data-tab')===name);});
  document.querySelectorAll('.tab-pane').forEach(function(p){p.classList.toggle('active', p.id==='pane-'+name);});
  if(name==='bank') listBank();
  else if(name==='students') listStudents();
  else if(name==='review') loadPending();
  else if(name==='materials') loadMaterials();
  else if(name==='assignments'){ loadStudentsForAssign(); loadAssignments(); }
  else if(name==='stats') loadStats();
  else if(name==='ratelimit') loadRatelimit();
  else if(name==='variants'){ initVariantsTab(); loadVariantsList(); }
}

// ---------- ЗАГРУЗКА ЗАДАНИЯ 1 ----------
async function doPreview(){
  var btn=document.getElementById('upBtnPreview'), r=document.getElementById('upPreviewRes');
  var pv=document.getElementById('upPreviewArea');
  var text=document.getElementById('upText').value.trim();
  var task_type=document.getElementById('upTaskType').value;
  var topic_letter=document.getElementById('upTopic').value;
  if(!text){r.className='res err';r.textContent='⚠ Вставь текст';return;}
  pv.innerHTML=''; btn.disabled=true; btn.textContent='🛰 Парсим и озвучиваем…';
  r.className='res'; r.textContent='Обработка…'; _preview=null;
  try{
    var d=await api({action:'preview', task_type:task_type, topic_letter:topic_letter, text:text});
    if(d.error){r.className='res err'; r.innerHTML='💥 '+esc(d.error); return;}
    _preview=d;
    r.className='res ok'; r.innerHTML='✅ Готово к предпросмотру.';
    renderPreview(d, task_type, topic_letter);
  }catch(e){r.className='res err'; r.innerHTML='💥 '+esc(e.message);}
  finally{btn.disabled=false; btn.textContent='🔍 Предпросмотр (с озвучкой)';}
}

function renderPreview(d, task_type, topic_letter){
  var pv=document.getElementById('upPreviewArea');
  var s=d.summary||{}, h='';
  if(d.duplicate_of) h+='<div class="res warn">⚠ Похожее задание уже есть: <b>'+esc(d.duplicate_of)+'</b></div>';
  h+='<div class="preview-summary">';
  h+='<b>Распарсено:</b><br>';
  h+='• Утверждений: <b>'+s.statements+'</b> / 7<br>';
  h+='• Монологов: <b>'+s.scripts+'</b> / 6<br>';
  h+='• Лишнее: <b>'+esc(s.extra_statement)+'</b><br>';
  h+='• Ключ: <b>'+Object.keys(s.answer_key||{}).map(function(k){return k+'→'+s.answer_key[k];}).join(', ')+'</b><br>';
  h+='• MP3: <b>'+d.audio_size_kb+' КБ</b></div>';
  var bytes=b64ToBytes(d.audio_b64);
  var url=URL.createObjectURL(new Blob([bytes],{type:'audio/mpeg'}));
  h+='<div class="audio-box"><audio controls src="'+url+'"></audio></div>';
  h+='<div class="row" style="margin-top:16px"><div><button class="btn btn-ok" id="saveBtn" onclick="doSavePreview(false)">✅ Сохранить в банк</button></div><div><button class="btn btn-cancel" onclick="doCancelPreview()">❌ Отменить</button></div></div>';
  pv.innerHTML=h;
}

async function doSavePreview(force){
  if(!_preview) return;
  var r=document.getElementById('upPreviewRes'), b=document.getElementById('saveBtn');
  var task_type=document.getElementById('upTaskType').value;
  var topic_letter=document.getElementById('upTopic').value;
  if(b){b.disabled=true;b.textContent='📥 Сохраняю…';}
  try{
    var d=await api({action:'save_previewed', task_type:task_type, topic_letter:topic_letter,
      task_data:_preview.task_data, audio_b64:_preview.audio_b64, force:!!force});
    if(d.error){r.className='res err'; r.innerHTML='💥 '+esc(d.error); if(b){b.disabled=false;b.textContent='✅ Сохранить в банк';} return;}
    if(d.warning){
      r.className='res warn';
      r.innerHTML='⚠ '+esc(d.warning)+'<br><br><button class="btn btn-ok" style="max-width:240px" onclick="doSavePreview(true)">Всё равно сохранить</button>';
      if(b){b.disabled=false;b.textContent='✅ Сохранить в банк';} return;
    }
    if(d.ok){
      r.className='res ok';
      r.innerHTML='✅ Сохранено! Код: <code>'+esc(d.code)+'</code> ('+d.size_kb+' КБ)';
      document.getElementById('upText').value='';
      document.getElementById('upPreviewArea').innerHTML=''; _preview=null;
    }
  }catch(e){r.className='res err'; r.innerHTML='💥 '+esc(e.message); if(b){b.disabled=false;b.textContent='✅ Сохранить в банк';}}
}
function doCancelPreview(){_preview=null; document.getElementById('upPreviewArea').innerHTML=''; document.getElementById('upPreviewRes').textContent='';}

// ---------- БАНК ----------
async function listBank(){
  var r=document.getElementById('bankRes'), v=document.getElementById('bankList');
  v.innerHTML=''; r.className='res'; r.textContent='Загрузка…';
  try{
    var d=await api({action:'list_bank',
      task_type:document.getElementById('bankFilterType').value || null,
      topic_letter:document.getElementById('bankFilterTopic').value || null});
    if(d.error){r.className='res err'; r.textContent='💥 '+d.error; return;}
    r.className='res ok';
    if(!d.tasks||!d.tasks.length){r.textContent='Банк пуст.'; return;}
    _bankData=d.tasks;
    r.innerHTML='Всего: <b>'+d.count+'</b>';
    var h='<div style="margin-top:12px">';
    d.tasks.forEach(function(t,i){
      h+='<div class="list-item">';
      h+='<div class="info"><div class="code">'+esc(t.code)+'</div>';
      h+='<div class="meta">'+esc(t.topic_full)+' · '+(t.has_audio?'🔊':'🔇')+'</div></div>';
      h+='<button class="btn btn-sm btn-outline" onclick="openTaskByIdx('+i+')">👁</button>';
      h+='<button class="btn btn-sm btn-danger" onclick="delTaskByIdx('+i+')">🗑</button>';
      h+='</div>';
    });
    v.innerHTML=h+'</div>';
  }catch(e){r.className='res err'; r.textContent='💥 '+e.message;}
}
function openTaskByIdx(i){var t=_bankData[i]; if(t) openTask(t.task_type, t.topic, t.code);}
function delTaskByIdx(i){var t=_bankData[i]; if(t) delTask(t.task_type, t.topic, t.code);}

async function openTask(task_type, topic_letter, code){
  var v=document.getElementById('bankList');
  v.innerHTML='<div class="res">Загружаю '+esc(code)+'…</div>';
  try{
    var d=await api({action:'get_bank_task', task_type:task_type, topic_letter:topic_letter, code:code});
    if(d.error){v.innerHTML='<div class="res err">💥 '+esc(d.error)+'</div>'; return;}
    _loadedBankTask = d; _loadedBankTask.task_type = task_type;
    var h='<div class="res ok" style="margin-top:12px">';
    h+='<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px"><b style="font-family:monospace;font-size:16px">'+esc(d.code)+'</b><button class="btn btn-sm btn-outline" onclick="listBank()">✕ Закрыть</button></div>';
    if(d.audio_b64){
      var bytes=b64ToBytes(d.audio_b64);
      var url=URL.createObjectURL(new Blob([bytes],{type:'audio/mpeg'}));
      h+='<audio controls src="'+url+'" style="width:100%;margin:8px 0"></audio>';
    }
    h+='<div style="margin-top:10px"><b style="color:#c9b8ff">Утверждения/задания:</b><br>';
    (d.statements||[]).forEach(function(s){h+='<div style="margin:3px 0;color:#d0d5f5;font-size:13px">'+s.number+'. '+esc(s.text)+'</div>';});
    h+='<div style="margin-top:10px"><b style="color:#c9b8ff">Ключ:</b> '+Object.keys(d.answer_key||{}).map(function(k){return '<span style="font-family:monospace;color:#00e5ff">'+k+'→'+d.answer_key[k]+'</span>';}).join(', ')+'</div>';
    if(d.explanations){
      h+='<details style="margin-top:10px;background:rgba(46,204,113,.08);border:1px solid rgba(46,204,113,.3);border-radius:10px;padding:10px"><summary style="cursor:pointer;color:#2ecc71;font-weight:700">💡 Объяснения</summary><div style="margin-top:8px;color:#d0d5f5;font-size:13px;line-height:1.7">';
      Object.keys(d.explanations).forEach(function(k){
        h+='<div style="margin:4px 0;padding:6px 10px;background:rgba(5,6,15,.4);border-radius:6px"><b style="color:#2ecc71;font-family:monospace">'+esc(k)+':</b> '+esc(d.explanations[k])+'</div>';
      });
      h+='</div></details>';
    }
    h+='</div>';
    h+='<div style="margin-top:14px;padding-top:14px;border-top:1px solid rgba(123,92,255,.2)"><b style="color:#c9b8ff">📥 Скачать PDF:</b><br>'
      +'<button class="btn btn-sm btn-outline" style="margin-right:8px;margin-top:8px" onclick="downloadLoadedBankTask(false)">📄 Для ученика</button>'
      +'<button class="btn btn-sm" style="margin-top:8px" onclick="downloadLoadedBankTask(true)">📄 Для учителя</button></div>';
    h+='</div>';
    v.innerHTML=h;
  }catch(e){v.innerHTML='<div class="res err">💥 '+esc(e.message)+'</div>';}
}

function downloadLoadedBankTask(withAnswers){
  if(!_loadedBankTask){alert('Ничего не загружено');return;}
  var d=_loadedBankTask;
  var t=d.task_type;
  var body='<h1>Задание '+esc(t)+'</h1>';
  if(d.code) body+='<div class="meta">Код: '+esc(d.code)+'</div>';
  body+=renderTaskForPrint(t,d,{withAnswers:withAnswers});
  openPrintWindow(body, 'Задание '+t);
}

async function delTask(task_type, topic_letter, code){
  if(!confirm('Удалить '+code+'?')) return;
  var d=await api({action:'delete_bank_task', task_type:task_type, topic_letter:topic_letter, code:code});
  if(d.error){alert('Ошибка: '+d.error); return;}
  alert('Удалено: '+code); listBank();
}

// ---------- ВАРИАНТЫ ----------
const V_TASKS=["1","2","3-9","10","11","12-18","19-24","25-29","30-36","37","38.1","38.2"];
const V_TOPICS=[
  ["any","🎲 Любая"],["А. Повседневная жизнь семьи. Межличностные отношения","А. Семья"],
  ["Б. Внешность и характеристика человека","Б. Внешность"],
  ["В. Здоровый образ жизни и забота о здоровье","В. ЗОЖ"],
  ["Г. Школьное образование, школьная жизнь","Г. Школа"],
  ["Д. Современный мир профессий","Д. Профессии"],
  ["Е. Место иностранного языка в жизни","Е. Иностранный язык"],
  ["Ж. Молодёжь в современном обществе","Ж. Молодёжь"],
  ["З. Покупки: одежда, обувь, продукты","З. Покупки"],
  ["И. Роль спорта в современной жизни","И. Спорт"],
  ["К. Деловое общение","К. Деловое"],
  ["Л. Туризм. Виды отдыха. Экотуризм","Л. Туризм"],
  ["М. Вселенная и человек. Природа. Экология","М. Природа"],
  ["Н. Средства массовой информации","Н. СМИ"],
  ["О. Технический прогресс. Интернет-безопасность","О. Техпрогресс"],
  ["П. Проблемы современной цивилизации","П. Проблемы"],
  ["Р. Родная страна и страны изучаемого языка","Р. Родная страна"],
  ["С. Выдающиеся люди родной страны и мира","С. Выдающиеся"]
];
const V_TASK_LABEL={"1":"1 (A–F, 2 б.)","2":"2 (T/F/NS, 3 б.)","3-9":"3–9 (7 б.)",
  "10":"10 (заголовки, 3 б.)","11":"11 (пропуски, 2 б.)","12-18":"12–18 (7 б.)",
  "19-24":"19–24 (6 б.)","25-29":"25–29 (5 б.)","30-36":"30–36 (7 б.)",
  "37":"37 (Email, 6 б.)","38.1":"38.1 (эссе, 14 б.)","38.2":"38.2 (эссе, 14 б.)"};

let _vGenerated = null;

function initVariantsTab(){
  var inc = document.getElementById('vIncludeList');
  if (!inc || inc.dataset.init === '1') return;
  inc.dataset.init = '1';
  inc.innerHTML = V_TASKS.map(function(t){
    return '<label style="display:flex;gap:6px;align-items:center"><input type="checkbox" id="vInc_'+t+'" checked style="width:auto">'+esc(V_TASK_LABEL[t])+'</label>';
  }).join('');
  var tbl = document.getElementById('vPerTaskTable');
  tbl.innerHTML = V_TASKS.map(function(t){
    return '<div class="row" style="align-items:center;margin-bottom:6px">'
      + '<div style="flex:0 0 240px;font-size:13px;color:#c8cdf0">'+esc(V_TASK_LABEL[t])+'</div>'
      + '<div style="flex:1"><select id="vTopic_'+t+'">'+V_TOPICS.map(function(o){
          return '<option value="'+esc(o[0])+'">'+esc(o[1])+'</option>';
        }).join('')+'</select></div></div>';
  }).join('');
}

function onVModeChange(){
  var m = document.getElementById('vMode').value;
  document.getElementById('vSameWrap').style.display = (m==='same') ? 'block' : 'none';
  document.getElementById('vPerTaskWrap').style.display = (m==='per_task') ? 'block' : 'none';
}

async function variantGenerate(){
  initVariantsTab();
  var r = document.getElementById('vRes'), area = document.getElementById('vArea');
  var btn = document.getElementById('vGenBtn');
  area.innerHTML = ''; _vGenerated = null;
  var mode = document.getElementById('vMode').value;
  var topic_config = {};
  var any_included = false;
  V_TASKS.forEach(function(t){
    var inc = document.getElementById('vInc_'+t);
    if (!inc || !inc.checked) return;
    any_included = true;
    if (mode === 'same') { topic_config[t] = document.getElementById('vTopic').value; }
    else if (mode === 'per_task') { var s = document.getElementById('vTopic_'+t); topic_config[t] = s ? s.value : 'any'; }
    else { topic_config[t] = 'random'; }
  });
  if (!any_included) { r.className='res err'; r.textContent='⚠ Не выбрано ни одно задание'; return; }
  btn.disabled = true;
  var includedList = Object.keys(topic_config);
  var total = 0;
  includedList.forEach(function(t){
    var b = V_TASK_LABEL[t];
    if (t==='1'||t==='11') total += 2;
    else if (t==='2'||t==='10') total += 3;
    else if (t==='3-9'||t==='12-18'||t==='30-36') total += 7;
    else if (t==='19-24') total += 6;
    else if (t==='25-29') total += 5;
    else if (t==='37') total += 6;
    else if (t==='38.1'||t==='38.2') total += 14;
  });
  var i = 0;
  for (var tt in topic_config){
    i++;
    r.className='res'; r.textContent = '🎲 Генерирую '+i+'/'+includedList.length+': задание '+tt+'…';
    try{
      var g = await api({action:'variant_generate', topic_config: (function(){var o={}; o[tt]=topic_config[tt]; return o;})()});
      if (g.error) throw new Error(g.error);
      if (!_vGenerated) _vGenerated = {tasks: {}, topic_config: {}, chosen_topics: {}};
      _vGenerated.tasks[tt] = g.tasks[tt];
      _vGenerated.topic_config[tt] = topic_config[tt];
      if (g.chosen_topics && g.chosen_topics[tt]) _vGenerated.chosen_topics[tt] = g.chosen_topics[tt];
    } catch(e){
      r.className='res err'; r.textContent = '💥 '+e.message;
      btn.disabled = false; btn.textContent = '🎲 Сгенерировать вариант'; return;
    }
  }
  r.className='res ok';
  r.innerHTML = '✅ Вариант сгенерирован. Заданий: <b>'+includedList.length+'</b>. Максимум: <b>'+total+'</b>.';
  btn.disabled = false; btn.textContent = '🎲 Сгенерировать вариант';
  renderVariantPreview(_vGenerated, total);
}

async function renderVariantPreview(v, totalMax){
  var area = document.getElementById('vArea');
  var students = await api({action:'list_students'});
  var opts = '<option value="">— выбери —</option>';
  (students.students||[]).forEach(function(s){
    var full = ((s.surname||'')+' '+(s.name||'')).trim() || s.code;
    opts += '<option value="'+esc(s.code)+'">'+esc(full)+' ('+esc(s.code)+')</option>';
  });
  var h = '';
  h += '<div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:14px">';
  h += '<button class="btn btn-outline" style="width:auto" onclick="variantSave()">💾 Сохранить в банк вариантов</button>';
  h += '<button class="btn btn-outline" style="width:auto" onclick="variantDownloadPDF(false)">📄 PDF для ученика</button>';
  h += '<button class="btn btn-outline" style="width:auto" onclick="variantDownloadPDF(true)">📄 PDF для учителя</button>';
  h += '</div>';
  h += '<div class="panel" style="margin-top:14px;background:rgba(123,92,255,.08);border-color:rgba(0,229,255,.4)">';
  h += '<h3>🎯 Назначить ученику</h3>';
  h += '<div class="row" style="gap:10px"><div style="flex:1"><select id="vStudent">'+opts+'</select></div>';
  h += '<div style="flex:0 0 auto"><button class="btn btn-ok" style="width:auto" onclick="variantAssignAfterSave()">🎯 Сохранить и назначить</button></div></div>';
  h += '</div>';
  if (v.chosen_topics){
    h += '<div class="hint" style="margin-top:12px">Темы, выпавшие: ';
    h += Object.keys(v.chosen_topics).map(function(t){return '<b>'+esc(t)+'</b>: '+esc(v.chosen_topics[t]);}).join(' • ');
    h += '</div>';
  }
  h += '<h3 style="margin-top:18px;color:#c9b8ff">Предпросмотр заданий</h3>';
  V_TASKS.forEach(function(t, idx){
    if (!v.tasks[t]) return;
    h += '<details style="margin-top:12px;background:rgba(5,6,15,.4);border-radius:10px;padding:12px;border:1px solid rgba(123,92,255,.2)">';
    h += '<summary style="cursor:pointer;color:#00e5ff;font-weight:700;font-size:15px">Задание '+esc(t)+'</summary>';
    h += '<div id="vTask_'+idx+'" style="margin-top:12px"></div>';
    h += '</details>';
  });
  area.innerHTML = h;
  var idx = 0;
  V_TASKS.forEach(function(t){
    if (!v.tasks[t]) return;
    var el = document.getElementById('vTask_'+idx);
    if (el) el.innerHTML = renderTaskForPrint(t, v.tasks[t], {withAnswers:true});
    idx++;
  });
}

async function variantSave(){
  if (!_vGenerated) { alert('Сначала сгенерируйте вариант'); return; }
  var r = document.getElementById('vRes');
  r.className='res'; r.textContent='💾 Сохраняю…';
  var d = await api({action:'variant_create', tasks:_vGenerated.tasks, topic_config:_vGenerated.topic_config});
  if (d.error) { r.className='res err'; r.textContent='💥 '+d.error; return; }
  _vGenerated.saved_id = d.id; _vGenerated.saved_code = d.code;
  r.className='res ok'; r.innerHTML = '✅ Сохранено! Код: <code>'+esc(d.code)+'</code>';
  loadVariantsList();
}

async function variantAssignAfterSave(){
  var sid = document.getElementById('vStudent').value;
  if (!sid) { alert('Выбери ученика'); return; }
  if (!_vGenerated) return;
  if (!_vGenerated.saved_id) { await variantSave(); if (!_vGenerated.saved_id) return; }
  var d = await api({action:'variant_assign', id:_vGenerated.saved_id, student_codes:[sid]});
  if (d.error) { alert('Ошибка: '+d.error); return; }
  alert('✅ Назначено');
}

function variantDownloadPDF(withAnswers){
  if (!_vGenerated) return;
  var tasks = _vGenerated.tasks;
  var body = '<h1>Вариант '+(_vGenerated.saved_code || '')+'</h1>';
  body += '<div class="meta">Письменная часть ЕГЭ по английскому языку</div>';
  var first = true;
  V_TASKS.forEach(function(t){
    if (!tasks[t]) return;
    if (!first) body += '<div class="page-break"></div>';
    first = false;
    body += '<h2>Задание '+esc(t)+'</h2>';
    body += renderTaskForPrint(t, tasks[t], {withAnswers:false});
  });
  body += '<div class="page-break"></div>';
  body += renderAnswerSheet(tasks);
  if (withAnswers){
    body += '<div class="page-break"></div>';
    body += '<h2>ОТВЕТЫ И КРИТЕРИИ (для учителя)</h2>';
    V_TASKS.forEach(function(t){
      if (!tasks[t]) return;
      body += renderTaskForPrint(t, tasks[t], {withAnswers:true});
    });
  }
  openPrintWindow(body, 'Вариант');
}

function renderAnswerSheet(tasks){
  var h = '<h2>Бланк ответов</h2>';
  if (tasks['1']){
    h += '<h3>Задание 1</h3><table><tr><th>Говорящий</th>'+'ABCDEF'.split('').map(function(k){return '<th>'+k+'</th>';}).join('')+'</tr>';
    h += '<tr><td>Ответ</td>'+'ABCDEF'.split('').map(function(){return '<td style="height:24pt"></td>';}).join('')+'</tr></table>';
  }
  if (tasks['2']){
    h += '<h3>Задание 2</h3><table><tr><th>Утв.</th>'+'ABCDEFG'.split('').map(function(k){return '<th>'+k+'</th>';}).join('')+'</tr>';
    h += '<tr><td>Ответ</td>'+'ABCDEFG'.split('').map(function(){return '<td style="height:24pt"></td>';}).join('')+'</tr></table>';
    h += '<div style="font-size:10pt">1 – True, 2 – False, 3 – Not stated</div>';
  }
  if (tasks['3-9']){
    h += '<h3>Задания 3–9</h3><table><tr>'+[3,4,5,6,7,8,9].map(function(n){return '<th>'+n+'</th>';}).join('')+'</tr>';
    h += '<tr>'+[3,4,5,6,7,8,9].map(function(){return '<td style="height:24pt"></td>';}).join('')+'</tr></table>';
  }
  if (tasks['10']){
    h += '<h3>Задание 10</h3><table><tr>'+'ABCDEFG'.split('').map(function(k){return '<th>'+k+'</th>';}).join('')+'</tr>';
    h += '<tr>'+'ABCDEFG'.split('').map(function(){return '<td style="height:24pt"></td>';}).join('')+'</tr></table>';
  }
  if (tasks['11']){
    h += '<h3>Задание 11</h3><table><tr>'+'ABCDEF'.split('').map(function(k){return '<th>'+k+'</th>';}).join('')+'</tr>';
    h += '<tr>'+'ABCDEF'.split('').map(function(){return '<td style="height:24pt"></td>';}).join('')+'</tr></table>';
  }
  if (tasks['12-18']){
    h += '<h3>Задания 12–18</h3><table><tr>'+[12,13,14,15,16,17,18].map(function(n){return '<th>'+n+'</th>';}).join('')+'</tr>';
    h += '<tr>'+[12,13,14,15,16,17,18].map(function(){return '<td style="height:24pt"></td>';}).join('')+'</tr></table>';
  }
  if (tasks['19-24']){
    h += '<h3>Задания 19–24</h3><table>';
    [19,20,21,22,23,24].forEach(function(n){h += '<tr><td style="width:60pt"><b>'+n+'</b></td><td style="height:24pt"></td></tr>';});
    h += '</table>';
  }
  if (tasks['25-29']){
    h += '<h3>Задания 25–29</h3><table>';
    [25,26,27,28,29].forEach(function(n){h += '<tr><td style="width:60pt"><b>'+n+'</b></td><td style="height:24pt"></td></tr>';});
    h += '</table>';
  }
  if (tasks['30-36']){
    h += '<h3>Задания 30–36</h3><table><tr>'+[30,31,32,33,34,35,36].map(function(n){return '<th>'+n+'</th>';}).join('')+'</tr>';
    h += '<tr>'+[30,31,32,33,34,35,36].map(function(){return '<td style="height:24pt"></td>';}).join('')+'</tr></table>';
  }
  if (tasks['37']){
    h += '<h3>Задание 37 — письмо</h3>';
    for (var i=0; i<20; i++) h += '<div style="border-bottom:1pt dotted #888;height:22pt"></div>';
  }
  if (tasks['38.1'] || tasks['38.2']){
    var label = tasks['38.1'] && tasks['38.2'] ? '38.1 / 38.2' : (tasks['38.1'] ? '38.1' : '38.2');
    h += '<h3>Задание '+label+' — эссе</h3>';
    for (var j=0; j<28; j++) h += '<div style="border-bottom:1pt dotted #888;height:22pt"></div>';
  }
  return h;
}

async function loadVariantsList(){
  var v = document.getElementById('vList');
  v.innerHTML = '<div class="empty">Загрузка…</div>';
  var d = await api({action:'variant_list'});
  if (d.error) { v.innerHTML = '<div class="res err">💥 '+esc(d.error)+'</div>'; return; }
  if (!d.variants || !d.variants.length) { v.innerHTML = '<div class="empty">Пока нет вариантов</div>'; return; }
  var h = '';
  d.variants.forEach(function(x){
    h += '<div class="list-item"><div class="info">';
    h += '<b style="color:#c9b8ff;font-family:monospace">'+esc(x.code)+'</b> <span style="font-size:12px;color:#8b93c4">'+esc(fmtDate(x.created_at))+'</span>';
    h += '<div class="meta">'+x.task_types.length+' заданий · макс. '+x.total_max+'</div>';
    h += '</div>';
    h += '<button class="btn btn-sm btn-outline" onclick="openVariantFromBank(\''+esc(x.id)+'\')">👁</button>';
    h += '<button class="btn btn-sm btn-danger" onclick="deleteVariant(\''+esc(x.id)+'\')">🗑</button>';
    h += '</div>';
  });
  v.innerHTML = h;
}

async function openVariantFromBank(vid){
  var d = await api({action:'variant_get', id:vid});
  if (d.error) { alert(d.error); return; }
  _vGenerated = {tasks: d.data, topic_config: d.topic_config || {}, saved_id: d.id, saved_code: d.code, chosen_topics: d.chosen_topics || {}};
  var total = d.total_max || 0;
  document.getElementById('vRes').className = 'res ok';
  document.getElementById('vRes').innerHTML = '📂 Открыт вариант <code>'+esc(d.code)+'</code> · макс. '+total;
  renderVariantPreview(_vGenerated, total);
  switchTab('variants');
}

async function deleteVariant(vid){
  if (!confirm('Удалить вариант?')) return;
  var d = await api({action:'variant_delete', id:vid});
  if (d.error) { alert(d.error); return; }
  loadVariantsList();
}

// ---------- УЧЕНИКИ ----------
async function createStudent(){
  var sn=document.getElementById('stSurname').value.trim();
  var nm=document.getElementById('stName').value.trim();
  if(!sn && !nm){alert('Введи фамилию или имя'); return;}
  var r=document.getElementById('stRes');
  r.className='res'; r.textContent='Создаю…';
  var d=await api({action:'create_student', surname:sn, name:nm});
  if(d.error){r.className='res err'; r.innerHTML='💥 '+esc(d.error); return;}
  var link=window.location.origin+window.location.pathname+'?code='+d.code;
  r.className='res ok';
  r.innerHTML='✅ Создан!<br><b>'+esc((d.surname+' '+d.name).trim())+'</b><br>Код: <code>'+esc(d.code)+'</code><br><br>Ссылка:<br><a href="'+esc(link)+'" target="_blank" style="color:#00e5ff;word-break:break-all">'+esc(link)+'</a>';
  document.getElementById('stSurname').value='';
  document.getElementById('stName').value='';
  listStudents();
}
async function listStudents(){
  var v=document.getElementById('stList');
  var d=await api({action:'list_students'});
  if(d.error){v.innerHTML='<div class="res err">💥 '+esc(d.error)+'</div>'; return;}
  _students=d.students||[];
  if(!_students.length){v.innerHTML='<div class="empty">Пока никого нет</div>'; return;}
  var h='';
  _students.forEach(function(s,i){
    var full=((s.surname||'')+' '+(s.name||'')).trim()||'—';
    h+='<div class="list-item ok"><div class="info"><b style="color:#c9b8ff">'+esc(full)+'</b>';
    h+='<div class="meta" style="font-family:monospace">'+esc(s.code)+'</div></div>';
    h+='<button class="btn btn-sm btn-outline" onclick="editStudent('+i+')">✏</button>';
    h+='<button class="btn btn-sm btn-outline" onclick="copyLink('+i+')">🔗</button>';
    h+='<button class="btn btn-sm btn-danger" onclick="delStudent('+i+')">🗑</button></div>';
  });
  v.innerHTML=h;
}
function editStudent(i){
  var s=_students[i]; if(!s) return;
  var sn=prompt('Фамилия:', s.surname||''); if(sn===null) return;
  var nm=prompt('Имя:', s.name||''); if(nm===null) return;
  api({action:'update_student', code:s.code, surname:sn, name:nm}).then(function(d){
    if(d.error){alert('Ошибка: '+d.error); return;} listStudents();
  });
}
function copyLink(i){
  var s=_students[i]; if(!s) return;
  var link=window.location.origin+window.location.pathname+'?code='+s.code;
  if(navigator.clipboard) navigator.clipboard.writeText(link).then(function(){alert('Скопировано:\n'+link);});
  else prompt('Скопируй:', link);
}
function delStudent(i){
  var s=_students[i]; if(!s) return;
  var full=((s.surname||'')+' '+(s.name||'')).trim()||s.code;
  if(!confirm('Удалить '+full+'?')) return;
  api({action:'delete_student', code:s.code}).then(function(d){
    if(d.error){alert('Ошибка: '+d.error); return;} listStudents();
  });
}

// ---------- ПРОВЕРКА ----------
async function loadPending(){
  var r=document.getElementById('pendingRes'), v=document.getElementById('pendingList');
  v.innerHTML=''; r.className='res'; r.textContent='Загрузка…';
  var [d, dv] = await Promise.all([api({action:'list_pending'}), api({action:'variant_pending_reviews'})]);
  var singles = (d && d.submissions) || [];
  var fromVariants = (dv && dv.pending) || [];
  _pendingList = singles.map(function(s){ s._kind='single'; return s; })
    .concat(fromVariants.map(function(s){ s._kind='variant'; return s; }));
  var cnt=document.getElementById('pendingCnt');
  if(cnt){ cnt.textContent=_pendingList.length; cnt.style.display=_pendingList.length?'inline-block':'none'; }
  r.className='res ok';
  if(!_pendingList.length){ r.textContent='Очередь пуста 🎉'; return; }
  r.innerHTML='Работ на проверке: <b>'+_pendingList.length+'</b>';
  var h='<div style="margin-top:10px">';
  _pendingList.forEach(function(s,i){
    h+='<div class="list-item warn"><div class="info">';
    h+='<b style="color:#c9b8ff">'+esc(s.student_name||s.student_code)+'</b>';
    h+='<div class="meta">'+(s._kind==='variant'?'📦 Вариант <b>'+esc(s.variant_code||'')+'</b> · ':'')+'Задание <b>'+esc(s.task_type)+'</b> · '+esc(fmtDate(s.submitted_at))+'</div></div>';
    h+='<button class="btn btn-sm" onclick="openReview('+i+')">🔍 Проверить</button></div>';
  });
  v.innerHTML=h+'</div>';
}

async function openReview(i){
  var s=_pendingList[i]; if(!s) return;
  _reviewSub=s;
  var critResp=await api({action:'get_criteria', task_type:s.task_type});
  if (s._kind === 'variant'){
    var vfull=await api({action:'variant_get_full', id:s.variant_id, student_code:s.student_code});
    if (vfull.error){alert('Ошибка: '+vfull.error); return;}
    var sub = vfull.submission;
    var taskData = vfull.variant.data[s.task_type] || {};
    var ansObj = (sub.answers && sub.answers[s.task_type]) || {};
    var fake = {student_code:s.student_code, task_type:s.task_type, submitted_at:sub.submitted_at,
      answer_text: ansObj.text || '', task_data: taskData, _variant_id: s.variant_id};
    _reviewCrit=critResp;
    renderReviewModal(fake, critResp);
    return;
  }
  var full=await api({action:'get_submission', student_code:s.student_code, submission_id:s.id});
  if(full.error){alert('Ошибка: '+full.error); return;}
  _reviewCrit=critResp;
  renderReviewModal(full, critResp);
}

function renderReviewModal(sub, critResp){
  var criteria=critResp.criteria;
  var checklist=critResp.checklist;
  var list=criteria.criteria||[];
  var h='<button class="close" onclick="closeAdminModal()">✕</button>';
  h+='<h3>🔍 Проверка работы</h3>';
  h+='<div style="display:flex;gap:16px;flex-wrap:wrap;margin-bottom:14px;font-size:14px;color:#c8cdf0">';
  h+='<div>Ученик: <b style="color:#c9b8ff">'+esc(sub.student_code)+'</b></div>';
  h+='<div>Задание: <b style="color:#c9b8ff">'+esc(sub.task_type)+'</b></div>';
  h+='<div>Отправлено: <b style="color:#c9b8ff">'+esc(fmtDate(sub.submitted_at))+'</b></div></div>';
  if(sub.task_data && sub.task_data.task_text){
    h+='<details style="background:rgba(5,6,15,.4);border-radius:10px;padding:10px;border:1px solid rgba(123,92,255,.2);margin-bottom:12px"><summary style="cursor:pointer;color:#c9b8ff;font-weight:600">📄 Условие</summary><div style="margin-top:8px;color:#d0d5f5;font-size:13px;line-height:1.7;white-space:pre-wrap">'+esc(sub.task_data.task_text)+'</div></details>';
  }
  h+='<div style="margin:12px 0"><div style="font-size:12px;color:#8b93c4;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px">📝 Текст работы</div>';
  h+='<div style="background:rgba(5,6,15,.55);border:1px solid rgba(123,92,255,.2);border-radius:12px;padding:16px;color:#e8ecff;font-size:15px;line-height:1.8;white-space:pre-wrap;font-family:Georgia,serif;max-height:400px;overflow-y:auto">'+esc(sub.answer_text||'')+'</div>';
  var wordCount=(sub.answer_text||'').trim().split(/\s+/).filter(function(w){return w.length>0;}).length;
  h+='<div style="font-size:12px;color:#8b93c4;margin-top:6px">Слов: <b style="color:#00e5ff">'+wordCount+'</b></div></div>';
  if(checklist){
    h+='<details style="background:rgba(5,6,15,.4);border-radius:10px;padding:12px;border:1px solid rgba(123,92,255,.2);margin-bottom:12px">';
    h+='<summary style="cursor:pointer;color:#c9b8ff;font-weight:700;font-size:14px">📋 Схема оценивания</summary>';
    h+='<div style="margin-top:12px;color:#c8cdf0;font-size:13px;line-height:1.7">';
    h+='<div style="margin-bottom:8px;color:#00e5ff;font-weight:600">'+esc(checklist.title||'')+'</div>';
    if(checklist.k1 && checklist.k1.aspects){
      h+='<div style="margin-bottom:10px"><b style="color:#c9b8ff">'+esc(checklist.k1.code)+' '+esc(checklist.k1.name)+'</b><ul style="margin:6px 0 0 20px">';
      checklist.k1.aspects.forEach(function(a){h+='<li>'+esc(a)+'</li>';});
      h+='</ul></div>';
    }
    h+='</div></details>';
  }
  h+='<div style="margin-top:16px">';
  h+='<div style="font-size:13px;text-transform:uppercase;letter-spacing:1.2px;color:#c9b8ff;font-weight:700;margin-bottom:10px">🎯 Баллы</div>';
  list.forEach(function(c){
    h+='<div style="display:flex;gap:12px;align-items:center;padding:10px 12px;margin:6px 0;background:rgba(5,6,15,.4);border-radius:10px">';
    h+='<div style="min-width:40px;font-family:monospace;font-weight:700;color:#00e5ff;font-size:15px">'+esc(c.code)+'</div>';
    h+='<div style="flex:1;font-size:13px;color:#c8cdf0">'+esc(c.name)+'</div>';
    h+='<select id="score_'+esc(c.code)+'" style="width:auto;min-width:90px;padding:8px 10px" onchange="updateTotal()">';
    for(var v=c.max; v>=0; v--){h+='<option value="'+v+'"'+(v===c.max?' selected':'')+'>'+v+' / '+c.max+'</option>';}
    h+='</select></div>';
  });
  h+='</div>';
  h+='<div style="text-align:right;font-size:22px;font-weight:800;font-family:monospace;color:#2ecc71;margin-top:14px" id="totalPreview">ИТОГО: '+criteria.max_total+' / '+criteria.max_total+'</div>';
  h+='<div style="margin-top:16px">';
  h+='<div style="font-size:12px;text-transform:uppercase;letter-spacing:1px;color:#8b93c4;font-weight:600;margin-bottom:8px">💬 Комментарий</div>';
  h+='<textarea id="reviewComment" style="width:100%;min-height:120px;resize:vertical;font-family:inherit;font-size:14px"></textarea></div>';
  h+='<div class="row" style="margin-top:16px"><div><button class="btn btn-ok" id="submitReviewBtn" onclick="submitReview()">📤 Отправить оценку</button></div><div><button class="btn btn-cancel" onclick="closeAdminModal()">Отмена</button></div></div>';
  document.getElementById('adminModalBody').innerHTML=h;
  document.getElementById('adminModal').classList.add('show');
  updateTotal();
}

function updateTotal(){
  if(!_reviewCrit) return;
  var list=_reviewCrit.criteria.criteria||[];
  var total=0, k1=null;
  list.forEach(function(c){
    var el=document.getElementById('score_'+c.code);
    if(!el) return;
    var v=parseInt(el.value)||0;
    if(c.code==='К1') k1=v;
    total+=v;
  });
  var k1zero = _reviewCrit.criteria.rule_k1_zero && k1===0;
  if(k1zero) total=0;
  document.getElementById('totalPreview').innerHTML='ИТОГО: '+total+' / '+_reviewCrit.criteria.max_total+(k1zero?' <span style="font-size:14px;color:#e74c3c">(К1=0)</span>':'');
}

async function submitReview(){
  if(!_reviewSub) return;
  var list=_reviewCrit.criteria.criteria||[];
  var scores={};
  list.forEach(function(c){var el=document.getElementById('score_'+c.code); if(el) scores[c.code]=parseInt(el.value)||0;});
  var comment=(document.getElementById('reviewComment').value||'').trim();
  if(!confirm('Отправить оценку ученику?')) return;
  var b=document.getElementById('submitReviewBtn');
  if(b){b.disabled=true;b.textContent='📤 Отправляю…';}
  var d;
  if (_reviewSub._variant_id){
    d = await api({action:'variant_review_manual', student_code:_reviewSub.student_code,
      variant_id:_reviewSub._variant_id, task_type:_reviewSub.task_type, scores:scores, comment:comment});
  } else {
    d = await api({action:'review_submission', student_code:_reviewSub.student_code,
      submission_id:_reviewSub.id, scores:scores, comment:comment});
  }
  if(d.error){alert('Ошибка: '+d.error); if(b){b.disabled=false;b.textContent='📤 Отправить оценку';} return;}
  closeAdminModal(); loadPending();
  alert('✅ Оценка отправлена. Итого: '+(d.total!=null?d.total:d.score));
}

function closeAdminModal(){
  document.getElementById('adminModal').classList.remove('show');
  _reviewSub=null; _reviewCrit=null;
}

// ---------- МАТЕРИАЛЫ ----------
async function loadMaterials(){
  var v=document.getElementById('matList');
  var d=await api({action:'materials_list'});
  if(d.error){v.innerHTML='<div class="res err">💥 '+esc(d.error)+'</div>'; return;}
  _materials=d.materials||[];
  if(!_materials.length){v.innerHTML='<div class="empty">Пока ничего нет</div>'; return;}
  var icon={pdf:'📄',image:'🖼',text:'📝',link:'🔗'};
  var h='';
  _materials.forEach(function(m,i){
    h+='<div class="list-item"><div class="info">';
    h+='<b style="color:#c9b8ff">'+(icon[m.type]||'📎')+' '+esc(m.title)+'</b>';
    h+='<div class="meta">'+esc(m.type)+(m.size?' · '+(m.size/1024).toFixed(0)+' КБ':'')+(m.url?' · '+esc(m.url):'')+'</div></div>';
    h+='<button class="btn btn-sm btn-outline" onclick="moveMaterial(\''+esc(m.id)+'\',\'up\')" '+(i===0?'disabled':'')+'>⬆</button>';
    h+='<button class="btn btn-sm btn-outline" onclick="moveMaterial(\''+esc(m.id)+'\',\'down\')" '+(i===_materials.length-1?'disabled':'')+'>⬇</button>';
    h+='<button class="btn btn-sm btn-danger" onclick="deleteMaterial(\''+esc(m.id)+'\')">🗑</button></div>';
  });
  v.innerHTML=h;
}
async function uploadMaterial(){
  var title=document.getElementById('matTitle').value.trim();
  var url=document.getElementById('matUrl').value.trim();
  var fileEl=document.getElementById('matFile');
  var r=document.getElementById('matRes');
  if(!title){r.className='res err'; r.textContent='⚠ Нужно название'; return;}
  if(!url && (!fileEl.files || !fileEl.files[0])){r.className='res err'; r.textContent='⚠ Нужен файл или ссылка'; return;}
  r.className='res'; r.textContent='Загружаю…';
  var payload={action:'materials_add', title:title};
  if(url) payload.url=url;
  else {
    var f=fileEl.files[0];
    if(f.size > 7*1024*1024){r.className='res err'; r.textContent='⚠ Файл больше 7 МБ'; return;}
    try{ var b64=await fileToBase64(f); payload.file_b64=b64; payload.filename=f.name; payload.content_type=f.type; }
    catch(e){r.className='res err'; r.textContent='⚠ '+e.message; return;}
  }
  var d=await api(payload);
  if(d.error){r.className='res err'; r.textContent='💥 '+d.error; return;}
  r.className='res ok'; r.textContent='✅ Добавлено';
  document.getElementById('matTitle').value=''; document.getElementById('matUrl').value=''; fileEl.value='';
  loadMaterials();
}
function fileToBase64(file){
  return new Promise(function(resolve,reject){
    var reader=new FileReader();
    reader.onload=function(){var res=reader.result; var i=res.indexOf(','); resolve(i>=0?res.slice(i+1):res);};
    reader.onerror=function(){reject(new Error('Ошибка чтения'));};
    reader.readAsDataURL(file);
  });
}
async function deleteMaterial(id){ if(!confirm('Удалить?')) return; var d=await api({action:'materials_delete', id:id}); if(d.error){alert(d.error); return;} loadMaterials(); }
async function moveMaterial(id, dir){ var d=await api({action:'materials_move', id:id, direction:dir}); if(d.error){alert(d.error); return;} loadMaterials(); }

// ---------- НАЗНАЧЕНИЯ ----------
function onAsSourceChange(){
  var v=document.getElementById('asSource').value;
  document.getElementById('asBankWrap').style.display=(v==='bank')?'block':'none';
  document.getElementById('asGenWrap').style.display=(v==='generate')?'block':'none';
}
function onAsTypeChange(){}

async function loadStudentsForAssign(){
  var sel=document.getElementById('asStudent');
  var d=await api({action:'list_students'});
  if(d.error || !d.students) return;
  sel.innerHTML='<option value="">— выбери —</option>';
  d.students.forEach(function(s){
    var full=((s.surname||'')+' '+(s.name||'')).trim()||s.code;
    sel.innerHTML+='<option value="'+esc(s.code)+'">'+esc(full)+' ('+esc(s.code)+')</option>';
  });
}

async function createAssignment(){
  var r=document.getElementById('asRes');
  var student=document.getElementById('asStudent').value;
  var task_type=document.getElementById('asTaskType').value;
  var source=document.getElementById('asSource').value;
  var note=document.getElementById('asNote').value.trim();
  if(!student){r.className='res err'; r.textContent='⚠ Выбери ученика'; return;}
  r.className='res'; r.textContent='Обрабатываю…';
  var payload={action:'assignment_create', student_code:student, task_type:task_type, note:note};
  if(source==='bank'){
    var code=document.getElementById('asBankCode').value.trim();
    if(!code){r.className='res err'; r.textContent='⚠ Введи код задания'; return;}
    var parts=code.split('-');
    if(parts.length<3){r.className='res err'; r.textContent='⚠ Неверный код'; return;}
    var topic=parts[1];
    var bankTask=await api({action:'get_bank_task', task_type:task_type, topic_letter:topic, code:code});
    if(bankTask.error){r.className='res err'; r.textContent='💥 '+bankTask.error; return;}
    delete bankTask.audio_b64; delete bankTask.audio_size_kb;
    payload.task_data=bankTask; payload.bank_code=code;
  } else {
    var topic=document.getElementById('asTopic').value;
    r.textContent='🤖 Генерирую (1-2 мин)…';
    var gen=await api({action:'fetch', task_type:task_type, topic:topic, student_code:student});
    if(gen.error){r.className='res err'; r.textContent='💥 '+gen.error; return;}
    payload.task_data=gen.task_data;
  }
  var d=await api(payload);
  if(d.error){r.className='res err'; r.textContent='💥 '+d.error; return;}
  r.className='res ok'; r.textContent='✅ Назначено!';
  document.getElementById('asNote').value=''; document.getElementById('asBankCode').value='';
  loadAssignments();
}

async function loadAssignments(){
  var v=document.getElementById('asList');
  var d=await api({action:'assignment_list'});
  if(d.error){v.innerHTML='<div class="res err">💥 '+esc(d.error)+'</div>'; return;}
  var arr=d.assignments||[];
  if(!arr.length){v.innerHTML='<div class="empty">Пока нет назначений</div>'; return;}
  var h='';
  arr.forEach(function(a){
    h+='<div class="list-item"><div class="info">';
    h+='<div style="color:#c9b8ff;font-weight:700">Задание '+esc(a.task_type)+'</div>';
    h+='<div class="meta">Ученик: <code>'+esc(a.student_code)+'</code>'+(a.bank_code?' · код: '+esc(a.bank_code):'')+' · '+esc(fmtDate(a.created_at))+'</div>';
    if(a.note) h+='<div class="meta" style="color:#f39c12">📌 '+esc(a.note)+'</div>';
    h+='</div><button class="btn btn-sm btn-danger" onclick="delAssignment(\''+esc(a.id)+'\')">🗑</button></div>';
  });
  v.innerHTML=h;
}
async function delAssignment(id){
  if(!confirm('Отменить назначение?')) return;
  var d=await api({action:'assignment_delete', id:id});
  if(d.error){alert('Ошибка: '+d.error); return;}
  loadAssignments();
}

// ---------- СТАТИСТИКА ----------
async function loadStats(){
  var g=document.getElementById('statsGlobal'), t=document.getElementById('statsTable');
  g.innerHTML='<div class="empty">Загрузка…</div>'; t.innerHTML='<div class="empty">Загрузка…</div>';
  var d=await api({action:'stats'});
  if(d.error){g.innerHTML='<div class="res err">💥 '+esc(d.error)+'</div>'; return;}
  var gs=d.global||{};
  g.innerHTML='<div style="display:flex;gap:20px;flex-wrap:wrap;font-size:14px;color:#c8cdf0">'
    +'<div>Проверено: <b style="color:#00e5ff;font-size:18px">'+gs.count+'</b></div>'
    +'<div>На проверке: <b style="color:#f39c12;font-size:18px">'+gs.pending+'</b></div>'
    +'<div>Всего баллов: <b style="color:#2ecc71;font-size:18px">'+gs.total+' / '+gs.max+'</b></div></div>';
  if(!d.students||!d.students.length){t.innerHTML='<div class="empty">Нет данных</div>'; return;}
  var h='<div style="overflow-x:auto"><table style="width:100%;border-collapse:collapse;margin-top:10px">';
  h+='<tr style="background:rgba(123,92,255,.15)"><th style="padding:10px;text-align:left;color:#c9b8ff">Ученик</th><th style="padding:10px;color:#c9b8ff">Работ</th><th style="padding:10px;color:#c9b8ff">Вариантов</th><th style="padding:10px;color:#c9b8ff">На проверке</th><th style="padding:10px;color:#c9b8ff">Баллы</th></tr>';
  d.students.forEach(function(s){
    h+='<tr style="border-top:1px solid rgba(123,92,255,.15)">';
    h+='<td style="padding:10px">'+esc(s.student_name)+'</td>';
    h+='<td style="padding:10px;text-align:center">'+s.count+'</td>';
    h+='<td style="padding:10px;text-align:center">'+(s.variants_count||0)+'</td>';
    h+='<td style="padding:10px;text-align:center">'+(s.pending||0)+'</td>';
    h+='<td style="padding:10px;text-align:center"><b style="color:#2ecc71;font-family:monospace">'+s.total+' / '+s.max+'</b></td></tr>';
  });
  h+='</table></div>';
  t.innerHTML=h;
}

// ---------- ЛИМИТЫ ----------
async function loadRatelimit(){
  var v=document.getElementById('rlList'), r=document.getElementById('rlRes');
  r.className='res'; r.textContent='Загрузка…'; v.innerHTML='';
  var info=await api({action:'ratelimit_info'});
  if(!info.error){ document.getElementById('rlMax').textContent=info.max; }
  var d=await api({action:'ratelimit_list'});
  if(d.error){r.className='res err'; r.textContent='💥 '+d.error; return;}
  r.className='res ok'; r.textContent='Записей: '+d.count;
  if(!d.records||!d.records.length){v.innerHTML='<div class="empty">Пусто</div>'; return;}
  var h='<div style="margin-top:10px">';
  d.records.forEach(function(x){
    var usedColor=x.used>=(info.max||5)?'#e74c3c':'#c8cdf0';
    h+='<div class="list-item"><div class="info">';
    h+='<div style="font-family:monospace;font-size:12px;color:#8b93c4">'+esc(x.kind.toUpperCase())+' '+esc(x.hash)+'</div>';
    h+='<div class="meta">Использовано: <b style="color:'+usedColor+'">'+x.used+'</b> · '+esc(fmtDate(x.last_seen))+'</div></div>';
    h+='<button class="btn btn-sm btn-danger" onclick="resetOneRl(\''+esc(x.key)+'\')">🗑</button></div>';
  });
  v.innerHTML=h+'</div>';
}
async function resetOneRl(key){ if(!confirm('Сбросить?')) return; var d=await api({action:'ratelimit_reset', key:key}); if(d.error){alert(d.error); return;} loadRatelimit(); }
async function resetAllRl(){ if(!confirm('СБРОСИТЬ ВСЕ?')) return; var d=await api({action:'ratelimit_reset', key:'all'}); if(d.error){alert(d.error); return;} alert('Сброшено: '+d.deleted); loadRatelimit(); }
async function loadAudit(){
  var v=document.getElementById('auditList');
  v.innerHTML='<div class="empty">Загрузка…</div>';
  var d=await api({action:'ratelimit_audit'});
  if(d.error||!d.events||!d.events.length){v.innerHTML='<div class="empty">Пусто</div>'; return;}
  var h='<div style="margin-top:10px;font-family:monospace;font-size:12px">';
  d.events.slice(0,50).forEach(function(e){
    var color=e.event==='blocked'?'#e74c3c':'#2ecc71';
    h+='<div style="padding:6px 10px;margin:3px 0;background:rgba(5,6,15,.4);border-radius:6px;border-left:3px solid '+color+'">';
    h+='<b style="color:'+color+'">'+esc(e.event)+'</b> · '+esc(fmtDate(e.ts))+' · used='+e.used_ip;
    if(e.note) h+=' · '+esc(e.note);
    h+='</div>';
  });
  v.innerHTML=h+'</div>';
}

loadPending();
initVariantsTab();
</script>
</body>
</html>"""
TOPIC_OPTIONS_HTML = (
    '<option value="any">Любая (по выбору модели)</option>'
    '<option value="А. Повседневная жизнь семьи. Межличностные отношения">А. Повседневная жизнь семьи</option>'
    '<option value="Б. Внешность и характеристика человека">Б. Внешность и характеристика человека</option>'
    '<option value="В. Здоровый образ жизни и забота о здоровье">В. Здоровый образ жизни</option>'
    '<option value="Г. Школьное образование, школьная жизнь">Г. Школьное образование</option>'
    '<option value="Д. Современный мир профессий">Д. Современный мир профессий</option>'
    '<option value="Е. Место иностранного языка в жизни">Е. Место иностранного языка</option>'
    '<option value="Ж. Молодёжь в современном обществе">Ж. Молодёжь в современном обществе</option>'
    '<option value="З. Покупки: одежда, обувь, продукты">З. Покупки</option>'
    '<option value="И. Роль спорта в современной жизни">И. Роль спорта</option>'
    '<option value="К. Деловое общение">К. Деловое общение</option>'
    '<option value="Л. Туризм. Виды отдыха. Экотуризм">Л. Туризм и отдых</option>'
    '<option value="М. Вселенная и человек. Природа. Экология">М. Природа и экология</option>'
    '<option value="Н. Средства массовой информации">Н. СМИ</option>'
    '<option value="О. Технический прогресс. Интернет-безопасность">О. Технический прогресс</option>'
    '<option value="П. Проблемы современной цивилизации">П. Проблемы цивилизации</option>'
    '<option value="Р. Родная страна и страны изучаемого языка">Р. Родная страна</option>'
    '<option value="С. Выдающиеся люди родной страны и мира">С. Выдающиеся люди</option>'
)

MAIN_HTML = MAIN_HTML.replace("__TOPIC_OPTIONS__", TOPIC_OPTIONS_HTML)