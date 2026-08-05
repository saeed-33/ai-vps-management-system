# تصميم Users & Roles Foundation

## الفكرة

ننتقل تدريجيا من bootstrap auth إلى إدارة مستخدمين فعلية.

في هذه المرحلة، مصدر المستخدمين ليس قاعدة البيانات بعد. نعرض المستخدم الحالي المستخرج من token كمستخدم bootstrap، ونستعمل RBAC catalog الحالي لعرض الأدوار والصلاحيات.

## Backend

### الملفات

```text
apps/api/src/control_plane_api/schemas/users.py
apps/api/src/control_plane_api/modules/users/service.py
apps/api/src/control_plane_api/api/routes/users.py
apps/api/tests/test_users.py
```

### endpoints

```text
GET /api/v1/users
GET /api/v1/users/me
GET /api/v1/users/roles
```

كل endpoint يحتاج:

```text
Authorization: Bearer <token>
```

## Frontend

### الملفات

```text
apps/admin-panel/src/app/users/page.tsx
apps/admin-panel/src/features/users/components/users-view.tsx
apps/admin-panel/src/lib/users-client.ts
```

## القيود

- البيانات مؤقتة وليست من PostgreSQL.
- لا يوجد create/update/delete.
- لا يتم تعديل RBAC catalog من الواجهة.

هذه القيود مقصودة. الهدف هو تثبيت المسار بين الواجهة والـ Backend قبل إضافة persistence.
