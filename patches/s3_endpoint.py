# patches/s3_endpoint.py
PATCH_NAME = "Configurable S3 endpoint + storage sanity check"
PATCH_DESCRIPTION = "STORAGE_ENDPOINT/STORAGE_REGION env vars; logger warns when creds missing."

CFG_OLD = 'BUCKET_NAME    = os.getenv("STORAGE_BUCKET", "ege-tasks-bank")'
CFG_NEW = (
    'BUCKET_NAME    = os.getenv("STORAGE_BUCKET", "ege-tasks-bank")\n'
    'STORAGE_ENDPOINT = os.getenv("STORAGE_ENDPOINT", "https://storage.yandexcloud.net")\n'
    'STORAGE_REGION   = os.getenv("STORAGE_REGION", "ru-central1")'
)

S3_OLD = (
    'def _s3():\n'
    '    return boto3.client(\n'
    '        "s3",\n'
    '        endpoint_url="https://storage.yandexcloud.net",\n'
    '        aws_access_key_id=STORAGE_KEY_ID,\n'
    '        aws_secret_access_key=STORAGE_SECRET,\n'
    '        config=Config(signature_version="s3v4"),\n'
    '        region_name="ru-central1",\n'
    '    )'
)
S3_NEW = (
    'def _s3():\n'
    '    if (not STORAGE_KEY_ID) or STORAGE_KEY_ID == "placeholder":\n'
    '        print("[s3] WARNING: STORAGE_KEY_ID not set — storage calls will fail.")\n'
    '    return boto3.client(\n'
    '        "s3",\n'
    '        endpoint_url=STORAGE_ENDPOINT,\n'
    '        aws_access_key_id=STORAGE_KEY_ID,\n'
    '        aws_secret_access_key=STORAGE_SECRET,\n'
    '        config=Config(signature_version="s3v4"),\n'
    '        region_name=STORAGE_REGION,\n'
    '    )'
)

JS_OLD = "    document.getElementById('draftHint').textContent = '⚠ Не удалось сохранить';"
JS_NEW = (
    "    document.getElementById('draftHint').textContent = '⚠ Не удалось сохранить: ' + e.message;\n"
    "    console.error('[saveDraft]', e);"
)


def is_applied(src):
    return "STORAGE_ENDPOINT" in src and "def _s3():" in src


def apply(src):
    if CFG_OLD not in src:
        raise ValueError("Config line not found")
    src = src.replace(CFG_OLD, CFG_NEW, 1)

    if S3_OLD not in src:
        raise ValueError("_s3() block not found")
    src = src.replace(S3_OLD, S3_NEW, 1)

    if JS_OLD in src:
        src = src.replace(JS_OLD, JS_NEW, 1)

    return src
