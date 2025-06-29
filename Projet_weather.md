# Projet : API de Données Météorologiques

## Vue d'ensemble du projet

Ce projet consiste à développer une API REST complète qui agrège des données météorologiques provenant de plusieurs sources externes. L'objectif est d'appliquer les bonnes pratiques de développement, notamment le Test-Driven Development (TDD), les tests de contrat, les tests de charge, et la mise en place d'un système de monitoring.

## Objectifs pédagogiques

- Maîtriser le développement d'API REST avec une approche TDD
- Comprendre l'agrégation de données de sources multiples
- Implémenter des tests de différents niveaux (unitaires, intégration, contrat, charge)
- Mettre en place un système de monitoring et d'alertes
- Gérer la qualité du code et les métriques de performance

## Architecture du projet

### Stack technologique recommandée
- **Backend** : Node.js avec Express ou Python avec FastAPI
- **Base de données** : PostgreSQL pour les données persistantes, Redis pour le cache
- **Tests** : Jest/Mocha (Node.js) ou pytest (Python)
- **Tests de charge** : Locust ou Artillery
- **Monitoring** : Prometheus + Grafana
- **Documentation** : Swagger/OpenAPI

### Sources de données météo suggérées

**APIs recommandées pour les étudiants :**

1. **OpenWeatherMap** - [https://openweathermap.org/api](https://openweathermap.org/api)
   - **Gratuit** : 1000 appels/jour, 60 appels/minute
   - **Inscription** : Email requis, activation sous 2h
   - **Avantages** : Documentation complète, très populaire, données fiables
   - **Endpoints** : Météo actuelle, prévisions 5 jours, historique

2. **WeatherAPI** - [https://www.weatherapi.com/](https://www.weatherapi.com/)
   - **Gratuit** : 1 million d'appels/mois
   - **Inscription** : Immédiate, pas d'attente
   - **Avantages** : Quotas généreux, activation instantanée
   - **Endpoints** : Météo actuelle, prévisions, historique, alertes

3. **Open-Meteo** - [https://open-meteo.com/](https://open-meteo.com/) ⭐ **SANS INSCRIPTION**
   - **Gratuit** : 10,000 appels/jour, pas de clé API requise
   - **Avantages** : Aucune inscription, démarrage immédiat
   - **Données** : Météo européenne de haute qualité
   - **Parfait pour** : Prototypage rapide et tests

4. **API Météo France** - [https://portail-api.meteofrance.fr/](https://portail-api.meteofrance.fr/)
   - **Gratuit** : Données publiques françaises
   - **Inscription** : Compte requis
   - **Avantages** : Données officielles françaises
   - **Limitations** : Principalement France métropolitaine

**Recommandation pour démarrer rapidement :**
Commencer avec **Open-Meteo** (pas d'inscription) pour le développement initial, puis ajouter OpenWeatherMap et WeatherAPI pour l'agrégation de données.

## Phase 1 : Conception et setup initial

### 1.1 Analyse des besoins
- Définir les endpoints nécessaires :
  - `GET /weather/current/:city` - Météo actuelle
  - `GET /weather/forecast/:city` - Prévisions sur 5 jours
  - `GET /weather/history/:city` - Données historiques
  - `GET /health` - Vérification de l'état de l'API

### 1.2 Modélisation des données
Définir une structure de données normalisée qui inclut :
- Informations de localisation (ville, pays, coordonnées)
- Données temporelles avec timestamp
- Température (actuelle, ressentie, min/max avec unités)  
- Conditions météorologiques (état, description, humidité, pression, visibilité)
- Informations sur le vent (vitesse, direction, unités)
- Traçabilité des sources de données utilisées

**Exemple de structure partielle** :
```json
{
  "city": "Paris",
  "temperature": {
    "current": 22,
    "unit": "celsius"
  },
  "sources": ["openweather", "weatherapi"]
}
```

### 1.3 Configuration de l'environnement

#### Structure du projet
```
weather-api/
├── src/
│   ├── controllers/
│   ├── services/
│   ├── models/
│   └── tests/
├── config/
├── docker-compose.yml
├── package.json
└── .env.example
```

#### Variables d'environnement (.env)
```bash
# APIs externes
OPENWEATHER_API_KEY=your_key_here
WEATHERAPI_KEY=your_key_here

# Base de données
DATABASE_URL=postgresql://user:pass@localhost:5432/weather_db
REDIS_URL=redis://localhost:6379

# Configuration serveur
PORT=3000
NODE_ENV=development
```

#### Comment obtenir les clés API météo

**OpenWeatherMap** (Recommandé - 1000 appels/jour gratuits)
1. Aller sur [https://openweathermap.org/api](https://openweathermap.org/api)
2. Cliquer sur "Sign Up" pour créer un compte gratuit
3. Confirmer l'email de vérification
4. Aller dans la section "My API Keys" du tableau de bord
5. Copier la clé par défaut générée automatiquement
6. **Important** : La clé peut prendre jusqu'à 2 heures pour être activée

**WeatherAPI** (1 million d'appels/mois gratuits)
1. Aller sur [https://www.weatherapi.com/](https://www.weatherapi.com/)
2. Cliquer sur "Sign Up Free" 
3. Remplir le formulaire d'inscription
4. Vérifier l'email et se connecter
5. La clé API est immédiatement disponible dans le tableau de bord
6. Copier la "API Key" affichée

**Alternative gratuite sans inscription : Open-Meteo**
```bash
# Pas de clé requise pour Open-Meteo
OPEN_METEO_BASE_URL=https://api.open-meteo.com/v1
```

**Exemple d'appel API simple pour tester :**
```bash
# Test OpenWeatherMap
curl "https://api.openweathermap.org/data/2.5/weather?q=Paris&appid=YOUR_API_KEY&units=metric"

# Test WeatherAPI
curl "https://api.weatherapi.com/v1/current.json?key=YOUR_API_KEY&q=Paris&aqi=no"

# Test Open-Meteo (sans clé)
curl "https://api.open-meteo.com/v1/forecast?latitude=48.8566&longitude=2.3522&current_weather=true"
```

#### Docker Compose pour les services
```yaml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: weather_db
      POSTGRES_USER: weather_user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

#### Installation des dépendances (package.json)
```json
{
  "dependencies": {
    "express": "^4.18.0",
    "axios": "^1.4.0",
    "pg": "^8.11.0",
    "redis": "^4.6.0"
  },
  "devDependencies": {
    "jest": "^29.5.0",
    "supertest": "^6.3.0",
    "locust": "pour tests de charge"
  }
}
```

## Phase 2 : Développement TDD

### 2.1 Tests unitaires (Red-Green-Refactor)

Le Test-Driven Development (TDD) suit un cycle en 3 étapes : écrire un test qui échoue (Red), implémenter le code minimal pour le faire passer (Green), puis refactoriser (Refactor).

#### Cycle TDD pour l'endpoint météo actuelle :

**Phase Red** : Écrire les tests avant l'implémentation
```javascript
// tests/weather.test.js
const request = require('supertest');
const app = require('../src/app');

describe('Weather API', () => {
  describe('GET /weather/current/:city', () => {
    it('should return weather data for valid city', async () => {
      const response = await request(app)
        .get('/weather/current/Paris')
        .expect(200);
      
      expect(response.body).toHaveProperty('city', 'Paris');
      expect(response.body).toHaveProperty('temperature');
      expect(response.body.temperature).toHaveProperty('current');
      expect(typeof response.body.temperature.current).toBe('number');
    });

    it('should return 404 for invalid city', async () => {
      const response = await request(app)
        .get('/weather/current/InvalidCity123')
        .expect(404);
      
      expect(response.body).toHaveProperty('error');
    });

    it('should return 400 for missing city parameter', async () => {
      const response = await request(app)
        .get('/weather/current/')
        .expect(400);
    });
  });
});
```

**Phase Green** : Implémentation minimale
```javascript
// src/controllers/weatherController.js
const weatherService = require('../services/weatherService');

const getCurrentWeather = async (req, res) => {
  try {
    const { city } = req.params;
    
    if (!city) {
      return res.status(400).json({ error: 'City parameter is required' });
    }

    const weatherData = await weatherService.getCurrentWeather(city);
    
    if (!weatherData) {
      return res.status(404).json({ error: 'City not found' });
    }

    res.json(weatherData);
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
};

module.exports = { getCurrentWeather };
```

**Phase Refactor** : Amélioration du code
- Ajout de middleware de validation
- Centralisation de la gestion d'erreurs
- Optimisation des performances avec cache
- Amélioration du logging

### 2.2 Service d'agrégation
Développer un service qui :
- Interroge plusieurs sources météo en parallèle
- Agrège les données (moyenne, consensus)
- Gère les pannes de sources (fallback)
- Implement un système de cache intelligent

#### Tests pour le service d'agrégation
```javascript
// tests/weatherService.test.js
describe('WeatherService', () => {
  describe('getCurrentWeather', () => {
    it('should aggregate data from multiple sources', async () => {
      // Mock des APIs externes
      const mockOpenWeather = { temp: 20, humidity: 65 };
      const mockWeatherAPI = { temp: 22, humidity: 70 };
      
      const result = await weatherService.getCurrentWeather('Paris');
      
      expect(result.temperature.current).toBe(21); // Moyenne
      expect(result.sources).toContain('openweather');
      expect(result.sources).toContain('weatherapi');
    });

    it('should fallback when one source fails', async () => {
      // Simuler la panne d'une source
      // Vérifier que l'autre source est utilisée
    });
  });
});
```

#### Exemple d'implémentation avec les vraies APIs

```javascript
// src/services/weatherService.js
const axios = require('axios');

class WeatherService {
  constructor() {
    this.openWeatherKey = process.env.OPENWEATHER_API_KEY;
    this.weatherApiKey = process.env.WEATHERAPI_KEY;
    this.openMeteoBase = 'https://api.open-meteo.com/v1';
  }

  async getCurrentWeather(city) {
    try {
      // Appels parallèles aux différentes sources
      const promises = [
        this.getOpenWeatherData(city),
        this.getWeatherAPIData(city),
        this.getOpenMeteoData(city)
      ];
      
      const results = await Promise.allSettled(promises);
      return this.aggregateWeatherData(results, city);
    } catch (error) {
      throw new Error(`Failed to fetch weather for ${city}: ${error.message}`);
    }
  }

  async getOpenWeatherData(city) {
    if (!this.openWeatherKey) return null;
    
    const url = `https://api.openweathermap.org/data/2.5/weather`;
    const response = await axios.get(url, {
      params: {
        q: city,
        appid: this.openWeatherKey,
        units: 'metric'
      }
    });
    
    return {
      source: 'openweather',
      temperature: response.data.main.temp,
      humidity: response.data.main.humidity,
      description: response.data.weather[0].description
    };
  }

  async getWeatherAPIData(city) {
    if (!this.weatherApiKey) return null;
    
    const url = `https://api.weatherapi.com/v1/current.json`;
    const response = await axios.get(url, {
      params: {
        key: this.weatherApiKey,
        q: city,
        aqi: 'no'
      }
    });
    
    return {
      source: 'weatherapi',
      temperature: response.data.current.temp_c,
      humidity: response.data.current.humidity,
      description: response.data.current.condition.text
    };
  }

  async getOpenMeteoData(city) {
    // Géocodage simple (à améliorer avec une vraie API de géocodage)
    const coords = this.getCityCoordinates(city);
    if (!coords) return null;
    
    const url = `${this.openMeteoBase}/forecast`;
    const response = await axios.get(url, {
      params: {
        latitude: coords.lat,
        longitude: coords.lon,
        current_weather: true,
        hourly: 'temperature_2m,relativehumidity_2m'
      }
    });
    
    return {
      source: 'open-meteo',
      temperature: response.data.current_weather.temperature,
      humidity: response.data.hourly.relativehumidity_2m[0],
      description: this.getWeatherDescription(response.data.current_weather.weathercode)
    };
  }

  getCityCoordinates(city) {
    // Coordonnées de quelques villes pour les tests
    const cities = {
      'Paris': { lat: 48.8566, lon: 2.3522 },
      'London': { lat: 51.5074, lon: -0.1278 },
      'Tokyo': { lat: 35.6762, lon: 139.6503 },
      'New York': { lat: 40.7128, lon: -74.0060 }
    };
    return cities[city] || null;
  }

  aggregateWeatherData(results, city) {
    const validData = results
      .filter(result => result.status === 'fulfilled' && result.value)
      .map(result => result.value);
    
    if (validData.length === 0) {
      throw new Error('No weather data available');
    }

    // Logique d'agrégation simple
    const avgTemp = validData.reduce((sum, data) => sum + data.temperature, 0) / validData.length;
    const avgHumidity = validData.reduce((sum, data) => sum + data.humidity, 0) / validData.length;
    
    return {
      city,
      timestamp: new Date().toISOString(),
      temperature: {
        current: Math.round(avgTemp * 10) / 10,
        unit: 'celsius'
      },
      humidity: Math.round(avgHumidity),
      sources: validData.map(data => data.source),
      description: validData[0].description // Prendre la première description
    };
  }
}

module.exports = WeatherService;
```

**Instructions pour les étudiants :**
1. **Démarrage rapide** : Commencer avec Open-Meteo (pas de clé requise)
2. **Inscription APIs** : Créer les comptes en parallèle (activation sous 2h pour OpenWeather)
3. **Configuration** : Ajouter les clés au fichier `.env` quand disponibles
4. **Fallback** : L'API fonctionne même si certaines clés manquent
5. **Tests** : Utiliser les URLs de test fournies pour vérifier les clés

## Phase 3 : Tests de contrat

### 3.1 Validation des schémas JSON
Définir et implémenter des schémas de validation pour :
- Structure des réponses API avec propriétés requises et optionnelles
- Types de données et formats (nombres, chaînes, dates)
- Contraintes de validation (énumérations, plages de valeurs)
- Gestion des propriétés imbriquées (température, conditions météo)

**Exemple de schéma simplifié** :
```javascript
const weatherSchema = {
  type: 'object',
  required: ['city', 'temperature'],
  properties: {
    city: { type: 'string' },
    temperature: {
      type: 'object',
      required: ['current']
      // À compléter...
    }
  }
};
```
- Faites le votre ici 

### 3.2 Tests de contrat avec les APIs externes
- Mock des réponses des APIs tierces
- Tests de robustesse en cas de changement de format
- Validation des transformations de données

## Phase 4 : Tests de charge avec Locust

### Qu'est-ce que Locust ?

**Locust** est un outil de test de charge open-source écrit en Python qui permet de simuler des milliers d'utilisateurs simultanés sur votre application. Contrairement à d'autres outils, Locust utilise du code Python pour définir le comportement des utilisateurs, ce qui le rend très flexible et expressif.

**Avantages de Locust** :
- **Scriptable** : Définition des tests en Python (facile à comprendre et maintenir)
- **Distribué** : Peut répartir la charge sur plusieurs machines
- **Interface web** : Dashboard en temps réel pour monitoring
- **Flexible** : Simulation de comportements utilisateur complexes
- **Extensible** : Intégration facile avec d'autres outils

### 4.1 Installation et configuration Locust

#### Installation
```bash
pip install locust
```

#### Structure des fichiers de test
```
tests/load/
├── locustfile.py          # Fichier principal
├── weather_tasks.py       # Tâches spécifiques météo
└── config.py             # Configuration des tests
```

### 4.2 Configuration des tests de charge

#### Fichier principal (locustfile.py)
```python
from locust import HttpUser, task, between
import random

class WeatherAPIUser(HttpUser):
    # Temps d'attente entre les requêtes (1 à 3 secondes)
    wait_time = between(1, 3)
    
    def on_start(self):
        """Exécuté au démarrage de chaque utilisateur"""
        # Initialisation si nécessaire (login, setup, etc.)
        pass
    
    @task(3)  # Poids 3 : cette tâche sera exécutée 3x plus souvent
    def get_current_weather(self):
        """Test de l'endpoint météo actuelle"""
        cities = ["Paris", "London", "Tokyo", "New York", "Berlin"]
        city = random.choice(cities)
        
        with self.client.get(f"/weather/current/{city}", 
                           catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(2)  # Poids 2
    def get_weather_forecast(self):
        """Test de l'endpoint prévisions"""
        cities = ["Paris", "Madrid", "Rome"]
        city = random.choice(cities)
        
        self.client.get(f"/weather/forecast/{city}")
    
    @task(1)  # Poids 1 : moins fréquent
    def get_weather_history(self):
        """Test de l'endpoint historique"""
        self.client.get("/weather/history/Paris?days=7")
    
    @task(1)
    def health_check(self):
        """Vérification de santé de l'API"""
        self.client.get("/health")
```

#### Configuration avancée
```python
# config.py
class LoadTestConfig:
    # URLs de test
    BASE_URL = "http://localhost:3000"
    
    # Profils de charge
    LIGHT_LOAD = {
        "users": 10,
        "spawn_rate": 2,
        "duration": "2m"
    }
    
    NORMAL_LOAD = {
        "users": 50,
        "spawn_rate": 5,
        "duration": "10m"
    }
    
    STRESS_LOAD = {
        "users": 200,
        "spawn_rate": 10,
        "duration": "15m"
    }
    
    # Villes pour les tests
    CITIES = [
        "Paris", "London", "Berlin", "Madrid", "Rome",
        "Tokyo", "Sydney", "New York", "Los Angeles"
    ]
```

### 4.3 Exécution des tests

#### Commandes de base
```bash
# Test interactif avec interface web
locust -f locustfile.py --host=http://localhost:3000

# Test en ligne de commande
locust -f locustfile.py --host=http://localhost:3000 \
       --users 50 --spawn-rate 5 --run-time 10m --headless

# Test avec rapport HTML
locust -f locustfile.py --host=http://localhost:3000 \
       --users 100 --spawn-rate 10 --run-time 5m \
       --headless --html=report.html
```

#### Test distribué (plusieurs machines) à titre de compréhension
```bash
# Machine maître
locust -f locustfile.py --master --host=http://localhost:3000

# Machines esclaves
locust -f locustfile.py --worker --master-host=192.168.1.100
```

### 4.4 Scénarios de test avancés

#### Test de montée en charge progressive
```python
# scenarios.py
from locust import HttpUser, task, between
import logging

class RampUpTest(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def weather_scenario(self):
        """Scénario réaliste d'utilisation"""
        # 1. Consultation météo actuelle
        response = self.client.get("/weather/current/Paris")
        
        if response.status_code == 200:
            # 2. Si succès, consulter les prévisions
            self.client.get("/weather/forecast/Paris")
            
            # 3. Parfois consulter l'historique (10% des cas)
            if random.random() < 0.1:
                self.client.get("/weather/history/Paris?days=3")

    ### Terminer le par vous même et faites votre propre scénario###
```

#### Validation des réponses
```python
class WeatherAPIUser(HttpUser):
    @task
    def validate_weather_response(self):
        with self.client.get("/weather/current/Paris", 
                           catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Status code: {response.status_code}")
            else:
                try:
                    data = response.json()
                    # Validation de la structure
                    if 'city' not in data or 'temperature' not in data:
                        response.failure("Missing required fields")
                    elif data['city'] != 'Paris':
                        response.failure("Wrong city in response")
                    else:
                        response.success()
                except Exception as e:
                    response.failure(f"Invalid JSON: {e}")
```

### 4.5 Métriques et analyse des résultats

#### Métriques clés à surveiller pendant les tests
- **Temps de réponse** (p50, p95, p99)
- **Taux d'erreur** (pourcentage de requêtes échouées)
- **Débit** (requests/second)
- **Utilisation des ressources** (CPU, mémoire)

#### Interface web Locust
Accessible sur `http://localhost:8089` pendant les tests :
- **Graphiques temps réel** : Temps de réponse et nombre d'utilisateurs
- **Statistiques détaillées** : Par endpoint et méthode HTTP
- **Graphiques de charge** : Distribution des requêtes dans le temps
- **Logs d'erreurs** : Détail des échecs

#### Automatisation des rapports
```python
# Custom listener pour métriques personnalisées
from locust import events
import logging

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    logging.info("Test de charge démarré")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    logging.info("Test de charge terminé")
    
    # Génération de rapport personnalisé
    stats = environment.stats
    
    # Critères de succès/échec
    if stats.total.avg_response_time > 2000:  # > 2 secondes
        logging.error("ÉCHEC: Temps de réponse trop élevé")
    
    if stats.total.num_failures / stats.total.num_requests > 0.05:  # > 5% d'erreurs
        logging.error("ÉCHEC: Taux d'erreur trop élevé")
```
- Jouer avec les paramètres et modifier à votre convenance 

#### Bonnus  Intégration CI/CD
    ### A faire ####

## Phase 5 : Bonus Monitoring et alertes  

### 5.1 Métriques applicatives avec Prometheus
Implémenter la collecte de métriques personnalisées :
- Histogrammes pour mesurer la durée des requêtes HTTP par endpoint
- Compteurs pour traquer les appels aux APIs externes et leurs statuts
- Jauges pour monitorer l'utilisation des ressources système
- Labels pour segmenter les métriques par source de données, méthode HTTP, codes de statut

**Exemple d'initialisation d'une métrique** :
```javascript
const httpRequestDuration = new promClient.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route']
});
```

### 5.2 Dashboard Grafana
Créer des tableaux de bord pour :
- Métriques de performance de l'API
- Santé des sources de données externes
- Utilisation du cache
- Erreurs et alertes

### 5.3 Système d'alertes
- Temps de réponse > 2 secondes
- Taux d'erreur > 5%
- Indisponibilité d'une source de données
- Utilisation mémoire > 80%



## Livrables attendus

1. **Code source** avec architecture claire et tests complets
2. **Documentation API** (OpenAPI/Swagger)
3. **Rapport de tests** incluant les résultats des tests de charge
4. **Configuration monitoring** avec dashboards Grafana
5. **Guide de déploiement** et procédures opérationnelles

## Évaluation

### Critères techniques (60%)
- Qualité du code et respect des bonnes pratiques
- Couverture de tests (objectif : 80%+)
- Performance de l'API (temps de réponse < 500ms)
- Robustesse face aux pannes

### Critères fonctionnels (30%)
- Respect des spécifications
- Qualité de l'agrégation des données
- Pertinence des métriques de monitoring

### Critères de présentation (10%)
- Qualité de la documentation
- Clarté des explications techniques
- Démonstration du monitoring

## Ressources et outils

### APIs météo gratuites
- [OpenWeatherMap](https://openweathermap.org/api) - 1000 calls/jour gratuits
- [WeatherAPI](https://www.weatherapi.com/) - 1M calls/mois gratuits
- [Météo France API](https://portail-api.meteofrance.fr/)

### Outils de développement
- **Postman/Insomnia** : Test des APIs
- **Docker** : Containerisation
- **GitHub Actions** : CI/CD
- **SonarQube** : Analyse de code

### Documentation
- [Locust Documentation](https://docs.locust.io/)
- [Prometheus Getting Started](https://prometheus.io/docs/introduction/getting_started/)
- [Grafana Tutorials](https://grafana.com/tutorials/)

