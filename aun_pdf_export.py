"""PDF-Export (fpdf2, Kernschriften): Einstellungen, Kennzahlen der Hauptansicht, Auszahlungen je Betrieb und die Verdikte. Erst nach Klick erzeugt (DEMO-PLAYBOOK §1c)."""

from __future__ import annotations

from fpdf import FPDF

import aun_constants as C
import aun_evaluation as V
from aun_scenario import Settings

_REPLACE = {"–": "-", "—": "-", "≤": "<=", "≥": ">=", "≠": "!=", "√": "Wurzel", "²": "2", "Σ": "Summe", "°": " Grad", "·": "*", "−": "-", "„": '"', "“": '"', "∞": "unendlich",
            "→": "->", "ε": "eps", "β": "beta", "α": "alpha", "θ": "theta", "λ": "lambda", "σ": "sigma", "π": "pi", "δ": "delta", "η": "eta", "Δ": "Delta", "γ": "gamma", "ρ": "rho",
            "φ": "phi", "κ": "kappa", "≈": "~", "½": "1/2", "…": "...", "‚": ",", "‘": "'", "’": "'", "”": '"', "µ": "mu", "∈": "in", "¹": "1", "₀": "0", "₁": "1", "₂": "2",
            "±": "+-", "⋅": "*", "€": "EUR", "⁻": "-", "³": "3"}


def _latin(text: str) -> str:
    """Kernschriften kennen nur Latin-1 (Umlaute gehören dazu): Sonderzeichen ersetzen, Markdown-Zeichen entfernen."""
    for a, b in _REPLACE.items():
        text = text.replace(a, b)
    return text.replace("**", "").replace("`", "").encode("latin-1", "replace").decode("latin-1")


def build_pdf(s: Settings, view: V.View, verdicts: list[tuple[str, str]]) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 9, _latin("Wer hat im Netz Verhandlungsmacht? Das Austauschnetz"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    extra = f"; Kantenwahrscheinlichkeit {s.p} %" if s.net in ("rand_bip", "rand_gen") else ""
    pdf.multi_cell(0, 5, _latin(f"Netz: {C.NETS[s.net]}; Betriebe (Regler) {s.n}{extra}; Dämpfung {V.de(s.kappa, 2)}; Zufalls-Seed {s.seed}."), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "Kennzahlen", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    net = view.net
    lines = [f"{net.n} Betriebe, {len(net.edges)} Touren; größtes Matching {view.ip}, LP-Wert {V.de(view.lp, 2)}; stabiles Ergebnis: {'ja' if view.stable else 'nein'}."]
    if view.ok:
        lines.append(f"Ausgewogenes Ergebnis ({view.outcome.method}); {len(view.fixed)} Betriebe festgelegt, {net.n - len(view.fixed)} offen.")
        shown = min(net.n, 40)
        lines.append("Auszahlungen: " + "; ".join(f"{net.label(i)}: {V.val_text(view.y(i), view.yx(i))}" for i in range(shown)) + (" ..." if net.n > shown else "") + ".")
    for line in lines:
        pdf.multi_cell(0, 5, _latin(line), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "Verdikte", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    for _, text in verdicts:
        pdf.multi_cell(0, 5, _latin(text), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)
    pdf.set_font("Helvetica", "I", 8)
    pdf.multi_cell(0, 4, _latin("Netze, Überschüsse und Auszahlungen sind Modellannahmen, keine Aussagen über echte Betriebe. Alle Zahlen sind eigene Rechnung (exakt in Brüchen, wo vermerkt), "
                                "gestützt durch Handrechnung und unabhängige Rechenwege in den Tests."), new_x="LMARGIN", new_y="NEXT")
    return bytes(pdf.output())
