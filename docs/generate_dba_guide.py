#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Guide pratique DBA — WEB_NATHANAEL v1.22.5"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# ── Couleurs ──────────────────────────────────────────────────────────────────
H_BLUE   = colors.HexColor('#3A6EA5')
H_DARK   = colors.HexColor('#2B5280')
ACCENT   = colors.HexColor('#4A80BC')
TH_BG    = colors.HexColor('#3A6EA5')
ROW_ALT  = colors.HexColor('#EAF0F8')
BORDER   = colors.HexColor('#C5D8F0')
TXT      = colors.HexColor('#1A2A3A')
WHITE    = colors.white
GREEN    = colors.HexColor('#28A745')
GREEN_BG = colors.HexColor('#D4EDDA')
ORANGE   = colors.HexColor('#FD7E14')
ORANGE_BG= colors.HexColor('#FFF3CD')
RED      = colors.HexColor('#DC3545')
RED_BG   = colors.HexColor('#F8D7DA')
FOOTER   = colors.HexColor('#2B5280')

W, H = A4
M = 1.8 * cm

AUTHOR        = "Christophe Lambert"
DATE_CREATE   = "2026-05-06"
DATE_MODIF    = "2026-05-06"
VERSION       = "v 1.22.5"
VERSION_LABEL = "v1.22.5"

# ── Styles ────────────────────────────────────────────────────────────────────
def mk_styles():
    s = getSampleStyleSheet()
    def add(name, **kw):
        s.add(ParagraphStyle(name, **kw))
    add('H1', fontName='Helvetica-Bold', fontSize=14, textColor=H_DARK,
        spaceBefore=14, spaceAfter=5)
    add('H2', fontName='Helvetica-Bold', fontSize=11, textColor=ACCENT,
        spaceBefore=10, spaceAfter=4)
    add('H3', fontName='Helvetica-Bold', fontSize=9.5, textColor=H_DARK,
        spaceBefore=7, spaceAfter=3)
    add('Body', fontName='Helvetica', fontSize=9, textColor=TXT,
        spaceAfter=4, leading=13)
    add('Bold', fontName='Helvetica-Bold', fontSize=9, textColor=TXT,
        spaceAfter=3)
    add('BulletItem', fontName='Helvetica', fontSize=9, textColor=TXT,
        leftIndent=14, spaceAfter=2, leading=13)
    add('CodeBlock', fontName='Courier', fontSize=7.8,
        textColor=colors.HexColor('#1A3A5A'),
        backColor=colors.HexColor('#EAF0F8'),
        leftIndent=8, rightIndent=8, spaceAfter=5, spaceBefore=3, leading=11)
    add('Center', fontName='Helvetica', fontSize=9, textColor=TXT,
        alignment=TA_CENTER)
    add('Warning', fontName='Helvetica-Bold', fontSize=9,
        textColor=colors.HexColor('#856404'),
        backColor=ORANGE_BG, leftIndent=8, rightIndent=8,
        spaceAfter=5, spaceBefore=3, leading=13)
    add('Success', fontName='Helvetica-Bold', fontSize=9,
        textColor=colors.HexColor('#155724'),
        backColor=GREEN_BG, leftIndent=8, rightIndent=8,
        spaceAfter=5, spaceBefore=3, leading=13)
    return s

S = mk_styles()

