from prompt_common import _COMMON

PROMPT_37_STIMULUS_SCHEMA = """Ты — эксперт-составитель ЕГЭ по английскому языку (ФИПИ).
Разработай каркас для задания 37 (электронное письмо).

Тема: {TOPIC}

=== ПЕРСОНАЖ ===
Популярное англоязычное имя друга по переписке (НЕ Sophia, НЕ Ben). Например: Megan, Chloe, Oliver, Ethan, Emily.

=== ПРОЕКТНЫЙ КОНТЕКСТ ===
ОДНО предложение: почему друг задаёт вопросы (пишет школьный проект, готовит презентацию, изучает тему).

=== 3 ВОПРОСА ===
Чёткие, конкретные, требуют развёрнутых ответов. НЕ yes/no.
- Вопрос 1: факт, текущее положение дел, личный опыт ученика.
- Вопрос 2: мероприятия, традиции, общественное мнение, ситуация в России.
- Вопрос 3: личное отношение, планы или совет ученика.
Если тема Р (Родная страна) или С (Выдающиеся люди) — вопросы привязаны к культурным/историческим особенностям России.
⚠️ НЕ используй повторы одного слова (famous, famous, famous). Применяй синонимы (well-known, notable, prominent).
⚠️ Уровень B1 — вопросы короткие и понятные. НЕ используй "perseverance", "in terms of", "dedication".

=== ЛИЧНАЯ НОВОСТЬ ===
1 предложение о событии в жизни друга.
НЕ связана с основной темой {TOPIC}.
Конкретная, даёт повод задать 3 разных вопроса.
Примеры: "I've joined a local volunteer group", "I've started taking violin lessons", "My family has adopted a puppy".

=== СУЩНОСТЬ ДЛЯ ИНСТРУКЦИИ ===
В поле news_topic_for_instruction — СУЩЕСТВИТЕЛЬНОЕ, а НЕ действие:
- "I've joined a volunteer group" → "the volunteer group" ✅
- "I've started taking violin lessons" → "the violin lessons" ✅ (НЕ "learning the violin")
- "My family adopted a puppy" → "the puppy" ✅

=== ФОРМАТ ВЫВОДА ===
ТОЛЬКО JSON-объект:

{{
  "sender_name": "Megan",
  "subject_line": "Famous people project",
  "project_context": "I'm preparing a presentation about famous people from different countries and their impact on society.",
  "questions": [
    {{"id": 1, "text": "Can you tell me about a famous Russian person who has made significant contributions to their field?"}},
    {{"id": 2, "text": "How are the achievements of such people celebrated or remembered in Russia?"}},
    {{"id": 3, "text": "What can young people learn from the lives of such people?"}}
  ],
  "personal_news": "I've just started learning to play the violin.",
  "news_topic_for_instruction": "the violin lessons"
}}""" + _COMMON