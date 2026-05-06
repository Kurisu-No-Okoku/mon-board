-- =============================================================================
-- 03_backup.sql  — Stratégie de sauvegarde WEB_NATHANAEL
-- Version : v1.22.4  |  2026-05-06
-- =============================================================================
-- Contexte : SQL Server tourne dans un conteneur Docker sur Mac Mini.
-- Le dossier /var/opt/mssql/backup est monté via volume Docker.
-- =============================================================================

USE master;
GO

-- -----------------------------------------------------------------------------
-- 1. Créer le dossier de backup dans le conteneur (à exécuter une seule fois)
-- -----------------------------------------------------------------------------
-- Dans le terminal Mac, pas dans SSMS :
--   docker exec sql_server_m4 mkdir -p /var/opt/mssql/backup
-- -----------------------------------------------------------------------------

-- -----------------------------------------------------------------------------
-- 2. Backup complet manuel
-- -----------------------------------------------------------------------------
DECLARE @filename NVARCHAR(255) =
    '/var/opt/mssql/backup/WEB_NATHANAEL_' +
    FORMAT(GETDATE(), 'yyyyMMdd_HHmm') + '.bak';

BACKUP DATABASE WEB_NATHANAEL
    TO DISK = @filename
    WITH
        FORMAT,                  -- écrase si fichier existant
        INIT,                    -- nouvelle séquence de backup
        NAME = 'WEB_NATHANAEL — Backup complet',
        STATS = 10;              -- affiche la progression tous les 10%

PRINT 'Backup créé : ' + @filename;
GO

-- -----------------------------------------------------------------------------
-- 3. Vérifier l'intégrité du backup
-- -----------------------------------------------------------------------------
-- Remplace le nom du fichier par celui généré au-dessus
RESTORE VERIFYONLY
    FROM DISK = '/var/opt/mssql/backup/WEB_NATHANAEL_20260506_1200.bak';
GO

-- -----------------------------------------------------------------------------
-- 4. Restauration (en cas de besoin)
-- -----------------------------------------------------------------------------
-- /!\ Met la base en mode single-user pour éviter les connexions actives
ALTER DATABASE WEB_NATHANAEL SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
GO

RESTORE DATABASE WEB_NATHANAEL
    FROM DISK = '/var/opt/mssql/backup/WEB_NATHANAEL_20260506_1200.bak'
    WITH REPLACE,   -- écrase la base existante
         RECOVERY,  -- met la base en ligne immédiatement après
         STATS = 10;
GO

ALTER DATABASE WEB_NATHANAEL SET MULTI_USER;
GO

-- =============================================================================
-- 5. Automatisation via Docker (cron sur le Mac)
-- =============================================================================
-- Ajouter dans le crontab du Mac (crontab -e) :
--
--   0 2 * * * docker exec sql_server_m4 /opt/mssql-tools/bin/sqlcmd \
--     -S localhost -U sa -P "$SA_PASSWORD" \
--     -Q "BACKUP DATABASE WEB_NATHANAEL TO DISK='/var/opt/mssql/backup/WEB_NATHANAEL_$(date +\%Y\%m\%d).bak' WITH FORMAT, INIT, STATS=10"
--
-- → Sauvegarde automatique chaque nuit à 2h00.
--
-- Pour copier le .bak hors du conteneur (vers le Mac) :
--   docker cp sql_server_m4:/var/opt/mssql/backup/WEB_NATHANAEL_20260506.bak ~/Desktop/
-- =============================================================================
