# EURO-STAT

Full-stack EuroMillions statistics app.

- **`euro-stat-BE`** — FastAPI + MongoDB + Google Drive (Python 3.12)
- **`euro-stat-FE`** — React 19 + TypeScript + Vite + Tailwind + ApexCharts

The backend extracts draw data from Google Drive, stores it in MongoDB and
exposes aggregated statistics/charts. The frontend renders those statistics
in dashboards and per-chart pages.

## Project layout

```
euro-stat-BE/
  app/
    core/         # configuration
    db/           # Mongo client + collection helpers
    models/       # Pydantic schemas
    repositories/ # data access
    services/     # business logic (aggregation, parsing, Drive, charts, ...)
    api/          # FastAPI router (all /api endpoints)
    main.py       # app factory (app.main:app)
  scripts/        # one-off maintenance scripts
  tests/          # pytest suite
euro-stat-FE/
  src/
    components/charts/  # generic BarChart + ChartPage + chart configs
    services/           # API layer (src/services/api.ts, src/services/*)
    config.ts           # API base URL
```

## Prerequisites

- Python 3.12+
- Node.js 20+
- MongoDB (local or via Docker)

## Backend (local)

```bash
cd euro-stat-BE
python -m venv .venv
.venv\Scripts\activate            # Windows
# source .venv/bin/activate       # Linux/macOS
pip install -r requirements.txt
py -m uvicorn app.main:app --reload
```

The API is served at http://localhost:8000 (interactive docs at `/docs`).
Importing the app does **not** connect to MongoDB or Google Drive; those
connections are lazy.

### Tests

```bash
pip install -r requirements-dev.txt
py -m pytest
```

### Google Drive

Drop a Google service-account file at `euro-stat-BE/credentials.json`
(override the path with `GOOGLE_CREDENTIALS_FILE`). The file is git-ignored.

## Frontend (local)

```bash
cd euro-stat-FE
npm install
npm run dev
```

The dev server runs at http://localhost:5173 and talks to the backend using
`VITE_API_URL` (defaults to `http://localhost:8000`). Copy `.env.example` to
`.env` to override it.

```bash
npm run build     # type-check + production build
npm run lint      # eslint
```

## Environment variables

See the root `.env.example` and `euro-stat-FE/.env.example`.

| Variable | Default | Used by |
| --- | --- | --- |
| `MONGO_URL` | `mongodb://localhost:27017` | backend |
| `MONGO_DB` | `euro_stat_db` | backend |
| `MONGO_COLLECTION_NUMBERS` | `numbers_full` | backend |
| `MONGO_COLLECTION_STARS` | `stars_full` | backend |
| `MONGO_COLLECTION_DRAW_DATA` | `draw_data` | backend |
| `DRIVE_DATA_FOLDER_ID` | *(built-in folder id)* | backend |
| `GOOGLE_CREDENTIALS_FILE` | `credentials.json` | backend |
| `CORS_ORIGINS` | localhost dev origins | backend |
| `VITE_API_URL` | `http://localhost:8000` | frontend |

> The `MONGO_URL` default has no credentials (local dev). Docker Compose
> provides a credentialed URL via `MONGO_URL`.

## Docker

```bash
docker compose up --build
```

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- MongoDB: localhost:27018 (root credentials default to `admin` / `admin123`)

Override defaults by creating a `.env` at the repository root (see
`.env.example`).

### Frontend : mode développement (hot reload)

Par défaut, `docker compose up -d` démarre le frontend en **mode dev**
(`euro-stat-FE/Dockerfile.dev`) : le serveur Vite tourne dans le conteneur
avec le dossier `src/` monté depuis l'hôte (`./euro-stat-FE:/app`). Modifiez
un fichier (`src/pages/Home.tsx`, `src/components/...`, ...) et la page se
recharge automatiquement dans le navigateur, **sans rebuild ni redémarrage**.

- La détection de fichiers utilise le **polling** (`usePolling`) car le file
  watching natif ne fonctionne pas avec Docker Desktop/Windows.
