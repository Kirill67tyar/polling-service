import secrets

generated_key = secrets.token_hex(24)
print(f'\nSECRET_KEY={generated_key}')