#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Documentation complète WEB_NATHANAEL — v1.22.2"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.graphics.shapes import Drawing, Rect, String, Line
import os

# ── Couleurs ──────────────────────────────────────────────────────────────────
H_BLUE   = colors.HexColor('#3A6EA5')
H_DARK   = colors.HexColor('#2B5280')
H_LIGHT  = colors.HexColor('#5A8EC5')
ACCENT   = colors.HexColor('#4A80BC')
TH_BG    = colors.HexColor('#3A6EA5')
ROW_ALT  = colors.HexColor('#EAF0F8')
BORDER   = colors.HexColor('#C5D8F0')
TXT      = colors.HexColor('#1A2A3A')
TXT_MED  = colors.HexColor('#3A4A5A')
WHITE    = colors.white
GREEN    = colors.HexColor('#28A745')
ORANGE   = colors.HexColor('#FD7E14')
RED      = colors.HexColor('#DC3545')
YELLOW   = colors.HexColor('#856404')
YELLOW_BG= colors.HexColor('#FFF3CD')
GREEN_BG = colors.HexColor('#D4EDDA')
FOOTER   = colors.HexColor('#2B5280')

W, H = A4
M = 1.8 * cm

AUTHOR       = "Kurisu-No-Okoku"
DATE_CREATE  = "2026-05-05"
DATE_MODIF   = "2026-05-06"
VERSION      = "v 1.22.3"
VERSION_LABEL= "v1.22.3"

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
    add('FooterTxt', fontName='Helvetica', fontSize=7.5,
        textColor=colors.HexColor('#C8DEFF'), alignment=TA_CENTER)
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
    canvas.drawCentredString(W/2, H-1.8*cm, doc._sub)
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
    doc._title = "Board de Nathanaël — Documentation Complète BDD"
    doc._sub   = "WEB_NATHANAEL · Azure SQL Edge 15.0.2000 · ARM64"
    return doc

def sec(title, level=1):
    st = {1: 'H1', 2: 'H2', 3: 'H3'}[level]
    out = [Paragraph(title, S[st])]
    if level == 1:
        out.append(HRFlowable(width='100%', thickness=1.5, color=H_BLUE, spaceAfter=5))
    return out

def bul(text): return Paragraph(f"•  {text}", S['BulletItem'])

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

def info_tbl(rows):
    t = Table(rows, colWidths=[4.5*cm, 12.5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), ROW_ALT),
        ('TEXTCOLOR',  (0,0), (0,-1), H_DARK),
        ('FONTNAME',   (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME',   (1,0), (1,-1), 'Helvetica'),
        ('FONTSIZE',   (0,0), (-1,-1), 9),
        ('GRID',       (0,0), (-1,-1), 0.5, BORDER),
        ('PADDING',    (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.HexColor('#F5F9FF'), WHITE]),
    ]))
    return t

