"""Rasmiy attestatsiya pasporti va individual o‘quv rejasi (PDF, ReportLab)."""
from __future__ import annotations

import io
from pathlib import Path

from reportlab.graphics import renderPDF
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Flowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.models import EvalSession
from app.seed.catalog_data import BLOCKS
from app.services.scoring_engine import BLOCKS as CODES, DEFAULT_WEIGHTS

NAVY = colors.HexColor("#1B365D")
SLATE = colors.HexColor("#2B547E")
EMERALD = colors.HexColor("#10B981")
CRIMSON = colors.HexColor("#EF4444")
AMBER = colors.HexColor("#F59E0B")

_FONT_CANDIDATES = [
    ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    ("C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/arialbd.ttf"),
]


def _fonts() -> tuple[str, str]:
    if "CCG" in pdfmetrics.getRegisteredFontNames():
        return "CCG", "CCG-Bold"
    for regular, bold in _FONT_CANDIDATES:
        if Path(regular).exists() and Path(bold).exists():
            pdfmetrics.registerFont(TTFont("CCG", regular))
            pdfmetrics.registerFont(TTFont("CCG-Bold", bold))
            pdfmetrics.registerFontFamily("CCG", normal="CCG", bold="CCG-Bold", italic="CCG", boldItalic="CCG-Bold")
            return "CCG", "CCG-Bold"
    return "Helvetica", "Helvetica-Bold"


class QR(Flowable):
    def __init__(self, value: str, size: float = 30 * mm):
        super().__init__()
        self.value, self.size = value, size
        self.width = self.height = size

    def draw(self):
        w = QrCodeWidget(self.value)
        x1, y1, x2, y2 = w.getBounds()
        d = Drawing(self.size, self.size, transform=[self.size / (x2 - x1), 0, 0, self.size / (y2 - y1), 0, 0])
        d.add(w)
        renderPDF.draw(d, self.canv, 0, 0)


