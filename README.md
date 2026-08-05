# AI VPS Management System

نظام لإدارة ومراقبة سيرفرات VPS عبر لوحة إدارة ووكيل ذكي مقيد بسياسات واضحة.

## الحالة الحالية

المشروع أنهى المرحلة التاسعة: Monitoring Profiles Management Foundation.

## القرارات الأساسية

- لا يوجد RLHF في المرحلة الحالية.
- لا نبدأ بمودل متخصص لتقارير المراقبة.
- التنفيذ على السيرفرات ممنوع افتراضيا.
- المراقبة الدورية تنشئ وكيلا فرعيا لكل سيرفر.
- الوكلاء المتخصصون يعرفون من لوحة الإدارة ويعملون عند الحاجة.
- الحلول تختبر أو تحاكى في sandbox قبل عرضها على المستخدم.

## الهيكل العام

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

## التوثيق

- `docs/phase-1/`: وثائق تثبيت النطاق والبنية.
- `docs/phase-2/`: وثائق تأسيس المشروع والمستودع.
- `docs/phase-3/`: وثائق قاعدة البيانات والنماذج الأساسية.
- `docs/phase-3/database-schema-guide.md`: مخطط قاعدة البيانات وشرح الجداول.
- `docs/phase-3/docker-guide.md`: شرح Docker Compose وخدمات التطوير.
- `docs/phase-4/`: وثائق أساس Backend API / Control Plane.
- `docs/phase-5/`: وثائق أساس لوحة الإدارة.
- `docs/phase-6/`: وثائق أساس المصادقة والصلاحيات.
- `docs/phase-7/`: وثائق أساس إدارة المستخدمين والأدوار.
- `docs/phase-8/`: وثائق أساس إدارة السيرفرات.
- `docs/phase-9/`: وثائق أساس إدارة ملفات المراقبة.
- `docs/architecture-decisions/`: قرارات معمارية موثقة للبنية.
- `docs/stage-log.md`: سجل المراحل وما تم إنجازه.

## تشغيل API

```bash
cd apps/api
uv sync --extra dev
uv run uvicorn control_plane_api.main:app --reload --host 127.0.0.1 --port 8000
```

## اختبار API

```bash
cd apps/api
uv run pytest
```

## تشغيل لوحة الإدارة

```bash
cd apps/admin-panel
npm install --no-audit --no-fund --ignore-scripts
npm run dev
```

لوحة الإدارة تعمل على:

```text
http://127.0.0.1:3000
```

## إنشاء Bootstrap Admin Password Hash

```bash
cd apps/api
uv run python scripts/hash_password.py
```

## GitHub

المستودع مربوط بـ GitHub:

```text
https://github.com/saeed-33/ai-vps-management-system
```
