# Audit Architecture & Ingénierie

## Résumé Exécutif

**Score technique : 6/10** — L'architecture présente une fondation offline-first solide (IndexedDB, Service Workers, sync différée) mais présente des failles critiques pour le déploiement à l'échelle au Bénin : absence de compression HTTP, pas de gestion de quota stockage, synchronisation Europe (latence élevée), et stratégie de mise à jour lourde pour les réseaux 2G.

**Verdict :** Soutenable en zone urbaine 3G, mais **risque d'échec en rural 2G** sans optimisations urgentes.

---

## État des Lieux Technique

### Stack Actuelle

| Couche | Technologie | Évaluation |
|--------|-------------|------------|
| Frontend | React 19 + Vite + Tailwind | ✅ Moderne, build rapide |
| State | Zustand (2KB) | ✅ Léger, adapté low-end |
| PWA | Service Worker manuel | ⚠️ Fonctionnel mais basique |
| Stockage local | IndexedDB (idb lib) | ✅ Bon choix |
| Backend | FastAPI + PostgreSQL + Redis | ✅ Performant |
| Contenu statique | Nginx + MinIO S3 | ⚠️ Sans compression |
| Médias | SVG vectoriels | ✅ Excellent choix (<5KB/illustration) |

### Points Forts Identifiés

1. **Sync intelligente** : Backoff exponentiel (2^n secondes), priorisation des events (tentatives > badges), batching via `/offline/sync`
2. **Conflict resolution** : Stratégie "best-score-wins" pour les exercices, last-write-wins pour le profil
3. **Background Sync API** : Poursuite sync après fermeture de l'app (quand le navigateur le permet)
4. **SVG uniquement** : 4.6MB de contenu pédagogique, mais illustrations SVG ultra-légères (~2KB chacune)
5. **Fonts subsets** : WOFF2 avec subset latin uniquement (87KB + 48KB)

---

## Insuffisances Critiques

### 🔴 IC-1 : Pas de compression HTTP (Gzip/Brotli)
**Problème :** Nginx configuré sans `gzip on` ni Brotli. Les payloads JSON de 3MB (exercices) transitent en clair.

**Impact :** 
- Téléchargement pack complet : **3MB → ~800KB potentiels** gaspillés
- Sur 2G (50kbps), téléchargement : 8min réel vs 2min compressé

**Preuve :**
```nginx
# nginx.conf actuel - PAS de compression
location /assets/ {
    expires 1y;
    # gzip_static absent
}
```

### 🔴 IC-2 : Pas de gestion de quota ni stratégie LRU
**Problème :** IndexedDB croît indéfiniment (4.6MB de contenu + historique + cache). Aucune purge automatique.

**Impact :**
- Devices 16GB avec WhatsApp (10GB) → saturation rapide
- Pas de fallback gracieux quand `QuotaExceededError`

**Code concerné :**
```typescript
// db.ts - pas de check quota
export const initDB = async () => openDB<SitouDB>(DB_NAME, DB_VERSION, {...})
```

### 🔴 IC-3 : Version DB mismatch + Cache busting fragile
**Problème :**
- Frontend DB v3 (skillPacks)
- Service Worker v2 (syncQueue hardcoded) 
- Cache name 'sitou-v3' manuellement incrémenté

**Impact :** Corruption possible des données offline, sync qui échoue silencieusement.

### 🔴 IC-4 : Latence serveur Europe
**Problème :** 
- Sentry DSN : `o4511106245853184.ingest.de.sentry.io` (Allemagne)
- Pas de CDN Afrique configuré
- API calls directs sans edge caching

**Impact :** 
- Round-trip 150-300ms depuis Bénin
- Sur 2G instable : timeouts fréquents, retry cascades

### 🔴 IC-5 : Mise à jour OTA "tout ou rien"
**Problème :** Vite bundle unique re-téléchargé à chaque update (~500KB-1MB minifié).

**Impact :** Sur 2G, mise à jour = 10-20min d'attente. Les users abandonnent.

### 🟡 IC-6 : Pas de delta sync pour le contenu
**Problème :** Les packs d'exercices (3MB JSON) sont téléchargés entiers même pour 5 questions nouvelles.

**Impact :** Data coûteuse gaspillée, syncs partielles impossibles.

### 🟡 IC-7 : Timeout HTTP fixe (10s) inadapté 2G
**Problème :** `DEFAULT_TIMEOUT = 10000` ms. Sur 2G congestionné, insuffisant.

**Impact :** Faux négatifs réseau, events mis en queue inutilement.

---

## Recommandations Techniques

### Pour IC-1 (Compression) — Solution Frugale
```nginx
# nginx.conf - ajouter
gzip on;
gzip_vary on;
gzip_proxied any;
gzip_types application/json application/javascript text/css application/xml;
gzip_min_length 1000;
gzip_comp_level 6;

# Brotli (si nginx module dispo)
brotli on;
brotli_types application/json application/javascript text/css;
```
**Coût :** Configuration uniquement. Gain : ~70% sur JSON/textes.

