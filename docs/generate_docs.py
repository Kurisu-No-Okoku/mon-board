#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether, PageBreak
)
from reportlab.platypus.flowables import Flowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Circle
from reportlab.graphics import renderPDF
import datetime

# ─── Couleurs ──────────────────────────────────────────────────────────────────
HEADER_BLUE   = colors.HexColor('#3A6EA5')   # bleu moyen principal
HEADER_DARK   = colors.HexColor('#2B5280')   # bleu foncé
HEADER_LIGHT  = colors.HexColor('#5A8EC5')   # bleu clair
ACCENT        = colors.HexColor('#4A80BC')
TABLE_HEADER  = colors.HexColor('#3A6EA5')
TABLE_ROW_ALT = colors.HexColor('#EAF0F8')
TABLE_BORDER  = colors.HexColor('#C5D8F0')
TEXT_DARK     = colors.HexColor('#1A2A3A')
TEXT_MED      = colors.HexColor('#3A4A5A')
TEXT_LIGHT    = colors.HexColor('#6A7A8A')
WHITE         = colors.white
SUCCESS       = colors.HexColor('#28A745')
WARNING       = colors.HexColor('#FFC107')
DANGER        = colors.HexColor('#DC3545')
FOOTER_BG     = colors.HexColor('#2B5280')

W, H = A4
MARGIN = 2 * cm

# ─── Métadonnées communes ──────────────────────────────────────────────────────
AUTHOR        = "Kurisu-No-Okoku"
DATE_CREATION = "2026-05-05"
DATE_MODIF    = "2026-05-06"

# ─── Helpers ──────────────────────────────────────────────────────────────────

def make_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        'DocTitle',
        fontName='Helvetica-Bold',
        fontSize=22,
        textColor=WHITE,
        alignment=TA_CENTER,
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        'DocSubtitle',
        fontName='Helvetica',
        fontSize=11,
        textColor=colors.HexColor('#C8DEFF'),
        alignment=TA_CENTER,
        spaceAfter=2,
    ))
    styles.add(ParagraphStyle(
        'DocVersion',
        fontName='Helvetica-BoldOblique',
        fontSize=10,
        textColor=colors.HexColor('#A0C4FF'),
        alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        'H1',
        fontName='Helvetica-Bold',
        fontSize=15,
        textColor=HEADER_DARK,
        spaceBefore=14,
        spaceAfter=6,
        borderPad=4,
    ))
    styles.add(ParagraphStyle(
        'H2',
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=ACCENT,
        spaceBefore=10,
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        'Body',
        fontName='Helvetica',
        fontSize=9.5,
        textColor=TEXT_DARK,
        spaceAfter=5,
        leading=14,
    ))
    styles.add(ParagraphStyle(
        'BodyBold',
        fontName='Helvetica-Bold',
        fontSize=9.5,
        textColor=TEXT_DARK,
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        'BulletItem',
        fontName='Helvetica',
        fontSize=9.5,
        textColor=TEXT_DARK,
        leftIndent=16,
        spaceAfter=3,
        leading=13,
    ))
    styles.add(ParagraphStyle(
        'CodeBlock',
        fontName='Courier',
        fontSize=8.5,
        textColor=colors.HexColor('#1A3A5A'),
        backColor=colors.HexColor('#EAF0F8'),
        leftIndent=10,
        rightIndent=10,
        spaceAfter=6,
        spaceBefore=4,
        leading=12,
        borderPad=4,
    ))
    styles.add(ParagraphStyle(
        'FooterText',
        fontName='Helvetica',
        fontSize=7.5,
        textColor=colors.HexColor('#C8DEFF'),
        alignment=TA_CENTER,
    ))
    return styles

STYLES = make_styles()


def header_footer(canvas, doc):
    """En-tête bleu + pied de page bleu foncé."""
    canvas.saveState()

    # ── En-tête ─────────────────────────────────────────────────────────────
    hh = 2.8 * cm
    canvas.setFillColor(HEADER_BLUE)
    canvas.rect(0, H - hh, W, hh, fill=1, stroke=0)
    # Dégradé simulé (deux rectangles)
    canvas.setFillColor(HEADER_DARK)
    canvas.rect(0, H - hh, W, hh * 0.35, fill=1, stroke=0)

    canvas.setFont('Helvetica-Bold', 13)
    canvas.setFillColor(WHITE)
    canvas.drawCentredString(W / 2, H - 1.2 * cm, doc._page_title)

    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#A0C4FF'))
    canvas.drawCentredString(W / 2, H - 1.9 * cm, doc._page_subtitle)

    # Badge version (coin droit)
    badge_w, badge_h = 2.8 * cm, 0.6 * cm
    bx = W - MARGIN - badge_w
    by = H - 1.65 * cm
    canvas.setFillColor(HEADER_DARK)
    canvas.roundRect(bx, by, badge_w, badge_h, 4, fill=1, stroke=0)
    canvas.setFont('Helvetica-Bold', 8)
    canvas.setFillColor(colors.HexColor('#A0C4FF'))
    canvas.drawCentredString(bx + badge_w / 2, by + 0.15 * cm, doc._version_label)

    # ── Pied de page ─────────────────────────────────────────────────────────
    fh = 1.1 * cm
    canvas.setFillColor(FOOTER_BG)
    canvas.rect(0, 0, W, fh, fill=1, stroke=0)

    canvas.setFont('Helvetica', 7.5)
    canvas.setFillColor(colors.HexColor('#C8DEFF'))
    left_txt  = f"Créé le : {DATE_CREATION}   |   Modifié le : {DATE_MODIF}"
    right_txt = f"Auteur : {AUTHOR}   |   Page {canvas.getPageNumber()}"
    canvas.drawString(MARGIN, 0.35 * cm, left_txt)
    canvas.drawRightString(W - MARGIN, 0.35 * cm, right_txt)

    canvas.restoreState()


def make_doc(path, page_title, page_subtitle, version_label):
    doc = SimpleDocTemplate(
        path,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=3.4 * cm,
        bottomMargin=1.6 * cm,
    )
    doc._page_title    = page_title
    doc._page_subtitle = page_subtitle
    doc._version_label = version_label
    return doc


def section_header(title, level=1):
    style = STYLES['H1'] if level == 1 else STYLES['H2']
    items = [Paragraph(title, style)]
    if level == 1:
        items.append(HRFlowable(width='100%', thickness=1.5,
                                color=HEADER_BLUE, spaceAfter=6))
    return items


def bullet(text):
    return Paragraph(f"•  {text}", STYLES['BulletItem'])


