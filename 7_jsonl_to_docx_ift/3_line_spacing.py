def apply_115_spacing(paragraph):
    """Apply 1.15 line spacing with no extra spacing before/after"""
    pf = paragraph.paragraph_format
    pf.line_spacing = 1.15
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)


def add_heading_115(doc, text):
    h = doc.add_heading(text, level=1)
    apply_115_spacing(h)
    return h


def add_paragraph_115(doc, text):
    p = doc.add_paragraph(text)
    apply_115_spacing(p)
    return p