# Runbooks Opérationnels — Sitou

## 1. Restauration Base de Données

**Symptôme** : Données corrompues, migration échouée, ou perte de données.

```bash
# 1. Lister les backups disponibles
ls -la /var/backups/ilma/daily/
ls -la /var/backups/ilma/weekly/

# 2. Arrêter l'API (éviter les écritures pendant la restauration)
docker compose stop api

# 3. Restaurer depuis un backup
gunzip -c /var/backups/ilma/daily/ilma_daily_YYYYMMDD_HHMMSS.sql.gz \
  | docker exec -i ilma-db psql -U ilma_user -d ilma_db

# 4. Redémarrer l'API
docker compose start api

# 5. Vérifier
docker compose logs api --tail=50
curl -s http://localhost:8000/api/v1/health | jq .
```

## 2. Downtime Serveur

**Symptôme** : Application inaccessible, erreurs 502/503.

```bash
# 1. Vérifier l'état des containers
docker compose ps

# 2. Si un container est down, le relancer
docker compose up -d

# 3. Vérifier les logs
docker compose logs --tail=100 api
docker compose logs --tail=100 nginx

# 4. Si disque plein
df -h
docker system prune -f  # Nettoyer images/containers inutilisés

# 5. Si mémoire saturée
free -h
docker stats --no-stream
```

## 3. Violation de Données (Breach Protocol)

**Symptôme** : Accès non autorisé détecté, données exposées.

1. **Isoler** : Couper l'accès réseau si nécessaire
2. **Évaluer** : Vérifier les audit logs (`audit_logs` table)
3. **Contenir** : Révoquer les tokens compromis, changer les secrets
4. **Notifier** : Informer l'APDP dans les 72h (obligation légale)
5. **Remédier** : Corriger la vulnérabilité, rotation des credentials

```bash
# Vérifier les connexions suspectes
docker exec ilma-db psql -U ilma_user -d ilma_db \
  -c "SELECT action, ip_address, created_at FROM audit_logs ORDER BY created_at DESC LIMIT 50;"

# Rotation du SECRET_KEY (invalide tous les tokens)
# 1. Générer une nouvelle clé
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
# 2. Mettre à jour dans .env
# 3. Redémarrer: docker compose restart api
```

## 4. Fournisseur de Paiement Indisponible

**Symptôme** : KKiaPay ou FedaPay retourne des erreurs.

1. Vérifier le status page du fournisseur
2. Les paiements en attente restent en `PENDING` — ils seront retraités
3. Si prolongé, basculer vers l'autre fournisseur via la config

```bash
# Vérifier les paiements en échec récents
docker exec ilma-db psql -U ilma_user -d ilma_db \
  -c "SELECT provider, status, count(*) FROM payments WHERE created_at > now() - interval '1 hour' GROUP BY provider, status;"
```

## 5. Contacts d'Urgence

| Rôle | Contact |
|------|---------|
| Tech Lead | (à renseigner) |
| DPO | dpo@sitou.bj |
| APDP (breach) | apdp.bj |
| KKiaPay support | support@kkiapay.me |
| FedaPay support | support@fedapay.com |