def info_table(rows, col_widths=None):
    if col_widths is None:
        col_widths = [5 * cm, 10.5 * cm]
    t = Table(rows, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#EAF0F8')),
        ('BACKGROUND', (1, 0), (1, -1), WHITE),
        ('TEXTCOLOR',  (0, 0), (0, -1), HEADER_DARK),
        ('FONTNAME',   (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME',   (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE',   (0, 0), (-1, -1), 9),
        ('VALIGN',     (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID',       (0, 0), (-1, -1), 0.5, TABLE_BORDER),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.HexColor('#F5F9FF'), WHITE]),
        ('PADDING',    (0, 0), (-1, -1), 6),
    ]))
    return t


def api_table(rows, col_widths=None):
    if col_widths is None:
        col_widths = [3.2 * cm, 1.8 * cm, 2.5 * cm, 3.0 * cm, 5.0 * cm]
    t = Table(rows, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('BACKGROUND',  (0, 0), (-1, 0), TABLE_HEADER),
        ('TEXTCOLOR',   (0, 0), (-1, 0), WHITE),
        ('FONTNAME',    (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',    (0, 0), (-1, -1), 8.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, TABLE_ROW_ALT]),
        ('GRID',        (0, 0), (-1, -1), 0.4, TABLE_BORDER),
        ('VALIGN',      (0, 0), (-1, -1), 'TOP'),
        ('PADDING',     (0, 0), (-1, -1), 5),
        ('FONTNAME',    (0, 1), (0, -1), 'Courier-Bold'),
        ('TEXTCOLOR',   (0, 1), (0, -1), HEADER_DARK),
    ]))
    return t


# ═══════════════════════════════════════════════════════════════════════════════
# DOC 1 — SITE (FRONT-END)
# ═══════════════════════════════════════════════════════════════════════════════

def build_site_doc():
    path = "/Users/kurisu/Documents/Visual Code/docs/DOC_SITE_v1.22.1.pdf"
    doc  = make_doc(path,
                    "Board de Nathanaël — Documentation Site",
                    "Documentation technique et fonctionnelle — Front-end",
                    "v 1.22.1")

    S = STYLES
    story = []

    # ── Page de garde ────────────────────────────────────────────────────────
    story.append(Spacer(1, 1.2 * cm))
    story.append(Paragraph("Documentation Site Front-End", S['H1']))
    story.append(HRFlowable(width='100%', thickness=2, color=HEADER_BLUE, spaceAfter=8))
    story.append(info_table([
        ["Projet",    "Board de Nathanaël"],
        ["Type",      "Application web mono-page (SPA statique)"],
        ["Version",   "1.22.1"],
        ["URL",       "https://board.kurisu-no-okoku.com"],
        ["Technos",   "HTML5 · CSS3 · JavaScript vanilla"],
        ["Date doc.", DATE_CREATION],
    ]))
    story.append(Spacer(1, 0.5 * cm))

    # ── 1. Présentation ──────────────────────────────────────────────────────
    story += section_header("1. Présentation générale")
    story.append(Paragraph(
        "Le Board de Nathanaël est une application web personnelle à usage familial. "
        "Elle centralise plusieurs fonctionnalités (suivi orthophoniste, boutons configurables, "
        "gestion des comptes) dans une interface sombre/clair responsive, sans framework JavaScript.",
        S['Body']))

    # ── 2. Architecture ──────────────────────────────────────────────────────
    story += section_header("2. Architecture front-end")
    story.append(Paragraph("Fichiers principaux :", S['BodyBold']))
    story.append(info_table([
        ["index.html",          "SPA principale — toute l'interface utilisateur"],
        ["reset-password.html", "Page autonome de création/réinitialisation de mot de passe"],
    ], [4 * cm, 11.5 * cm]))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        "L'application est servie statiquement par Express via <b>express.static()</b>. "
        "Il n'y a aucun bundler (Webpack, Vite, etc.) ni framework (React, Vue). "
        "Les appels API sont effectués directement avec <b>fetch()</b>.",
        S['Body']))

    # ── 3. Thème & Design ────────────────────────────────────────────────────
    story += section_header("3. Système de thème")
    story.append(Paragraph(
        "L'interface propose deux thèmes commutables via un bouton (☀/🌙) persisté en localStorage :",
        S['Body']))
    rows = [
        ["Variable CSS",        "Thème sombre",   "Thème clair"],
        ["--bg-color",          "#252e42",         "#e9edf3"],
        ["--header-start",      "#445a72",         "#d2dae7"],
        ["--button-bg",         "#2d3f55",         "#ffffff"],
        ["--accent",            "#8aa5c3",         "#718096"],
    ]
    t = Table(rows, colWidths=[5.5 * cm, 5 * cm, 5 * cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',  (0, 0), (-1, 0), TABLE_HEADER),
        ('TEXTCOLOR',   (0, 0), (-1, 0), WHITE),
        ('FONTNAME',    (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',    (0, 0), (-1, -1), 8.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, TABLE_ROW_ALT]),
        ('GRID',        (0, 0), (-1, -1), 0.4, TABLE_BORDER),
        ('FONTNAME',    (0, 1), (0, -1), 'Courier'),
        ('FONTSIZE',    (0, 1), (0, -1), 8),
        ('PADDING',     (0, 0), (-1, -1), 5),
    ]))
    story.append(t)

    # ── 4. Navigation ────────────────────────────────────────────────────────
    story += section_header("4. Navigation et sections")
    story.append(Paragraph(
        "L'application utilise un système de panneaux (show/hide) sans rechargement de page. "
        "La barre de navigation filtre les panneaux par catégorie :",
        S['Body']))
    for s in [
        "<b>Accueil</b> — Vue par défaut avec les boutons configurables (SiteButtons)",
        "<b>Orthophoniste</b> — Tableau de suivi des séances (mots travaillés, total, statut complet/incomplet), export Excel/PDF, barre d'actions sticky",
        "<b>Administration</b> — Gestion des utilisateurs (activation, reset MDP, toggle actif/inactif) — accès Admin uniquement",
        "<b>Connexion</b> — Modale de login / demande d'activation de compte",
    ]:
        story.append(bullet(s))
    story.append(Spacer(1, 0.3 * cm))

    # ── 5. Authentification côté client ──────────────────────────────────────
    story += section_header("5. Authentification côté client")
    story.append(Paragraph(
        "Le token de session Bearer est stocké en <b>sessionStorage</b> (effacé à la fermeture du navigateur). "
        "À chaque chargement de page, un appel <code>/api/verify-session</code> valide le token et "
        "adapte l'interface (affichage des sections protégées, badge de rôle).",
        S['Body']))
    story.append(Paragraph("Règles de visibilité :", S['BodyBold']))
    for item in [
        "Non connecté → seul le panneau Accueil est visible (lecture seule)",
        "Connecté (User) → accès Orthophoniste + boutons",
        "Connecté (Admin) → accès complet + panneau Administration",
    ]:
        story.append(bullet(item))

    # ── 6. Module Orthophoniste ───────────────────────────────────────────────
    story += section_header("6. Module Orthophoniste")
    for item in [
        "Tableau unifié avec regroupement mensuel (tiroirs collapsibles)",
        "Barre d'actions sticky (blur + opacité au scroll)",
        "Import CSV de séances (format : mots, date, total mots)",
        "Ajout manuel d'une séance (Admin)",
        "Export Excel (.xlsx) et PDF via SheetJS/jsPDF",
        "Panneau latéral liste des mots — clic filtre les lignes du tableau",
        "Barre de progression Total/10 (verte si séance complète ≥ 10 mots)",
    ]:
        story.append(bullet(item))

    # ── 7. Sécurité front ────────────────────────────────────────────────────
    story += section_header("7. Sécurité front-end")
    for item in [
        "Pas de données sensibles dans le DOM — le PasswordHash n'est jamais renvoyé au client",
        "Token stocké en sessionStorage (non accessible en XSS persistant via cookies)",
        "Validation du formulaire reset-password : regex /^(?=.*[A-Z])(?=.*\\d).{6,}$/ avant envoi",
        "escapeHtml() appliqué côté serveur sur les valeurs renvoyées dans le HTML",
    ]:
        story.append(bullet(item))

    # ── 8. Gestion des boutons ────────────────────────────────────────────────
    story += section_header("8. Boutons configurables (SiteButtons)")
    story.append(Paragraph(
        "Les libellés des boutons de l'accueil sont stockés en BDD (table <b>SiteButtons</b>) "
        "et chargés dynamiquement au démarrage via <code>GET /api/buttons</code>. "
        "Un Admin peut modifier les libellés directement dans l'interface sans redéploiement. "
        "La sauvegarde utilise un <b>MERGE SQL</b> transactionnel.",
        S['Body']))

    # ── 9. Reset password ────────────────────────────────────────────────────
    story += section_header("9. Page reset-password.html")
    story.append(Paragraph(
        "Page autonome accessible via lien e-mail (paramètre <code>?login=</code> dans l'URL). "
        "Elle permet à l'utilisateur de définir son mot de passe initial ou de le réinitialiser. "
        "Après soumission valide, <code>MotDePasseIsActive</code> est passé à 1 en BDD.",
        S['Body']))

    # ── 10. Déploiement ──────────────────────────────────────────────────────
    story += section_header("10. Déploiement")
    story.append(Paragraph(
        "L'application est conteneurisée (Docker). Le conteneur <b>web-nathanael-api</b> "
        "sert à la fois l'API et les fichiers statiques (index.html, reset-password.html) "
        "via Express sur le port 3000.",
        S['Body']))
    story.append(info_table([
        ["URL publique",   "https://board.kurisu-no-okoku.com"],
        ["Conteneur",      "web-nathanael-api (port 3000)"],
        ["Réseau Docker",  "web-nathanael-network (bridge)"],
        ["Image base",     "node:18-alpine"],
    ]))

    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    print(f"  [OK] {path}")


# ═══════════════════════════════════════════════════════════════════════════════
# DOC 2 — API (BACK-END)
# ═══════════════════════════════════════════════════════════════════════════════

def build_api_doc():
    path = "/Users/kurisu/Documents/Visual Code/docs/DOC_API_v1.22.3.pdf"
    doc  = make_doc(path,
                    "Board de Nathanaël — Documentation API",
                    "Documentation technique — Back-end Node.js / Express",
                    "v 1.22.3")

    S = STYLES
    story = []

    story.append(Spacer(1, 1.2 * cm))
    story.append(Paragraph("Documentation API Back-End", S['H1']))
    story.append(HRFlowable(width='100%', thickness=2, color=HEADER_BLUE, spaceAfter=8))
    story.append(info_table([
        ["Projet",      "Board de Nathanaël"],
        ["Runtime",     "Node.js 18 (LTS)"],
        ["Framework",   "Express 4.x"],
        ["Version API", "1.22.3"],
        ["Port",        "3000"],
        ["Base URL",    "https://board.kurisu-no-okoku.com"],
        ["Date création", DATE_CREATION],
        ["Date modif.",   "2026-05-06"],
    ]))
    story.append(Spacer(1, 0.5 * cm))

    # ── 1. Dépendances ───────────────────────────────────────────────────────
    story += section_header("1. Dépendances")
    rows = [
        ["Package",      "Version", "Rôle"],
        ["express",      "^4.18.2", "Serveur HTTP + routing"],
        ["mssql",        "^9.2.1",  "Driver SQL Server (tedious)"],
        ["bcrypt",       "^5.1.1",  "Hachage des mots de passe (salt 10)"],
        ["nodemailer",   "^6.9.7",  "Envoi d'e-mails (Gmail SMTP)"],
        ["dotenv",       "^17.4.2", "Variables d'environnement (.env)"],
        ["crypto",       "built-in","Génération de tokens sécurisés (32 bytes)"],
    ]
    t = Table(rows, colWidths=[3.5 * cm, 2.5 * cm, 9.5 * cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',  (0, 0), (-1, 0), TABLE_HEADER),
        ('TEXTCOLOR',   (0, 0), (-1, 0), WHITE),
        ('FONTNAME',    (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',    (0, 0), (-1, -1), 8.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, TABLE_ROW_ALT]),
        ('GRID',        (0, 0), (-1, -1), 0.4, TABLE_BORDER),
        ('FONTNAME',    (0, 1), (0, -1), 'Courier-Bold'),
        ('TEXTCOLOR',   (0, 1), (0, -1), HEADER_DARK),
        ('PADDING',     (0, 0), (-1, -1), 5),
    ]))
    story.append(t)

    # ── 2. Sécurité ──────────────────────────────────────────────────────────
    story += section_header("2. Sécurité & Middlewares")
    story += section_header("2.1 Authentification (authMiddleware)", level=2)
    story.append(Paragraph(
        "Vérifie la présence d'un token Bearer valide dans le header <code>Authorization</code>. "
        "Le token est recherché dans la Map en mémoire <code>sessions</code>. "
        "Retourne 401 si absent ou invalide.",
        S['Body']))

    story += section_header("2.2 Autorisation Admin (adminMiddleware)", level=2)
    story.append(Paragraph(
        "Étend authMiddleware : vérifie que <code>session.role === 'Admin'</code>. "
        "Retourne 403 si le rôle est insuffisant.",
        S['Body']))

    story += section_header("2.3 Rate limiting login", level=2)
    story.append(Paragraph(
        "Protection anti-bruteforce sur <code>POST /api/login</code> : "
        "<b>10 tentatives max par IP</b> sur une fenêtre glissante de <b>15 minutes</b>. "
        "Retourne HTTP 429 avec le délai restant.",
        S['Body']))

    story += section_header("2.4 CORS", level=2)
    story.append(Paragraph(
        "Middleware CORS permissif (<code>Access-Control-Allow-Origin: *</code>) "
        "autorisant le header <code>Authorization</code> — suffisant pour un usage interne/familial. "
        "À restreindre si l'API devait être ouverte publiquement.",
        S['Body']))

    # ── 3. Sessions ───────────────────────────────────────────────────────────
    story += section_header("3. Gestion des sessions")
    story.append(Paragraph(
        "Les sessions sont stockées <b>en mémoire</b> dans une <code>Map()</code> "
        "(<code>token → { username, role }</code>). Cela implique :",
        S['Body']))
    for item in [
        "Perte de toutes les sessions au redémarrage du conteneur",
        "Pas de session partagée entre plusieurs instances (mono-instance uniquement)",
        "Le rôle est figé en session au moment du login — un changement de rôle en BDD nécessite un re-login",
        "Token : 32 bytes aléatoires via crypto.randomBytes() → 64 caractères hex",
    ]:
        story.append(bullet(item))

    # ── 4. Référentiel des endpoints ──────────────────────────────────────────
    story += section_header("4. Référentiel des endpoints")

    story += section_header("4.1 Publics (sans authentification)", level=2)
    rows = [
        ["Endpoint",                  "Méthode", "Auth",    "Description",                                   "Réponse"],
        ["/api/info",                 "GET",     "—",       "Version et statut de l'API",                    "{ version, status }"],
        ["/api/login",                "POST",    "—",       "Authentification (rate-limit 10/15 min)",        "{ token, UserID, Role, … }"],
        ["/api/logout",               "POST",    "—",       "Suppression du token de session",                "{ message }"],
        ["/api/activate",             "POST",    "—",       "Demande d'activation de compte + e-mails",      "{ message }"],
        ["/api/confirm-activation",   "GET",     "—",       "Validation admin par clic e-mail",               "HTML"],
        ["/api/reset-password",       "POST",    "—",       "Définition / réinitialisation du MDP",          "{ message }"],
        ["/api/buttons",              "GET",     "—",       "Lecture des libellés de boutons",                "Array[SiteButton]"],
    ]
    story.append(api_table(rows))

    story += section_header("4.2 Authentifiés (User + Admin)", level=2)
    rows = [
        ["Endpoint",              "Méthode", "Auth",    "Description",                             "Réponse"],
        ["/api/verify-session",   "GET",     "Bearer",  "Vérification du token et retour du rôle", "{ valid, username, role }"],
        ["/api/orthophoniste",    "GET",     "Bearer",  "Liste des séances orthophoniste (CTE)",   "Array[Séance]"],
        ["/api/mots",             "GET",     "Bearer",  "Dictionnaire de mots",                    "Array[Mot]"],
        ["/api/export-csv",       "GET",     "Bearer",  "Export CSV des séances",                  "text/csv"],
    ]
    story.append(api_table(rows))

    story += section_header("4.3 Admin uniquement", level=2)
    rows = [
        ["Endpoint",                    "Méthode", "Auth",      "Description",                                     "Réponse"],
        ["/api/buttons",                "POST",    "Admin",     "MERGE des libellés de boutons (transactionnel)",  "{ message }"],
        ["/api/users",                  "GET",     "Admin",     "Liste complète des utilisateurs",                 "Array[User]"],
        ["/api/users/toggle-active",    "POST",    "Admin",     "Toggle MotDePasseIsActive (activer/désactiver)",  "{ message }"],
        ["/api/request-reset",          "POST",    "Admin",     "Force reset MDP + envoi e-mail",                  "{ message }"],
        ["/api/import-csv",             "POST",    "Admin",     "Import CSV de séances (transactionnel)",          "{ message }"],
        ["/api/orthophoniste",          "POST",    "Admin",     "Ajout manuel d'une séance",                       "{ message }"],
    ]
    story.append(api_table(rows))

    # ── 5. Logique de connexion ───────────────────────────────────────────────
    story += section_header("5. Logique de connexion (POST /api/login)")
    rows_login = [
        ["MotDePasseIsActive", "Role",   "Comportement"],
        ["true (1)",           "User / Admin", "Vérification bcrypt obligatoire"],
        ["false (0)",          "Admin",        "Connexion autorisée sans mot de passe"],
        ["false (0)",          "User",         "HTTP 401 — Compte en attente d'activation"],
    ]
    t = Table(rows_login, colWidths=[4 * cm, 4 * cm, 7.5 * cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',  (0, 0), (-1, 0), TABLE_HEADER),
        ('TEXTCOLOR',   (0, 0), (-1, 0), WHITE),
        ('FONTNAME',    (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',    (0, 0), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, TABLE_ROW_ALT]),
        ('GRID',        (0, 0), (-1, -1), 0.5, TABLE_BORDER),
        ('PADDING',     (0, 0), (-1, -1), 6),
    ]))
    story.append(t)

    # ── 6. E-mails ────────────────────────────────────────────────────────────
    story += section_header("6. Service e-mail (Nodemailer)")
    story.append(Paragraph(
        "Transport SMTP via <b>Gmail</b> avec mot de passe d'application (App Password). "
        "Quatre scénarios d'envoi :",
        S['Body']))
    for item in [
        "<b>Activation de compte</b> — notification admin + confirmation utilisateur",
        "<b>Réinitialisation MDP</b> — lien vers reset-password.html?login=…",
        "<b>Relance automatique</b> — job toutes les 24h pour les utilisateurs MustResetPassword=1",
        "<b>Promotion Admin</b> — email automatique lors du passage Role User → Admin (v1.22.3)",
    ]:
        story.append(bullet(item))

    # ── 6b. Jobs de fond ──────────────────────────────────────────────────────
    story += section_header("6.1 Tâches de fond (background jobs)", level=2)
    rows = [
        ["Job", "Intervalle", "Rôle", "v"],
        ["Relance MustResetPassword", "24h", "Envoie un e-mail de relance aux utilisateurs avec MustResetPassword=1", "1.22.0"],
        ["Notification promotion Admin", "2 min", "Détecte RoleNotifPending=1 (posé par trigger BDD), envoie l'e-mail délog/relog, remet le flag à 0", "1.22.3"],
    ]
    t = Table(rows, colWidths=[4.5*cm, 1.8*cm, 8.5*cm, 1.5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',  (0,0), (-1,0), TABLE_HEADER),
        ('TEXTCOLOR',   (0,0), (-1,0), WHITE),
        ('FONTNAME',    (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',    (0,0), (-1,-1), 8.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, TABLE_ROW_ALT]),
        ('GRID',        (0,0), (-1,-1), 0.4, TABLE_BORDER),
        ('VALIGN',      (0,0), (-1,-1), 'TOP'),
        ('PADDING',     (0,0), (-1,-1), 5),
    ]))
    story.append(t)

    # ── 7. Import CSV ────────────────────────────────────────────────────────
    story += section_header("7. Import CSV (POST /api/import-csv)")
    story.append(Paragraph(
        "Traitement ligne par ligne avec détection regex de la date en français "
        "(<code>dd mois yyyy</code>). Pour chaque ligne :",
        S['Body']))
    for item in [
        "Résolution des mots (table Mots) — upsert via INSERT ou SELECT",
        "Insertion de la séance (table Orthophoniste)",
        "Insertion des liaisons (table Orthophoniste_Mots)",
        "Le tout dans une seule transaction SQL — rollback en cas d'erreur",
        "Cache en mémoire (Map) pour éviter les aller-retours BDD répétés sur les mots",
    ]:
        story.append(bullet(item))

    # ── 8. Infra Docker ───────────────────────────────────────────────────────
    story += section_header("8. Infrastructure Docker")
    story.append(info_table([
        ["Image",         "node:18-alpine"],
        ["Conteneur API", "web-nathanael-api (port 3000)"],
        ["BDD cible",     "mac-mini-de-christophe.tailbf2a66.ts.net:1433"],
        ["Réseau",        "web-nathanael-network (bridge)"],
        ["Restart",       "unless-stopped"],
        ["Env injectés",  "DB_SERVER, DB_USER, DB_PASSWORD, DB_DATABASE, DB_PORT, EMAIL_PASSWORD, PUBLIC_URL"],
    ]))

    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    print(f"  [OK] {path}")


# ═══════════════════════════════════════════════════════════════════════════════
# DOC 3 — BASE DE DONNÉES
# ═══════════════════════════════════════════════════════════════════════════════

def db_schema_diagram():
    """Retourne un Drawing ReportLab représentant le schéma de la BDD."""
    DW, DH = 15.5 * cm, 11 * cm
    d = Drawing(DW, DH)

    # Couleurs locales
    tbl_bg    = colors.HexColor('#E8F0FA')
    tbl_head  = colors.HexColor('#3A6EA5')
    tbl_bord  = colors.HexColor('#3A6EA5')
    pk_color  = colors.HexColor('#1A5276')
    fk_color  = colors.HexColor('#1D6A31')
    line_col  = colors.HexColor('#3A6EA5')

    def draw_table(x, y, title, fields, w=4.0*cm, row_h=0.48*cm, head_h=0.6*cm):
        # En-tête
        r = Rect(x, y - head_h, w, head_h,
                 fillColor=tbl_head, strokeColor=tbl_bord, strokeWidth=1.2)
        d.add(r)
        d.add(String(x + w/2, y - head_h + 0.15*cm, title,
                     fontName='Helvetica-Bold', fontSize=8.5,
                     fillColor=colors.white, textAnchor='middle'))
        # Lignes
        total_h = head_h + len(fields) * row_h
        body = Rect(x, y - total_h, w, len(fields) * row_h,
                    fillColor=tbl_bg, strokeColor=tbl_bord, strokeWidth=0.8)
        d.add(body)
        for i, (fname, ftype, flags) in enumerate(fields):
            fy = y - head_h - (i + 0.75) * row_h
            color = pk_color if 'PK' in flags else (fk_color if 'FK' in flags else colors.HexColor('#222'))
            weight = 'Helvetica-Bold' if 'PK' in flags else 'Helvetica'
            label = f"{'🔑 ' if 'PK' in flags else ('↗ ' if 'FK' in flags else '   ')}{fname}  {ftype}"
            d.add(String(x + 0.15*cm, fy, label,
                         fontName=weight, fontSize=7.2, fillColor=color))
            # Séparateur
            if i < len(fields) - 1:
                d.add(Line(x, y - head_h - (i+1)*row_h, x+w, y - head_h - (i+1)*row_h,
                           strokeColor=tbl_bord, strokeWidth=0.3))
        return total_h

    # ── Table Utilisateurs (x=0.3, y=10.5) ──────────────────────────────────
    draw_table(0.3*cm, 10.5*cm, "Utilisateurs", [
        ("UserID",                  "INT IDENTITY", ["PK"]),
        ("Username",                "NVARCHAR",     []),
        ("Email",                   "NVARCHAR",     []),
        ("Role",                    "NVARCHAR",     []),
        ("PasswordHash",            "NVARCHAR",     []),
        ("MotDePasseIsActive",       "BIT",          []),
        ("MustResetPassword",       "BIT",          []),
        ("UserCreatedBy",           "NVARCHAR",     []),
        ("LastModificationUserBy",  "NVARCHAR",     []),
    ], w=4.8*cm)

    # ── Table SiteButtons (x=0.3, y=4.0) ─────────────────────────────────────
    draw_table(0.3*cm, 3.8*cm, "SiteButtons", [
        ("ButtonKey",       "NVARCHAR", ["PK"]),
        ("ButtonText",      "NVARCHAR", []),
        ("last_change_date","DATETIME2",[]),
    ], w=4.8*cm)

    # ── Table Orthophoniste (x=6.2, y=10.5) ──────────────────────────────────
    draw_table(6.2*cm, 10.5*cm, "Orthophoniste", [
        ("Id",   "INT IDENTITY", ["PK"]),
        ("Date", "DATETIME2",    []),
    ], w=4.2*cm)

    # ── Table Mots (x=11.0, y=10.5) ──────────────────────────────────────────
    draw_table(11.0*cm, 10.5*cm, "Mots", [
        ("Id",  "INT IDENTITY", ["PK"]),
        ("Mot", "NVARCHAR",     []),
    ], w=4.2*cm)

    # ── Table Orthophoniste_Mots (x=6.2, y=5.5) ──────────────────────────────
    draw_table(6.2*cm, 5.5*cm, "Orthophoniste_Mots", [
        ("Id",               "INT IDENTITY", ["PK"]),
        ("OrthophonisteId",  "INT",          ["FK"]),
        ("MotId",            "INT",          ["FK"]),
    ], w=4.8*cm)

    # ── Relations ─────────────────────────────────────────────────────────────
    # Orthophoniste → Orthophoniste_Mots
    d.add(Line(6.2*cm, 4.0*cm, 8.6*cm, 4.0*cm,
               strokeColor=line_col, strokeWidth=1.2))
    d.add(Line(8.6*cm, 4.0*cm, 8.6*cm, 5.5*cm - 0.48*cm - 0.02*cm,
               strokeColor=line_col, strokeWidth=1.2))

    # Mots → Orthophoniste_Mots
    d.add(Line(13.1*cm, 8.98*cm, 13.1*cm, 6.0*cm,
               strokeColor=line_col, strokeWidth=1.2))
    d.add(Line(13.1*cm, 6.0*cm, 11.0*cm, 4.8*cm,
               strokeColor=line_col, strokeWidth=1.2))

    # Légende
    d.add(Rect(0.3*cm, 0.1*cm, 0.3*cm, 0.3*cm,
               fillColor=pk_color, strokeColor=pk_color))
    d.add(String(0.8*cm, 0.17*cm, "PK = Clé primaire",
                 fontName='Helvetica', fontSize=7, fillColor=pk_color))
    d.add(Rect(5.5*cm, 0.1*cm, 0.3*cm, 0.3*cm,
               fillColor=fk_color, strokeColor=fk_color))
    d.add(String(6.0*cm, 0.17*cm, "FK = Clé étrangère",
                 fontName='Helvetica', fontSize=7, fillColor=fk_color))

    return d


def build_db_doc():
    path = "/Users/kurisu/Documents/Visual Code/docs/DOC_BDD_v1.22.2.pdf"
    doc  = make_doc(path,
                    "Board de Nathanaël — Documentation Base de Données",
                    "Documentation technique — SQL Server WEB_NATHANAEL",
                    "v 1.22.2")

    S = STYLES
    story = []

    story.append(Spacer(1, 1.2 * cm))
    story.append(Paragraph("Documentation Base de Données", S['H1']))
    story.append(HRFlowable(width='100%', thickness=2, color=HEADER_BLUE, spaceAfter=8))
    story.append(info_table([
        ["Projet",          "Board de Nathanaël"],
        ["SGBD",            "Azure SQL Edge Developer 15.0.2000 (ARM64)"],
        ["Base",            "WEB_NATHANAEL"],
        ["Schéma",          "dbo"],
        ["Serveur",         "mac-mini-de-christophe.tailbf2a66.ts.net:1433"],
        ["Driver Node.js",  "mssql ^9.2.1 (tedious)"],
        ["Date création",   DATE_CREATION],
        ["Date modif.",     "2026-05-05"],
    ]))
    story.append(Spacer(1, 0.5 * cm))

    # ── 1. Schéma ─────────────────────────────────────────────────────────────
    story += section_header("1. Schéma entité-relation")
    story.append(db_schema_diagram())
    story.append(Spacer(1, 0.4 * cm))

    # ── 2. Tables ─────────────────────────────────────────────────────────────
    story += section_header("2. Description des tables")

    # Utilisateurs
    story += section_header("2.1 Utilisateurs", level=2)
    story.append(Paragraph(
        "Table centrale de gestion des comptes utilisateur.",
        S['Body']))
    rows = [
        ["Colonne",                 "Type",           "Contrainte", "Description"],
        ["UserID",                  "INT IDENTITY",   "PK",         "Identifiant auto-incrémenté"],
        ["Username",                "NVARCHAR",       "NOT NULL",   "Nom d'utilisateur (login)"],
        ["Email",                   "NVARCHAR",       "NOT NULL",   "Adresse e-mail"],
        ["Role",                    "NVARCHAR",       "NOT NULL",   "Rôle : 'Admin' ou 'User'"],
        ["PasswordHash",            "NVARCHAR",       "",           "Hash bcrypt (salt 10) ou 'WAITING_FOR_HASH'"],
        ["MotDePasseIsActive",       "BIT",            "DEFAULT 0",  "1 = MDP actif, 0 = compte en attente"],
        ["MustResetPassword",       "BIT",            "DEFAULT 0",  "1 = l'utilisateur doit changer son MDP"],
        ["UserCreatedBy",           "NVARCHAR",       "",           "Login de l'auteur de la création"],
        ["LastModificationUserBy",  "NVARCHAR",       "",           "Dernier modificateur"],
    ]
    t = Table(rows, colWidths=[4.0*cm, 2.8*cm, 2.2*cm, 6.5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',  (0, 0), (-1, 0), TABLE_HEADER),
        ('TEXTCOLOR',   (0, 0), (-1, 0), WHITE),
        ('FONTNAME',    (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',    (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, TABLE_ROW_ALT]),
        ('GRID',        (0, 0), (-1, -1), 0.4, TABLE_BORDER),
        ('FONTNAME',    (0, 1), (0, -1), 'Courier-Bold'),
        ('TEXTCOLOR',   (0, 1), (0, -1), HEADER_DARK),
        ('PADDING',     (0, 0), (-1, -1), 5),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.3*cm))

    # SiteButtons
    story += section_header("2.2 SiteButtons", level=2)
    story.append(Paragraph("Libellés configurables des boutons de l'accueil.", S['Body']))
    rows = [
        ["Colonne",         "Type",     "Contrainte", "Description"],
        ["ButtonKey",       "NVARCHAR", "PK",         "Clé fonctionnelle du bouton (ex: btn_ortho)"],
        ["ButtonText",      "NVARCHAR", "NOT NULL",   "Texte affiché sur le bouton"],
        ["last_change_date","DATETIME2","",            "Horodatage de la dernière modification"],
    ]
    t = Table(rows, colWidths=[3.5*cm, 2.8*cm, 2.2*cm, 7.0*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',  (0, 0), (-1, 0), TABLE_HEADER),
        ('TEXTCOLOR',   (0, 0), (-1, 0), WHITE),
        ('FONTNAME',    (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',    (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, TABLE_ROW_ALT]),
        ('GRID',        (0, 0), (-1, -1), 0.4, TABLE_BORDER),
        ('FONTNAME',    (0, 1), (0, -1), 'Courier-Bold'),
        ('TEXTCOLOR',   (0, 1), (0, -1), HEADER_DARK),
        ('PADDING',     (0, 0), (-1, -1), 5),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.3*cm))

    # Orthophoniste
    story += section_header("2.3 Orthophoniste", level=2)
    story.append(Paragraph(
        "Enregistre chaque séance orthophoniste. Les colonnes Total, Complet et Mots "
        "sont <b>calculées à la lecture</b> via CTE (Common Table Expression) — "
        "elles ne sont pas stockées.", S['Body']))
    rows = [
        ["Colonne", "Type",        "Contrainte", "Description"],
        ["Id",      "INT IDENTITY","PK",          "Identifiant de la séance"],
        ["Date",    "DATETIME2",   "NOT NULL",    "Date de la séance"],
    ]
    t = Table(rows, colWidths=[2.5*cm, 3.0*cm, 2.5*cm, 7.5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',  (0, 0), (-1, 0), TABLE_HEADER),
        ('TEXTCOLOR',   (0, 0), (-1, 0), WHITE),
        ('FONTNAME',    (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',    (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, TABLE_ROW_ALT]),
        ('GRID',        (0, 0), (-1, -1), 0.4, TABLE_BORDER),
        ('FONTNAME',    (0, 1), (0, -1), 'Courier-Bold'),
        ('TEXTCOLOR',   (0, 1), (0, -1), HEADER_DARK),
        ('PADDING',     (0, 0), (-1, -1), 5),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.3*cm))

    # Mots
    story += section_header("2.4 Mots", level=2)
    story.append(Paragraph("Dictionnaire dédupliqué de tous les mots travaillés.", S['Body']))
    rows = [
        ["Colonne", "Type",        "Contrainte", "Description"],
        ["Id",      "INT IDENTITY","PK",          "Identifiant du mot"],
        ["Mot",     "NVARCHAR",    "NOT NULL",    "Mot orthophonique (clé métier dédupliquée)"],
    ]
    t = Table(rows, colWidths=[2.5*cm, 3.0*cm, 2.5*cm, 7.5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',  (0, 0), (-1, 0), TABLE_HEADER),
        ('TEXTCOLOR',   (0, 0), (-1, 0), WHITE),
        ('FONTNAME',    (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',    (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, TABLE_ROW_ALT]),
        ('GRID',        (0, 0), (-1, -1), 0.4, TABLE_BORDER),
        ('FONTNAME',    (0, 1), (0, -1), 'Courier-Bold'),
        ('TEXTCOLOR',   (0, 1), (0, -1), HEADER_DARK),
        ('PADDING',     (0, 0), (-1, -1), 5),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.3*cm))

    # Orthophoniste_Mots
    story += section_header("2.5 Orthophoniste_Mots", level=2)
    story.append(Paragraph(
        "Table de liaison many-to-many entre <b>Orthophoniste</b> et <b>Mots</b>. "
        "Une séance peut avoir N mots, un mot peut apparaître dans N séances.", S['Body']))
    rows = [
        ["Colonne",          "Type",        "Contrainte", "Description"],
        ["Id",               "INT IDENTITY","PK",         "Identifiant de la ligne"],
        ["OrthophonisteId",  "INT",         "FK → Orthophoniste.Id", "Séance associée"],
        ["MotId",            "INT",         "FK → Mots.Id",          "Mot associé"],
    ]
    t = Table(rows, colWidths=[3.5*cm, 3.0*cm, 3.5*cm, 5.5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',  (0, 0), (-1, 0), TABLE_HEADER),
        ('TEXTCOLOR',   (0, 0), (-1, 0), WHITE),
        ('FONTNAME',    (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',    (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, TABLE_ROW_ALT]),
        ('GRID',        (0, 0), (-1, -1), 0.4, TABLE_BORDER),
        ('FONTNAME',    (0, 1), (0, -1), 'Courier-Bold'),
        ('TEXTCOLOR',   (0, 1), (0, -1), HEADER_DARK),
        ('PADDING',     (0, 0), (-1, -1), 5),
    ]))
    story.append(t)

    # ── 3. Requêtes clés ──────────────────────────────────────────────────────
    story += section_header("3. Requêtes SQL notables")

    story += section_header("3.1 Lecture séances orthophoniste (CTE)", level=2)
    story.append(Paragraph(
        "Les champs <b>Total</b>, <b>Complet</b> et <b>Mots</b> sont calculés dynamiquement :",
        S['Body']))
    story.append(Paragraph(
        "WITH WordData AS (<br/>"
        "&nbsp;&nbsp;SELECT OM.OrthophonisteId, COUNT(OM.MotId) AS MotCount,<br/>"
        "&nbsp;&nbsp;STRING_AGG(M.Mot, ', ') WITHIN GROUP (ORDER BY M.Mot) AS Mots<br/>"
        "&nbsp;&nbsp;FROM Orthophoniste_Mots OM JOIN Mots M ON OM.MotId = M.Id<br/>"
        "&nbsp;&nbsp;GROUP BY OM.OrthophonisteId<br/>"
        ")<br/>"
        "SELECT O.Id, O.Date,<br/>"
        "&nbsp;&nbsp;ISNULL(WD.MotCount, 0) AS Total,<br/>"
        "&nbsp;&nbsp;CASE WHEN ISNULL(WD.MotCount, 0) >= 10 THEN 1 ELSE 0 END AS Complet,<br/>"
        "&nbsp;&nbsp;ISNULL(WD.Mots, '') AS Mots<br/>"
        "FROM Orthophoniste O LEFT JOIN WordData WD ON O.Id = WD.OrthophonisteId<br/>"
        "ORDER BY O.Date DESC",
        S['CodeBlock']))

    story += section_header("3.2 MERGE SiteButtons (upsert)", level=2)
    story.append(Paragraph(
        "Utilisation de <b>MERGE</b> pour insérer ou mettre à jour un bouton en une seule opération :",
        S['Body']))
    story.append(Paragraph(
        "MERGE INTO SiteButtons AS target<br/>"
        "USING (SELECT @key AS ButtonKey, @text AS ButtonText) AS source<br/>"
        "ON (target.ButtonKey = source.ButtonKey)<br/>"
        "WHEN MATCHED THEN UPDATE SET ButtonText = source.ButtonText, last_change_date = GETDATE()<br/>"
        "WHEN NOT MATCHED THEN INSERT (ButtonKey, ButtonText, last_change_date)<br/>"
        "&nbsp;&nbsp;VALUES (source.ButtonKey, source.ButtonText, GETDATE());",
        S['CodeBlock']))

    # ── 4. Connexion & pool ───────────────────────────────────────────────────
    story += section_header("4. Connexion et pool")
    story.append(Paragraph(
        "La connexion est gérée par un <b>ConnectionPool</b> mssql, initialisé au démarrage de l'API. "
        "Toutes les requêtes utilisent ce pool partagé. "
        "Les opérations multi-tables (import CSV, MERGE boutons) sont enveloppées dans des <b>transactions SQL explicites</b> "
        "avec rollback automatique en cas d'erreur.",
        S['Body']))
    story.append(info_table([
        ["Hôte",     "mac-mini-de-christophe.tailbf2a66.ts.net"],
        ["Port",     "1433 (SQL Server standard)"],
        ["Base",     "WEB_NATHANAEL"],
        ["User",     "sa (via variable d'env DB_USER)"],
        ["Encrypt",  "false (réseau privé Tailscale)"],
        ["TrustCert","true"],
    ]))

    # ── 5. Sécurité BDD ───────────────────────────────────────────────────────
    story += section_header("5. Sécurité des données")
    for item in [
        "Toutes les requêtes utilisent des <b>paramètres nommés</b> mssql (.input()) — protection contre l'injection SQL",
        "Le champ PasswordHash n'est jamais renvoyé au client (destructuring avant la réponse JSON)",
        "Le réseau est isolé via <b>Tailscale</b> — SQL Server non exposé sur Internet",
        "Mots de passe hashés bcrypt avec salt factor 10",
        "Compte bloqué (MotDePasseIsActive=0) tant que l'utilisateur n'a pas défini son mot de passe",
    ]:
        story.append(bullet(item))

    # ── 6. Maintenance IDENTITY (v1.22.2) ────────────────────────────────────
    story += section_header("6. Maintenance — Correction des colonnes IDENTITY (2026-05-05)")

    # Badge warning
    warn_rows = [["Contexte"]]
    warn_t = Table([["  Correction appliquée le 2026-05-05 — v1.22.2"]],
                   colWidths=[15.5*cm])
    warn_t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FFF3CD')),
        ('TEXTCOLOR',  (0,0), (-1,-1), colors.HexColor('#856404')),
        ('FONTNAME',   (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE',   (0,0), (-1,-1), 9),
        ('PADDING',    (0,0), (-1,-1), 8),
        ('GRID',       (0,0), (-1,-1), 0.5, colors.HexColor('#FFEEBA')),
    ]))
    story.append(warn_t)
    story.append(Spacer(1, 0.3*cm))

    story += section_header("6.1 Problème constaté", level=2)
    story.append(Paragraph(
        "Deux anomalies IDENTITY détectées suite à des redémarrages passés du conteneur <b>sql_server_m4</b>. "
        "Azure SQL Edge perd le cache d'identité au redémarrage et reprend à <i>dernière_valeur_cache + 1</i>, "
        "créant des gaps de ~1000 entre les IDs. "
        "<b>Utilisateurs</b> présentait un gap 6 → 1005 (UserID 1005 existant réel). "
        "<b>Mots</b> avait un last_value de 1027 alors que le MAX réel était 29.",
        S['Body']))

    rows = [
        ["Table",           "last_value avant", "MAX(id) réel", "Action"],
        ["Utilisateurs",    "1005",              "7 (après renumérotation)", "UserID 1005 → 7 + RESEED 7"],
        ["Mots",            "1027",              "29",            "RESEED → corrigé à 29"],
        ["Orthophoniste",   "38",                "38",            "Aucune — déjà aligné"],
    ]
    t = Table(rows, colWidths=[4.5*cm, 3.5*cm, 3.5*cm, 4.0*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',  (0, 0), (-1, 0), TABLE_HEADER),
        ('TEXTCOLOR',   (0, 0), (-1, 0), WHITE),
        ('FONTNAME',    (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',    (0, 0), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, TABLE_ROW_ALT]),
        ('GRID',        (0, 0), (-1, -1), 0.5, TABLE_BORDER),
        ('BACKGROUND',  (3, 2), (3, 2), colors.HexColor('#FDECEA')),
        ('TEXTCOLOR',   (3, 2), (3, 2), DANGER),
        ('FONTNAME',    (3, 2), (3, 2), 'Helvetica-Bold'),
        ('PADDING',     (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.3*cm))

    story += section_header("6.2 Correction appliquée", level=2)
    story.append(Paragraph(
        "Deux corrections effectuées :",
        S['Body']))
    for item in [
        "<b>Utilisateurs</b> — UserID 1005 renuméroté en 7 via DELETE + INSERT IDENTITY_INSERT ON, puis RESEED à 7",
        "<b>Mots</b> — RESEED explicite de 1027 à 29 (valeur MAX réelle)",
        "<b>Orthophoniste</b> — déjà aligné, aucune action",
    ]:
        story.append(bullet(item))
    story.append(Paragraph(
        "-- Utilisateurs : renumérotation UserID 1005 → 7<br/>"
        "DELETE FROM [dbo].[Utilisateurs] WHERE UserID = 1005;<br/>"
        "SET IDENTITY_INSERT [dbo].[Utilisateurs] ON;<br/>"
        "INSERT INTO [dbo].[Utilisateurs] (UserID, Username, ...) VALUES (7, ...);<br/>"
        "SET IDENTITY_INSERT [dbo].[Utilisateurs] OFF;<br/>"
        "DBCC CHECKIDENT ('[dbo].[Utilisateurs]', RESEED, 7);<br/><br/>"
        "-- Mots : reseed uniquement<br/>"
        "DBCC CHECKIDENT ('[dbo].[Mots]', RESEED, 29);",
        S['CodeBlock']))

    story += section_header("6.3 Limitation Azure SQL Edge", level=2)
    story.append(Paragraph(
        "La commande <code>ALTER DATABASE SET IDENTITY_CACHE OFF</code> disponible sur "
        "SQL Server 2017+ <b>n'est pas supportée</b> sur Azure SQL Edge (édition embarquée ARM64). "
        "En conséquence, <b>les sauts peuvent se reproduire à chaque redémarrage du conteneur</b>.",
        S['Body']))

    story += section_header("6.4 Procédure de maintenance à répéter après redémarrage", level=2)
    story.append(Paragraph(
        "Après tout redémarrage de <b>sql_server_m4</b>, exécuter les commandes suivantes "
        "via SSMS ou le script Node.js de maintenance :",
        S['Body']))
    story.append(Paragraph(
        "-- Vérifier les écarts<br/>"
        "SELECT OBJECT_NAME(OBJECT_ID) AS Tbl, last_value FROM sys.identity_columns<br/>"
        "WHERE OBJECT_NAME(OBJECT_ID) IN ('Utilisateurs','Mots','Orthophoniste');<br/><br/>"
        "-- Corriger si last_value > MAX réel<br/>"
        "DECLARE @maxU INT = (SELECT MAX(UserID) FROM Utilisateurs);<br/>"
        "DECLARE @maxM INT = (SELECT MAX(Id) FROM Mots);<br/>"
        "DECLARE @maxO INT = (SELECT MAX(Id) FROM Orthophoniste);<br/>"
        "EXEC('DBCC CHECKIDENT (''[dbo].[Utilisateurs]'',  RESEED, ' + @maxU + ')');<br/>"
        "EXEC('DBCC CHECKIDENT (''[dbo].[Mots]'',          RESEED, ' + @maxM + ')');<br/>"
        "EXEC('DBCC CHECKIDENT (''[dbo].[Orthophoniste]'', RESEED, ' + @maxO + ')');",
        S['CodeBlock']))

    rows_etat = [
        ["Table",           "last_value après", "MAX(id) réel", "Statut"],
        ["Utilisateurs",    "7",                 "7",            "Corrigé (était 1005)"],
        ["Mots",            "29",                "29",           "Corrigé (était 1027)"],
        ["Orthophoniste",   "38",                "38",           "Aligné (inchangé)"],
    ]
    t2 = Table(rows_etat, colWidths=[4.5*cm, 3.5*cm, 3.5*cm, 4.0*cm])
    t2.setStyle(TableStyle([
        ('BACKGROUND',  (0, 0), (-1, 0), TABLE_HEADER),
        ('TEXTCOLOR',   (0, 0), (-1, 0), WHITE),
        ('FONTNAME',    (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',    (0, 0), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, TABLE_ROW_ALT]),
        ('GRID',        (0, 0), (-1, -1), 0.5, TABLE_BORDER),
        ('BACKGROUND',  (3, 1), (3, 2), colors.HexColor('#D4EDDA')),
        ('TEXTCOLOR',   (3, 1), (3, 2), SUCCESS),
        ('FONTNAME',    (3, 1), (3, 2), 'Helvetica-Bold'),
        ('BACKGROUND',  (3, 3), (3, 3), colors.HexColor('#EAF0F8')),
        ('TEXTCOLOR',   (3, 3), (3, 3), TEXT_MED),
        ('PADDING',     (0, 0), (-1, -1), 6),
    ]))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph("État après correction :", S['BodyBold']))
    story.append(t2)

    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    print(f"  [OK] {path}")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else 'all'
    print("Génération des documents...")
    if target in ('all', 'site'):
        build_site_doc()
    if target in ('all', 'api'):
        build_api_doc()
    if target in ('all', 'bdd'):
        build_db_doc()
    print("Terminé.")
