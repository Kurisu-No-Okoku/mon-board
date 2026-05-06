-- =============================================================================
-- 01_indexes.sql  — Index non-clusterisés WEB_NATHANAEL
-- Version : v1.22.4  |  2026-05-06
-- =============================================================================
-- Pourquoi ces index ?
--   Les PK créent automatiquement un index CLUSTERED sur chaque table.
--   Ces index supplémentaires (NONCLUSTERED) accélèrent les filtres les plus
--   fréquents qui ne portent pas sur la PK.
-- =============================================================================

USE WEB_NATHANAEL;
GO

-- -----------------------------------------------------------------------------
-- HistoriqueUtilisateurs
-- -----------------------------------------------------------------------------
-- Requêtes ciblées : WHERE UserID = X  et  ORDER BY ChangeDate DESC
-- Sans index → Table Scan (lit toutes les lignes)
-- Avec index  → Index Seek (accès direct)

IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE object_id = OBJECT_ID('dbo.HistoriqueUtilisateurs')
      AND name = 'IX_Historique_UserID_ChangeDate'
)
BEGIN
    CREATE NONCLUSTERED INDEX IX_Historique_UserID_ChangeDate
        ON dbo.HistoriqueUtilisateurs (UserID, ChangeDate DESC);

    PRINT 'Index IX_Historique_UserID_ChangeDate créé.';
END
ELSE
    PRINT 'Index IX_Historique_UserID_ChangeDate déjà présent.';
GO

-- -----------------------------------------------------------------------------
-- Orthophoniste_Mots
-- -----------------------------------------------------------------------------
-- La PK composite est (OrthophonisteId, MotId).
-- SQL Server peut donc chercher par OrthophonisteId seul efficacement,
-- mais PAS par MotId seul — il faut un index dédié.

IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE object_id = OBJECT_ID('dbo.Orthophoniste_Mots')
      AND name = 'IX_OrthophonisteMots_MotId'
)
BEGIN
    CREATE NONCLUSTERED INDEX IX_OrthophonisteMots_MotId
        ON dbo.Orthophoniste_Mots (MotId);

    PRINT 'Index IX_OrthophonisteMots_MotId créé.';
END
ELSE
    PRINT 'Index IX_OrthophonisteMots_MotId déjà présent.';
GO

-- -----------------------------------------------------------------------------
-- Vérification
-- -----------------------------------------------------------------------------
SELECT
    t.name          AS [Table],
    i.name          AS [Index],
    i.type_desc     AS [Type],
    i.is_unique     AS [Unique],
    STRING_AGG(c.name, ', ') WITHIN GROUP (ORDER BY ic.key_ordinal) AS [Colonnes]
FROM sys.indexes i
JOIN sys.tables t ON i.object_id = t.object_id
JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
WHERE t.name IN ('HistoriqueUtilisateurs', 'Orthophoniste_Mots',
                 'Utilisateurs', 'Mots', 'Orthophoniste', 'SiteButtons')
  AND ic.is_included_column = 0
GROUP BY t.name, i.name, i.type_desc, i.is_unique
ORDER BY t.name, i.type_desc DESC;
GO
