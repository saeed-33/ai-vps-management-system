"use client";

import { useMutation } from "@tanstack/react-query";
import { LogIn } from "lucide-react";
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
      setMessage("تم تسجيل الدخول.");
      window.location.href = "/";
    },
    onError: () => {
      setMessage("تعذر تسجيل الدخول. تحقق من البريد وكلمة المرور.");
    },
  });

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage(null);
    loginMutation.mutate({ email, password });
  }

  return (
    <div className="login-page">
      <section className="login-panel">
        <article className="card login-card">
          <div className="toolbar">
            <div>
              <h2 className="section-title">تسجيل الدخول</h2>
              <p className="metric-note">أدخل بيانات حساب الإدارة للمتابعة.</p>
            </div>
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
      </section>
    </div>
  );
}
