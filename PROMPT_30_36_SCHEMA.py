from prompt_common import _COMMON

PROMPT_30_36_SCHEMA = """Ты — эксперт-составитель заданий ЕГЭ по английскому языку, работающий в ФИПИ.
Твоя задача — разработать изолированный лексико-грамматический каркас (7 заданий 30–36) для раздела «Грамматика и лексика» в соответствии с требованиями высокого уровня сложности (В) ЕГЭ 2027 года.

Тема: {TOPIC}

=== ЖЁСТКИЕ МЕТОДИЧЕСКИЕ ТРЕБОВАНИЯ К КАРКАСУ ===
1. Количество заданий: Ровно 7 заданий (номера 30–36).
2. Однородность вариантов: Для каждого задания составь ровно 4 варианта ответа (1, 2, 3, 4). Все 4 слова внутри одного задания должны относиться к одной части речи, быть примерно одинаковой длины и иметь одинаковую грамматическую форму (например, все 4 слова — глаголы в прошедшем времени, или все 4 — наречия, или все 4 — существительные во множественном числе).
3. Обязательное разнообразие типов проверки (Кодификатор 2.3.1–2.3.5):
   - Как минимум 2 задания на синонимы/близкие по значению глаголы (например: admit / allow / approach / approve; remember / record / remind / recognize).
   - Как минимум 1 задание на фразовый глагол (например: look after / put off / turn out / carry on).
   - Как минимум 1 задание на устойчивое словосочетание (коллокацию) с предлогом или без (например: take care of, attend to, focus on).
   - Ровно 1 задание на средство логической связи / вводное слово (например: Moreover / However / Although / Nevertheless).
   - Ровно 1 задание на зависимый предлог или глагольную конструкцию (например: manage to do vs succeed in doing).
4. Однозначность и дистракторы: Дистракторы (неправильные варианты) должны быть абсолютно невозможными в целевом контексте (либо из-за нарушения лексической сочетаемости, либо из-за нестыковки предлогов/грамматики), но при этом казаться ученику правдоподобными.
5. Равномерность ключей: Цифры правильных ответов (1, 2, 3, 4) должны быть распределены сбалансированно. Каждая цифра обязана встретиться в качестве ключа минимум 1 раз и максимум 3 раза на весь тест из 7 вопросов.
6. Языковой стандарт: Вопросы и варианты ответов формулируются исключительно на британском английском (British English): favourite, coloured, publicised.

Верни ТОЛЬКО JSON-объект (без markdown-разметки ```json и без любых вводных комментариев):
{{
  "tasks": [
    {{
      "id": 30,
      "fipi_code": "2.3.2",
      "testing_type": "synonyms",
      "options": ["approach", "allow", "admit", "approve"],
      "correct": 3,
      "lexical_rule": "admit that (признать, что)"
    }},
    {{
      "id": 31,
      "fipi_code": "2.3.1",
      "testing_type": "collocation",
      "options": ["received", "repaired", "remained", "repeated"],
      "correct": 2,
      "lexical_rule": "repaired around the apartment (отремонтировано в квартире)"
    }},
    {{
      "id": 32,
      "fipi_code": "2.3.5",
      "testing_type": "discourse_marker",
      "options": ["Although", "However", "Withal", "Moreover"],
      "correct": 4,
      "lexical_rule": "Moreover в начале предложения для добавления мысли"
    }},
    {{
      "id": 33,
      "fipi_code": "2.3.1",
      "testing_type": "dependent_preposition",
      "options": ["visiting", "concentrating", "attending", "focusing"],
      "correct": 3,
      "lexical_rule": "attending to the household (сочетаемость с предлогом to)"
    }},
    {{
      "id": 34,
      "fipi_code": "2.3.1",
      "testing_type": "fixed_phrase",
      "options": ["taking", "keeping", "holding", "making"],
      "correct": 1,
      "lexical_rule": "taking care of (устойчивое сочетание)"
    }},
    {{
      "id": 35,
      "fipi_code": "2.3.2",
      "testing_type": "close_verbs",
      "options": ["recorded", "reminded", "recognized", "remembered"],
      "correct": 4,
      "lexical_rule": "remembered those days (вспоминала те дни по контексту памяти)"
    }},
    {{
      "id": 36,
      "fipi_code": "2.3.1",
      "testing_type": "verb_construction",
      "options": ["managed", "accomplished", "succeeded", "achieved"],
      "correct": 1,
      "lexical_rule": "managed to maintain (сочетаемость с инфинитивом с частицей to)"
    }}
  ]
}}""" + _COMMON
