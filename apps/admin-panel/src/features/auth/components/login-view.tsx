"use client";

import { useMutation } from "@tanstack/react-query";
import { LogIn, ShieldCheck } from "lucide-react";
import { FormEvent, useState } from "react";
import { loginWithPassword, storeAccessToken } from "@/lib/auth-client";

export function LoginView() {
  const [email, setEmail] = useState("admin@example.com");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState<string | null>(null);

  const loginMutation = useMutation({
    mutationFn: loginWithPassword,
    onSuccess: (token) => {
      storeAccessToken(token.access_token);
      setMessage("تم تسجيل الدخول وحفظ access token محليا.");
    },
    onError: () => {
      setMessage("تعذر تسجيل الدخول. تحقق من إعدادات bootstrap admin في Backend API.");
    },
  });

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage(null);
    loginMutation.mutate({ email, password });
  }

  return (
    <div className="page-stack">
      <section className="grid">
        <article className="card wide-card">
          <div className="toolbar">
            <div>
              <h2 className="section-title">تسجيل دخول المشرف الأولي</h2>
              <p className="metric-note">
                يستخدم Bootstrap Auth إلى أن يتم بناء إدارة المستخدمين والصلاحيات من قاعدة البيانات.
              </p>
            </div>
            <span className="badge neutral">Phase 6</span>
          </div>

          <form className="form-stack" onSubmit={handleSubmit}>
            <label className="field">
              <span>البريد الإلكتروني</span>
              <input
                dir="ltr"
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                required
              />
            </label>

            <label className="field">
              <span>كلمة المرور</span>
              <input
                dir="ltr"
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                required
              />
            </label>

            <button className="button primary" type="submit" disabled={loginMutation.isPending}>
              <LogIn aria-hidden="true" />
              {loginMutation.isPending ? "جاري الدخول" : "دخول"}
            </button>
          </form>

          {message ? (
            <p className={`notice ${loginMutation.isSuccess ? "success" : "danger"}`}>{message}</p>
          ) : null}
        </article>

        <article className="card side-card">
          <h2 className="section-title">متطلبات Backend</h2>
          <ul className="status-list">
            <li className="status-row">
              <div>
                <strong>AUTH_SECRET_KEY</strong>
                <span>قيمة طويلة وعشوائية لتوقيع JWT.</span>
              </div>
              <ShieldCheck aria-hidden="true" />
            </li>
            <li className="status-row">
              <div>
                <strong>BOOTSTRAP_ADMIN_EMAIL</strong>
                <span>البريد المسموح له بالدخول الأولي.</span>
              </div>
            </li>
            <li className="status-row">
              <div>
                <strong>BOOTSTRAP_ADMIN_PASSWORD_HASH</strong>
                <span>hash لكلمة المرور وليس النص الصريح.</span>
              </div>
            </li>
          </ul>
        </article>
      </section>
    </div>
  );
}
