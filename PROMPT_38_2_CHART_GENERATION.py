from prompt_common import _COMMON

PROMPT_38_2_CHART_GENERATION = """Ты — эксперт-составитель ЕГЭ по английскому языку (ФИПИ).
Собери шапку задания 38.2 по образцу КИМ ЕГЭ 2027.

Тема: {TOPIC}
Каркас: {CHART_SCHEMA}

=== СТРУКТУРА task_text ===

1. "Choose only ONE of the two given tasks (38.1 or 38.2), indicate its number in ANSWER SHEET NO. 2 and complete it according to the plan. In your answer to task 38, write numerals in digits."
Пустая строка.

2. "[38.2]"
Пустая строка.

3. "Imagine that you are doing a project on {PROJECT_SUBJECT} in Zetland. You have found some data on the subject – the results of a survey conducted among {SURVEY_AUDIENCE} (see the pie chart below)."
С НОВОЙ строки:
"Comment on the survey data and give your opinion on the subject of the project."

СТОП. Дальше НЕ добавляй:
- маркер диаграммы (её рисует фронт),
- "Write 200–250 words.",
- план.

=== ЧТО ВЕРНУТЬ ===
ТОЛЬКО JSON:

{{
  "task_text": "Choose only ONE of the two given tasks (38.1 or 38.2), indicate its number in ANSWER SHEET NO. 2 and complete it according to the plan. In your answer to task 38, write numerals in digits.\\n\\n[38.2]\\n\\nImagine that you are doing a project on {PROJECT_SUBJECT} in Zetland. You have found some data on the subject – the results of a survey conducted among {SURVEY_AUDIENCE} (see the pie chart below).\\nComment on the survey data and give your opinion on the subject of the project.",
  "stimulus_analysis": {{"topic": "{TOPIC}", "sum_check": "100%"}}
}}""" + _COMMON