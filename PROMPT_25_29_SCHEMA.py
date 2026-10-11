from prompt_common import _COMMON

PROMPT_25_29_SCHEMA = """Ты — эксперт-составитель заданий ЕГЭ по английскому языку (ФИПИ).
Разработай словообразовательный каркас (5 заданий 25–29) для раздела «Грамматика и лексика».

Тема: {TOPIC}

=== ГЛАВНОЕ ===
Это словообразование — ответ ДОЛЖЕН быть другой частью речи, образованной через суффикс или префикс.
ЗАПРЕЩЕНО: просто менять форму слова (множественное число, времена, степени сравнения).

=== РАЗНООБРАЗИЕ (обязательно разные типы) ===
- Ровно 1: наречие через -ly (прил → наречие).
- Ровно 1: отрицательный префикс (un-, in-/im-, il-/ir-, dis-, mis-).
- Оставшиеся 3 — РАЗНЫЕ направления:
  * глагол → существительное (-tion, -ment, -ance/-ence, -er/-or)
  * существительное → прилагательное (-ful, -less, -ous, -al, -ive, -y)
  * прилагательное → существительное (-ness, -ity)
  * прилагательное → глагол (-ise/-ize, -en)
  * существительное → глагол (re-, over-, dis-)
ЗАПРЕЩЕНО: все 5 заданий на один тип (например, все существительные через -tion).

=== ЗАПРЕТ НА ПРОСТЫЕ ===
НЕ используй в качестве ответов: "-er" (reader, writer) как основной тип, если можно взять менее тривиальный аффикс.
Хороший набор: CERTAIN→certainly, COLLECT→collection, POSSIBLE→impossible, HELP→helpful, DEVELOP→development.

=== ЯЗЫК ===
Британский английский: organise→organisation, colour→colourful.
Базовые слова ЗАГЛАВНЫМИ.

=== ФОРМАТ ВЫВОДА ===
ТОЛЬКО JSON-объект:

{{
  "tasks": [
    {{"id": 25, "fipi_subcode": "2.3.11.4", "base_word": "CERTAIN", "base_part_of_speech": "adjective", "target_word": "certainly", "target_part_of_speech": "adverb", "affix_used": "suffix -ly"}},
    {{"id": 26, "fipi_subcode": "2.3.11.2", "base_word": "COLLECT", "base_part_of_speech": "verb", "target_word": "collection", "target_part_of_speech": "noun", "affix_used": "suffix -tion"}},
    {{"id": 27, "fipi_subcode": "2.3.11.3", "base_word": "POSSIBLE", "base_part_of_speech": "adjective", "target_word": "impossible", "target_part_of_speech": "adjective", "affix_used": "prefix im-"}},
    {{"id": 28, "fipi_subcode": "2.3.11.3", "base_word": "HELP", "base_part_of_speech": "noun", "target_word": "helpful", "target_part_of_speech": "adjective", "affix_used": "suffix -ful"}},
    {{"id": 29, "fipi_subcode": "2.3.11.2", "base_word": "DEVELOP", "base_part_of_speech": "verb", "target_word": "development", "target_part_of_speech": "noun", "affix_used": "suffix -ment"}}
  ]
}}""" + _COMMON