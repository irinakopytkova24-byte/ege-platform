from prompt_common import _COMMON

PROMPT_19_24_SCHEMA = """Ты — эксперт-составитель заданий ЕГЭ по английскому языку (ФИПИ).
Разработай грамматический каркас (6 заданий 19–24) для раздела «Грамматика и лексика».

Тема: {TOPIC}

=== КРИТИЧЕСКИ ВАЖНО: ПРЕОБРАЗОВАНИЕ ОБЯЗАТЕЛЬНО ===
Базовое слово ДОЛЖНО требовать преобразования.
ЗАПРЕЩЕНО давать слова, которые в тексте стоят в своей базовой форме.
Проверь каждое задание: если ученик напишет базовое слово без изменений и получит правильный ответ — это ОШИБКА.
Пример ПРАВИЛЬНО: base_word="TWO", target_form="second" (числительное → порядковое).
Пример НЕПРАВИЛЬНО: base_word="TWO", target_form="two" (не требует преобразования).

=== ФОРМАТ ===
Выбери случайно один из двух:
- "format_1": один связный текст, 6 пропусков (19–24).
- "format_2": два коротких текста по 3 пропуска (19–21 и 22–24).

=== ЗАПРЕТ НА СЛОВООБРАЗОВАНИЕ ===
Это задание ТОЛЬКО на изменение грамматической формы. Часть речи базового слова и ответа ДОЛЖНА совпадать.
ЗАПРЕЩЕНО: добавлять суффиксы, меняющие часть речи (глагол→сущ через -er/-tion, сущ→прил через -ful/-ous, прил→наречие через -ly).

=== ЗАПРЕТ НА ЧАСТИЦУ "to" ===
В target_form НЕ должно быть частицы "to". Если планируешь used to / be going to — ответом должно быть только само слово (used, going). Многословные ответы допустимы ТОЛЬКО со вспомогательными глаголами: was, were, is, are, have, has, had, will, been.

=== РАЗНООБРАЗИЕ ЭЛЕМЕНТОВ (Кодификатор 2.4.x) ===
Распредели строго между 6 заданиями:
- 3–4 задания: глаголы (времена Active/Passive, неличные формы без смены части речи).
- Ровно 1: существительное (множественное число, желательно исключение) — НЕ бери MOUSE/MICE (используй FOOT→FEET, CHILD→CHILDREN, TOOTH→TEETH).
- Ровно 1: прилагательное или наречие (степень сравнения, включая исключения).
- Ровно 1: числительное (ONE→FIRST, TWO→SECOND) ИЛИ местоимение (THEY→THEM/THEIR).

=== ФОРМАТ ВЫВОДА ===
ТОЛЬКО JSON-объект:

{{
  "chosen_format": "format_1",
  "tasks": [
    {{"id": 19, "fipi_code": "2.4.24", "base_word": "SITUATE", "part_of_speech": "verb", "target_form": "situated", "acceptable_alternatives": []}},
    {{"id": 20, "fipi_code": "2.4.37", "base_word": "TWO", "part_of_speech": "numeral", "target_form": "second", "acceptable_alternatives": []}},
    {{"id": 21, "fipi_code": "2.4.29", "base_word": "FOOT", "part_of_speech": "noun", "target_form": "feet", "acceptable_alternatives": []}},
    {{"id": 22, "fipi_code": "2.4.25", "base_word": "WORK", "part_of_speech": "verb", "target_form": "have worked", "acceptable_alternatives": ["have been working"]}},
    {{"id": 23, "fipi_code": "2.4.33", "base_word": "BAD", "part_of_speech": "adjective", "target_form": "worse", "acceptable_alternatives": []}},
    {{"id": 24, "fipi_code": "2.4.24", "base_word": "FOUND", "part_of_speech": "verb", "target_form": "was founded", "acceptable_alternatives": []}}
  ]
}}""" + _COMMON