import re

# Read file
with open('backend/app/services/gemini_service.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern 1: Replace function call signature
pattern1 = r'self\._log_gemini_usage\(\s*db=self\.db,\s*provider="gemini",\s*model='
replacement1 = 'self._log_gemini_usage(\n                model='

pattern2 = r',\s*user_id=self\.user_id,\s*request_metadata=metadata'
replacement2 = ',\n                metadata=metadata'

content = re.sub(pattern1, replacement1, content)
content = re.sub(pattern2, replacement2, content)

# Write back
with open('backend/app/services/gemini_service.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed all log_usage calls")
