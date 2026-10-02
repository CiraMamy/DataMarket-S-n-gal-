# DataMarket frontend

## Architecture

- App Router Next.js
- TypeScript strict
- Tailwind CSS
- Design system DataMarket
- API client + mock fallback

## Types et services

Les services de données sont centralisés dans `lib/api`. Le client HTTP gère les erreurs, et le mode démonstration est activé par `NEXT_PUBLIC_DEMO_MODE=true`.

## Routes principales

- `/`
- `/dashboard`
- `/explore`
- `/studies`
- `/studies/new`
- `/territories`
- `/analyses`
- `/reports`
- `/assistant`
- `/auth/login`
- `/profile`
- `/settings`

## Données de démonstration

Toutes les données de cette base sont marquées comme démonstration et doivent être remplacées par des données tierces validées via le backend.
