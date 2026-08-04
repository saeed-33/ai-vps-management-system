# المرحلة الثانية: تأسيس المشروع والمستودع

## الهدف

تحويل الوثائق المعمارية إلى مشروع عملي منظم وقابل للتطوير، مع تهيئة Git منذ البداية حتى تكون كل مرحلة موثقة بإصدارات واضحة.

## النطاق

هذه المرحلة لا تبني لوحة الإدارة أو الوكيل بعد. هدفها تجهيز الأرضية:

- مجلد مشروع مستقل.
- هيكل ملفات واضح.
- توثيق مرحلي.
- Git repository محلي.
- استعداد للربط مع GitHub.
- مكان واضح لكل خدمة مستقبلية.

## الهيكل المطلوب

```text
apps/
  admin-panel/
  api/
  agent/
  worker/
packages/
  shared-types/
  database/
  policy-core/
  mcp-contracts/
monitoring-profiles/
allowed-tools/
allowed-solutions/
docs/
infra/
sandbox/
tests/
```

## معايير الإنجاز

- وجود مجلد مشروع جديد.
- وجود README واضح.
- وجود `.gitignore`.
- وجود `.env.example`.
- وجود سجل مراحل `docs/stage-log.md`.
- وجود وثائق المرحلة الأولى داخل المشروع.
- تهيئة Git وإنشاء commit أول.
- توثيق حالة GitHub بوضوح.

## ملاحظات GitHub

إذا كانت GitHub CLI أو GitHub connector غير متاحة، يتم الاكتفاء بتجهيز المستودع المحلي وتوثيق الخطوة المتبقية بدقة.
