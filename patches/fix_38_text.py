# patches/fix_38_text.py
PATCH_NAME = "Fix task 38.1/38.2: rebuild task_text server-side"
PATCH_DESCRIPTION = "Ignores LLM task_text for 38; always builds from schema. Prevents data duplication."

OLD_381 = """    task_text = r2.get("formatted_task") or r2.get("task_text") or ""
    HEADER = ("Choose only ONE of the two given tasks (38.1 or 38.2), indicate its number "
              "in ANSWER SHEET NO. 2 and complete it according to the plan. In your answer "
              "to task 38, write numerals in digits.")
    if not task_text.strip():
        task_text = (HEADER + "\\n\\n[38.1]\\n\\n"
                     f"Imagine that you are doing a project on {schema.get('project_subject','')} in Zetland. "
                     f"You have found some data on the subject – the results of a survey conducted among "
                     f"{schema.get('survey_audience','')} (see the table below).\\n"
                     "Comment on the survey data and give your opinion on the subject of the project.")
    elif "Choose only ONE" not in task_text:
        task_text = HEADER + "\\n\\n" + task_text
"""

NEW_381 = """    HEADER = ("Choose only ONE of the two given tasks (38.1 or 38.2), indicate its number "
              "in ANSWER SHEET NO. 2 and complete it according to the plan. In your answer "
              "to task 38, write numerals in digits.")
    task_text = (HEADER + "\\n\\n[38.1]\\n\\n"
                 f"Imagine that you are doing a project on {schema.get('project_subject','')} in Zetland. "
                 f"You have found some data on the subject – the results of a survey conducted among "
                 f"{schema.get('survey_audience','')} (see the table below).\\n"
                 "Comment on the survey data and give your opinion on the subject of the project.")
"""

OLD_382 = """    task_text = r2.get("formatted_task") or r2.get("task_text") or ""
    HEADER = ("Choose only ONE of the two given tasks (38.1 or 38.2), indicate its number "
              "in ANSWER SHEET NO. 2 and complete it according to the plan. In your answer "
              "to task 38, write numerals in digits.")
    if not task_text.strip():
        task_text = (HEADER + "\\n\\n[38.2]\\n\\n"
                     f"Imagine that you are doing a project on {schema.get('project_subject','')} in Zetland. "
                     f"You have found some data on the subject – the results of a survey conducted among "
                     f"{schema.get('survey_audience','')} (see the pie chart below).\\n"
                     "Comment on the survey data and give your opinion on the subject of the project.")
    elif "Choose only ONE" not in task_text:
        task_text = HEADER + "\\n\\n" + task_text
"""

NEW_382 = """    HEADER = ("Choose only ONE of the two given tasks (38.1 or 38.2), indicate its number "
              "in ANSWER SHEET NO. 2 and complete it according to the plan. In your answer "
              "to task 38, write numerals in digits.")
    task_text = (HEADER + "\\n\\n[38.2]\\n\\n"
                 f"Imagine that you are doing a project on {schema.get('project_subject','')} in Zetland. "
                 f"You have found some data on the subject – the results of a survey conducted among "
                 f"{schema.get('survey_audience','')} (see the pie chart below).\\n"
                 "Comment on the survey data and give your opinion on the subject of the project.")
"""


def is_applied(src):
    return (OLD_381 not in src
            and OLD_382 not in src
            and "r2.get(\"formatted_task\") or r2.get(\"task_text\")" not in src)


def apply(src):
    if OLD_381 in src:
        src = src.replace(OLD_381, NEW_381, 1)
    if OLD_382 in src:
        src = src.replace(OLD_382, NEW_382, 1)
    if OLD_381 in src or OLD_382 in src:
        raise ValueError("Failed to replace one of the blocks")
    return src