def build_passport_pdf(sess: EvalSession, verify_url: str) -> bytes:
    regular, bold = _fonts()
    st = {
        "h1": ParagraphStyle("h1", fontName=bold, fontSize=13, leading=17, textColor=NAVY, alignment=TA_CENTER),
        "h2": ParagraphStyle("h2", fontName=bold, fontSize=11, leading=14, textColor=NAVY, spaceBefore=8,
                             spaceAfter=4),
        "p": ParagraphStyle("p", fontName=regular, fontSize=9, leading=12),
        "small": ParagraphStyle("s", fontName=regular, fontSize=7.5, leading=10, textColor=colors.HexColor("#475569")),
        "center": ParagraphStyle("c", fontName=regular, fontSize=9, leading=12, alignment=TA_CENTER),
        "cell": ParagraphStyle("cell", fontName=regular, fontSize=8.5, leading=11),
        "cellb": ParagraphStyle("cellb", fontName=bold, fontSize=8.5, leading=11, textColor=colors.white),
    }
    off = sess.officer
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm, topMargin=14 * mm,
                            bottomMargin=14 * mm, title=f"Attestatsiya pasporti — {off.full_name}",
                            author="CyberComp-Gov")
    story = [
        Paragraph("O‘ZBEKISTON RESPUBLIKASI", st["center"]),
        Paragraph("CyberComp-Gov — Davlat organlari AKT mas’ul xodimlari axborot xavfsizligi "
                  "kompetensiyalarini baholash axborot tizimi", st["center"]),
        Spacer(1, 5 * mm),
        Paragraph("AXBOROT XAVFSIZLIGI KOMPETENSIYALARI BO‘YICHA<br/>INDIVIDUAL ATTESTATSIYA PASPORTI", st["h1"]),
        Paragraph(f"№ {sess.verify_code} · {sess.created_at:%d.%m.%Y}", st["center"]),
        Spacer(1, 5 * mm),
    ]

    phi_ok = sess.phi_flag == 1
    meta = [
        ["F.I.Sh.", off.full_name],
        ["PINFL", off.pinfl],
        ["Lavozimi", off.position],
        ["Davlat organi", f"{off.agency.name} ({off.agency.category})"],
        ["Ish staji", f"{off.experience_years} yil"],
        ["Baholash bosqichi", {"before": "Manzilli o‘qitishdan oldin", "after": "Manzilli o‘qitishdan keyin"}
         .get(sess.stage, "Attestatsiya")],
    ]
    meta_tbl = Table([[Paragraph(a, st["cell"]), Paragraph(b, st["cell"])] for a, b in meta],
                     colWidths=[38 * mm, 98 * mm])
    meta_tbl.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F1F5F9")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    head = Table([[meta_tbl, [QR(verify_url), Paragraph("QR — haqiqiylikni tekshirish", st["small"])]]],
                 colWidths=[140 * mm, 38 * mm])
    head.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story += [head, Spacer(1, 4 * mm)]

    level_color = EMERALD if phi_ok and sess.i_axk >= 71 else (CRIMSON if sess.i_axk < 55 or not phi_ok else AMBER)
    summary = Table([
        [Paragraph("Integral indeks I<sub>AXK</sub>", st["cellb"]), Paragraph("Chegara sharti Φ(C2, C3)", st["cellb"]),
         Paragraph("Kvalimetrik daraja", st["cellb"])],
        [Paragraph(f"<b>{sess.i_axk:.2f}</b> / 100", st["cell"]),
         Paragraph(f"<b>Φ = {sess.phi_flag}</b> — " + ("bajarilgan" if phi_ok else "BAJARILMAGAN: " + ", ".join(
             f"{b} = {v:.0f} &lt; 50" for b, v in (("C2", sess.c2_score), ("C3", sess.c3_score)) if v < 50)),
                   st["cell"]),
         Paragraph(f"<b>{sess.level_name}</b>", st["cell"])],
    ], colWidths=[50 * mm, 60 * mm, 68 * mm])
    summary.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("BOX", (0, 0), (-1, -1), 0.8, NAVY),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
        ("LINEBELOW", (2, 1), (2, 1), 2, level_color),
    ]))
    story += [summary, Spacer(1, 2 * mm),
              Paragraph(f"<b>Komissiya qarori:</b> {sess.decision_text}", st["p"])]

    story.append(Paragraph("KSA dekompozitsiyasi va ko‘nikmalar bo‘shlig‘i (Skill Gap Matrix)", st["h2"]))
    names = {b["code"]: b["name"] for b in BLOCKS}
    rows = [[Paragraph(x, st["cellb"]) for x in
             ("Blok", "w<sub>i</sub>", "K (0.30)", "S (0.40)", "A (0.30)", "C<sub>i</sub>",
              f"ΔC<sub>i</sub> (C<sub>norm</sub>={sess.norm_threshold:.0f})")]]
    c = {"C1": sess.c1_score, "C2": sess.c2_score, "C3": sess.c3_score, "C4": sess.c4_score}
    for b in CODES:
        delta = max(0.0, sess.norm_threshold - c[b])
        rows.append([Paragraph(f"<b>{b}</b> — {names[b]}", st["cell"]), f"{DEFAULT_WEIGHTS[b]:.2f}",
                     f"{sess.k_scores_json[b]:.1f}", f"{sess.s_scores_json[b]:.1f}", f"{sess.a_scores_json[b]:.1f}",
                     f"{c[b]:.0f}", f"{delta:.1f}"])
    t = Table(rows, colWidths=[70 * mm, 13 * mm, 17 * mm, 17 * mm, 17 * mm, 14 * mm, 30 * mm])
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), SLATE),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
        ("FONTNAME", (1, 1), (-1, -1), regular),
        ("FONTSIZE", (1, 1), (-1, -1), 8.5),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]
    for i, b in enumerate(CODES, start=1):
        if b in ("C2", "C3") and c[b] < 50:
            style.append(("BACKGROUND", (5, i), (5, i), colors.HexColor("#FEE2E2")))
        if max(0.0, sess.norm_threshold - c[b]) > 15:
            style.append(("BACKGROUND", (6, i), (6, i), colors.HexColor("#FEF3C7")))
    t.setStyle(TableStyle(style))
    story += [t, Paragraph("C<sub>i</sub> = 0.30·K + 0.40·S + 0.30·A; I<sub>AXK</sub> = 0.20·C1 + 0.35·C2 + 0.25·C3 + "
                           "0.20·C4; ΔC<sub>i</sub> = max(0, C<sub>norm</sub> − C<sub>i</sub>)", st["small"])]

    story.append(Paragraph("Avtomatik shakllantirilgan individual o‘quv trayektoriyasi", st["h2"]))
    if sess.gaps:
        rows = [[Paragraph(x, st["cellb"]) for x in ("Blok", "O‘quv moduli", "ΔC", "Soat", "Muddat")]]
        for g in sess.gaps:
            rows.append([g.block_code if g.block_code != "BASE" else "Barcha", Paragraph(
                g.assigned_course_title + (f" ({g.sub_code})" if g.sub_code else ""), st["cell"]),
                f"{g.delta_c:.1f}", str(g.course_hours), f"{g.deadline_days} kun"])
        t = Table(rows, colWidths=[16 * mm, 108 * mm, 16 * mm, 16 * mm, 22 * mm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), SLATE),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
            ("FONTNAME", (0, 1), (-1, -1), regular),
            ("FONTSIZE", (0, 1), (-1, -1), 8.5),
            ("ALIGN", (2, 1), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(t)
    else:
        story.append(Paragraph("ΔC<sub>i</sub> > 15 bo‘lgan blok aniqlanmadi — majburiy qayta tayyorlash talab "
                               "etilmaydi.", st["p"]))

    story += [
        Spacer(1, 12 * mm),
        Table([[Paragraph("Attestatsiya komissiyasi raisi: ____________________", st["p"]),
                Paragraph("Xodim: ____________________", st["p"])]], colWidths=[95 * mm, 83 * mm]),
        Spacer(1, 6 * mm),
        Paragraph(f"Hujjat CyberComp-Gov tizimida avtomatik shakllantirildi. Tekshirish: {verify_url}", st["small"]),
    ]
    doc.build(story)
    return buf.getvalue()