# ─────────────────────────────────────────────────────────────────────────────
# DIAGRAMME ER COMPLET
# ─────────────────────────────────────────────────────────────────────────────
def er_diagram():
    DW, DH = 17*cm, 13.5*cm
    d = Drawing(DW, DH)

    TBG  = colors.HexColor('#E8F0FA')
    THEAD= colors.HexColor('#3A6EA5')
    TB   = colors.HexColor('#3A6EA5')
    PK   = colors.HexColor('#1A5276')
    FK   = colors.HexColor('#1D6A31')
    LC   = colors.HexColor('#3A6EA5')
    RH   = 0.44*cm
    HH   = 0.56*cm

    def draw_table(x, y, title, fields, w=4.2*cm):
        d.add(Rect(x, y-HH, w, HH, fillColor=THEAD, strokeColor=TB, strokeWidth=1.2))
        d.add(String(x+w/2, y-HH+0.15*cm, title,
              fontName='Helvetica-Bold', fontSize=8, fillColor=WHITE, textAnchor='middle'))
        total_h = HH + len(fields)*RH
        d.add(Rect(x, y-total_h, w, len(fields)*RH, fillColor=TBG, strokeColor=TB, strokeWidth=0.8))
        for i, (fname, ftype, flag) in enumerate(fields):
            fy = y - HH - (i+0.72)*RH
            fc = PK if 'PK' in flag else (FK if 'FK' in flag else TXT)
            fw = 'Helvetica-Bold' if 'PK' in flag else 'Helvetica'
            pfx = '🔑 ' if 'PK' in flag else ('↗ ' if 'FK' in flag else '   ')
            d.add(String(x+0.12*cm, fy, f"{pfx}{fname}  {ftype}",
                  fontName=fw, fontSize=6.8, fillColor=fc))
            if i < len(fields)-1:
                d.add(Line(x, y-HH-(i+1)*RH, x+w, y-HH-(i+1)*RH,
                      strokeColor=TB, strokeWidth=0.25))
        return total_h

    def arrow(x1,y1,x2,y2):
        d.add(Line(x1,y1,x2,y2, strokeColor=LC, strokeWidth=1.0))

    # Utilisateurs  (col 1, haut)
    draw_table(0.2*cm, 13.0*cm, "Utilisateurs", [
        ("UserID",                 "INT IDENTITY", ["PK"]),
        ("Username",               "NVARCHAR(50)", []),
        ("Email",                  "NVARCHAR(100)",[]),
        ("Role",                   "NVARCHAR(20)", []),
        ("PasswordHash",           "NVARCHAR(255)",[]),
        ("MotDePasseIsActive",     "BIT",          []),
        ("MustResetPassword",      "BIT",          []),
        ("UserCreatedDate",        "DATETIME",     []),
        ("UserCreatedBy",          "NVARCHAR(50)", []),
        ("LastChangeDate",         "DATETIME",     []),
        ("LastModificationUserBy", "NVARCHAR(50)", []),
    ], w=4.8*cm)

    # HistoriqueUtilisateurs (col 1, bas)
    draw_table(0.2*cm, 5.0*cm, "HistoriqueUtilisateurs", [
        ("LogID",      "INT IDENTITY", ["PK"]),
        ("UserID",     "INT",          []),
        ("ActionType", "NVARCHAR(50)", []),
        ("OldValue",   "NVARCHAR(MAX)",[]),
        ("NewValue",   "NVARCHAR(MAX)",[]),
        ("ChangedBy",  "NVARCHAR(50)", []),
        ("ChangeDate", "DATETIME",     []),
    ], w=4.8*cm)

    # Orthophoniste (col 2)
    draw_table(6.2*cm, 13.0*cm, "Orthophoniste", [
        ("Id",      "INT IDENTITY", ["PK"]),
        ("Date",    "DATETIME",     []),
        ("Total",   "INT",          []),
        ("Complet", "BIT",          []),
    ], w=4.0*cm)

    # Orthophoniste_Mots (col 2, bas)
    draw_table(6.2*cm, 7.0*cm, "Orthophoniste_Mots", [
        ("OrthophonisteId", "INT (PK/FK)", ["PK","FK"]),
        ("MotId",           "INT (PK/FK)", ["PK","FK"]),
    ], w=4.4*cm)

    # Mots (col 3)
    draw_table(12.0*cm, 13.0*cm, "Mots", [
        ("Id",  "INT IDENTITY", ["PK"]),
        ("Mot", "NVARCHAR(255)",[]),
    ], w=4.0*cm)

    # SiteButtons (col 3, bas)
    draw_table(12.0*cm, 8.0*cm, "SiteButtons", [
        ("id",              "INT IDENTITY", ["PK"]),
        ("ButtonKey",       "NVARCHAR(255)",[]),
        ("ButtonText",      "NVARCHAR(MAX)",[]),
        ("last_change_date","DATETIME2",    []),
    ], w=4.8*cm)

    # ── Relations ─────────────────────────────────────────────────────────────
    # Utilisateurs ──► HistoriqueUtilisateurs (trigger, pas FK formelle)
    arrow(2.6*cm, 7.5*cm, 2.6*cm, 5.0*cm)
    d.add(String(2.7*cm, 6.3*cm, "TRIGGER", fontName='Helvetica-Oblique',
          fontSize=6.5, fillColor=ORANGE))

    # Orthophoniste ──► Orthophoniste_Mots (FK)
    arrow(8.2*cm, 8.56*cm, 8.2*cm, 7.0*cm)

    # Mots ──► Orthophoniste_Mots (FK)
    arrow(14.0*cm, 11.12*cm, 10.64*cm, 6.5*cm)

    # Trigger trg_Update_Ortho_Stats sur Orthophoniste_Mots → Orthophoniste
    d.add(Line(6.2*cm, 6.1*cm, 5.6*cm, 6.1*cm, strokeColor=ORANGE, strokeWidth=1.0))
    d.add(Line(5.6*cm, 6.1*cm, 5.6*cm, 11.0*cm, strokeColor=ORANGE, strokeWidth=1.0))
    d.add(Line(5.6*cm, 11.0*cm, 6.2*cm, 11.0*cm, strokeColor=ORANGE, strokeWidth=1.0))
    d.add(String(5.65*cm, 9.0*cm, "TRIGGER", fontName='Helvetica-Oblique',
          fontSize=6.5, fillColor=ORANGE))

    # Légende
    lx = 0.2*cm
    d.add(Rect(lx, 0.05*cm, 0.28*cm, 0.28*cm, fillColor=PK, strokeColor=PK))
    d.add(String(lx+0.38*cm, 0.1*cm, "PK  Clé primaire",
          fontName='Helvetica', fontSize=6.5, fillColor=PK))
    d.add(Rect(4.5*cm, 0.05*cm, 0.28*cm, 0.28*cm, fillColor=FK, strokeColor=FK))
    d.add(String(4.9*cm, 0.1*cm, "FK  Clé étrangère",
          fontName='Helvetica', fontSize=6.5, fillColor=FK))
    d.add(Line(8.5*cm, 0.19*cm, 9.1*cm, 0.19*cm, strokeColor=ORANGE, strokeWidth=1.5))
    d.add(String(9.2*cm, 0.1*cm, "Trigger (relation logique)",
          fontName='Helvetica', fontSize=6.5, fillColor=ORANGE))
    d.add(Line(13.5*cm, 0.19*cm, 14.1*cm, 0.19*cm, strokeColor=LC, strokeWidth=1.5))
    d.add(String(14.2*cm, 0.1*cm, "FK formelle",
          fontName='Helvetica', fontSize=6.5, fillColor=LC))

    return d