- `node_modules` vit dans le volume nommé `fe_node_modules` (les dépendances
  ne sont pas écrasées par le dossier hôte).
- Après une modification de `package.json`, réinstallez les dépendances :
  `docker compose exec euro_stat_fe npm install`.

Le `Dockerfile` d'origine (build Vite + nginx) reste disponible pour servir
une image statique de production.

## Maintenance scripts

```bash
cd euro-stat-BE
py -m scripts.migrate_legacy_ids   # migrate legacy draw ids
```

## Dashboard des numéros — signification des graphes

Page : http://localhost:5173/dashboard-numbers

**Contrôle global** : le curseur en haut à droite (1 à 100) choisit le nombre de
*derniers tirages* N pris en compte par tous les graphes. Chaque graphe possède
son propre curseur local (bouton **Use global** pour revenir à la valeur
globale). Les axes Y indiquent toujours un **nombre de boules** (parmi les
5 numéros tirés × N tirages) ou un **nombre de tirages**, selon le graphe.

### Colonne de gauche

1. **Sorties** (`chart-out`)
   - Distribution du **nombre d'apparitions historiques** (« sorties ») des
     5 boules tirées sur les N derniers tirages.
   - Lecture : une barre « 15 » à hauteur 12 signifie que 12 boules tirées
     récemment étaient apparues exactement 15 fois dans toute l'histoire.

2. **Fréquence récente** (`chart-recent-frequency`)
   - Distribution de la **fréquence récente** (en %) des boules tirées sur la
     période courante.
   - Lecture : une barre « 10 » à hauteur 8 signifie que 8 boules tirées
     avaient une fréquence récente d'environ 10 %.

3. **Fréquence** (`chart-frequency`)
   - Pour chaque tirage, les fréquences (%) des 5 boules sont regroupées dans
     des **tranches entières** puis résumées en une combinaison, ex. `4x2 | 5x3`
     (= 2 boules avec une fréquence entre 4 et 5, 3 boules entre 5 et 6).
   - Lecture : une barre `4x2 | 5x3` à hauteur 6 signifie que 6 tirages (parmi
     les N) présentaient ce profil de fréquence. C'est le **profil type de
     fréquences** des tirages.

### Colonne de droite

4. **Rapports** (`chart-report`)
   - Distribution du **rapport moyen** (gain moyen d'une boule sur l'histoire,
     ex. `1,35`) des boules tirées.
   - Lecture : répartition des boules tirées selon leur rapport moyen.

5. **Progression** (`chart-progression`)
   - Distribution de l'**évolution** de chaque boule : `+200%`, `=`, `-100%`, ...
   - Lecture : une barre `=` à hauteur 9 signifie que 9 boules tirées étaient
     stables; une barre haute `+…` indique un nombre élevé de boules en hausse.

6. **Fréquence période précédente** (`chart-frequency-previous-period`)
   - Distribution de la **fréquence (%) sur la période précédente** des boules
     tirées.
   - Lecture : à comparer avec Fréquence récente / Fréquence pour apprécier
     l'évolution d'une période à l'autre.

7. **Retards** (`chart-delay`)
   - Distribution du **retard** de chaque boule tirée = nombre de tirages
     écoulés depuis sa dernière sortie (0 = la boule sort au tirage courant).
   - Lecture : les décalages faibles (0 à 5) sont les plus courants
     (numéros « chauds ») ; les valeurs élevées signalent des numéros « froids ».

8. **Tranches des retards** (`chart-delay-range`)
   - Pour chaque tirage, les 5 retards sont regroupés en tranches `[0-5]`
     / `[6-10]` / `[11+]` et résumés en une combinaison,
     ex. `[0-5]x2 | [6-10]x3` (= 2 boules retard 0-5 et 3 boules retard 6-10).
   - Lecture : une barre haute sur `[0-5]xN` indique des tirages riches en
     numéros récemment sortis.

