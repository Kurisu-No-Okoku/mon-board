-- =============================================================================
-- 04_execution_plan.sql  — Comprendre les plans d'exécution
-- Version : v1.22.4  |  2026-05-06
-- =============================================================================
-- Un plan d'exécution montre COMMENT SQL Server exécute une requête.
-- Deux opérations clés à reconnaître :
--
--   Table Scan / Clustered Index Scan  → lit TOUTES les lignes  (mauvais sur grande table)
--   Index Seek                         → accès direct à la bonne ligne (bon)
-- =============================================================================

USE WEB_NATHANAEL;
GO

-- =============================================================================
-- ÉTAPE 1 — Activer les statistiques I/O (dans SSMS ou Azure Data Studio)
-- =============================================================================
SET STATISTICS IO ON;
SET STATISTICS TIME ON;
GO

-- =============================================================================
-- ÉTAPE 2 — Comparer avant/après index
-- =============================================================================

-- Requête A : filtre sur UserID (colonne indexée après 01_indexes.sql)
-- Avant index → Clustered Index Scan  (lit toute la table)
-- Après index → Index Seek            (saute directement)
SELECT LogID, ActionType, OldValue, NewValue, ChangeDate
FROM dbo.HistoriqueUtilisateurs
WHERE UserID = 5
ORDER BY ChangeDate DESC;
GO

-- Requête B : filtre sur plage de dates
SELECT LogID, UserID, ActionType, ChangeDate
FROM dbo.HistoriqueUtilisateurs
WHERE ChangeDate >= '2026-05-01' AND ChangeDate < '2026-05-07';
GO

-- Requête C : recherche de tous les mots d'une séance orthophoniste
-- Sans IX_OrthophonisteMots_MotId → Scan de Orthophoniste_Mots
-- Avec index → Seek direct sur MotId
SELECT M.Mot
FROM dbo.Orthophoniste_Mots OM
JOIN dbo.Mots M ON OM.MotId = M.Id
WHERE OM.OrthophonisteId = 10;
GO

SET STATISTICS IO OFF;
SET STATISTICS TIME OFF;
GO

-- =============================================================================
-- ÉTAPE 3 — Lire la sortie STATISTICS IO
-- =============================================================================
-- Exemple de sortie pour Requête A SANS index :
--   Table 'HistoriqueUtilisateurs'. Scan count 1, logical reads 42
--
-- Exemple de sortie AVEC index IX_Historique_UserID_ChangeDate :
--   Table 'HistoriqueUtilisateurs'. Scan count 1, logical reads 3
--
-- "logical reads" = nombre de pages lues en mémoire
-- Moins il y en a, plus la requête est efficace.
-- =============================================================================

-- =============================================================================
-- ÉTAPE 4 — Plan graphique dans SSMS / Azure Data Studio
-- =============================================================================
-- Dans SSMS : Ctrl+M  (ou bouton "Include Actual Execution Plan")
-- Dans Azure Data Studio : bouton "Explain" avant d'exécuter
--
-- Icônes à surveiller :
--   Flèche épaisse entre nœuds   → beaucoup de données transférées (mauvais signe)
--   Table Scan / Index Scan       → lecture complète (chercher pourquoi)
--   Index Seek                    → accès ciblé  (bon)
--   Key Lookup                    → index partiel, SQL doit retourner à la table
--                                   (envisager un index couvrant avec INCLUDE)
-- =============================================================================

-- =============================================================================
-- ÉTAPE 5 — Voir les index utilisés dynamiquement
-- =============================================================================
SELECT
    i.name          AS [Index],
    s.user_seeks    AS [Seeks],    -- nombre de fois utilisé efficacement
    s.user_scans    AS [Scans],    -- nombre de fois parcouru entièrement
    s.user_lookups  AS [Lookups],
    s.last_user_seek
FROM sys.dm_db_index_usage_stats s
JOIN sys.indexes i ON s.object_id = i.object_id AND s.index_id = i.index_id
JOIN sys.tables t  ON i.object_id = t.object_id
WHERE t.name IN ('HistoriqueUtilisateurs', 'Orthophoniste_Mots')
  AND s.database_id = DB_ID()
ORDER BY s.user_seeks DESC;
GO
-- Note : cette vue se remet à zéro au redémarrage de SQL Server.
