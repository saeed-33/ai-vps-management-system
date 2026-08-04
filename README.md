# AI VPS Management System

نظام لإدارة ومراقبة سيرفرات VPS عبر لوحة إدارة ووكيل ذكي مقيد بسياسات واضحة.

## الحالة الحالية

المشروع أنهى المرحلة الثالثة: قاعدة البيانات والنماذج الأساسية.

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
- `docs/stage-log.md`: سجل المراحل وما تم إنجازه.

## GitHub

المستودع مربوط بـ GitHub:

```text
https://github.com/saeed-33/ai-vps-management-system
```
