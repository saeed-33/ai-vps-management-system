# تصميم أساس لوحة الإدارة

## دور لوحة الإدارة

لوحة الإدارة هي واجهة التحكم والعرض. لا تنفذ أوامر مباشرة على السيرفرات، ولا تقرر صلاحيات التنفيذ وحدها. كل العمليات الحساسة تمر عبر Backend / Control Plane.

## البنية

```text
apps/admin-panel/
  src/
    app/
    components/
    features/
    lib/
    types/
```

## الطبقات

### `app`

مسؤولة عن routing والصفحات العامة باستخدام Next.js App Router.

### `components`

مكونات مشتركة لا تنتمي إلى feature واحدة، مثل:

- layout.
- sidebar.
- status badge.
- cards.

### `features`

كل مجال مستقل يوضع هنا.

أمثلة:

```text
features/dashboard
features/system-status
features/servers
features/specialist-agents
```

### `lib`

أدوات مشتركة:

- API client.
- routes.
- formatting.

### `types`

أنواع مشتركة على مستوى الواجهة.

## الصفحات الأولية

```text
/
/api-status
```

`/` تعرض dashboard أولي.

`/api-status` تعرض اتصال لوحة الإدارة بالـ Backend:

- liveness.
- metadata.
- رابط API المستخدم.

## قواعد تصميم الواجهة

- واجهة تشغيل عملية وليست landing page.
- Sidebar واضح.
- Top bar بسيط.
- معلومات كثيفة لكن منظمة.
- ألوان هادئة.
- لا hero sections.
- لا زخارف غير ضرورية.
- التركيز على قابلية التوسع والإدارة.
