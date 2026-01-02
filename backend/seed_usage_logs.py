"""Seed sample AI usage logs for testing dashboard"""
import sys
from datetime import datetime, timedelta
from random import randint, uniform

sys.path.insert(0, 'D:\\Thang\\thang-phan-tools\\backend')
from app.core.database import SessionLocal
from app.models.models import AIUsageLog
from sqlalchemy import text

db = SessionLocal()

# Get provider key IDs
gemini_id = db.execute(text('SELECT id FROM ai_provider_keys WHERE provider=:provider'), {'provider': 'gemini'}).scalar()
claude_id = db.execute(text('SELECT id FROM ai_provider_keys WHERE provider=:provider'), {'provider': 'claude'}).scalar()
adobe_id = db.execute(text('SELECT id FROM ai_provider_keys WHERE provider=:provider'), {'provider': 'adobe'}).scalar()

logs = []

# Create 30 sample logs over the past 7 days
for i in range(30):
    days_ago = randint(0, 7)
    hours_ago = randint(0, 23)
    
    if i % 3 == 0:  # Gemini
        provider_id = gemini_id
        operation = ['chat', 'vision', 'text-generation'][i % 3]
        model = 'gemini-2.5-flash'
        input_tokens = randint(100, 2000)
        output_tokens = randint(50, 1500)
        total_tokens = input_tokens + output_tokens
        input_cost = input_tokens * 0.00001875 / 1000  # $0.01875 per 1M tokens
        output_cost = output_tokens * 0.0000375 / 1000  # $0.0375 per 1M tokens
    elif i % 3 == 1:  # Claude
        provider_id = claude_id
        operation = ['chat', 'analysis'][i % 2]
        model = 'claude-3-5-sonnet'
        input_tokens = randint(200, 3000)
        output_tokens = randint(100, 2000)
        total_tokens = input_tokens + output_tokens
        input_cost = input_tokens * 0.003 / 1000  # $3 per 1M tokens
        output_cost = output_tokens * 0.015 / 1000  # $15 per 1M tokens
    else:  # Adobe
        provider_id = adobe_id
        operation = 'pdf-processing'
        model = 'adobe-pdf-services'
        input_tokens = 0
        output_tokens = 0
        total_tokens = 0
        input_cost = 0.02  # Fixed cost per operation
        output_cost = 0
    
    log = AIUsageLog(
        provider_key_id=provider_id,
        user_id=1,
        operation=operation,
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        input_cost=input_cost,
        output_cost=output_cost,
        total_cost=input_cost + output_cost,
        processing_time_ms=uniform(100, 3000),
        status='success',
        created_at=datetime.utcnow() - timedelta(days=days_ago, hours=hours_ago)
    )
    logs.append(log)

db.add_all(logs)
db.commit()
db.close()

print('✅ Created 30 sample usage logs!')
print(f'   Gemini: 10 logs')
print(f'   Claude: 10 logs')
print(f'   Adobe: 10 logs')
print(f'   Total cost: ~${sum(log.total_cost for log in logs):.4f}')
