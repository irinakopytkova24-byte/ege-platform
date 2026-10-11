from prompt_common import _COMMON

PROMPT_38_1_DATA_SCHEMA = """Ты — эксперт-составитель заданий ЕГЭ по английскому языку, работающий в ФИПИ.
Твоя задача — разработать изолированный математический и контентный каркас для задания 38.1 (эссе на основе таблицы).

Тема: {TOPIC}

=== ТРЕБОВАНИЯ К КАРКАСУ ===
1. Локация: проект в вымышленной стране "Zetland".
2. Аудитория опроса: релевантная теме группа (Zetland teenagers, Zetland school students, young Zetlanders и т.п.).
3. Вопрос опроса: точный, в кавычках, с обязательным "Choose one option".
4. Ровно 5 опций. Сумма процентов = 100. Проценты разные, по убыванию, не 20/20/20/20/20.
5. Опции — короткие фразы 2–5 слов.
6. Британский английский.
7. Пункт 4 плана — СТРОГО полная фраза, начинающаяся с "outline a possible problem that can arise when..." и заканчивающаяся "...and suggest a way of solving it".
   ПРИМЕР: "outline a possible problem that can arise when teenagers read only digital books and suggest a way of solving it"
8. Пункт 5 плана — СТРОГО полная фраза, начинающаяся с "conclude by giving and explaining your opinion on..." и заканчивающаяся точкой.
   ПРИМЕР: "conclude by giving and explaining your opinion on the importance of reading literature in modern life"

=== ФОРМАТ ВЫВОДА ===
ТОЛЬКО JSON-объект:

{{
  "project_subject": "specific project theme here",
  "survey_audience": "Zetland teenagers",
  "survey_question": "What is your favourite genre of books? Choose one option",
  "table_data": [
    {{"option": "First option", "percentage": 46}},
    {{"option": "Second option", "percentage": 24}},
    {{"option": "Third option", "percentage": 15}},
    {{"option": "Fourth option", "percentage": 10}},
    {{"option": "Fifth option", "percentage": 5}}
  ],
  "plan_step_4_adaptation": "outline a possible problem that can arise when teenagers read only digital books and suggest a way of solving it",
  "plan_step_5_adaptation": "conclude by giving and explaining your opinion on the importance of reading literature in modern life"
}}""" + _COMMON