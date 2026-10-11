from prompt_common import _COMMON

PROMPT_2_STATEMENTS = """Ты — эксперт-составитель заданий ЕГЭ по английскому языку, работающий в ФИПИ.
Твоя задача — разработать каркас для задания 2 раздела «Аудирование» (7 утверждений A–G с ключами).

Тема: {TOPIC}

=== КРИТИЧЕСКИ ВАЖНО: ИМЕНА ПЕРСОНАЖЕЙ ===
СНАЧАЛА придумай ДВА англоязычных имени для будущего диалога — одно мужское, одно женское.
- НЕ Ben, НЕ Sophie, НЕ Maya, НЕ Oliver (это из примеров).
- Используй другие популярные имена: Harry, Tom, Emma, Kate, Lily, Daniel, Jack, Chloe, Megan, Ryan.
Запиши их в поля "speaker_1_name" и "speaker_2_name".
ВСЕ утверждения ниже должны ссылаться ТОЛЬКО на эти два имени. Никаких третьих лиц.

=== ТРЕБОВАНИЯ К СЕТКЕ ===
1. Ровно 7 утверждений A–G.
2. Все — про этих двух персонажей.
3. Распределение ответов строго по критериям ФИПИ:
   - True (1): 2–3 утверждения.
   - False (2): 2–3 утверждения.
   - Not Stated (3): 1–2 утверждения.
4. Логика для False: подмени деталь, время, причину или намерение — чтобы в диалоге можно было однозначно опровергнуть.
5. Логика для Not Stated: тема близка к контексту, но конкретный факт (место, опыт, отношение) не упоминается.
6. Каждое — одно предложение. Британский английский.
7. НЕ использовать игровые механики.

Верни ТОЛЬКО JSON:
{{
  "speaker_1_name": "Harry",
  "speaker_2_name": "Chloe",
  "statements": [
    {{"letter": "A", "text": "Harry first heard about the cooking course from a colleague.", "target_answer": 1}},
    {{"letter": "B", "text": "The cooking course takes place on Saturday mornings.", "target_answer": 2}},
    {{"letter": "C", "text": "Chloe has attended a similar cooking course before.", "target_answer": 3}},
    {{"letter": "D", "text": "They plan to register for the course online before Friday.", "target_answer": 1}},
    {{"letter": "E", "text": "The course fee includes all the ingredients they will need.", "target_answer": 2}},
    {{"letter": "F", "text": "Chloe wants to join the course mainly to improve her professional cooking skills.", "target_answer": 3}},
    {{"letter": "G", "text": "There is a car park at the venue where the course is held.", "target_answer": 1}}
  ]
}}""" + _COMMON