def hf(canvas, doc):
    canvas.saveState()
    hh = 2.6 * cm
    canvas.setFillColor(H_BLUE); canvas.rect(0, H-hh, W, hh, fill=1, stroke=0)
    canvas.setFillColor(H_DARK); canvas.rect(0, H-hh, W, hh*0.32, fill=1, stroke=0)
    canvas.setFont('Helvetica-Bold', 12); canvas.setFillColor(WHITE)
    canvas.drawCentredString(W/2, H-1.15*cm, doc._title)
    canvas.setFont('Helvetica', 8); canvas.setFillColor(colors.HexColor('#A0C4FF'))
    canvas.drawCentredString(W/2, H-2.2*cm, doc._sub)
    bw, bh = 2.6*cm, 0.58*cm
    bx = W-M-bw; by = H-1.6*cm
    canvas.setFillColor(H_DARK); canvas.roundRect(bx, by, bw, bh, 4, fill=1, stroke=0)
    canvas.setFont('Helvetica-Bold', 8); canvas.setFillColor(colors.HexColor('#A0C4FF'))
    canvas.drawCentredString(bx+bw/2, by+0.14*cm, VERSION)
    fh = 1.05*cm
    canvas.setFillColor(FOOTER); canvas.rect(0, 0, W, fh, fill=1, stroke=0)
    canvas.setFont('Helvetica', 7.5); canvas.setFillColor(colors.HexColor('#C8DEFF'))
    canvas.drawString(M, 0.33*cm, f"Créé le : {DATE_CREATE}   |   Modifié le : {DATE_MODIF}")
    canvas.drawRightString(W-M, 0.33*cm, f"Auteur : {AUTHOR}   |   Page {canvas.getPageNumber()}")
    canvas.restoreState()

def make_doc(path):
    doc = SimpleDocTemplate(path, pagesize=A4,
        leftMargin=M, rightMargin=M, topMargin=3.2*cm, bottomMargin=1.5*cm)
    doc._title = "Board de Nathanaël — Guide pratique DBA"
    doc._sub   = "WEB_NATHANAEL · 4 axes d'amélioration · v1.22.5"
    return doc

def sec(title, level=1):
    st = {1: 'H1', 2: 'H2', 3: 'H3'}[level]
    out = [Paragraph(title, S[st])]
    if level == 1:
        out.append(HRFlowable(width='100%', thickness=1.5, color=H_BLUE, spaceAfter=5))
    return out

def bul(text):
    return Paragraph(f"•  {text}", S['BulletItem'])

def badge(text, bg, fg):
    t = Table([[text]], colWidths=[17*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg),
        ('TEXTCOLOR',  (0,0), (-1,-1), fg),
        ('FONTNAME',   (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE',   (0,0), (-1,-1), 9),
        ('PADDING',    (0,0), (-1,-1), 8),
        ('GRID',       (0,0), (-1,-1), 0.5, fg),
    ]))
    return t

def tbl(rows, widths, head=True):
    t = Table(rows, colWidths=widths)
    style = [
        ('FONTSIZE',  (0,0), (-1,-1), 8.5),
        ('GRID',      (0,0), (-1,-1), 0.4, BORDER),
        ('VALIGN',    (0,0), (-1,-1), 'TOP'),
        ('PADDING',   (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0, 1 if head else 0), (-1,-1), [WHITE, ROW_ALT]),
    ]
    if head:
        style += [
            ('BACKGROUND', (0,0), (-1,0), TH_BG),
            ('TEXTCOLOR',  (0,0), (-1,0), WHITE),
            ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
        ]
    t.setStyle(TableStyle(style))
    return t