# ─────────────────────────────────────────────────────────────────────────────
# CONTENU
# ─────────────────────────────────────────────────────────────────────────────
def build():
    path = "/Users/kurisu/Documents/Visual Code/docs/DOC_BDD_COMPLETE_v1.22.3.pdf"
    doc  = make_doc(path)
    story = []

    # ── Fiche d'identité ──────────────────────────────────────────────────────
    story.append(Spacer(1, 0.8*cm))
    story.append(Paragraph("Documentation complète — Base de données WEB_NATHANAEL", S['H1']))
    story.append(HRFlowable(width='100%', thickness=2, color=H_BLUE, spaceAfter=6))
    story.append(info_tbl([
        ["Projet",       "Board de Nathanaël"],
        ["SGBD",         "Azure SQL Edge Developer 15.0.2000.1574 (ARM64 / Linux Ubuntu 18.04)"],
        ["Base",         "WEB_NATHANAEL  |  Schéma : dbo  |  Compat. level : 150"],
        ["Serveur",      "mac-mini-de-christophe.tailbf2a66.ts.net : 1433"],
        ["Réseau",       "Tailscale (privé) — non exposé sur Internet"],
        ["Driver API",   "mssql ^9.2.1 (tedious)  |  Node.js 18"],
        ["Version doc.", VERSION_LABEL + "  |  " + DATE_MODIF],
    ]))
    story.append(Spacer(1, 0.4*cm))

    # ── Historique des versions ───────────────────────────────────────────────
    story += sec("Historique des versions")
    rows = [
        ["Version", "Date",       "Modifications"],
        ["1.22.0",  "2026-04-xx", "Création initiale de la base WEB_NATHANAEL"],
        ["1.22.1",  "2026-05-05", "Première documentation"],
        ["1.22.2",  "2026-05-05", "Correction IDENTITY (Mots 1027→29, UserID 1005→7). Procédure startup usp_ReseedIdentity_WEB_NATHANAEL. Documentation complète."],
        ["1.22.3",  "2026-05-06", "Ajout colonne RoleNotifPending (Utilisateurs). Trigger TRG_RolePromotionNotif (notification email promotion Admin). Fee971 promu Admin."],
    ]
    story.append(tbl(rows, [2*cm, 2.8*cm, 12.2*cm]))
    story.append(Spacer(1, 0.3*cm))

    # ── 1. Schéma ER ──────────────────────────────────────────────────────────
    story += sec("1. Schéma Entité-Relation")
    story.append(er_diagram())
    story.append(Spacer(1, 0.3*cm))

    # ── 2. Tables ──────────────────────────────────────────────────────────────
    story += sec("2. Description des tables")

    # 2.1 Utilisateurs
    story += sec("2.1  Utilisateurs", level=2)
    story.append(Paragraph(
        "Table centrale des comptes utilisateurs. "
        "Contraintes UNIQUE sur <b>Username</b> et <b>Email</b>. "
        "Les dates utilisent la fonction <b>dbo.Maintenant()</b> (UTC+2) comme valeur par défaut.",
        S['Body']))
    rows = [
        ["Colonne","Type","Nullable","Défaut","Notes"],
        ["UserID","INT IDENTITY","NO","—","PK auto-incrémenté"],
        ["Username","NVARCHAR(50)","NO","—","UNIQUE — login"],
        ["Email","NVARCHAR(100)","NO","—","UNIQUE"],
        ["Role","NVARCHAR(20)","YES","'User'","'Admin' ou 'User'"],
        ["PasswordHash","NVARCHAR(255)","YES","—","bcrypt salt 10 ou 'WAITING_FOR_HASH'"],
        ["MotDePasseIsActive","BIT","YES","0","0=en attente, 1=actif"],
        ["MustResetPassword","BIT","YES","0","1=reset requis"],
        ["UserCreatedDate","DATETIME","YES","Maintenant()","Date de création"],
        ["UserCreatedBy","NVARCHAR(50)","YES","—","Login créateur"],
        ["LastChangeDate","DATETIME","YES","Maintenant()","Dernière modif"],
        ["LastModificationUserBy","NVARCHAR(50)","YES","—","Login dernier modif"],
        ["RoleNotifPending","BIT","NO","0","1=email promotion Admin en attente d'envoi (v1.22.3)"],
    ]
    story.append(tbl(rows, [3.8*cm, 3.0*cm, 1.8*cm, 2.4*cm, 6.0*cm]))

    # 2.2 HistoriqueUtilisateurs
    story += sec("2.2  HistoriqueUtilisateurs", level=2)
    story.append(Paragraph(
        "Journal d'audit alimenté automatiquement par le trigger <b>TRG_UpdateUserAudit</b> "
        "lors de chaque UPDATE sur Utilisateurs. "
        "OldValue et NewValue contiennent les snapshots JSON complets de la ligne.",
        S['Body']))
    rows = [
        ["Colonne","Type","Nullable","Défaut","Notes"],
        ["LogID","INT IDENTITY","NO","—","PK auto-incrémenté"],
        ["UserID","INT","NO","—","Référence logique → Utilisateurs.UserID (pas de FK formelle)"],
        ["ActionType","NVARCHAR(50)","YES","—","Ex : 'UPDATE_PROFILE'"],
        ["OldValue","NVARCHAR(MAX)","YES","—","JSON de la ligne avant UPDATE"],
        ["NewValue","NVARCHAR(MAX)","YES","—","JSON de la ligne après UPDATE"],
        ["ChangedBy","NVARCHAR(50)","YES","—","Valeur de LastModificationUserBy"],
        ["ChangeDate","DATETIME","YES","Maintenant()","Horodatage UTC+2"],
    ]
    story.append(tbl(rows, [3.0*cm, 3.2*cm, 1.8*cm, 2.4*cm, 6.6*cm]))

    # 2.3 Orthophoniste
    story += sec("2.3  Orthophoniste", level=2)
    story.append(Paragraph(
        "Enregistre chaque séance orthophoniste. "
        "Les colonnes <b>Total</b> et <b>Complet</b> sont maintenues par le trigger "
        "<b>trg_Update_Ortho_Stats</b> et recalculées dynamiquement en CTE dans l'API.",
        S['Body']))
    rows = [
        ["Colonne","Type","Nullable","Notes"],
        ["Id","INT IDENTITY","NO","PK"],
        ["Date","DATETIME","YES","Date de la séance"],
        ["Total","INT","YES","Nb de mots — maintenu par trigger"],
        ["Complet","BIT","YES","1 si Total ≥ 10 — maintenu par trigger"],
    ]
    story.append(tbl(rows, [3.5*cm, 3.5*cm, 2.0*cm, 8.0*cm]))

    # 2.4 Orthophoniste_Mots
    story += sec("2.4  Orthophoniste_Mots", level=2)
    story.append(Paragraph(
        "Table de liaison many-to-many. PK composite (OrthophonisteId, MotId). "
        "FK formelles vers Orthophoniste.Id et Mots.Id.",
        S['Body']))
    rows = [
        ["Colonne","Type","Contrainte","Notes"],
        ["OrthophonisteId","INT","PK + FK → Orthophoniste.Id","Séance"],
        ["MotId","INT","PK + FK → Mots.Id","Mot travaillé"],
    ]
    story.append(tbl(rows, [4.0*cm, 2.5*cm, 5.0*cm, 5.5*cm]))

    # 2.5 Mots
    story += sec("2.5  Mots", level=2)
    story.append(Paragraph("Dictionnaire dédupliqué de tous les mots orthophoniques.", S['Body']))
    rows = [
        ["Colonne","Type","Nullable","Notes"],
        ["Id","INT IDENTITY","NO","PK"],
        ["Mot","NVARCHAR(255)","YES","Mot — clé métier dédupliquée côté API"],
    ]
    story.append(tbl(rows, [3.5*cm, 3.5*cm, 2.0*cm, 8.0*cm]))

    # 2.6 SiteButtons
    story += sec("2.6  SiteButtons", level=2)
    story.append(Paragraph(
        "Libellés configurables des boutons de l'accueil. "
        "Mise à jour via MERGE SQL transactionnel (Admin).",
        S['Body']))
    rows = [
        ["Colonne","Type","Nullable","Notes"],
        ["id","INT IDENTITY","NO","PK technique"],
        ["ButtonKey","NVARCHAR(255)","NO","Clé fonctionnelle (ex: btn_ortho)"],
        ["ButtonText","NVARCHAR(MAX)","YES","Texte affiché"],
        ["last_change_date","DATETIME2","YES","DEFAULT getdate()"],
    ]
    story.append(tbl(rows, [3.5*cm, 3.5*cm, 2.0*cm, 8.0*cm]))

    # ── 3. Contraintes ────────────────────────────────────────────────────────
    story += sec("3. Contraintes")

    story += sec("3.1  Clés primaires", level=2)
    rows = [
        ["Table","Colonne(s) PK","Type","Nom contrainte"],
        ["Utilisateurs","UserID","CLUSTERED IDENTITY","PK__Utilisat__1788CCAC…"],
        ["HistoriqueUtilisateurs","LogID","CLUSTERED IDENTITY","PK__Historiq__5E5499A8…"],
        ["Mots","Id","CLUSTERED IDENTITY","PK__Mots__3214EC07…"],
        ["Orthophoniste","Id","CLUSTERED IDENTITY","PK__Orthopho__3214EC07…"],
        ["Orthophoniste_Mots","OrthophonisteId + MotId","CLUSTERED composite","PK_Orthophoniste_Mots"],
        ["SiteButtons","id","CLUSTERED IDENTITY","PK__SiteButt__3213E83F…"],
    ]
    story.append(tbl(rows, [4.0*cm, 4.5*cm, 3.5*cm, 5.0*cm]))

    story += sec("3.2  Clés étrangères (FK formelles)", level=2)
    rows = [
        ["Nom FK","Table source","Colonne","→ Table cible","Colonne"],
        ["FK_Orthophoniste_Mots_Orthophoniste","Orthophoniste_Mots","OrthophonisteId","Orthophoniste","Id"],
        ["FK_Orthophoniste_Mots_Mots","Orthophoniste_Mots","MotId","Mots","Id"],
    ]
    story.append(tbl(rows, [5.5*cm, 3.5*cm, 2.8*cm, 3.2*cm, 2.0*cm]))
    story.append(Paragraph(
        "Note : <b>HistoriqueUtilisateurs.UserID</b> référence logiquement Utilisateurs.UserID "
        "mais sans FK formelle déclarée — relation maintenue par le trigger.",
        S['Body']))

    story += sec("3.3  Contraintes UNIQUE", level=2)
    rows = [
        ["Table","Colonne","Nom contrainte"],
        ["Utilisateurs","Username","UQ__Utilisat__536C85E4…"],
        ["Utilisateurs","Email","UQ__Utilisat__A9D10534…"],
    ]
    story.append(tbl(rows, [5*cm, 5*cm, 7*cm]))

    story += sec("3.4  Contraintes DEFAULT", level=2)
    rows = [
        ["Table","Colonne","Valeur par défaut"],
        ["Utilisateurs","Role","'User'"],
        ["Utilisateurs","MustResetPassword","0"],
        ["Utilisateurs","MotDePasseIsActive","0"],
        ["Utilisateurs","UserCreatedDate","dbo.Maintenant()"],
        ["Utilisateurs","LastChangeDate","dbo.Maintenant()"],
        ["HistoriqueUtilisateurs","ChangeDate","dbo.Maintenant()"],
        ["SiteButtons","last_change_date","getdate()"],
    ]
    story.append(tbl(rows, [5*cm, 5*cm, 7*cm]))

    # ── 4. Index ──────────────────────────────────────────────────────────────
    story += sec("4. Index")
    rows = [
        ["Table","Index","Type","Unique","Colonnes"],
        ["Utilisateurs","PK__Utilisat__…","CLUSTERED","Oui","UserID"],
        ["Utilisateurs","UQ__Utilisat__536C…","NONCLUSTERED","Oui","Username"],
        ["Utilisateurs","UQ__Utilisat__A9D1…","NONCLUSTERED","Oui","Email"],
        ["HistoriqueUtilisateurs","PK__Historiq__…","CLUSTERED","Oui","LogID"],
        ["Mots","PK__Mots__…","CLUSTERED","Oui","Id"],
        ["Orthophoniste","PK__Orthopho__…","CLUSTERED","Oui","Id"],
        ["Orthophoniste_Mots","PK_Orthophoniste_Mots","CLUSTERED","Oui","OrthophonisteId, MotId"],
        ["SiteButtons","PK__SiteButt__…","CLUSTERED","Oui","id"],
    ]
    story.append(tbl(rows, [4.0*cm, 4.5*cm, 2.8*cm, 1.5*cm, 4.2*cm]))

    # ── 5. Triggers ───────────────────────────────────────────────────────────
    story.append(PageBreak())
    story += sec("5. Triggers")

    story += sec("5.1  TRG_UpdateUserAudit", level=2)
    story.append(info_tbl([
        ["Table",       "Utilisateurs"],
        ["Événement",   "AFTER UPDATE"],
        ["Statut",      "Actif (is_disabled = false)"],
        ["Rôle",        "Insère une ligne dans HistoriqueUtilisateurs à chaque modification d'un utilisateur"],
    ]))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "CREATE TRIGGER [dbo].[TRG_UpdateUserAudit]<br/>"
        "ON [dbo].[Utilisateurs] AFTER UPDATE<br/>"
        "AS BEGIN<br/>"
        "&nbsp;&nbsp;SET NOCOUNT ON;<br/>"
        "&nbsp;&nbsp;INSERT INTO [dbo].[HistoriqueUtilisateurs]<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;(UserID, ActionType, OldValue, NewValue, ChangedBy, ChangeDate)<br/>"
        "&nbsp;&nbsp;SELECT i.UserID, 'UPDATE_PROFILE',<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;(SELECT * FROM deleted  d WHERE d.UserID = i.UserID FOR JSON PATH, WITHOUT_ARRAY_WRAPPER),<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;(SELECT * FROM inserted i2 WHERE i2.UserID = i.UserID FOR JSON PATH, WITHOUT_ARRAY_WRAPPER),<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;i.LastModificationUserBy, dbo.Maintenant()<br/>"
        "&nbsp;&nbsp;FROM inserted i;<br/>"
        "END;",
        S['CodeBlock']))

    story += sec("5.2  trg_Update_Ortho_Stats", level=2)
    story.append(info_tbl([
        ["Table",     "Orthophoniste_Mots"],
        ["Événement", "AFTER INSERT, DELETE"],
        ["Statut",    "Actif (is_disabled = false)"],
        ["Rôle",      "Met à jour Total et Complet dans Orthophoniste après chaque ajout/suppression de mot"],
    ]))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "CREATE TRIGGER trg_Update_Ortho_Stats<br/>"
        "ON Orthophoniste_Mots AFTER INSERT, DELETE<br/>"
        "AS BEGIN<br/>"
        "&nbsp;&nbsp;SET NOCOUNT ON;<br/>"
        "&nbsp;&nbsp;UPDATE O SET<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;Total   = (SELECT COUNT(*) FROM Orthophoniste_Mots OM WHERE OM.OrthophonisteId = O.Id),<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;Complet = CASE WHEN (SELECT COUNT(*) ...) >= 10 THEN 1 ELSE 0 END<br/>"
        "&nbsp;&nbsp;FROM Orthophoniste O<br/>"
        "&nbsp;&nbsp;WHERE O.Id IN (SELECT OrthophonisteId FROM inserted UNION SELECT OrthophonisteId FROM deleted);<br/>"
        "END;",
        S['CodeBlock']))

    story += sec("5.3  TRG_RolePromotionNotif  (v1.22.3)", level=2)
    story.append(info_tbl([
        ["Table",     "Utilisateurs"],
        ["Événement", "AFTER UPDATE"],
        ["Statut",    "Actif (is_disabled = false)"],
        ["Rôle",      "Pose RoleNotifPending=1 quand le rôle passe de non-Admin à Admin. Le background job API envoie l'email dans les 2 minutes puis remet le flag à 0."],
    ]))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "CREATE OR ALTER TRIGGER [dbo].[TRG_RolePromotionNotif]<br/>"
        "ON [dbo].[Utilisateurs] AFTER UPDATE<br/>"
        "AS BEGIN<br/>"
        "&nbsp;&nbsp;SET NOCOUNT ON;<br/>"
        "&nbsp;&nbsp;UPDATE U SET RoleNotifPending = 1<br/>"
        "&nbsp;&nbsp;FROM [dbo].[Utilisateurs] U<br/>"
        "&nbsp;&nbsp;INNER JOIN inserted i ON U.UserID = i.UserID<br/>"
        "&nbsp;&nbsp;INNER JOIN deleted  d ON U.UserID = d.UserID<br/>"
        "&nbsp;&nbsp;WHERE i.Role = 'Admin' AND d.Role &lt;&gt; 'Admin';<br/>"
        "END;",
        S['CodeBlock']))
    story.append(Paragraph(
        "Le flag est consommé par le <b>background job API</b> (intervalle 2 min) qui envoie "
        "un email à l'utilisateur promu lui indiquant de se déconnecter et reconnecter "
        "pour que le nouveau rôle prenne effet en session.",
        S['Body']))

    # ── 6. Fonctions ──────────────────────────────────────────────────────────
    story += sec("6. Fonctions utilisateur")

    story += sec("6.1  dbo.Maintenant()", level=2)
    story.append(info_tbl([
        ["Retourne",   "DATETIME"],
        ["Rôle",       "Retourne l'heure courante en UTC+2 (heure de Paris été)"],
        ["Utilisée par","Colonnes DEFAULT : UserCreatedDate, LastChangeDate (Utilisateurs), ChangeDate (HistoriqueUtilisateurs)"],
    ]))
    story.append(Paragraph(
        "CREATE FUNCTION dbo.Maintenant() RETURNS DATETIME AS BEGIN<br/>"
        "&nbsp;&nbsp;RETURN DATEADD(hour, 2, GETUTCDATE());<br/>"
        "END;",
        S['CodeBlock']))
    story.append(Paragraph(
        "Limitation : UTC+2 est fixe — ne tient pas compte du passage heure été/hiver. "
        "En hiver l'heure sera en avance d'1h.",
        S['Body']))

    # ── 7. Requêtes SQL clés ──────────────────────────────────────────────────
    story += sec("7. Requêtes SQL clés")

    story += sec("7.1  Lecture séances orthophoniste (CTE)", level=2)
    story.append(Paragraph(
        "Utilisée par <code>GET /api/orthophoniste</code>. "
        "Calcule Total, Complet et la liste des mots dynamiquement "
        "(les colonnes de la table sont aussi mises à jour par trigger) :",
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
        "ORDER BY O.Date DESC;",
        S['CodeBlock']))

    story += sec("7.2  MERGE SiteButtons", level=2)
    story.append(Paragraph(
        "INSERT ou UPDATE en une seule opération transactionnelle :", S['Body']))
    story.append(Paragraph(
        "MERGE INTO SiteButtons AS target<br/>"
        "USING (SELECT @key AS ButtonKey, @text AS ButtonText) AS source<br/>"
        "ON (target.ButtonKey = source.ButtonKey)<br/>"
        "WHEN MATCHED THEN UPDATE SET ButtonText = source.ButtonText,<br/>"
        "&nbsp;&nbsp;last_change_date = CAST(GETDATE() AS DATETIME2(0))<br/>"
        "WHEN NOT MATCHED THEN INSERT (ButtonKey, ButtonText, last_change_date)<br/>"
        "&nbsp;&nbsp;VALUES (source.ButtonKey, source.ButtonText, CAST(GETDATE() AS DATETIME2(0)));",
        S['CodeBlock']))

    # ── 8. IDENTITY & fix permanent ───────────────────────────────────────────
    story.append(PageBreak())
    story += sec("8. Gestion des colonnes IDENTITY")

    story += sec("8.1  État actuel des colonnes IDENTITY", level=2)
    rows = [
        ["Table","Colonne","Seed","Incrément","last_value actuel"],
        ["Utilisateurs","UserID","1","1","7"],
        ["HistoriqueUtilisateurs","LogID","1","1","18"],
        ["Mots","Id","1","1","29"],
        ["Orthophoniste","Id","1","1","38"],
        ["SiteButtons","id","1","1","5"],
    ]
    t2 = Table(rows, colWidths=[4.5*cm, 3.0*cm, 1.5*cm, 2.5*cm, 5.5*cm])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), TH_BG), ('TEXTCOLOR', (0,0), (-1,0), WHITE),
        ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'), ('FONTSIZE', (0,0), (-1,-1), 9),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, ROW_ALT]),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER), ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t2)

    story += sec("8.2  Pourquoi le redémarrage génère-t-il un saut de 1000 ?", level=2)
    story.append(Paragraph(
        "Ce comportement vient de l'architecture interne du cache IDENTITY de SQL Server :",
        S['Body']))
    for item in [
        "<b>Réservation par blocs en mémoire</b> — au démarrage, SQL Server ne relit pas la table pour connaître le dernier ID. Il réserve un bloc de 1000 valeurs en RAM (ex : IDs 30 à 1029) pour éviter une écriture disque à chaque INSERT. Tant que le service tourne, les INSERTs consomment ce pool en mémoire.",
        "<b>Cache non persisté sur disque</b> — ce bloc réservé n'est jamais écrit sur le disque. Si le conteneur s'arrête (même proprement), le cache est perdu. Au prochain démarrage, SQL Server lit le dernier ID écrit physiquement (29), réserve un nouveau bloc (1030–2029), et le premier INSERT suivant reçoit l'ID 1030.",
        "<b>Taille du bloc = 1000</b> — c'est la valeur par défaut pour les colonnes INT IDENTITY depuis SQL Server 2012. D'où les sauts toujours multiples de 1000.",
        "<b>ALTER DATABASE SET IDENTITY_CACHE OFF non disponible</b> — cette option (SQL Server 2017+) n'a pas été portée sur Azure SQL Edge, édition embarquée allégée ARM64.",
    ]:
        story.append(bul(item))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "Exemple observé sur cette base : table <b>Mots</b>, dernier ID réel = 29, "
        "last_value après redémarrage = 1027 (29 + 998 de cache perdu).",
        S['Body']))

    story += sec("8.3  Fix permanent : procédure de démarrage automatique", level=2)

    # Badge vert
    fix_t = Table([["  Correction permanente active depuis le 2026-05-05 — v1.22.2"]],
                  colWidths=[17*cm])
    fix_t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), GREEN_BG),
        ('TEXTCOLOR',  (0,0), (-1,-1), colors.HexColor('#155724')),
        ('FONTNAME',   (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE',   (0,0), (-1,-1), 9),
        ('PADDING',    (0,0), (-1,-1), 8),
        ('GRID',       (0,0), (-1,-1), 0.5, colors.HexColor('#C3E6CB')),
    ]))
    story.append(fix_t)
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph(
        "<b>ALTER DATABASE … SET IDENTITY_CACHE OFF</b> n'est pas disponible sur Azure SQL Edge. "
        "La solution retenue est une <b>procédure stockée dans master</b> marquée "
        "<code>is_auto_executed = true</code> via <b>sp_procoption</b> : "
        "elle s'exécute automatiquement à chaque démarrage du service SQL Server.",
        S['Body']))

    story.append(Paragraph(
        "-- Créée dans master (requis par sp_procoption)<br/>"
        "CREATE OR ALTER PROCEDURE [dbo].[usp_ReseedIdentity_WEB_NATHANAEL] AS<br/>"
        "BEGIN<br/>"
        "&nbsp;&nbsp;SET NOCOUNT ON;<br/>"
        "&nbsp;&nbsp;DECLARE @maxU INT = (SELECT ISNULL(MAX(UserID),0) FROM WEB_NATHANAEL.dbo.Utilisateurs);<br/>"
        "&nbsp;&nbsp;DECLARE @maxM INT = (SELECT ISNULL(MAX(Id),    0) FROM WEB_NATHANAEL.dbo.Mots);<br/>"
        "&nbsp;&nbsp;DECLARE @maxO INT = (SELECT ISNULL(MAX(Id),    0) FROM WEB_NATHANAEL.dbo.Orthophoniste);<br/>"
        "&nbsp;&nbsp;DECLARE @maxH INT = (SELECT ISNULL(MAX(LogID), 0) FROM WEB_NATHANAEL.dbo.HistoriqueUtilisateurs);<br/>"
        "&nbsp;&nbsp;DECLARE @maxS INT = (SELECT ISNULL(MAX(id),    0) FROM WEB_NATHANAEL.dbo.SiteButtons);<br/>"
        "&nbsp;&nbsp;DBCC CHECKIDENT ('WEB_NATHANAEL.dbo.Utilisateurs',           RESEED, @maxU) WITH NO_INFOMSGS;<br/>"
        "&nbsp;&nbsp;DBCC CHECKIDENT ('WEB_NATHANAEL.dbo.Mots',                   RESEED, @maxM) WITH NO_INFOMSGS;<br/>"
        "&nbsp;&nbsp;DBCC CHECKIDENT ('WEB_NATHANAEL.dbo.Orthophoniste',          RESEED, @maxO) WITH NO_INFOMSGS;<br/>"
        "&nbsp;&nbsp;DBCC CHECKIDENT ('WEB_NATHANAEL.dbo.HistoriqueUtilisateurs', RESEED, @maxH) WITH NO_INFOMSGS;<br/>"
        "&nbsp;&nbsp;DBCC CHECKIDENT ('WEB_NATHANAEL.dbo.SiteButtons',            RESEED, @maxS) WITH NO_INFOMSGS;<br/>"
        "END;<br/><br/>"
        "-- Activation exécution automatique au démarrage<br/>"
        "EXEC sp_procoption @ProcName='usp_ReseedIdentity_WEB_NATHANAEL',<br/>"
        "&nbsp;&nbsp;@OptionName='startup', @OptionValue='on';",
        S['CodeBlock']))

    story.append(Paragraph("Vérification :", S['Bold']))
    story.append(Paragraph(
        "SELECT name, is_auto_executed FROM master.sys.procedures<br/>"
        "WHERE name = 'usp_ReseedIdentity_WEB_NATHANAEL';<br/>"
        "-- Résultat : is_auto_executed = 1",
        S['CodeBlock']))

    story += sec("8.4  Procédure de vérification manuelle", level=2)
    story.append(Paragraph(
        "Si besoin de vérifier/corriger manuellement après un redémarrage :", S['Body']))
    story.append(Paragraph(
        "SELECT OBJECT_NAME(OBJECT_ID) AS Tbl, last_value,<br/>"
        "  CASE OBJECT_NAME(OBJECT_ID)<br/>"
        "    WHEN 'Utilisateurs'           THEN (SELECT MAX(UserID) FROM Utilisateurs)<br/>"
        "    WHEN 'Mots'                   THEN (SELECT MAX(Id) FROM Mots)<br/>"
        "    WHEN 'Orthophoniste'          THEN (SELECT MAX(Id) FROM Orthophoniste)<br/>"
        "    WHEN 'HistoriqueUtilisateurs' THEN (SELECT MAX(LogID) FROM HistoriqueUtilisateurs)<br/>"
        "    WHEN 'SiteButtons'            THEN (SELECT MAX(id) FROM SiteButtons)<br/>"
        "  END AS max_real<br/>"
        "FROM sys.identity_columns<br/>"
        "WHERE OBJECT_NAME(OBJECT_ID) IN<br/>"
        "  ('Utilisateurs','Mots','Orthophoniste','HistoriqueUtilisateurs','SiteButtons');",
        S['CodeBlock']))

    # ── 9. Connexion & Sécurité ───────────────────────────────────────────────
    story += sec("9. Connexion, pool et sécurité")
    story.append(info_tbl([
        ["Hôte",      "mac-mini-de-christophe.tailbf2a66.ts.net : 1433"],
        ["Base",      "WEB_NATHANAEL"],
        ["User",      "sa (via variable d'env DB_USER)"],
        ["Encrypt",   "false — réseau privé Tailscale uniquement"],
        ["TrustCert", "true"],
        ["Pool",      "ConnectionPool mssql — partagé par toutes les requêtes API"],
        ["Transactions","Utilisées pour import CSV, MERGE SiteButtons, renumérotation IDENTITY"],
    ]))
    story.append(Spacer(1, 0.3*cm))
    for item in [
        "Toutes les requêtes utilisent des <b>paramètres nommés</b> .input() — protection SQL injection",
        "Le champ PasswordHash n'est jamais renvoyé au client (destructuring côté API)",
        "SQL Server non exposé sur Internet — accessible uniquement via réseau Tailscale",
        "Mots de passe hashés bcrypt salt factor 10",
        "Comptes bloqués (MotDePasseIsActive=0) tant que le mot de passe n'est pas défini",
    ]:
        story.append(bul(item))

    doc.build(story, onFirstPage=hf, onLaterPages=hf)
    print(f"  [OK] {path}")

if __name__ == '__main__':
    build()
