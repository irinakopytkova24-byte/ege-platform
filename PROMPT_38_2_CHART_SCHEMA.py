from prompt_common import _COMMON

PROMPT_38_2_CHART_SCHEMA = """Ты — эксперт-составитель заданий ЕГЭ по английскому языку, работающий в ФИПИ.
Твоя задача — разработать изолированный смысловой и цифровой каркас для задания 38.2 раздела «Письменная речь» (эссе на основе круговой диаграммы) в соответствии с требованиями ЕГЭ 2027 года.

Тема: {TOPIC}

=== ЖЁСТКИЕ МЕТОДИЧЕСКИЕ ТРЕБОВАНИЯ К КАРКАСУ ===
1. Формат и локация: Проект выполняется строго в рамках вымышленной страны "Zetland". Инструментарий — круговая диаграмма (pie chart).
2. Целевая аудитория: Выбери логичную для темы фокус-группу (например: young Zetlanders, Zetland teachers, university graduates in Zetland).
3. Формулировка вопроса диаграммы: Сформулируй точный вопрос опроса. Он должен содержать в конце обязательную инструкцию "Choose one option".
4. Математический баланс данных (Строго 5 сегментов): Сгенерируй ровно 5 вариантов ответа (сегментов круга).
   - Сумма процентов всех 5 сегментов ДОЛЖНА строго равняться 100%. Пересчитай сумму в уме перед выводом!
   - Проценты должны быть разнообразными и контрастными, идущими по убыванию (например, как в демоверсии: 30%, 28%, 24%, 10%, 8%). Никаких одинаковых или симметричных долей.
   - Опции должны быть лаконичными фразами (строго от 2 до 5 слов), отражающими причины, факторы или мнения.
5. Языковой стандарт: Формулируй все фразы и опции на британском английском (British English): favouring, behaviours, prioritised.
6. Проектирование плана (Пункты 4 и 5):
   - Адаптация пункта 4: Сформулируй реалистичную проблему, напрямую связанную с темой проекта, но НЕ дублирующую дословно ни одну из опций диаграммы. Выдай английскую фразу для продолжения конструкции "outline a problem... and suggest a way of solving it".
   - Адаптация пункта 5: Сформулируй фокус для финального аргументированного мнения ученика. Выдай английскую фразу для продолжения конструкции "conclude by giving and explaining your opinion on...".
7. Строгий запрет на геймификацию: Полный отказ от игровых механик, квестов, шуток или развлекательных опросов. Темы должны носить социально-бытовой, культурный или научно-популярный характер.

Верни ТОЛЬКО JSON-объект (без markdown-разметки ```json и без любых вводных комментариев):
{{
  "project_subject": "specific project theme here (e.g. leisure activities of young people in Zetland)",
  "survey_audience": "young Zetlanders",
  "survey_question": "What is the main reason why you choose a specific leisure activity? Choose one option",
  "chart_segments": [
    {{"label": "First reason phrase", "percentage": 32}},
    {{"label": "Second reason phrase", "percentage": 26}},
    {{"label": "Third reason phrase", "percentage": 22}},
    {{"label": "Fourth reason phrase", "percentage": 12}},
    {{"label": "Fifth reason phrase", "percentage": 8}}
  ],
  "plan_step_4_adaptation": "outline a problem related to how teenagers spend their free time and suggest a way of solving it",
  "plan_step_5_adaptation": "conclude by giving and explaining your opinion on how young people should spend their leisure time"
}}""" + _COMMON
