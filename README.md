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
| `MONGO_COLLECTION_COMBINATIONS` | `generated_combinations` | backend |
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

## Analyse statistique des numéros (`/data-numbers`)

Page : http://localhost:5173/data-numbers

### Principe et périmètre

La page répond à la question : « parmi les boules réellement tirées lors des
**N derniers tirages**, quels profils statistiques reviennent le plus
souvent ? »

- Elle **ne classe pas les 50 numéros** : seules les **5 boules gagnantes** de
  chaque tirage sont analysées (soit 5 observations par tirage).
- Les indicateurs de base (fréquence, retard, progression, sorties, rapport,
  …) proviennent des tableaux publiés par la source et importés depuis Google
  Drive ; l'application les **agrège, les classe et les compte** — elle ne les
  recalcule pas.
- Chaque carte présente un « **Top X** » : les X valeurs (ou combinaisons) les
  plus fréquentes, triées par nombre d'occurrences décroissant.
- Pour consulter l'état des 50 numéros à une date donnée, voir la page
  `/numbers` (tableau par date).

### Indicateurs affichés (dans l'ordre de la page)

| Carte | Question métier | Unité comptée |
| --- | --- | --- |
| **FRÉQUENCE** | Quels profils de fréquence globale composent les tirages ? | 1 combinaison par tirage |
| **RETARD RANGE** | Quels profils de retard composent les tirages ? | 1 combinaison par tirage |
| **RETARD** | Quels retards individuels reviennent chez les boules tirées ? | boule |
| **PROGRESSION** | Quelles évolutions de fréquence reviennent chez les boules tirées ? | boule |
| **FRÉQUENCE RÉCENTE** | Quelles valeurs de fréquence récente reviennent ? | boule |
| **FRÉQ. PÉRIODE PRÉC** | Quelles valeurs de fréquence de la période précédente reviennent ? | boule |
| **SORTIE** | Quels nombres de sorties historiques reviennent ? | boule |
| **SORTIE RANGE** | Quels profils de sorties (tranches de 10) composent les tirages ? | 1 combinaison par tirage |
| **RAPPORT** | Quels rapports moyens reviennent ? | boule |
| **PAIR / IMPAIR** | Quelle composition paire/impaire des 5 boules ? | 1 combinaison par tirage |
| **INTERVALLES 1-25 / 26-50** | Quelle répartition entre basses et hautes boules ? | 1 combinaison par tirage |
| **TRANCHES DE 10** | Quelle répartition par dizaines ? | 1 combinaison par tirage |

Les trois dernières cartes (PAIR / IMPAIR, INTERVALLES, TRANCHES DE 10) sont
calculées à la volée par le frontend à partir de l'historique des tirages ;
les neuf premières viennent des statistiques agrégées du backend.

### Règles de calcul et interprétation des notations

**`4x2 | 5x3` — FRÉQUENCE.** Pour chaque tirage, on prend la fréquence globale
(en %) des 5 boules gagnantes, on garde la **partie entière** de chacune (4,00 %
à 4,99 % → tranche 4 ; 5,76 % → tranche 5) et on résume la composition.
`4x2 | 5x3` = **2 boules** dont la fréquence est dans la tranche 4,xx et
**3 boules** dans la tranche 5,xx. Les tranches sont listées par ordre
croissant. Une ligne par combinaison distincte ; le compte est un **nombre de
tirages**.

> Exemple : fréquences des 5 boules = 4,82 / 5,76 / 4,10 / 4,90 / 7,00 →
> tranches 4, 5, 4, 4, 7 → combinaison `4x3 | 5x1 | 7x1`.

**`[0-5]x2 | [6-10]x3` — RETARD RANGE.** Pour chaque tirage, le retard de
chaque boule gagnante est rangé dans une des trois tranches fixes `[0-5]`,
`[6-10]`, `[11+]`, puis la composition est résumée. `[0-5]x2 | [6-10]x3` =
2 boules avec un retard de 0 à 5 et 3 boules avec un retard de 6 à 10. Les
tranches vides sont omises ; l'ordre est toujours `[0-5]`, `[6-10]`, `[11+]`.
Une ligne par combinaison ; le compte est un **nombre de tirages**.

> Exemple : retards des 5 boules = 2 / 3 / 7 / 15 / 40 →
> `[0-5]x2 | [6-10]x1 | [11+]x2`.

**RETARD (valeurs individuelles).** Nombre de tirages écoulés depuis la
dernière sortie de la boule (0 = boule sortie au tirage courant ; plus la
valeur est élevée, plus la boule était « froide » avant de sortir). Chaque
ligne = un retard observé ; le compte = **nombre de boules tirées** ayant ce
retard parmi les N tirages (5 × N observations au maximum).

