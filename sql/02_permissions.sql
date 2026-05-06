-- =============================================================================
-- 02_permissions.sql  — Login applicatif à droits limités
-- Version : v1.22.4  |  2026-05-06
-- =============================================================================
-- Problème actuel : l'API tourne avec le login "sa" (super-administrateur).
-- Si une faille d'injection SQL est exploitée, l'attaquant a un accès total.
--
-- Solution : créer un login dédié avec uniquement les droits nécessaires.
-- Principe du moindre privilège : accorder juste ce qu'il faut, rien de plus.
-- =============================================================================

USE master;
GO

-- -----------------------------------------------------------------------------
-- 1. Créer le login SQL Server (niveau serveur)
-- -----------------------------------------------------------------------------
-- Remplace 'MotDePasseApp!2026' par un mot de passe fort
IF NOT EXISTS (SELECT 1 FROM sys.server_principals WHERE name = 'web_nathanael_app')
BEGIN
    CREATE LOGIN web_nathanael_app
        WITH PASSWORD = 'MotDePasseApp!2026',
             CHECK_POLICY = OFF,          -- Azure SQL Edge ne supporte pas CHECK_POLICY
             CHECK_EXPIRATION = OFF;
    PRINT 'Login web_nathanael_app créé.';
END
ELSE
    PRINT 'Login web_nathanael_app déjà présent.';
GO

-- -----------------------------------------------------------------------------
-- 2. Créer l'utilisateur dans WEB_NATHANAEL (niveau base)
-- -----------------------------------------------------------------------------
USE WEB_NATHANAEL;
GO

IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'web_nathanael_app')
BEGIN
    CREATE USER web_nathanael_app FOR LOGIN web_nathanael_app;
    PRINT 'User web_nathanael_app créé dans WEB_NATHANAEL.';
END
ELSE
    PRINT 'User web_nathanael_app déjà présent.';
GO

-- -----------------------------------------------------------------------------
-- 3. Accorder les droits table par table
-- -----------------------------------------------------------------------------
-- Utilisateurs : lecture + modification (pas de suppression — l'API n'en a pas)
GRANT SELECT, INSERT, UPDATE ON dbo.Utilisateurs           TO web_nathanael_app;

-- HistoriqueUtilisateurs : lecture uniquement (les inserts sont faits par trigger)
GRANT SELECT                 ON dbo.HistoriqueUtilisateurs TO web_nathanael_app;

-- Orthophoniste : CRUD complet (l'API crée/lit/supprime des séances)
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.Orthophoniste  TO web_nathanael_app;

-- Orthophoniste_Mots : CRUD complet (liaison séance ↔ mot)
GRANT SELECT, INSERT, DELETE ON dbo.Orthophoniste_Mots     TO web_nathanael_app;

-- Mots : lecture + insertion (pas de suppression — dédupliqués côté API)
GRANT SELECT, INSERT         ON dbo.Mots                   TO web_nathanael_app;

-- SiteButtons : lecture + modification (MERGE utilisé par l'API)
GRANT SELECT, UPDATE, INSERT ON dbo.SiteButtons            TO web_nathanael_app;

PRINT 'Droits accordés à web_nathanael_app.';
GO

-- -----------------------------------------------------------------------------
-- 4. Vérification des droits accordés
-- -----------------------------------------------------------------------------
SELECT
    dp.name         AS [Objet],
    p.permission_name,
    p.state_desc    AS [Etat]
FROM sys.database_permissions p
JOIN sys.database_principals u ON p.grantee_principal_id = u.principal_id
JOIN sys.objects dp            ON p.major_id = dp.object_id
WHERE u.name = 'web_nathanael_app'
ORDER BY dp.name, p.permission_name;
GO

-- =============================================================================
-- 5. Mettre à jour le .env pour utiliser ce login à la place de "sa"
-- =============================================================================
-- Dans .env / docker-compose.yml, changer :
--   DB_USER=sa
--   DB_PASSWORD=<mot_de_passe_sa>
-- Par :
--   DB_USER=web_nathanael_app
--   DB_PASSWORD=MotDePasseApp!2026
-- =============================================================================
