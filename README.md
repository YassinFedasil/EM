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

## API overview

All routes are prefixed with `/api`:

- `GET /api/draw-data`, `DELETE /api/draw-data/{id}`, `POST /api/extract-drive`
- `GET /api/numbers/{date}`, `GET /api/numbers/{date}/filter-options`
- `GET /api/stars/{date}`
- `GET /api/charts/top`, `GET /api/charts/top-stars`
- `GET /api/chart-*` — chart aggregates (out, report, delay, ecarts,
  frequency, progression, recent-frequency, frequency-previous-period, ...)