**`+50`, `-25`, `=` — PROGRESSION.** Évolution de la fréquence de la boule
entre deux périodes, telle que publiée par la source (le symbole `%` est
retiré à l'import). `+50` = hausse publiée de 50 points, `-25` = baisse
publiée de 25 points, `=` = stable. Des libellés spéciaux (`+∞`, `-∞`, `N/A`)
peuvent apparaître tels quels. Chaque ligne = un libellé observé ; le compte =
**nombre de boules tirées** portant ce libellé.

> ⚠️ La longueur exacte des deux périodes comparées et la formule de la
> progression sont **définies par la source** (tableaux importés), pas par
> cette application : **à confirmer** auprès du fournisseur des données.

**FRÉQUENCE RÉCENTE** et **FRÉQ. PÉRIODE PRÉC.** Valeurs de fréquence (sur la
période récente / la période précédente) telles que publiées ; le libellé est
affiché tel quel. Chaque ligne = une valeur ; le compte = **nombre de boules
tirées**. La comparaison des deux cartes permet de repérer une tendance
(hausse/baisse) entre les deux périodes.

**SORTIE.** Nombre total d'apparitions historiques de la boule (« sorties »).
Chaque ligne = un nombre de sorties ; le compte = **nombre de boules tirées**
ayant ce total.

**`[10-19]x2 | [30-39]x3` — SORTIE RANGE.** Les sorties des 5 boules gagnantes
sont rangées en **tranches dynamiques de 10** (`[0-9]`, `[10-19]`, `[20-29]`,
…), puis résumées. Une ligne par combinaison ; le compte est un **nombre de
tirages**. Une tranche n'apparaît que si elle contient au moins une boule ;
les tirages dont aucune sortie n'est numérique (valeur `N/A`) sont ignorés.

> Exemple : sorties des 5 boules = 7 / 12 / 47 / 103 / 108 →
> `[0-9]x1 | [10-19]x1 | [40-49]x1 | [100-109]x2`.

**RAPPORT.** « Rapport moyen » de la boule tel que publié (ex. `1,35`). Chaque
ligne = une valeur ; le compte = **nombre de boules tirées**.

**`3 pairs / 2 impairs` — PAIR / IMPAIR.** Pour chaque tirage, on compte les
numéros pairs et impairs parmi les 5 boules (numéros de 1 à 50). Les
combinaisons possibles vont de `5 pairs / 0 impair` à `0 pair / 5 impairs`.
Une ligne par combinaison ; le compte est un **nombre de tirages**.

> Exemple : 4 / 12 / 23 / 37 / 48 → 3 pairs (4, 12, 48) et 2 impairs (23, 37)
> → `3 pairs / 2 impairs`.

**`3 numéros entre 1 et 25 / 2 numéros entre 26 et 50` — INTERVALLES.** Pour
chaque tirage, on compte les boules dans la moitié basse (1-25) et la moitié
haute (26-50) de la grille. Une ligne par combinaison ; le compte est un
**nombre de tirages**.

**`[1–10] : 1, [11–20] : 2, …` — TRANCHES DE 10.** Pour chaque tirage, les 5
numéros sont répartis dans les cinq tranches `[1–10]`, `[11–20]`, `[21–30]`,
`[31–40]`, `[41–50]`. Les cinq tranches sont toujours affichées, y compris
celles à 0, et leur somme vaut toujours 5. Une ligne par combinaison ; le
compte est un **nombre de tirages**.

> Exemple : 3 / 12 / 27 / 41 / 48 → `[1–10] : 1, [11–20] : 1, [21–30] : 1,
> [31–40] : 0, [41–50] : 2`.

### Nombre d'occurrences et pourcentage

Chaque ligne affiche « **X fois (Y %) »** (le pourcentage est en vert, arrondi
à l'entier le plus proche).

- **Cartes de combinaisons** (FRÉQUENCE, RETARD RANGE, SORTIE RANGE,
  PAIR / IMPAIR, INTERVALLES, TRANCHES DE 10) : X = **nombre de tirages**
  présentant cette combinaison, Y = X / nombre de tirages analysés → toujours
  ≤ 100 %. Exemple : « 3 pairs / 2 impairs : 8 fois (32 %) » sur 25 tirages.
- **Cartes de valeurs individuelles** (RETARD, PROGRESSION, FRÉQUENCE RÉCENTE,
  FRÉQ. PÉRIODE PRÉC, SORTIE, RAPPORT) : X = **nombre de boules tirées**
  portant cette valeur (au plus 5 par tirage), Y = X / nombre de tirages
  analysés. **Y peut donc dépasser 100 %** (jusqu'à 500 %) : ce n'est pas une
  probabilité de tirage, mais le nombre moyen de boules concernées par tirage
  × 100. Exemple : « Retard 7 : 10 fois (40 %) » sur 25 tirages = 10 boules
  tirées sur 125 (5 × 25) avaient un retard de 7.
- Le dénominateur est le **nombre réel de tirages analysés** = plus petit
  entre la valeur demandée (« Sur ») et le nombre de tirages disponibles dans
  l'historique. Si aucun historique n'est disponible, le pourcentage est
  masqué (aucune division par zéro). L'en-tête de la page affiche la valeur
  demandée, qui peut donc être supérieure au nombre réellement analysé.
- Les pourcentages des lignes d'une même carte ne totalisent pas forcément
  100 % : le Top X tronque la liste et les arrondis s'additionnent.

### Paramètres et fonctionnalités disponibles

| Élément | Rôle |
| --- | --- |
| **Top** (défaut 10) | Nombre maximum de lignes affichées **par carte** (valeurs ou combinaisons distinctes). Une carte peut en afficher moins si peu de valeurs existent. Bornes acceptées par l'API : 1 à 100. |
| **Sur (tirages)** (défaut 25) | Nombre de **tirages les plus récents** (par date décroissante) pris en compte. Bornes acceptées par l'API : 1 à 200. |
| **Appliquer** | Relance le chargement des statistiques et de l'historique des tirages. Les champs Top/Sur rechargent déjà automatiquement à chaque modification. |
| **Copier** | Copie dans le presse-papiers un rapport texte : en-tête « Top X (sur N tirages) », puis les indicateurs dans l'ordre de la page avec `- valeur : X fois`, accompagnés d'exemples explicatifs, puis PAIR / IMPAIR, INTERVALLES et TRANCHES DE 10 lorsqu'elles sont disponibles. Le bouton affiche « Copié ! » pendant 3 secondes. |

- Sans historique de tirages disponible, les cartes calculées (PAIR / IMPAIR,
  INTERVALLES, TRANCHES DE 10) sont masquées et les pourcentages ne sont pas
  affichés ; les cartes d'indicateurs restent visibles.
- Une valeur hors bornes est refusée par l'API : la mise à jour échoue
  silencieusement (les cartes conservent les données précédentes, ou restent
  vides au premier chargement) sans message d'erreur explicite.

## Analyse statistique des étoiles (`/data-stars`)

Page : http://localhost:5173/data-stars

### Principe et périmètre

Même logique que la page des numéros, mais appliquée aux **2 étoiles
gagnantes** de chaque tirage : on analyse uniquement les étoiles réellement
sorties lors des N derniers tirages, jamais les 12 étoiles de la grille.

- Un tirage fournit **2 observations** par indicateur individuel.
- Seuls **5 indicateurs** sont produits pour les étoiles (pas de SORTIE,
  SORTIE RANGE, RAPPORT ni RETARD RANGE) ; s'y ajoute PAIR / IMPAIR, calculé
  par le frontend.
- Les cartes sont affichées dans l'ordre renvoyé par l'API : Fréquence,
  Retard, Progression, Fréquence récente, Fréq. Période Préc.

### Indicateurs affichés

| Carte | Question métier | Unité comptée |
| --- | --- | --- |
| **Fréquence** | Quels profils de fréquence globale composent les tirages ? | 1 combinaison par tirage |
| **Retard** | Quels retards individuels reviennent chez les étoiles tirées ? | étoile |
| **Progression** | Quelles évolutions de fréquence reviennent chez les étoiles tirées ? | étoile |
| **Fréquence récente** | Quelles valeurs de fréquence récente reviennent ? | étoile |
| **Fréq. Période Préc** | Quelles valeurs de fréquence de la période précédente reviennent ? | étoile |
| **PAIR / IMPAIR** | Quelle composition paire/impaire des 2 étoiles ? | 1 combinaison par tirage |

### Règles de calcul et interprétation des notations

- **`7x1 | 9x1` — Fréquence.** Même principe que pour les numéros : les
  fréquences globales des 2 étoiles tirées sont réduites à leur partie entière
  puis résumées. `7x1 | 9x1` = 1 étoile dont la fréquence est dans la tranche
  7,xx et 1 étoile dans la tranche 9,xx. Une ligne par combinaison ; le compte
  est un **nombre de tirages** (≤ 100 %).
- **Retard, Progression, Fréquence récente, Fréq. Période Préc** : mêmes
  définitions que pour les numéros (voir ci-dessus), avec **2 observations par
  tirage**. Les pourcentages de ces cartes peuvent donc atteindre **200 %**
  (2 étoiles par tirage).
- **`1 paire / 1 impaire` — PAIR / IMPAIR.** Composition paire/impaire des 2
  étoiles. Trois combinaisons possibles : `2 paires / 0 impaire`,
  `1 paire / 1 impaire`, `0 paire / 2 impaires`. Une ligne par combinaison ;
  le compte est un **nombre de tirages**.

### Paramètres et fonctionnalités disponibles

Identiques à la page des numéros, avec les particularités suivantes :

| Élément | Différence |
| --- | --- |
| **Top** (défaut 10) | Borne acceptée par l'API : 1 à **50**. |
| **Sur (tirages)** (défaut 25) | Borne acceptée par l'API : 1 à 200 (identique). |
| **Copier** | Copie l'en-tête « Top X étoiles (sur N tirages) », les 5 indicateurs dans l'ordre de l'API (libellés en majuscules), un exemple pour la fréquence, puis PAIR / IMPAIR. Le bouton garde le libellé « Copier » (le retour visuel « copié » est très bref et non textuel). |

### Limites d'interprétation des statistiques (communes aux deux pages)

- **Statistiques descriptives, non prédictives** : elles décrivent les tirages
  **passés** et ne constituent en aucun cas une prévision garantie ni une
  probabilité de sortie des prochains tirages.
- **Périmètre partiel** : seules les boules/étoiles **effectivement tirées**
  sont agrégées. Ce ne sont pas des statistiques sur l'ensemble des 50 numéros
  ou des 12 étoiles ; pour cela, utiliser `/numbers` et les pages par date.
- **Définitions héritées de la source** : la fréquence « globale », les
  fenêtres de la période récente et de la période précédente, la formule de la
  progression et la signification exacte du « rapport moyen » sont fournies
  par les tableaux source (Loterie Nationale) importés depuis Google Drive.
  L'application ne les recalcule pas → **à confirmer** auprès du fournisseur
  des données pour toute interprétation fine.
- **Top X tronqué** : seules les X valeurs/combinaisons les plus fréquentes
  sont affichées ; les queues de distribution (valeurs rares) sont masquées.
  Le classement des ex æquo n'est pas garanti (ordre dépendant du backend).
- **Tailles d'échantillon** : avec peu de tirages (« Sur » faible), les
  pourcentages varient fortement ; une carte peut afficher « X fois » sans
  pourcentage si l'historique des tirages est indisponible.
- **Pourcentages > 100 %** sur les cartes individuelles : ils comptent des
  boules/étoiles par tirage, pas des tirages ; ne pas les lire comme une
  probabilité.
- **Couverture de l'historique** : les N derniers tirages sont ceux présents
  en base (issus des imports) ; un historique incomplet fausse la profondeur
  de l'analyse. Les valeurs sont un instantané des tableaux source au moment
  de l'import.
- **Valeurs spéciales** (`N/A`, `+∞`, `-∞`, `=`) : elles peuvent apparaître
  telles quelles ; les cartes de tranches ignorent les valeurs non numériques,
  et les tirages dont aucun indicateur n'est numérique peuvent être exclus de
  la carte concernée (le pourcentage total de la carte peut alors être
  inférieur à 100 %).

## Page des données par date (numéros) — signification de l'affichage

Page : http://localhost:5173/numbers

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

## Génération et historique des combinaisons (`/` et `/history`)

Cette section décrit deux écrans liés : la **génération** de combinaisons
(`EuroMillions.tsx`, route `/`) et l'**historique** qui les confronte aux
résultats officiels (`History.tsx`, route `/history`, entrée « History » de la
barre latérale).

> Les combinaisons produites sont des **propositions aléatoires**. Ce ne sont ni
> des prédictions, ni des recommandations de jeu : l'application ne calcule
> aucune probabilité de gain.

### 1. Génération des combinaisons (page `/`)

Page : http://localhost:5173/

1. Saisir une date de tirage au format `JJ-MM-AAAA` (la date du jour est
   pré-remplie) puis cliquer **Analyser**. La date doit être une date réelle :
   `32-13-2026` est refusé.
2. L'application charge les **pools disponibles** pour cette date :
   - les 50 numéros via `GET /api/numbers/{date}` ;
   - les 12 étoiles via `GET /api/stars/{date}`.

   Ces endpoints lisent le cache MongoDB et, en cas d'absence, les tableaux
   importés depuis Google Drive (même mécanisme que la page `/numbers`, voir
   [Page des données par date](#page-des-données-par-date-numéros--signification-de-laffichage)).
3. **Cinq combinaisons sont générées en une seule fois**, numérotées de **1 à
   5** dans l'ordre d'affichage.
4. Composition de **chaque** combinaison :
   - **5 numéros distincts** choisis entre **1 et 50**, affichés en ordre
     croissant ;
   - **2 étoiles distinctes** choisies entre **1 et 12**, affichées en ordre
     croissant.
5. Les 5 combinaisons de l'ensemble sont **distinctes entre elles** (aucun
   doublon exact de numéros + étoiles).

Le bouton **Nouvelle combinaison** régénère **un nouvel ensemble complet de 5
combinaisons** (il ne remplace pas une seule ligne) ; il ne modifie rien en base
tant que l'enregistrement n'a pas été demandé. Changer la date efface les
combinaisons affichées et impose un nouveau **Démarrer**.

| Situation | Comportement de l'écran |
| --- | --- |
| Date mal formée ou inexistante | Message d'erreur, aucune combinaison générée. |
| Tirage absent (aucune donnée pour la date) | Message « Aucun tirage disponible… » ; aucune combinaison. |
| Données incomplètes (< 5 numéros ou < 2 étoiles) | Message explicite ; aucune combinaison. |
| Serveur/Drive indisponible | Message d'indisponibilité temporaire ; aucune combinaison. |
| Aucune combinaison générée | Le bouton d'enregistrement n'est pas affiché. |

### 2. Enregistrement explicite et règle « une seule version par date »

L'enregistrement n'est **jamais automatique** : il faut cliquer sur
**Enregistrer les 5 combinaisons**. Régénérer, changer la date ou quitter la
page avant cet appui ne modifie pas la base.

Règles appliquées par le backend (`PUT /api/combinations/{date}`) :

- **Un seul ensemble de 5 combinaisons par date** est conservé. La date sert
  d'identifiant du document dans la collection `generated_combinations`
  (`_id = "JJ-MM-AAAA"`), ce qui rend l'unicité structurelle.
- Un nouvel enregistrement pour une date **remplace intégralement** l'ensemble
  précédent : ce n'est ni un ajout, ni une fusion, ni un remplacement ligne par
  ligne. Le remplacement est **atomique** (une seule écriture MongoDB).
- Le serveur **réindexe** les combinaisons de 1 à 5 dans l'ordre reçu et **trie**
  les numéros et les étoiles avant stockage.
- Le payload est refusé si : il ne contient pas exactement 5 combinaisons, un
  numéro est hors 1–50 ou dupliqué, une étoile est hors 1–12 ou dupliquée, ou la
  date n'existe pas réellement.
- Enregistrer une date **sans résultat officiel** est autorisé : les
  combinaisons seront visibles dans l'historique, mais non comparables tant que
  le résultat officiel n'est pas disponible.
- L'écran affiche un retour visuel de succès ou d'échec ; en cas d'échec, les
  combinaisons restent affichées et peuvent être réessayées.

Conséquence métier : l'historique ne montre que la **dernière version
enregistrée** pour chaque date. Il n'existe ni suppression ni conservation des
versions antérieures dans l'interface ; une suppression nécessiterait une
intervention directe en base (l'API n'expose pas de route `DELETE`).

### 3. Historique des tirages (page `/history`)

Page : http://localhost:5173/history

#### Contenu de la liste

L'historique est la **réunion de deux sources** :

- les dates possédant un **résultat officiel** (collection `draw_data`) ;
- les dates possédant des **combinaisons enregistrées**
  (`generated_combinations`).

Les dates sont triées de la plus récente à la plus ancienne. La page indique
« **Tirage X sur Y** » : X = position courante (1 = tirage le plus récent), Y =
nombre total de dates de la liste. Chaque date est chargée **à la demande** ;
le détail déjà consulté est mis en cache en mémoire pour la durée de la visite.

#### Affichage d'un tirage

| Bloc | Contenu |
| --- | --- |
| **Résultat officiel** | Les **5 numéros** et **2 étoiles** réellement tirés, lus dans `draw_data`. Rien n'est inventé ni complété. |
| **Combinaisons enregistrées** | Les **5 combinaisons** sauvegardées pour cette date, avec leurs numéros et étoiles. |
| **Comparaison** | Pour chaque combinaison : nombre de **numéros** trouvés (sur 5) et d'**étoiles** trouvées (sur 2). |
| **Surlignage vert** | Un numéro ou une étoile de la combinaison est affiché en vert lorsqu'il figure aussi dans le résultat officiel. |
| **Jackpot** | Message « 🎉 C'est chouette, tu as gagné le jackpot ! » **uniquement** si la combinaison contient les 5 numéros **et** les 2 étoiles gagnants. |

La comparaison se fait **par valeur, sans tenir compte de l'ordre** ; les
numéros/étoiles étant stockés triés, l'ordre d'affichage est toujours croissant.
Un jackpot n'est jamais affiché si le résultat officiel est absent, même si les
valeurs semblaient correspondre.

#### Navigation

- **Tirage précédent** (flèche gauche) : affiche le tirage **plus ancien**.
- **Tirage suivant** (flèche droite) : affiche le tirage **plus récent**.
- Les deux boutons sont **désactivés aux bornes** : « précédent » sur la date la
  plus ancienne, « suivant » sur la date la plus récente.
- Chaque changement de tirage recharge uniquement le détail de la date
  concernée (pas toute la liste).

#### Cas particuliers

| Situation | Comportement |
| --- | --- |
| Date avec résultat officiel mais **aucune combinaison** | Le résultat officiel s'affiche ; le bloc combinaisons indique « Aucune combinaison enregistrée pour ce tirage » et propose un lien vers le générateur. |
| Date avec combinaisons mais **aucun résultat officiel** | Les combinaisons s'affichent avec la mention « En attente du résultat officiel » ; aucun nombre de correspondances, aucun surlignage vert, aucun jackpot. Un avertissement précise que les gains ne peuvent pas être validés. |
| **Historique vide** | Message « Aucun tirage n'est disponible… » et lien vers le générateur. |
| Erreur de chargement de la liste | Message d'erreur et bouton **Réessayer**. |
| Erreur de chargement d'un tirage | Message d'erreur localisé dans les blocs du tirage concerné. |
| Serveur indisponible | Message d'indisponibilité temporaire (pas de résultats partiels présentés comme fiables). |

> Le résultat officiel provient exclusivement des données déjà importées dans
> `draw_data`. Une date sans résultat officiel (par exemple un tirage non encore
> importé ou non publié) reste donc explicitement non comparable ; l'application
> ne devine ni ne déduit aucun résultat.

### 4. Stockage et endpoints associés

- Collection : `generated_combinations` (nom configurable via
  `MONGO_COLLECTION_COMBINATIONS`), **un document par date** :

  ```json
  {
    "_id": "23-10-2026",
    "combinations": [
      { "index": 1, "numbers": [1, 5, 12, 23, 44], "stars": [3, 9] },
      { "index": 2, "numbers": [2, 7, 18, 33, 50], "stars": [1, 12] },
      { "index": 3, "numbers": [4, 9, 16, 27, 38], "stars": [5, 8] },
      { "index": 4, "numbers": [6, 11, 19, 31, 45], "stars": [2, 11] },
      { "index": 5, "numbers": [3, 8, 22, 35, 49], "stars": [4, 7] }
    ],
    "updated_at": "2026-10-22T12:00:00"
  }
  ```

- Aucune migration n'est nécessaire : la collection est créée au premier
  enregistrement.
- Routes (voir aussi [API overview](#api-overview)) :
  - `GET /api/combinations/{date}` — combinaisons enregistrées (`[]` si aucune) ;
  - `PUT /api/combinations/{date}` — enregistre/remplace les 5 combinaisons ;
  - `GET /api/history` — liste légère des dates (union officiels + combinaisons) ;
  - `GET /api/history/{date}` — détail d'un tirage (résultat officiel + comparaisons).

### 5. Limites à connaître

- **Non prédictif** : les combinaisons sont générées aléatoirement à partir des
  numéros/étoiles disponibles ; elles n'exploitent pas les statistiques des
  pages `/data-numbers` ou `/data-stars`.
- **Pas de résultat officiel inventé** : sans donnée dans `draw_data`, aucune
  correspondance n'est calculée et aucun jackpot n'est validé.
- **Une seule version par date** : réenregistrer écrase l'ensemble précédent ;
  aucun historique de versions n'est conservé.
- **Pas de suppression dans l'UI** : il n'existe pas de bouton pour supprimer un
  ensemble de combinaisons ; seul un remplacement est possible.
- **Actualisation** : la liste d'historique est chargée à l'ouverture de la
  page ; un enregistrement effectué dans un autre onglet n'apparaît qu'après
  rechargement de la page.
- **Dépendance aux imports** : la disponibilité et l'exactitude des résultats
  officiels dépendent des données importées dans `draw_data`.

## Moteur statistique de combinaisons

Page : http://localhost:5173/ (route `/`)

Le moteur évalue **10 000 grilles candidates** avec les statistiques disponibles
**avant** la date cible, puis retient les 5 meilleures combinaisons
suffisamment différentes. Chaque grille est explicable (score, facteurs,
profils, associations) et reproductible via une graine.

> Aucun modèle ne peut prédire un tirage : les scores sont des estimations
> historiques. Ils classent des grilles selon leur vraisemblance *passée*, pas
> selon une probabilité de gain future.

### 1. Données utilisées et absence de fuite

- **Snapshot cible** : tableaux `numbers_full` / `stars_full` de la date
  (50 numéros, 12 étoiles). Ces tableaux décrivent l'état **avant** le tirage :
  une boule tirée le jour D a toujours un `last_out` antérieur à D.
- Si la date exacte manque, le **dernier snapshot antérieur** est utilisé
  (mentionné dans `sources`, `source_mode` et `warnings`). À défaut de
  cache, les tableaux sont récupérés depuis Google Drive puis mis en cache.
- **Historique officiel** : uniquement les tirages de `draw_data` dont la date
  est **strictement antérieure** à la cible. Aucun résultat futur n'entre dans
  les profils ni dans les associations.
- Les indicateurs `sorties`, `progression` et `rapport_moyen` sont exclus du
  score individuel : `sorties` duplique la fréquence, `progression` est
  exactement `(récente - précédente) / précédente`, et `rapport_moyen` est un
  gain, pas une fréquence de sortie.

```bash
docker exec euro_stat_be python scripts/audit_engine_data.py
```

Ce script en lecture seule vérifie les résultats officiels, la complétude des
snapshots, l'alignement des tableaux `col_*`, la cohérence des indicateurs
pré-tirage et l'absence de fuite. **Audit du 22-10-2026** : 21 résultats
officiels valides (aucune boule dupliquée), 21 snapshots numéros et 19 snapshots
étoiles complets, 693/693 valeurs `col_*` alignées, 0 anomalie de fuite,
16/16 dates cibles avec snapshot exact (aucun fallback).

### 2. Score individuel (probabilité par boule)

**Problème corrigé en v1.1** : la fréquence long terme source n'est pas une
probabilité par tirage. Sur tous les snapshots, la somme des 50 fréquences vaut
environ **262** et celle des 12 étoiles environ **105**, alors que 5 numéros et
2 étoiles sont tirés (sommes attendues : **500** et **200** en pourcentage).
Le rapport `sorties / fréquence` est constant (~1978), ce qui indique un
simple facteur d'échelle commun. Le moteur recalibre donc les fréquences :

- `p_lt = (fréquence / 100) × 5 / Σ(fréquences numéros)` ;
- `p_lt = (fréquence / 100) × 2 / Σ(fréquences étoiles)` pour les étoiles.

La fréquence brute reste affichée dans l'API (`frequency`) ; la probabilité
recalibrée est exposée séparément (`probability`). Pour chaque boule :

- `p_recent = (récente + 25 × p_lt) / 50` (25 derniers tirages) ;
- `p_prev = (précédente + 25 × p_lt) / 50` (25 tirages précédents).

`p_est = moyenne(p_lt, p_recent, p_prev)`, bornée à `[10^-6, 1]` ; une valeur
absente est remplacée par `1/50` (numéros) ou `1/12` (étoiles) et signalée
dans `warnings`. Le facteur `individual` d'une grille est la moyenne des
`log(p_est)` de ses 5 numéros et 2 étoiles.

### 3. Profil de la grille (8 familles)

Chaque famille est modélisée sur les tirages antérieurs avec un lissage de
Laplace `(occurrences + 1) / (n + U)` (`U = valeurs distinctes observées + 1`) :

| Famille | Signature |
| --- | --- |
| `numbers_pair` | nombre de numéros pairs parmi les 5 |
| `numbers_low` | nombre de numéros dans 1-25 |
| `numbers_tens` | répartition par dizaines, ex. `[10-19]x2 \| [30-39]x3` |
| `numbers_frequency` | tranches entières de fréquence, ex. `4x1 \| 5x4` |
| `numbers_delay` | plages de retard `[0-5] / [6-10] / [11+]` |
| `stars_pair` | nombre d'étoiles paires |
| `stars_frequency` | tranches entières de fréquence des étoiles |
| `stars_delay` | plages de retard des étoiles |

Le facteur `profile` est la moyenne des log-probabilités de ces familles.
Il exige au moins **5 tirages** antérieurs. Ces familles sont fixes, sans
coefficient ajusté sur les résultats du backtest.

### 4. Associations (paires)

Pour chaque paire (10 paires de numéros, 1 paire d'étoiles, et 10 paires
numéro-étoile si l'historique atteint 30 tirages) :

- probabilité attendue corrigée du tirage sans remise :
  `q = p_i × p_j × N × (k-1) / (k × (N-1))` pour deux boules du même
  réservoir (`N=50, k=5` ou `N=12, k=2`) ;
- `q = p_i × p_j` pour une paire numéro-étoile (réservoirs séparés) ;
- `lift = (c + 1) / (n × q + 1)`, `w = c / (c + 2)`, contribution
  `log(1 + w × (lift - 1))` ;
- fiabilité globale `n / (n + 30)` appliquée à la moyenne des paires.

Les associations sont désactivées sous **10 tirages**. Le facteur
`associations` est cette moyenne pondérée ; les paires non observées ont une
contribution nulle. Les paires numéro-étoile ne sont pas évaluables sur
l'historique actuel (moins de 30 tirages avant chaque cible).

### 5. Agrégation, classement et diversité

1. Les trois dimensions (`individual`, `profile`, `associations`) sont
   **z-normalisées sur les candidates** (moyenne 0, écart-type 1).
2. `score = (z_individual + z_profile + z_associations) / 3` : poids égaux.
   Les flags `use_individual` / `use_profiles` / `use_associations` servent
   uniquement aux ablations du backtest ; au moins une dimension est requise.
3. `relative_score` = percentile du score parmi les candidates (0 = pire,
   100 = meilleure) ; `rank` = position (1 = meilleure).
4. **Échantillonnage** : `uniform` par défaut ; `guided` (pondéré par
   `p_est`) reste disponible pour comparaison. Dans les deux cas, les
   candidates sont **distinctes**.
5. **Diversité** : similarité `0,7 × numéros communs / 5 + 0,3 × étoiles
   communes / 2`. Les grilles sont prises par score décroissant en rejetant
   toute similarité `> 0,5` ; le seuil augmente par pas de `0,05` si besoin.
6. La graine (`seed`) rend l'ensemble reproductible ; elle est affichée avec
   le nombre de candidates et la durée d'exécution.

Le passage de `guided` à `uniform` par défaut est justifié par l'absence de
gain mesuré de l'échantillonnage guidé et par le fait qu'un classement doit
porter sur un échantillon représentatif, sans double emploi des probabilités
individuelles.

### 6. API

```http
GET /api/combination-engine/{JJ-MM-AAAA}?seed=42&candidates=10000&sampling=uniform
```

| Paramètre | Défaut | Valeurs |
| --- | --- | --- |
| `seed` | aléatoire (renvoyé) | entier 0 à 2^32-1 |
| `candidates` | `10000` | 100 à 50 000 |
| `sampling` | `uniform` | `uniform` ou `guided` |

La réponse contient : `date`, `seed`, `candidates`, `sampling`,
`elapsed_ms`, `source_mode` (`cache`/`drive`/`fallback`), `history`,
`sources`, `warnings`, les 50 + 12 indicateurs normalisés (fréquence source
et probabilité recalibrée), les 5 `combinations` (score, rang, percentile,
dimensions, facteurs, probabilités par boule, profils, associations,
similarité), `selected_diversity` et `meta` (formules, calibration,
pondérations, dimensions actives, limites). Codes d'erreur : `400`
date/paramètres invalides, `409` snapshot incomplet ou historique
`< 5` tirages, `502` Google Drive indisponible. L'API ne fait aucune écriture
MongoDB.

### 7. Vue détaillée (frontend)

Le bouton **Analyse détaillée** ouvre une modale (`EngineDetailsModal.tsx`)
qui affiche, pour chaque grille : décomposition du score et valeurs z,
probabilité estimée de chaque boule (fréquence source, retard), profil famille
par famille (clé observée, effectif, log-probabilité), associations triées par
contribution, fiabilité, similarité maximale et métadonnées du modèle.

- **Nouvelle combinaison** change la graine et relance l'analyse sur la même
  date. L'enregistrement reste **explicite** (même règle : un seul ensemble de
  5 grilles par date, remplacement atomique).
- Repli technique uniquement : si le moteur est injoignable (`status 0` ou
  `>= 500`), l'ancien tirage aléatoire est utilisé et clairement signalé. Une
  erreur de données (`400`, `404`, `409`) n'active **jamais** ce repli.

### 8. Backtest chronologique

Le script `euro-stat-BE/scripts/backtest_engine.py` rejoue chaque tirage
éligible (au moins 5 tirages antérieurs et un snapshot sans fuite), génère 5
grilles avec les seules données passées, puis compare *après coup* au résultat
officiel.

**Protocole** : 16 dates cibles (28-08-2026 → 20-10-2026), 5 graines
(1 à 5), 5 grilles par modèle et par date/graine, soit **400 grilles par
variante** avec 10 000 candidates. Tous les modèles voient les mêmes dates et
graines. La référence aléatoire produit 5 grilles distinctes (5/50 + 2/12). Les
intervalles de confiance à 95 % sont obtenus par **bootstrap sur les dates**
(2 000 rééchantillonnages, graines regroupées, graine 20261022). Le découpage
60/40 et les tiers chronologiques sont descriptifs : aucun hyperparamètre n'a
été choisi sur ces résultats.

```bash
docker exec euro_stat_be python scripts/backtest_engine.py \
  --candidates 10000 --seeds 1,2,3,4,5 --output /app/backtest.json
```

| Variante | Principe |
| --- | --- |
| `aleatoire` | 5 grilles uniformes distinctes, sans statistique |
| `moteur_uniforme` | moteur complet, candidates uniformes (défaut API) |
| `moteur_guide` | moteur complet, candidates guidées par `p_est` |
| `individuel_seul` | score individuel uniquement |
| `profil_seul` | profils uniquement |
| `associations_seul` | associations uniquement |
| `sans_associations` | individuel + profils |

Métriques produites : moyennes numéros/étoiles, meilleur résultat par tirage,
distributions 0-5 numéros et 0-2 étoiles, distribution conjointe, taux ≥ 2/3/4
numéros, deux étoiles avec/sans numéros, jackpots, diversité, temps de calcul,
résultats globaux, par graine, par période et comparaison appariée à la
référence aléatoire.

**Résultats globaux (10 000 candidates, graines 1-5, 400 grilles/variante)** :

| Variante | Numéros (IC 95 %) | Étoiles (IC 95 %) | Meilleur / tirage | ≥ 2 num. | ≥ 3 num. | 2 étoiles | Temps/run |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `aleatoire` | 0,480 [0,415 ; 0,547] | 0,330 [0,292 ; 0,367] | 1,238 | 6,75 % | 0,50 % | 1,25 % | 0 ms |
| `moteur_uniforme` | 0,522 [0,425 ; 0,615] | 0,405 [0,273 ; 0,535] | 1,275 | 8,00 % | 0,25 % | 1,50 % | 764 ms |
| `moteur_guide` | 0,505 [0,380 ; 0,642] | 0,328 [0,215 ; 0,432] | 1,150 | 7,50 % | 0 % | 1,25 % | 833 ms |
| `individuel_seul` | 0,438 [0,268 ; 0,645] | 0,278 [0,170 ; 0,405] | 0,963 | 6,25 % | 0,25 % | 0,25 % | 226 ms |
| `profil_seul` | 0,527 [0,453 ; 0,598] | 0,315 [0,208 ; 0,432] | 1,350 | 8,00 % | 1,00 % | 0,75 % | 345 ms |
| `associations_seul` | 0,560 [0,390 ; 0,743] | 0,385 [0,300 ; 0,465] | 1,262 | 8,00 % | 0,75 % | 1,00 % | 269 ms |
| `sans_associations` | 0,460 [0,343 ; 0,585] | 0,285 [0,190 ; 0,378] | 1,113 | 6,75 % | 0,50 % | 0,25 % | 533 ms |

Différences appariées vs aléatoire (numéros, IC 95 %) :
`moteur_uniforme` +0,042 [-0,085 ; +0,173] ; `profil_seul` +0,048
[-0,068 ; +0,148] ; `associations_seul` +0,080 [-0,115 ; +0,280] ;
`moteur_guide` +0,025 [-0,128 ; +0,195] ; `individuel_seul` -0,043
[-0,223 ; +0,187] ; `sans_associations` -0,020 [-0,143 ; +0,120]. Toutes
les différences incluent zéro.

Distributions des correspondances en numéros (aucune grille à 4 ou 5
numéros dans cet échantillon) :

| Numéros corrects | `aleatoire` | `moteur_uniforme` |
| --- | --- | --- |
| 0 | 59,25 % | 56,00 % |
| 1 | 34,00 % | 36,00 % |
| 2 | 6,25 % | 7,75 % |
| 3 | 0,50 % | 0,25 % |
| 4-5 | 0 % | 0 % |

Étoiles correctes : 0/1/2 = 68,25 % / 30,50 % / 1,25 % pour l'aléatoire et
61,00 % / 37,50 % / 1,50 % pour le moteur uniforme. Jackpots : 0 partout.

**Sensibilité** : avec 1 000 candidates et 10 graines, l'aléatoire obtenait
0,484 numéro et le moteur uniforme 0,470 ; avec 10 000 candidates et 5 graines,
les valeurs sont 0,480 et 0,522. Le signe de l'écart change : c'est le signe
d'un bruit d'échantillonnage, pas d'un effet robuste. Les résultats par période
varient également fortement (par ex. moteur uniforme : 0,512 / 0,488 / 0,560
numéros sur les trois tiers ; aléatoire : 0,456 / 0,584 / 0,413).

**Conclusion honnête** : aucune variante ne surpasse la référence aléatoire de
manière convaincante. Les associations seules ont la meilleure moyenne
ponctuelle (+0,080 numéro), mais leur IC inclut zéro [-0,115 ; +0,280] et
l'échantillon ne permet pas de conclure à un avantage. Sur le découpage 60/40,
les écarts restent instables (associations 0,542 puis 0,583 ; aléatoire 0,520
puis 0,429 numéros), avec de très petits effectifs. Le score individuel seul est
en retrait. Les profils et associations ne démontrent pas de valeur prédictive
hors échantillon. Le moteur reste utile comme outil d'explication et de
génération reproductible, pas comme prédicteur.

### 9. Limites

- Les tirages EuroMillions sont indépendants : le score ne change pas la
  probabilité réelle de gagner.
- L'historique disponible est court (21 tirages officiels, 16 cibles
  évaluables) ; les IC restent larges et les paires numéro-étoile ne peuvent
  pas être évaluées.
- La fréquence long terme est recalibrée à partir d'hypothèses de cohérence
  d'échelle ; la calibration ne crée pas d'information prédictive.
- Les snapshots sont des instantanés des tableaux source : une date sans
  snapshot exact réutilise un état antérieur (aucun cas sur les 16 cibles
  actuelles).
- Le backtest mesure des correspondances, pas un rendement financier ; les
  jackpots sont trop rares pour être estimés sur cet échantillon.
- Aucun résultat officiel n'est inventé ; une date sans résultat reste non
  comparable dans `/history`.

## API overview

All routes are prefixed with `/api`:

- `GET /api/draw-data`, `DELETE /api/draw-data/{id}`, `POST /api/extract-drive`
- `GET /api/numbers/{date}`, `GET /api/numbers/{date}/filter-options`
- `GET /api/stars/{date}`
- `GET /api/combinations/{date}`, `PUT /api/combinations/{date}`
- `GET /api/history`, `GET /api/history/{date}`
- `GET /api/combination-engine/{date}` — moteur statistique (seed, candidates, sampling ; défaut `uniform`)
- `GET /api/charts/top`, `GET /api/charts/top-stars`
- `GET /api/chart-*` — chart aggregates (out, report, delay, ecarts,
  frequency, progression, recent-frequency, frequency-previous-period, ...)