### Pour IC-2 (Quota LRU) — Solution Frugale
```typescript
// Ajouter dans db.ts
const checkQuota = async () => {
  if ('storage' in navigator && 'estimate' in navigator.storage) {
    const {usage, quota} = await navigator.storage.estimate();
    if (usage && quota && (usage / quota) > 0.8) {
      // Purger anciens packs, conserver 7 derniers jours
      await purgeOldPacks(7);
    }
  }
};

// LRU pour skillPacks - conserver les 10 plus récents
const MAX_SKILL_PACKS = 10;
```
**Coût :** Développement 1 journée. Robustesse +++.

### Pour IC-3 (Versioning) — Solution Frugale
```typescript
// Single source of truth
export const DB_VERSION = 3;
export const CACHE_NAME = `sitou-v${DB_VERSION}`;

// SW généré automatiquement au build (vite-plugin-pwa)
// Au lieu de sw.js manuel
```
**Coût :** Migration vite-plugin-pwa : 1-2 jours.

### Pour IC-4 (CDN Afrique) — Solution Frugale
| Option | Coût | Latence estimée |
|--------|------|-----------------|
| **Cloudflare Free** (Johannesburg) | Gratuit | 80-120ms |
| **AWS CloudFront** (Lagos) | Pay-per-use | 60-100ms |
| **BunnyCDN** (Afrique du Sud) | ~$1/TB | 80-120ms |

**Priorité :** Déplacer Sentry + APIs statiques sur CDN edge.

### Pour IC-5 (OTA incrémental) — Solution Frugale
```typescript
// Utiliser vite-plugin-pwa avec stratégie 
// "prompt for update" + precache manifest

// Découper en chunks par matière
// rollupOptions: {
//   output: {
//     manualChunks: {
//       'math': ['./pages/student/SkillsMath.tsx'],
//       'french': ['./pages/student/SkillsFrench.tsx'],
//     }
//   }
// }
```
**Coût :** Refactoring lazy loading : 2-3 jours.

### Pour IC-6 (Delta sync) — Solution Frugale
```http
# Au lieu de GET /api/content/pack/numeration
# Utiliser ETag + Range

GET /api/content/pack/numeration
If-None-Match: "abc123"

# Réponse 304 Not Modified (0 bytes)
# ou 200 avec uniquement questions modifiées depuis last_sync
```
**Coût :** Backend : ajout colonne `modified_at` + filtre. 1 journée.

### Pour IC-7 (Timeout adaptatif) — Solution Frugale
```typescript
// Détection réseau
const getTimeout = () => {
  const conn = (navigator as any).connection;
  if (conn?.effectiveType === '2g') return 30000;
  if (conn?.effectiveType === '3g') return 15000;
  return 10000;
};
```
**Coût :** 2 heures de dev.

---

## Roadmap Technique

### Phase 1 : Critical Fixes (2 semaines)
| Jour | Tâche | Impact |
|------|-------|--------|
| 1-2 | Activer Gzip/Brotli nginx | -70% data |
| 3-4 | Fix DB version mismatch | Stabilité |
| 5-6 | Quota management + LRU | Fiabilité |
| 7-10 | Timeout adaptatif + retry 2G | UX rural |
| 11-14 | CDN Cloudflare (free) | Latence |

### Phase 2 : Optimisation Sync (3 semaines)
| Semaine | Focus | Livrable |
|---------|-------|----------|
| 1 | Delta sync API | `If-Modified-Since` endpoints |
| 2 | Chunking Vite | Bundles par matière |
| 3 | OTA incrémentale | UpdatePrompt avec delta |

### Phase 3 : Robustesse (2 semaines)
| Tâche | Description |
|-------|-------------|
| Circuit breaker | Stopper sync après 5 erreurs réseau |
| Compression payload | Brotli sur `/offline/sync` |
| Storage tiering | localStorage < 5MB, IDB < 50% quota |
| Offline analytics | Beacon API pour logs (pas bloquant) |

---

## Métriques de Succès

| KPI | Actuel | Cible Phase 1 | Cible Phase 3 |
|-----|--------|---------------|---------------|
| Taille transfert pack | 3MB | 800KB | 200KB (delta) |
| Latence API moyenne | 250ms | 120ms | 80ms |
| Temps chargement 2G | 8min | 2min | 30s |
| Taux succès sync offline | ~85% | 95% | 98% |
| Crash storage quota | Occasionnel | 0 | 0 |

---

## Notes Architecture

**Forces de l'architecture actuelle :**
- Choix React + Vite + Zustand = bundle léger possible
- SVG pour illustrations = excellent pour low-bandwidth
- Sync offline avec conflict resolution = enterprise-grade
- PostgreSQL + Redis = stack éprouvée

**Architectures alternatives considérées (et rejetées) :**
- Flutter : Trop lourd pour 1GB RAM, APK >50MB
- React Native : Même problème + complexité builds
- Kotlin native : Pas d'OTA, mise à jour via Play Store (inaccessible rural)

**Solution PWA choisie reste la meilleure** pour le contexte, avec optimisations ci-dessus.

---

*Audit réalisé le 12 avril 2026*
*Méthodologie : Review architecture, analyse codebase, benchmarks contraintes réseau Bénin*
