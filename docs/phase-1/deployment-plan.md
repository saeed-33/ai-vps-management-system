# خطة النشر الأولية

## بيئة التطوير

```text
Docker Compose
PostgreSQL + pgvector
Redis
API
Agent
Worker
Admin Panel
```

## بيئة الإنتاج الأولى

يمكن البدء على VPS واحد أو أكثر:

```text
reverse proxy
admin panel
api
agent
worker
postgres
redis
storage
backup jobs
```

## الأسرار

لا تحفظ الأسرار كنص عادي في قاعدة البيانات:

- مفاتيح SSH.
- Telegram bot token.
- API keys.
- مفاتيح التشفير.

في MVP يمكن استخدام `.env` محمي، ولاحقا Secrets Manager.

## النسخ الاحتياطي

- نسخ PostgreSQL يوميا.
- نسخ storage للتقارير والوثائق.
- اختبار الاسترجاع دوريا.

## ما يؤجل

- Kubernetes.
- multi-region.
- execution agents ذات صلاحيات عالية.
- auto-remediation كامل.