9. **Tranches de sorties** (`chart-out-range`)
   - Pour chaque tirage, les 5 « sorties » sont regroupées en **tranches de
     10** (`[0-9]`, `[10-19]`, `[20-29]`, ...) et résumées en une combinaison,
     ex. `[10-19]x2 | [30-39]x3`.
   - Lecture : une barre haute sur `[20-39]xN` signale des tirages composés de
     numéros déjà fréquemment sortis.

> Ces graphes sont de **l'analyse descriptive a posteriori** : ils décrivent un
> historique (fréquences, retards, sorties, rapports) et n'ont aucune valeur
> prédictive sur le résultat d'un tirage futur.

## Page des données numéros — signification de l'affichage

Page : http://localhost:5173/data-numbers

Cette page expose, pour **une date de tirage choisie**, les statistiques
historiques de chacune des 50 boules (numéros 1 à 50). C'est l'équivalent
tableau des graphes du dashboard : on y consulte le détail boule par boule.

**Utilisation** : saisir une date au format `JJ-MM-AAAA` (la date du jour est
pré-remplie) puis cliquer **Exécuter**. Les données sont lues depuis le cache
MongoDB, ou récupérées puis parsées depuis Google Drive si elles manquent.

### Colonnes du tableau (1 ligne = 1 boule)

| Colonne | Signification |
| --- | --- |
| **Numéro** | Le numéro de la boule (1 à 50). |
| **Fréquence** | Taux de sortie de la boule sur l'ensemble de l'histoire (%). |
| **Retard** | Nombre de tirages écoulés depuis la dernière sortie de la boule (0 = sortie au tirage courant). Plus la valeur est élevée, plus la boule est « froide ». |
| **Progression** | Évolution de la fréquence entre deux périodes : `+…%` (en hausse), `=`, `-…%` (en baisse). |
| **Fréq_Récente** | Taux de sortie de la boule sur la période récente (%). |
| **Fréq_Période_Préc** | Taux de sortie de la boule sur la période précédente (%). À confronter à Fréq_Récente pour voir la tendance. |
| **Sorties** | Nombre total d'apparitions historiques de la boule. |
| **Rapport_moyen** | Ratio moyen (ex. `1,35`) : gain moyen rapporté par cette boule sur son historique. |

Le tableau peut contenir des valeurs spéciales héritées des sources :
`N/A` (donnée absente), `+∞` / `-∞`, `=`.

### Fonctions disponibles

- **Tri** : cliquer sur un en-tête de colonne pour trier ascendant/dés ascendant.
- **Filtres avancés** : bouton *Afficher filtres* — restreindre le tableau par
  intervalles (ex. Retard `[0-5]`, Sorties `[10-19]`) ou par valeurs
  individuelles, pour chaque indicateur. Le nombre de boules correspondant à
  chaque option est affiché. *Réinitialiser tous les filtres* revient à tout
  afficher.
- **Sélection** : double-cliquer sur une ligne la surligne en jaune (5 max,
  l'équivalent des 5 numéros d'une grille) ; passer la souris en maintenant le
  bouton enfoncé pour sélectionner une plage de lignes en bleu.
- **Copier le tableau** : copie dans le presse-papiers le tableau filtré/trié
  au format séparé par tabulations (collable directement dans Excel), précédé
  d'un en-tête « Voici le tableau de statistiques actuelles des Numéros ».

> Comme les graphes, ces données sont **descriptives** (état des indicateurs à
> une date donnée) et ne permettent pas de prédire un tirage futur.

## API overview

All routes are prefixed with `/api`:

- `GET /api/draw-data`, `DELETE /api/draw-data/{id}`, `POST /api/extract-drive`
- `GET /api/numbers/{date}`, `GET /api/numbers/{date}/filter-options`
- `GET /api/stars/{date}`
- `GET /api/charts/top`, `GET /api/charts/top-stars`
- `GET /api/chart-*` — chart aggregates (out, report, delay, ecarts,
  frequency, progression, recent-frequency, frequency-previous-period, ...)
