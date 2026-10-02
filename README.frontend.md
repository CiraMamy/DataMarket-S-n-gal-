# DataMarket Frontend

Ce dépôt contient désormais un frontend Next.js de type App Router préparé pour DataMarket.

## Stack

- Next.js 14 App Router
- React 18
- TypeScript strict
- Tailwind CSS
- Recharts
- Lucide Icons
- React Hook Form + Zod
- TanStack Query

## Lancement local

```bash
npm install
npm run dev
```

Puis ouvrir : http://localhost:3000

## Variables d’environnement

Créez un fichier `.env.local` :

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
NEXT_PUBLIC_DEMO_MODE=true
```

## Ce qui est prêt

- Page d’accueil marketing DataMarket
- Tableau de bord personnel
- Explorer les données
- Création d’une étude de marché
- Pages territoires, analyses, rapports et assistant IA
- Navigation responsive et design system
- Données de démonstration clairement signalées

## Ce qui reste dépendant du backend

- Authentification réelle
- Accès aux API de production
- Données en temps réel
- Contrats backend complets
- Gestion réelle des documents et des exports

## Notes

Le moteur métier Python existant est conservé comme source de vérité. Le frontend est conçu comme une couche d’exploitation moderne et exploitable, avec des données de démonstration identifiées et un adaptateur API typé.
