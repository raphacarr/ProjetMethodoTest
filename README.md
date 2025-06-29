# Projet Méthodologie de Test - API Météo

## Présentation du projet

Ce projet a été réalisé dans le cadre du cours de Méthodologie de Test en Master 2 Informatique. Il s'agit d'une API REST complète qui agrège des données météorologiques provenant de plusieurs sources externes (OpenWeatherMap, WeatherAPI, Open-Meteo).

L'objectif principal était d'appliquer les bonnes pratiques de développement, notamment :
- Le Test-Driven Development (TDD)
- Les tests de contrat
- Les tests de charge
- La mise en place d'un système de monitoring

## Fonctionnalités

L'API propose les endpoints suivants :
- `GET /weather/current/:city` - Météo actuelle
- `GET /weather/forecast/:city` - Prévisions sur 5 jours
- `GET /weather/history/:city` - Données historiques
- `GET /health` - Vérification de l'état de l'API

## Architecture technique

- **Backend** : Python avec FastAPI
- **Cache** : Redis
- **Tests** : pytest
- **Tests de charge** : Locust
- **Monitoring** : Prometheus + Grafana
- **Documentation** : Swagger/OpenAPI (intégré à FastAPI)

## Points forts du projet

1. **Agrégation de données** : L'API interroge plusieurs sources météo en parallèle et agrège les résultats
2. **Robustesse** : Gestion des erreurs et fallback en cas de panne d'une source
3. **Performance** : Mise en cache des résultats avec Redis
4. **Monitoring** : Suivi des performances et des appels API externes
5. **Tests complets** : Tests unitaires, d'intégration, de contrat et de charge

## Structure du projet

```
weather-api/
├── src/               # Code source de l'application
├── tests/             # Tests (unitaires, intégration, contrat, charge)
├── config/            # Fichiers de configuration
├── docker-compose.yml # Configuration des services (API, Redis, Prometheus, Grafana)
└── README.md          # Documentation détaillée
```

Pour plus de détails sur l'installation et l'utilisation, consultez le [README du dossier weather-api](./weather-api/README.md).

## Équipe

Ce projet a été réalisé par :
- Raphaël CARRILHO
- Noah SUHARD
- Keenan SCZCEPKOWSKI

## Licence

Ce projet est distribué sous licence MIT.
