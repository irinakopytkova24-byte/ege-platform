from prompt_common import _COMMON

PROMPT_11_FRAGMENTS = """Ты — эксперт-составитель заданий ЕГЭ по английскому языку, работающий в ФИПИ.
Твоя задача — разработать тестовый каркас (7 фрагментов предложений 1–7 и их ключи) для задания 11 раздела «Чтение».

Тема: {TOPIC}

=== ЖЁСТКИЕ МЕТОДИЧЕСКИЕ ТРЕБОВАНИЯ К ФРАГМЕНТАМ ===
1. Количество: Ровно 7 фрагментов предложений, пронумерованных от 1 до 7. 6 из них займут места пропусков A–F, 1 останется лишним.
2. Формат: Каждый фрагмент должен быть частью предложения, а не законченным самостоятельным предложением. Начинай фрагменты со строчной (маленькой) буквы. Длина варьируется от 3 до 12 слов.
3. Разнообразие грамматических структур (распредели типы между фрагментами):
   - Определительное придаточное (which / that / who + глагольная группа)
   - Причастный оборот (на -ing или -ed: forming..., based on..., situated in...)
   - Союзная конструкция (придаточные времени, причины или уступки: although..., because..., since..., while...)
   - Инфинитивная конструкция цели (to prevent..., to develop..., to study...)
   - Предложная фраза (including..., according to..., despite...)
   - Приложение (существительное с пояснением: a traditional event, a key factor)
4. Языковой стандарт: Лексика уровня B1+, орфография строго британская (British English): organised, programmes, favouring.
5. Лишний фрагмент (extra_fragment): Должен быть грамматически правдоподобным (например, начинаться с which или причастия), чтобы его теоретически можно было примерить к тексту, но по смыслу и контексту он не должен подходить ни в один из будущих пропусков.
6. Строгий запрет на геймификацию: Никаких шуток, игровых элементов, загадок. Контекст должен быть строго научно-популярным и реалистичным.

Верни ТОЛЬКО JSON-объект (без markdown-разметки ```json и без вводных комментариев):
{{
  "fragments": [
    {{
      "number": 1,
      "grammar_type": "relative_clause",
      "text": "which plays an essential role in development",
      "is_extra": false
    }},
    {{
      "number": 2,
      "grammar_type": "participle_clause",
      "text": "allowing young people to acquire key skills",
      "is_extra": false
    }},
    {{
      "number": 3,
      "grammar_type": "conjunction_clause",
      "text": "although many experts disagree with this approach",
      "is_extra": true
    }},
    {{
      "number": 4,
      "grammar_type": "infinitive_purpose",
      "text": "to achieve better cultural integration",
      "is_extra": false
    }},
    {{
      "number": 5,
      "grammar_type": "prepositional_phrase",
      "text": "despite the financial difficulties they face",
      "is_extra": false
    }},
    {{
      "number": 6,
      "grammar_type": "apposition",
      "text": "a fundamental aspect of modern education",
      "is_extra": false
    }},
    {{
      "number": 7,
      "grammar_type": "relative_clause",
      "text": "who participate in these community projects",
      "is_extra": false
    }}
  ]
}}""" + _COMMON
