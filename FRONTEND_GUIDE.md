# Frontend DataMarket - Guide d'intégration

## Installation rapide

```bash
npm install
npm run dev
```

Puis ouvrir : http://localhost:3000

## Arborescence du projet

```
app/                    # Pages Next.js App Router
components/             # Composants réutilisables
lib/
  ├── api/             # Services API et client HTTP
  ├── types.ts         # Types TypeScript
  ├── validation.ts    # Schémas Zod
  └── mock-data.ts     # Données de démonstration
public/                 # Assets statiques
```

## Variables d'environnement

Créez `.env.local` :

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
NEXT_PUBLIC_DEMO_MODE=true
```

## Architecture frontend

- **App Router** : navigation moderna avec segments optionnels
- **Design System** : tokens Tailwind + palette DataMarket
- **Composants** : modulaires, typés, réutilisables
- **API Layer** : client HTTP typé + fallback démonstration
- **Validation** : Zod pour tous les schémas

## Pages principales

| Route | Description |
|-------|-------------|
| `/` | Accueil public |
| `/dashboard` | Tableau de bord personnel |
| `/explore` | Explorateur de données |
| `/studies` | Études de marché |
| `/studies/new` | Créer une étude |
| `/territories` | Analyse territoriale |
| `/analyses` | Bibliothèque d'analyses |
| `/reports` | Espace de rapports |
| `/assistant` | Assistant IA |
| `/auth/login` | Connexion |
| `/profile` | Profil utilisateur |
| `/settings` | Paramètres |

## Composants clés

- `AppShell` : shell d'application + navigation
- `Sidebar`, `MobileNavigation` : navigation responsive
- `PageHeader` : en-tête de page unifié
- `DataTable` : tableau de données générique
- `MarketSizeChart`, `TimeSeriesChart` : graphiques Recharts
- `ProvenancePanel`, `AssumptionPanel`, `LimitationPanel` : métadonnées
- `Toast`, `ConfirmationDialog` : interactions utilisateur
- `EmptyState`, `LoadingState`, `ErrorState` : états de l'interface

## Mode démonstration

Quand `NEXT_PUBLIC_DEMO_MODE=true`, les données de démonstration sont utilisées avec des badges explicites "Mode démonstration" et des sources fictives clairement identifiées.

## Intégration backend

Le client API `lib/api/client.ts` se connectera au backend via `NEXT_PUBLIC_API_BASE_URL`. Les services dans `lib/api/services.ts` peuvent être adaptées au contrat API réel.

## Prochaines étapes

1. Valider le build : `npm run build`
2. Vérifier TypeScript : `npm run typecheck`
3. Lancer les tests : `npm test` (à ajouter)
4. Connecter le backend réel
5. Finaliser l'authentification
6. Ajouter les tests end-to-end

## Notes

- Le moteur métier Python existant reste la source de vérité
- Le frontend est un produit moderne et indépendant
- Les données de démonstration sont explicitement marquées
- Responsive design mobile, tablette, desktop
- Palette : marine #10233F, moutarde #D5A021, blanc #FFFFFF
