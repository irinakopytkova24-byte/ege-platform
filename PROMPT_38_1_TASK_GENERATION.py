from prompt_common import _COMMON

PROMPT_38_1_TASK_GENERATION = """Ты — эксперт-составитель ЕГЭ по английскому языку (ФИПИ).
Собери шапку задания 38.1 по образцу КИМ ЕГЭ 2027.

Тема: {TOPIC}
Каркас: {SURVEY_SCHEMA}

=== СТРУКТУРА task_text (СТРОГО ПО ПОРЯДКУ) ===

1. "Choose only ONE of the two given tasks (38.1 or 38.2), indicate its number in ANSWER SHEET NO. 2 and complete it according to the plan. In your answer to task 38, write numerals in digits."
Пустая строка.

2. "[38.1]"
Пустая строка.

3. "Imagine that you are doing a project on {PROJECT_SUBJECT} in Zetland. You have found some data on the subject – the results of a survey conducted among {SURVEY_AUDIENCE} (see the table below)."
С НОВОЙ строки:
"Comment on the survey data and give your opinion on the subject of the project."

СТОП. Дальше в task_text НЕ добавляй ничего:
- НЕ вставляй таблицу текстом (её рисует фронт из survey_data).
- НЕ добавляй "Write 200–250 words."
- НЕ добавляй план.

Всё это фронт соберёт сам.

=== ЧТО ВЕРНУТЬ ===
ТОЛЬКО JSON:

{{
  "task_text": "Choose only ONE of the two given tasks (38.1 or 38.2), indicate its number in ANSWER SHEET NO. 2 and complete it according to the plan. In your answer to task 38, write numerals in digits.\\n\\n[38.1]\\n\\nImagine that you are doing a project on {PROJECT_SUBJECT} in Zetland. You have found some data on the subject – the results of a survey conducted among {SURVEY_AUDIENCE} (see the table below).\\nComment on the survey data and give your opinion on the subject of the project.",
  "stimulus_analysis": {{"topic": "{TOPIC}", "sum_check": "100%"}}
}}""" + _COMMON