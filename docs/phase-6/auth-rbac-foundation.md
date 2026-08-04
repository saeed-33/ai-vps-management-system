# تصميم Auth & RBAC Foundation

## الفكرة

نبدأ بأساس مصادقة بسيط وقابل للاستبدال لاحقا.

المستخدمون الفعليون موجودون في مخطط قاعدة البيانات، لكن endpoints إدارة المستخدمين لم تبن بعد. لذلك توفر هذه المرحلة bootstrap admin login يعتمد على environment variables.

## Backend

### الملفات

```text
apps/api/src/control_plane_api/core/security.py
apps/api/src/control_plane_api/schemas/auth.py
apps/api/src/control_plane_api/modules/auth/rbac.py
apps/api/src/control_plane_api/api/routes/auth.py
```

### Password Hashing

نستخدم PBKDF2-HMAC-SHA256 من مكتبة Python القياسية.

صيغة hash:

```text
pbkdf2_sha256$iterations$salt$hash
```

### JWT

نستخدم HS256 عبر مكتبة Python القياسية:

- `hmac`
- `hashlib`
- `base64`
- `json`

هذا يقلل الاعتماديات في البداية. يمكن لاحقا استبداله بمكتبة متخصصة إذا احتجنا خصائص أكثر.

### Bootstrap Login

`POST /api/v1/auth/token`

يتحقق من:

- email يساوي `BOOTSTRAP_ADMIN_EMAIL`.
- password يطابق `BOOTSTRAP_ADMIN_PASSWORD_HASH`.
- `AUTH_SECRET_KEY` مضبوط.

إذا لم تضبط القيم يرجع `503`.

### Current User

`GET /api/v1/auth/me`

يحتاج:

```text
Authorization: Bearer <token>
```

ويرجع principal يحتوي:

- subject.
- email.
- display name.
- roles.
- permissions.

## RBAC

المرحلة الحالية توفر catalog ثابت:

- roles.
- permissions.

الأدوار الأولية:

```text
owner
admin
operator
viewer
auditor
```

هذا catalog سيستخدم لاحقا لتعبئة قاعدة البيانات أو لمقارنة ما هو موجود فيها.

## Frontend

### الملفات

```text
apps/admin-panel/src/app/login/page.tsx
apps/admin-panel/src/features/auth/components/login-view.tsx
apps/admin-panel/src/lib/auth-client.ts
```

### السلوك

- تعرض صفحة login.
- تحفظ access token في `localStorage`.
- تعرض نتيجة الدخول.
- لا تطبق route protection كاملا بعد.

## القيود

- لا يوجد refresh token.
- لا يوجد logout server-side.
- لا يوجد session persistence في backend.
- لا يوجد user CRUD بعد.
- لا يستخدم جدول `users` بعد.

هذه القيود مقصودة حتى لا نبني نظام مصادقة كبير قبل بناء modules المستخدمين والصلاحيات.