# ─────────────────────────────────────────────────────────────────────────────
def build():
    path = "/Users/kurisu/Documents/Visual Code/docs/DOC_DBA_GUIDE_v1.22.5.pdf"
    doc  = make_doc(path)
    story = []

    # ── Introduction ──────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("Guide pratique DBA — WEB_NATHANAEL", S['H1']))
    story.append(HRFlowable(width='100%', thickness=2, color=H_BLUE, spaceAfter=6))
    story.append(Paragraph(
        "Ce guide couvre les 4 axes d'amélioration appliqués en v1.22.4. "
        "Chaque section explique <b>pourquoi</b> c'est important, "
        "<b>comment</b> l'appliquer, et <b>quel script</b> exécuter.",
        S['Body']))
    story.append(Spacer(1, 0.3*cm))

    rows = [
        ["#", "Axe", "Script", "Priorité"],
        ["1", "Index NONCLUSTERED",          "sql/01_indexes.sql",        "Haute"],
        ["2", "Permissions (login dédié)",   "sql/02_permissions.sql",    "Haute"],
        ["3", "Backup / Restauration",       "sql/03_backup.sql",         "Moyenne"],
        ["4", "Plans d'exécution",           "sql/04_execution_plan.sql", "Pédagogique"],
    ]
    story.append(tbl(rows, [0.8*cm, 5.5*cm, 6.0*cm, 2.7*cm]))
    story.append(Spacer(1, 0.4*cm))

    # ── 1. INDEX ──────────────────────────────────────────────────────────────
    story.append(PageBreak())
    story += sec("1. Index NONCLUSTERED")

    story += sec("1.1  Pourquoi ?", level=2)
    story.append(Paragraph(
        "Chaque table possède déjà un index <b>CLUSTERED</b> sur sa clé primaire (créé automatiquement). "
        "Sans autre index, toute requête filtrant sur une autre colonne oblige SQL Server à lire "
        "<b>toutes les lignes</b> de la table — c'est un <b>Table Scan</b>.",
        S['Body']))
    story.append(Paragraph(
        "Un index NONCLUSTERED crée une structure séparée, triée sur la colonne choisie. "
        "SQL Server peut alors sauter directement à la bonne ligne — c'est un <b>Index Seek</b>.",
        S['Body']))

    rows = [
        ["Opération", "Lignes lues", "Analogy"],
        ["Table Scan (sans index)", "TOUTES les lignes", "Lire un livre page par page pour trouver un mot"],
        ["Index Seek (avec index)", "Uniquement les lignes ciblées", "Utiliser l'index en fin de livre"],
    ]
    story.append(tbl(rows, [4.5*cm, 4.5*cm, 8.0*cm]))
    story.append(Spacer(1, 0.2*cm))

    story += sec("1.2  Index créés", level=2)
    rows = [
        ["Index", "Table", "Colonnes", "Pourquoi ces colonnes ?"],
        ["IX_Historique_UserID_ChangeDate",
         "HistoriqueUtilisateurs",
         "UserID, ChangeDate DESC",
         "Les requêtes d'audit filtrent toujours par UserID et trient par date. "
         "Un seul index couvre les deux."],
        ["IX_OrthophonisteMots_MotId",
         "Orthophoniste_Mots",
         "MotId",
         "La PK composite commence par OrthophonisteId. "
         "Chercher par MotId seul faisait un scan complet sans cet index."],
    ]
    story.append(tbl(rows, [5.0*cm, 3.8*cm, 3.5*cm, 4.7*cm]))
    story.append(Spacer(1, 0.2*cm))

    story += sec("1.3  Comment appliquer", level=2)
    story.append(badge(
        "  Exécuter sql/01_indexes.sql dans SSMS ou Azure Data Studio (une seule fois — idempotent)",
        GREEN_BG, colors.HexColor('#155724')))
    story.append(Paragraph(
        "Le script vérifie si l'index existe déjà avant de le créer. "
        "Il peut être exécuté plusieurs fois sans risque (idempotent).",
        S['Body']))

    story += sec("1.4  Règle pour la suite", level=2)
    story.append(Paragraph(
        "Pour chaque nouvelle table, si les requêtes filtrent fréquemment sur une colonne "
        "autre que la PK, il convient de créer un index NONCLUSTERED sur cette colonne.",
        S['Body']))

    # ── 2. PERMISSIONS ────────────────────────────────────────────────────────
    story.append(PageBreak())
    story += sec("2. Permissions — Login dédié par rôle")

    story += sec("2.1  Pourquoi ?", level=2)
    story.append(Paragraph(
        "Par défaut l'API tourne avec le login <b>sa</b> (System Administrator). "
        "C'est l'équivalent de faire tourner un site web en <b>root</b> Linux. "
        "Si une faille est exploitée, l'attaquant peut tout faire : "
        "lire, modifier, supprimer, et même accéder à d'autres bases.",
        S['Body']))
    story.append(badge(
        "  Principe du moindre privilège : accorder uniquement ce dont l'application a besoin.",
        ORANGE_BG, colors.HexColor('#856404')))
    story.append(Spacer(1, 0.2*cm))

    story += sec("2.2  Architecture des logins", level=2)
    rows = [
        ["Login", "Utilisé par", "Droits", "Quand s'en servir"],
        ["sa",
         "L'administrateur (DBA)",
         "Tout — DROP TABLE, CREATE, BACKUP…",
         "SSMS, scripts de maintenance, urgences"],
        ["web_nathanael_app",
         "API Node.js",
         "SELECT/INSERT/UPDATE limités par table",
         "Toutes les requêtes applicatives"],
    ]
    story.append(tbl(rows, [3.5*cm, 3.0*cm, 4.5*cm, 6.0*cm]))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "<b>sa ne disparaît pas.</b> Les deux logins coexistent. "
        "L'administrateur (DBA) utilise sa pour toutes les opérations d'administration depuis SSMS.",
        S['Body']))

    story += sec("2.3  Droits accordés à web_nathanael_app", level=2)
    rows = [
        ["Table", "SELECT", "INSERT", "UPDATE", "DELETE", "Raison du refus"],
        ["Utilisateurs",           "✓","✓","✓","✗","Pas de suppression dans l'app"],
        ["HistoriqueUtilisateurs", "✓","✗","✗","✗","Inserts faits par trigger uniquement"],
        ["Orthophoniste",          "✓","✓","✓","✓","CRUD séances complet"],
        ["Orthophoniste_Mots",     "✓","✓","✗","✓","Liaison séance ↔ mot"],
        ["Mots",                   "✓","✓","✗","✗","Déduplication côté API"],
        ["SiteButtons",            "✓","✓","✓","✗","MERGE = INSERT + UPDATE"],
    ]
    story.append(tbl(rows, [4.0*cm, 1.5*cm, 1.5*cm, 1.8*cm, 1.8*cm, 6.4*cm]))
    story.append(Spacer(1, 0.2*cm))

    story += sec("2.4  Créer un user encore plus limité (exemple)", level=2)
    story.append(Paragraph(
        "Il est possible de créer autant de logins que nécessaire. "
        "Exemple : un login <b>lecture seule sur Orthophoniste</b> pour un partenaire externe :",
        S['Body']))
    story.append(Paragraph(
        "CREATE LOGIN user_ortho WITH PASSWORD='xxx', CHECK_EXPIRATION=OFF, CHECK_POLICY=OFF;<br/>"
        "CREATE USER  user_ortho FOR LOGIN user_ortho;<br/>"
        "GRANT SELECT ON dbo.Orthophoniste      TO user_ortho;<br/>"
        "GRANT SELECT ON dbo.Orthophoniste_Mots TO user_ortho;<br/>"
        "GRANT SELECT ON dbo.Mots               TO user_ortho;<br/>"
        "-- Résultat : SELECT * FROM Utilisateurs → Erreur de permission",
        S['CodeBlock']))

    story += sec("2.5  Comment appliquer", level=2)
    story.append(badge(
        "  Étape 1 — Exécuter sql/02_permissions.sql dans SSMS (avec le login sa)",
        GREEN_BG, colors.HexColor('#155724')))
    story.append(Spacer(1, 0.15*cm))
    story.append(badge(
        "  Étape 2 — Dans .env : changer DB_USER=sa → DB_USER=web_nathanael_app et DB_PASSWORD=MotDePasseApp!2026",
        GREEN_BG, colors.HexColor('#155724')))
    story.append(Spacer(1, 0.15*cm))
    story.append(badge(
        "  Étape 3 — Redémarrer le conteneur Docker (docker-compose restart web-nathanael-api)",
        GREEN_BG, colors.HexColor('#155724')))
    story.append(Spacer(1, 0.2*cm))

    story += sec("2.6  Règle pour la suite", level=2)
    story.append(Paragraph(
        "À chaque nouvelle table créée → ajouter le <code>GRANT</code> correspondant "
        "dans <code>sql/02_permissions.sql</code> et le réexécuter. "
        "Sans <code>GRANT</code>, l'API reçoit une erreur de permission.",
        S['Body']))

    # ── 3. BACKUP ─────────────────────────────────────────────────────────────
    story.append(PageBreak())
    story += sec("3. Backup et restauration")

    story += sec("3.1  Pourquoi ?", level=2)
    story.append(Paragraph(
        "Un conteneur Docker peut crasher, un disque peut mourir, "
        "une fausse manipulation peut supprimer des données. "
        "Sans backup = <b>tout est perdu définitivement</b>.",
        S['Body']))
    story.append(badge(
        "  Règle d'or : 3-2-1 — 3 copies, sur 2 supports différents, dont 1 hors site.",
        ORANGE_BG, colors.HexColor('#856404')))
    story.append(Spacer(1, 0.2*cm))

    story += sec("3.2  Fonctionnement dans ce projet", level=2)
    story.append(Paragraph(
        "SQL Server tourne dans le conteneur <b>sql_server_m4</b>. "
        "Le backup se crée à l'intérieur du conteneur dans <code>/var/opt/mssql/backup/</code>, "
        "puis est copié sur le Mac.",
        S['Body']))
    rows = [
        ["Étape", "Commande / Action", "Où"],
        ["1 — Créer le dossier backup",
         "docker exec sql_server_m4 mkdir -p /var/opt/mssql/backup",
         "Terminal Mac (une seule fois)"],
        ["2 — Backup manuel",
         "Exécuter la section 2 de sql/03_backup.sql",
         "SSMS avec login sa"],
        ["3 — Vérifier l'intégrité",
         "Exécuter la section 3 de sql/03_backup.sql",
         "SSMS"],
        ["4 — Copier sur le Mac",
         "docker cp sql_server_m4:/var/opt/mssql/backup/WEB_NATHANAEL_xxx.bak ~/Desktop/",
         "Terminal Mac"],
        ["5 — Automatiser (optionnel)",
         "Ajouter le cron du Mac (section 5 du script)",
         "Terminal Mac : crontab -e"],
    ]
    story.append(tbl(rows, [3.5*cm, 7.5*cm, 6.0*cm]))
    story.append(Spacer(1, 0.2*cm))

    story += sec("3.3  Restauration", level=2)
    story.append(Paragraph(
        "En cas de problème, la section 4 de <code>sql/03_backup.sql</code> restaure la base. "
        "Elle passe d'abord en <b>SINGLE_USER</b> pour couper les connexions actives, "
        "puis restaure, puis repasse en <b>MULTI_USER</b>.",
        S['Body']))
    story.append(badge(
        "  Important : remplacer le nom du fichier .bak dans les requêtes RESTORE par celui réellement créé.",
        ORANGE_BG, colors.HexColor('#856404')))

    # ── 4. PLANS D'EXÉCUTION ──────────────────────────────────────────────────
    story.append(PageBreak())
    story += sec("4. Plans d'exécution — Optimisation des requêtes")

    story += sec("4.1  Pourquoi ?", level=2)
    story.append(Paragraph(
        "Un plan d'exécution montre <b>comment SQL Server exécute une requête</b> : "
        "quels index il utilise, combien de lignes il lit, où il perd du temps. "
        "C'est l'outil principal du DBA pour diagnostiquer les requêtes lentes.",
        S['Body']))

    story += sec("4.2  Les deux opérations clés", level=2)
    rows = [
        ["Opération", "Signification", "Bon ou mauvais ?"],
        ["Index Seek",
         "SQL Server utilise un index pour aller directement aux bonnes lignes",
         "✓ Bon — accès ciblé"],
        ["Index Scan / Table Scan",
         "SQL Server lit toutes les lignes de la table ou de l'index",
         "⚠ À investiguer — normal sur petites tables, problème sur grandes"],
        ["Key Lookup",
         "L'index trouvé ne contient pas toutes les colonnes demandées, SQL doit retourner à la table",
         "⚠ Envisager un index couvrant (INCLUDE)"],
    ]
    story.append(tbl(rows, [3.5*cm, 7.5*cm, 6.0*cm]))
    story.append(Spacer(1, 0.2*cm))

    story += sec("4.3  Activer le plan dans SSMS", level=2)
    for item in [
        "<b>Plan graphique</b> : Ctrl+M avant d'exécuter → onglet 'Execution Plan' après",
        "<b>Statistiques texte</b> : SET STATISTICS IO ON → colonne 'logical reads' dans les messages",
        "<b>Azure Data Studio</b> : bouton 'Explain' avant d'exécuter",
    ]:
        story.append(bul(item))
    story.append(Spacer(1, 0.2*cm))

    story += sec("4.4  Lire les statistiques IO", level=2)
    story.append(Paragraph("Exemple de sortie de SET STATISTICS IO ON :", S['Body']))
    story.append(Paragraph(
        "-- AVANT index (Table Scan)<br/>"
        "Table 'HistoriqueUtilisateurs'. Scan count 1, logical reads 42<br/><br/>"
        "-- APRÈS index IX_Historique_UserID_ChangeDate (Index Seek)<br/>"
        "Table 'HistoriqueUtilisateurs'. Scan count 1, logical reads 3",
        S['CodeBlock']))
    story.append(Paragraph(
        "<b>logical reads</b> = nombre de pages de 8 Ko lues en mémoire. "
        "Moins il y en a, plus la requête est efficace. "
        "Ici l'index divise les lectures par 14.",
        S['Body']))

    story += sec("4.5  Vérifier l'utilisation des index", level=2)
    story.append(Paragraph(
        "Cette requête montre combien de fois chaque index a été utilisé depuis le dernier démarrage :",
        S['Body']))
    story.append(Paragraph(
        "SELECT i.name AS [Index], s.user_seeks, s.user_scans, s.last_user_seek<br/>"
        "FROM sys.dm_db_index_usage_stats s<br/>"
        "JOIN sys.indexes i ON s.object_id = i.object_id AND s.index_id = i.index_id<br/>"
        "JOIN sys.tables t  ON i.object_id = t.object_id<br/>"
        "WHERE t.name = 'HistoriqueUtilisateurs' AND s.database_id = DB_ID()<br/>"
        "ORDER BY s.user_seeks DESC;",
        S['CodeBlock']))
    story.append(Paragraph(
        "<b>user_seeks</b> élevé → index bien utilisé. "
        "<b>user_scans</b> élevé et <b>user_seeks</b> à 0 → l'index n'est pas utilisé, "
        "peut-être inutile ou mal ciblé.",
        S['Body']))

    story += sec("4.6  Comment s'exercer", level=2)
    story.append(badge(
        "  Exécuter sql/04_execution_plan.sql dans SSMS avec Ctrl+M activé et SET STATISTICS IO ON.",
        GREEN_BG, colors.HexColor('#155724')))
    story.append(Spacer(1, 0.15*cm))
    story.append(Paragraph(
        "En exécutant <code>sql/01_indexes.sql</code> puis les requêtes de ce script, "
        "il est possible d'observer concrètement l'impact des index sur les performances.",
        S['Body']))

    # ── Checklist finale ──────────────────────────────────────────────────────
    story.append(PageBreak())
    story += sec("Checklist — Dans quel ordre faire quoi ?")

    rows = [
        ["Ordre", "Action", "Script", "Durée estimée", "Fait ?"],
        ["1", "Exécuter les index",
         "sql/01_indexes.sql",
         "< 1 min", "☐"],
        ["2", "Créer le login web_nathanael_app",
         "sql/02_permissions.sql",
         "< 1 min", "☐"],
        ["3", "Modifier .env (DB_USER=web_nathanael_app)",
         "Fichier .env",
         "< 1 min", "☐"],
        ["4", "Redémarrer le conteneur API et tester",
         "docker-compose restart",
         "< 2 min", "☐"],
        ["5", "Créer le dossier backup dans le conteneur",
         "Terminal Mac",
         "< 1 min", "☐"],
        ["6", "Faire un premier backup manuel",
         "sql/03_backup.sql §2",
         "< 1 min", "☐"],
        ["7", "Vérifier l'intégrité du backup",
         "sql/03_backup.sql §3",
         "< 1 min", "☐"],
        ["8", "Copier le .bak sur le Mac",
         "docker cp",
         "< 1 min", "☐"],
        ["9", "Tester les plans d'exécution",
         "sql/04_execution_plan.sql",
         "10-15 min", "☐"],
        ["10", "Optionnel : automatiser le backup (cron)",
         "sql/03_backup.sql §5",
         "5 min", "☐"],
    ]
    story.append(tbl(rows, [1.2*cm, 5.5*cm, 4.5*cm, 3.0*cm, 1.8*cm]))

    doc.build(story, onFirstPage=hf, onLaterPages=hf)
    print(f"  [OK] {path}")

if __name__ == '__main__':
    build()
