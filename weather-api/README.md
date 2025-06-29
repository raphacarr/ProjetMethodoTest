# Weather API

## Description

Une API REST complète qui agrège des données météorologiques provenant de plusieurs sources externes. Cette API permet d'obtenir des informations météorologiques actuelles, des prévisions et des données historiques pour n'importe quelle ville dans le monde, en combinant les données de plusieurs fournisseurs pour une fiabilité et une précision accrues.

## Fonctionnalités

- **Météo actuelle** : Récupération des données météo en temps réel pour une ville spécifique
- **Prévisions météo** : Prévisions sur plusieurs jours (1 à 10 jours)
- **Historique météo** : Données historiques sur les jours précédents (1 à 30 jours)
- **Agrégation de données** : Combinaison intelligente des données depuis plusieurs sources :
  - Open-Meteo
  - OpenWeatherMap
  - WeatherAPI
- **Système de cache** : Utilisation de Redis pour optimiser les performances
- **Tests complets** : Tests unitaires, d'intégration, de contrat et de charge
- **Documentation API** : Interface Swagger interactive
- **Monitoring** : Intégration avec Prometheus et Grafana

## Structure du projet

```
weather-api/
├── src/                    # Code source principal
│   ├── routers/            # Définition des endpoints API
│   ├── services/           # Logique métier et services
│   │   ├── weather_service.py    # Service d'agrégation météo
│   │   ├── geocoding_service.py  # Service de géocodage
│   │   ├── redis_service.py      # Service de cache Redis
│   │   └── providers/      # Intégrations avec les APIs externes
│   ├── schemas/            # Modèles Pydantic pour validation des données
│   │   └── weather.py      # Schémas des données météo
│   └── main.py            # Point d'entrée de l'application
├── tests/                 # Tests automatisés
│   ├── test_contract.py   # Tests de contrat JSON
│   ├── test_weather_endpoints.py  # Tests des endpoints
│   ├── test_weather_service.py    # Tests unitaires des services
│   └── test_redis_service.py      # Tests du service Redis
├── config/                # Configuration de l'application
│   └── settings.py        # Paramètres et variables d'environnement
├── docker-compose.yml     # Configuration Docker pour les services
├── requirements.txt       # Dépendances Python
└── .env.example          # Exemple de variables d'environnement
```

## Prérequis

- Python 3.10+ (recommandé)
- Docker et Docker Compose (pour Redis)
- Clés API pour OpenWeatherMap et WeatherAPI (optionnel, mais recommandé)

## Installation

1. **Cloner le dépôt** :
```bash
git clone <repository-url>
cd weather-api
```

2. **Créer un environnement virtuel et l'activer** :
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. **Installer les dépendances** :
```bash
pip install -r requirements.txt
```

4. **Configurer les variables d'environnement** :
   - Copier le fichier `.env.example` en `.env`
   - Éditer le fichier `.env` avec vos clés API et autres configurations

```bash
cp .env.example .env
# Éditer le fichier .env avec vos clés API
```

Voici un exemple de configuration `.env` :
```
# API Settings
API_V1_STR=/api/v1

# Redis settings
REDIS_URL=redis://localhost:6379/0

# Weather API Keys
OPENWEATHER_API_KEY=votre_clé_openweather
WEATHERAPI_KEY=votre_clé_weatherapi

# Cache settings
CACHE_EXPIRATION=300  # 5 minutes
```

5. **Démarrer Redis avec Docker** :
```bash
docker-compose up -d redis
```

## Démarrage de l'application

### Démarrer le serveur de développement

```bash
uvicorn src.main:app --reload --port 8000
```

L'API sera disponible à l'adresse http://localhost:8000

### Documentation API

La documentation Swagger est disponible à l'adresse http://localhost:8000/docs

## Utilisation de l'API

### Endpoints principaux

#### Météo actuelle
```
GET /api/v1/weather/current/{city}
```
Exemple : `GET /api/v1/weather/current/Paris`

#### Prévisions météo
```
GET /api/v1/weather/forecast/{city}?days={nombre_de_jours}
```
Exemple : `GET /api/v1/weather/forecast/London?days=5`

#### Historique météo
```
GET /api/v1/weather/history/{city}?days={nombre_de_jours}
```
Exemple : `GET /api/v1/weather/history/New%20York?days=3`

#### Vérification de l'état de l'API
```
GET /api/v1/health/
```
Pour une vérification détaillée : `GET /api/v1/health/detailed`

## Système de cache Redis

L'API utilise Redis comme système de cache pour améliorer les performances :

- Les résultats des requêtes météo sont mis en cache pendant 5 minutes par défaut
- Réduction significative de la charge sur les APIs externes
- Temps de réponse amélioré pour les requêtes répétées
- L'application fonctionne en mode dégradé si Redis n'est pas disponible

## Exécution des tests

### Exécuter tous les tests

```bash
python -m pytest
```

### Exécuter des tests spécifiques

```bash
# Tests unitaires des services
python -m pytest tests/test_weather_service.py

# Tests de contrat JSON
python -m pytest tests/test_contract.py

# Tests des endpoints
python -m pytest tests/test_weather_endpoints.py
```

### Tests avec couverture de code

```bash
python -m pytest --cov=src tests/
```

## Sources de données météo

- **Open-Meteo** - https://open-meteo.com/
  - API gratuite sans clé requise
  - Données météo basées sur des modèles de prévision

- **OpenWeatherMap** - https://openweathermap.org/api
  - Nécessite une clé API (plan gratuit disponible)
  - Données météo actuelles, prévisions et historiques

- **WeatherAPI** - https://www.weatherapi.com/
  - Nécessite une clé API (plan gratuit disponible)
  - Données météo détaillées et précises

## Modèles de données

L'API utilise des modèles Pydantic pour la validation des données :

- `CurrentWeather` : Données météo actuelles
- `Forecast` : Prévisions météo
- `HistoricalWeather` : Données météo historiques
- `Temperature`, `Wind`, `WeatherCondition` : Composants des données météo

## Dépannage

### Problèmes courants

1. **Erreur de connexion Redis** :
   - Vérifier que le conteneur Redis est en cours d'exécution
   - Vérifier la configuration REDIS_URL dans le fichier .env

2. **Erreurs d'API externes** :
   - Vérifier que les clés API sont correctes et actives
   - Vérifier les quotas d'utilisation des APIs

3. **Ville non trouvée** :
   - Vérifier l'orthographe de la ville
   - Essayer d'ajouter le code du pays (ex: "Paris,FR")

## Contribution

Les contributions sont les bienvenues ! Voici comment contribuer :

1. Fork du projet
2. Créer une branche pour votre fonctionnalité (`git checkout -b feature/amazing-feature`)
3. Commit de vos changements (`git commit -m 'Add some amazing feature'`)
4. Push vers la branche (`git push origin feature/amazing-feature`)
5. Ouvrir une Pull Request

## Licence

Ce projet est sous licence MIT.
