# تصميم Servers Foundation

## الفكرة

نحتاج صفحة وAPI للسيرفرات قبل بناء المراقبة الدورية. في هذه المرحلة نستخدم بيانات مؤقتة داخل service، لكن contracts مصممة لتطابق جدول `servers` لاحقا.

## Backend

### الملفات

```text
apps/api/src/control_plane_api/schemas/servers.py
apps/api/src/control_plane_api/modules/servers/service.py
apps/api/src/control_plane_api/api/routes/servers.py
apps/api/tests/test_servers.py
```

### endpoints

```text
GET /api/v1/servers
GET /api/v1/servers/summary
GET /api/v1/servers/{server_id}
```

كل endpoint يحتاج:

```text
Authorization: Bearer <token>
```

وصلاحية:

```text
servers.read
```

## Frontend

### الملفات

```text
apps/admin-panel/src/app/servers/page.tsx
apps/admin-panel/src/features/servers/components/servers-view.tsx
apps/admin-panel/src/lib/servers-client.ts
```

## القيود

- البيانات مؤقتة وليست من PostgreSQL.
- لا يوجد create/update/delete.
- لا يوجد SSH أو credentials.
- لا يوجد اختبار اتصال فعلي.

هذه القيود مقصودة حتى يتم بناء repository layer وsecrets handling قبل أي اتصال حقيقي بالسيرفرات.
