# Phase 27: UI Structure And SOLID Guardrails

## Objective

Improve the admin panel structure before moving to chat, and make the implementation follow basic SOLID principles more consistently.

## Required Work

- Centralize unauthenticated UI behavior.
- Show only the login interface when no access token exists.
- Remove duplicated login-required cards from feature pages.
- Separate unrelated page sections into tabs.
- Introduce reusable UI primitives where appropriate.
- Keep backend service responsibilities narrower.
- Document the design guardrails for upcoming phases.

## SOLID Guardrails

- Single Responsibility: route/page components compose workflows; auth gating belongs to the shell; tabs belong to a reusable UI component; analysis report projection belongs to its own module.
- Open/Closed: new page sections should be added as tab items instead of changing the tab component itself.
- Liskov Substitution: API schemas remain explicit contracts and should not require consumers to know implementation details.
- Interface Segregation: frontend clients expose focused API functions by domain.
- Dependency Inversion: feature views depend on small client functions and reusable UI primitives rather than direct infrastructure details.

## Out Of Scope

- Full backend repository refactor.
- Replacing the current auth model.
- Adding chat functionality.
