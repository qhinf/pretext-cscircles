#!/usr/bin/env python3
"""Zet de gearchiveerde Nederlandse CS Circles-pagina's om naar PreTeXt.

Invoer:  archief/<naam>.html   (pagina's uit de Wayback Machine, zie tools/fetch_archive.py)
         tools/lessen.py       (volgorde en metadata van de lessen)
         tools/toetsen/*.py    (zelfgeschreven referentie-oplossingen en testgevallen)
Uitvoer: source/<chapter>.ptx

Gebruik: python3 tools/convert.py
"""

import copy
import html
import os
import re
import sys
import urllib.parse

import lxml.etree as ET
import lxml.html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import lessen  # noqa: E402
import toetsen  # noqa: E402
from harnas import maak_tests, voorcode as harnas_voorcode  # noqa: E402

XI = "http://www.w3.org/2001/XInclude"

# De tekst die CS Circles automatisch in lege programmeervakken zette.
AUTOCOMMENT = "# verwijder dit commentaar en type hier je code"

INLINE_TAGS = {"em", "i", "strong", "b", "code", "tt", "a", "span", "sup", "sub",
               "del", "s", "u", "font", "abbr", "kbd", "label", "big", "small", "q"}

WARNINGS = []

# Elementen waarin voorbeelden, opmerkingen en oefeningen mogen staan.
DIVISIONS = {"chapter", "appendix", "section", "subsection", "introduction", "conclusion", "preface"}


def warn(msg):
    WARNINGS.append(msg)
    print("waarschuwing:", msg, file=sys.stderr)


def slug_to_label(slug):
    return "oef-" + re.sub(r"[^A-Za-z0-9]+", "-", slug).strip("-").lower()


def classes(el):
    return (el.get("class") or "").split()


# --------------------------------------------------------------------------
# Inline-inhoud
# --------------------------------------------------------------------------

class Inline:
    """Verzamelt inline PreTeXt-inhoud (tekst + elementen) in een container-element."""

    def __init__(self, parent):
        self.parent = parent

    def text(self, s):
        if not s:
            return
        if len(self.parent):
            last = self.parent[-1]
            last.tail = (last.tail or "") + s
        else:
            self.parent.text = (self.parent.text or "") + s

    def add(self, tag, text=None, **attrs):
        el = ET.SubElement(self.parent, tag, {k.replace("_", "-"): v for k, v in attrs.items()})
        if text is not None:
            el.text = text
        return el


def is_empty_inline(el):
    """Is het (inline) element leeg, afgezien van witruimte?"""
    return (el.text is None or not el.text.strip()) and len(el) == 0


def normalize_space(s):
    return re.sub(r"\s+", " ", s)


# --------------------------------------------------------------------------
# De converter voor een pagina
# --------------------------------------------------------------------------

class Page:
    def __init__(self, info):
        self.info = info
        self.name = info["naam"]
        self.chapter_id = info["id"]
        path = os.path.join(ROOT, "archief", self.name + ".html")
        self.doc = lxml.html.parse(path).getroot()
        self.hints = {}
        for hb in self.doc.find_class("hintbox"):
            hid = hb.get("id", "").replace("hintbox", "")
            for link in hb.find_class("hintboxlink"):
                link.drop_tree()
            for em in hb.xpath(".//em"):
                if "hint verslepen" in em.text_content():
                    em.drop_tree()
            self.hints[hid] = hb
        self.example_count = 0
        self.pending_hints = []  # hints uit popups buiten oefeningen
        self.current_exercise_hints = None
        self.images = set()

    # ---------------- inline ----------------

    def inline(self, node, out, in_code=False):
        """Zet de kinderen van node om naar inline-inhoud in out (een Inline)."""
        out.text(normalize_space(node.text or "") if not in_code else (node.text or ""))
        for child in node:
            if not isinstance(child.tag, str):
                out.text(normalize_space(child.tail or ""))
                continue
            self.inline_element(child, out)
            out.text(normalize_space(child.tail or ""))

    def inline_element(self, el, out):
        tag = el.tag
        cls = classes(el)
        if tag in ("code", "tt", "kbd"):
            txt = el.text_content()
            if txt.strip():
                out.add("c", txt.replace("\n", " "))
            return
        if tag in ("em", "i"):
            e = out.add("em")
            self.inline(el, Inline(e))
            if is_empty_inline(e):
                self.remove_keep_tail(e)
            return
        if tag in ("strong", "b"):
            e = out.add("alert")
            self.inline(el, Inline(e))
            if is_empty_inline(e):
                self.remove_keep_tail(e)
            return
        if tag in ("del", "s"):
            e = out.add("delete")
            self.inline(el, Inline(e))
            return
        if tag == "a":
            self.link(el, out)
            return
        if tag == "img":
            self.inline_image(el, out)
            return
        if tag == "br":
            out.text(" ")
            return
        if tag == "sup":
            txt = el.text_content().strip()
            if txt:
                out.add("m", "^{\\text{%s}}" % txt)
            return
        if tag == "sub":
            txt = el.text_content().strip()
            if txt:
                out.add("m", "_{\\text{%s}}" % txt)
            return
        if tag in ("input", "select", "option", "script", "textarea"):
            return
        # span, font, label, ... : alleen de inhoud
        self.inline(el, out)

    def remove_keep_tail(self, el):
        parent = el.getparent()
        tail = el.tail
        prev = el.getprevious()
        parent.remove(el)
        if tail:
            if prev is not None:
                prev.tail = (prev.tail or "") + tail
            else:
                parent.text = (parent.text or "") + tail

    def link(self, el, out):
        cls = classes(el)
        if "hintlink" in cls:
            hid = el.get("id", "").replace("hintlink", "")
            ltext = normalize_space(el.text_content()).strip()
            # Losse linkteksten als "Hint 1" of "Klik hier voor een tip" verdwijnen uit de tekst
            # (de hint komt onder de oefening); linkteksten midden in een zin blijven staan.
            drop = re.search(r"(?i)klik", ltext) or re.match(r"^[A-Z#]", ltext)
            if not drop or self.current_exercise_hints is None:
                self.inline(el, out)
            hint = self.hints.get(hid)
            if hint is not None:
                title = normalize_space(el.text_content()).strip()
                if self.current_exercise_hints is not None:
                    self.current_exercise_hints.append((title, hint))
                else:
                    self.pending_hints.append((title, hint))
            return
        href = el.get("href")
        if not href:
            self.inline(el, out)
            return
        href = unarchive(href)
        if "consolecode=" in href:
            # "Probeer dit in de console": de tekst blijft, de code komt als ActiveCode na de alinea.
            code = urllib.parse.parse_qs(urllib.parse.urlparse(href).query).get("consolecode", [""])[0]
            self.inline(el, out)
            if code.strip():
                self.deferred_images.append(("console", code))
            return
        target = lessen.link_target(href)
        text_el = ET.Element("tmp")
        self.inline(el, Inline(text_el))
        if target:
            x = out.add("xref", ref=target)
            x.set("text", "custom")
            x.text = text_el.text
            for c in text_el:
                x.append(c)
            if not len(x) and not (x.text or "").strip():
                x.text = None
                x.set("text", "title")
            return
        if href.startswith("/"):
            href = "https://cscircles.cemc.uwaterloo.ca" + href
        if "cscircles.cemc.uwaterloo.ca" in href and not lessen.keep_url(href):
            # verwijzing naar iets dat niet meer bestaat (inloggen, console, ...): alleen tekst
            out.text(text_el.text or "")
            for c in list(text_el):
                tail = c.tail
                c.tail = None
                out.parent.append(c)
                out.text(tail or "")
            return
        u = out.add("url", href=href, visual=pretty_url(href))
        u.text = text_el.text
        for c in text_el:
            u.append(c)
        if not len(u) and not (u.text or "").strip():
            u.text = None

    def inline_image(self, el, out):
        if "latex" in classes(el):
            out.add("m", html.unescape(el.get("alt", "")).strip())
            return
        src = el.get("src", "")
        if any(x in src for x in ("checked.png", "icon.png", "warning.png", "smiley")):
            return
        # losse afbeelding midden in een alinea: als blok na de alinea
        self.deferred_images.append(el)

    # ---------------- blokken ----------------

    def blocks(self, container, parent):
        """Zet de kinderen van container om naar blokken in parent (een PreTeXt-element)."""
        para = None

        def flush():
            nonlocal para
            if para is not None:
                strip_para(para)
                if is_empty_inline(para):
                    parent.remove(para)
                para = None
            for img in self.deferred_images:
                if isinstance(img, tuple):
                    self.example_count += 1
                    prog = ET.SubElement(parent, "program", {"interactive": "activecode", "language": "python",
                                                            "label": "%s-console-%d" % (self.chapter_id,
                                                                                        self.example_count)})
                    ET.SubElement(prog, "code").text = "\n" + img[1].rstrip() + "\n"
                else:
                    self.block_image(img, parent)
            self.deferred_images = []

        def ensure_para():
            nonlocal para
            if para is None:
                para = ET.SubElement(parent, "p")
            return para

        def add_text(s):
            if s and s.strip():
                Inline(ensure_para()).text(normalize_space(s))
            elif s and para is not None:
                Inline(para).text(" ")

        add_text(container.text)
        for child in container:
            if not isinstance(child.tag, str):
                add_text(child.tail)
                continue
            tag = child.tag
            cls = classes(child)
            if tag == "br":
                nxt = child.getnext()
                if (child.tail or "").strip() == "" and nxt is not None and nxt.tag == "br":
                    flush()
                elif para is not None:
                    Inline(para).text(" ")
            elif (tag in INLINE_TAGS or tag == "img") and not has_blocks(child):
                if tag == "a" and child.get("href") is None and not child.text_content().strip():
                    pass
                else:
                    p = ensure_para()
                    self.inline_element(child, Inline(p))
            elif tag in ("script", "input", "style", "noscript"):
                pass
            else:
                flush()
                self.block(child, parent)
            add_text(child.tail)
        flush()

    def block(self, el, parent):
        tag = el.tag
        cls = classes(el)
        if tag == "p" or (tag == "div" and not cls) or tag in ("center", "blockquote") or tag in INLINE_TAGS:
            self.blocks(el, parent)
        elif tag == "pre":
            self.pre(el, parent)
        elif tag in ("ul", "ol"):
            self.listing(el, parent)
        elif tag == "dl":
            self.dlist(el, parent)
        elif tag == "table" and "pywarn" in cls:
            self.pywarn(el, parent)
        elif tag == "table":
            self.table(el, parent)
        elif tag == "form" and "pbform" in cls:
            box = el.find_class("pybox")
            if box:
                self.pybox(box[0], parent)
        elif tag == "div" and "pybox" in cls:
            if "modeNeutral" in cls:
                self.pybox(el, parent)
            else:
                self.worked_example(el, parent)
        elif tag == "div" and "collapseContain" in cls:
            self.collapse(el, parent)
        elif tag == "div" and "accordion" in cls:
            self.blocks(el, parent)
        elif tag == "iframe":
            self.iframe(el, parent)
        elif tag in ("h1", "h2", "h3", "h4", "h5"):
            # koppen worden in structure() afgehandeld; hier (in een blok) als vetgedrukte alinea
            p = ET.SubElement(parent, "p")
            a = ET.SubElement(p, "alert")
            self.inline(el, Inline(a))
        elif tag == "img":
            self.block_image(el, parent)
        elif tag == "hr":
            pass
        elif tag == "div":
            self.blocks(el, parent)
        else:
            warn("%s: onbekend blok-element <%s class=%s>" % (self.name, tag, cls))
            self.blocks(el, parent)

    def pre(self, el, parent, force_program=False):
        text = pre_text(el)
        if not text.strip():
            return
        pre = ET.SubElement(parent, "pre")
        pre.text = "\n" + text.strip("\n") + "\n"

    def listing(self, el, parent):
        # In PreTeXt staan lijsten in een alinea; hoort de lijst bij de vorige alinea (die eindigt
        # op een dubbele punt), dan komt hij daarin.
        prev = parent[-1] if len(parent) else None
        prev_text = ""
        if prev is not None and prev.tag == "p":
            prev_text = (prev[-1].tail if len(prev) else prev.text) or ""
        if prev is not None and prev.tag == "p" and prev_text.rstrip().endswith(":") and \
                not prev.xpath("./ul|./ol|./dl"):
            holder = prev
        else:
            holder = ET.SubElement(parent, "p")
        lst = ET.SubElement(holder, el.tag)
        for li in el:
            if not isinstance(li.tag, str) or li.tag != "li":
                continue
            item = ET.SubElement(lst, "li")
            self.blocks(li, item)
            if len(item) == 0:
                lst.remove(item)
        if len(lst) == 0:
            holder.remove(lst)
            if holder is not prev and len(holder) == 0:
                parent.remove(holder)

    def dlist(self, el, parent):
        # WordPress-afbeelding met onderschrift: <dl><dt><img/></dt><dd>onderschrift</dd></dl>
        imgs = el.xpath("./dt//img")
        if imgs:
            fig = ET.SubElement(parent, "figure")
            cap = ET.SubElement(fig, "caption")
            for dd in el.xpath("./dd"):
                self.inline(dd, Inline(cap))
            strip_para(cap)
            link = el.xpath("./dt//a/@href")
            if link:
                Inline(cap).text(" (")
                u = ET.SubElement(cap, "url", {"href": link[0], "visual": pretty_url(link[0])})
                u.text = "bron"
                Inline(cap).text(")")
            self.block_image(imgs[0], fig)
            return
        lst = ET.SubElement(ET.SubElement(parent, "p"), "dl")
        item = None
        for c in el:
            if not isinstance(c.tag, str):
                continue
            if c.tag == "dt":
                item = ET.SubElement(lst, "li")
                t = ET.SubElement(item, "title")
                self.inline(c, Inline(t))
            elif c.tag == "dd" and item is not None:
                self.blocks(c, item)

    def pywarn(self, el, parent):
        right = el.find_class("pywarnright")
        if parent.tag not in DIVISIONS:
            self.blocks(right[0] if right else el, parent)
            return
        box = ET.SubElement(parent, "assemblage")
        self.blocks(right[0] if right else el, box)
        if len(box) == 0:
            parent.remove(box)

    def table(self, el, parent):
        rows = el.xpath(".//tr")
        if not rows:
            return
        tab = ET.SubElement(parent, "tabular")
        mono = "mono" in classes(el)
        for tr in rows:
            row = ET.SubElement(tab, "row")
            if tr.xpath("./th") and not tr.xpath("./td"):
                row.set("header", "yes")
            for cell in tr:
                if not isinstance(cell.tag, str) or cell.tag not in ("td", "th"):
                    continue
                c = ET.SubElement(row, "cell")
                if cell.get("colspan"):
                    c.set("colspan", cell.get("colspan"))
                if mono and cell.tag == "td" and not cell.xpath(".//strong|.//del"):
                    txt = cell.text_content().strip()
                    if txt:
                        ET.SubElement(c, "c").text = txt
                else:
                    self.inline(cell, Inline(c))
                    strip_para(c)

    def worked_example(self, el, parent):
        if parent.tag not in DIVISIONS:
            self.blocks(el, parent)
            return
        ex = ET.SubElement(parent, "example")
        # Een uitgewerkt voorbeeld met een tabel die stap voor stap de waarden toont.
        self.blocks(el, ex)
        if len(ex) == 0:
            parent.remove(ex)

    def collapse(self, el, parent):
        head = el.find_class("collapseHead")
        body = el.find_class("collapseBody")
        body = body[0] if body else el
        # Bevat het een oefening, dan gewoon de inhoud tonen.
        if body.find_class("pybox"):
            self.blocks(body, parent)
            return
        title = normalize_space(head[0].text_content()).strip() if head else ""
        # Een uitklapbare aanwijzing in de beschrijving van een oefening wordt een hint.
        if self.current_exercise_hints is not None:
            self.current_exercise_hints.append((title, body))
            return
        # Een uitklapbare aanwijzing direct na een oefening hoort bij die oefening.
        prev = parent[-1] if len(parent) else None
        if prev is not None and prev.tag == "exercise":
            h = ET.Element("hint")
            if title:
                t = ET.SubElement(h, "title")
                Inline(t).text(title)
            self.blocks(body, h)
            insert_hint(prev, h)
            return
        if parent.tag not in DIVISIONS:
            if title:
                p = ET.SubElement(parent, "p")
                a = ET.SubElement(p, "alert")
                self.inline(head[0], Inline(a))
                strip_para(a)
            self.blocks(body, parent)
            return
        rem = ET.SubElement(parent, "remark")
        if title:
            t = ET.SubElement(rem, "title")
            self.inline(head[0], Inline(t))
            strip_para(t)
        self.blocks(body, rem)

    def iframe(self, el, parent):
        src = unarchive(el.get("src", ""))
        if "iframe-embed.html" in src or "pythontutor" in src.lower():
            frag = src.split("#", 1)[1] if "#" in src else src.split("?", 1)[-1]
            params = urllib.parse.parse_qs(frag)
            code = params.get("code", [""])[0]
            self.example_count += 1
            label = "%s-codelens-%d" % (self.chapter_id, self.example_count)
            prog = ET.SubElement(parent, "program", {"interactive": "codelens", "language": "python",
                                                    "label": label})
            c = ET.SubElement(prog, "code")
            c.text = "\n" + code.rstrip() + "\n"
            return
        m = re.search(r"youtube(?:-nocookie)?\.com/embed/([A-Za-z0-9_-]+)", src)
        if m:
            ET.SubElement(parent, "video", {"youtube": m.group(1), "width": "80%"})
            return
        warn("%s: onbekende iframe %s" % (self.name, src))

    def block_image(self, el, parent):
        src = unarchive(el.get("src", ""))
        if any(x in src for x in ("checked.png", "icon.png", "warning.png")):
            return
        fname = lessen.image_name(src)
        if not fname:
            warn("%s: afbeelding zonder bestand %s" % (self.name, src))
            return
        self.images.add((fname, src))
        attrs = {"source": "images/" + fname}
        width = el.get("width")
        px = None
        if width and width.rstrip("px").isdigit():
            px = int(width.rstrip("px"))
        else:
            px = image_width(os.path.join(ROOT, "assets", "images", fname))
        if px:
            # ongeveer de grootte zoals op CS Circles (tekstkolom van zo'n 700 pixels)
            attrs["width"] = "%d%%" % max(10, min(100, round(px / 7)))
        img = ET.SubElement(parent, "image", attrs)
        alt = el.get("alt") or el.get("title")
        if alt and alt.strip():
            ET.SubElement(img, "shortdescription").text = alt.strip()

    # ---------------- pybox: voorbeelden en oefeningen ----------------

    def pybox(self, box, parent):
        cls = classes(box)
        heading = box.find_class("heading")
        heading = heading[0] if heading else None
        title_el = heading.find_class("title")[0] if heading is not None and heading.find_class("title") else None
        type_el = heading.find_class("type") if heading is not None else []
        kind = normalize_space(type_el[0].text_content()).strip().rstrip(":").strip() if type_el else \
            (normalize_space(title_el.text_content()).strip() if title_el is not None else "")
        has_title = bool(type_el)

        textarea = box.find(".//textarea")
        if "scramble" in cls and "facultative" in cls:
            # een voorbeeld waarin je de regels zelf mag verschuiven: gewoon een voorbeeld
            lines = [li.text_content() for li in box.xpath(".//li[contains(@class,'pyscramble')]")]
            return self.example(box, parent, title_el if has_title else None, kind, code="\n".join(lines))
        if "scramble" in cls and "multiscramble" not in cls:
            return self.scramble(box, parent, title_el if has_title else None)
        if "multiscramble" in cls:
            return self.multiscramble(box, parent, title_el if has_title else None)
        if box.xpath(".//select[starts-with(@id,'pyselect')]"):
            return self.multiple_choice(box, parent, title_el if has_title else None)
        if box.xpath(".//input[starts-with(@id,'pyShortAnswer')]"):
            return self.short_answer(box, parent, title_el if has_title else None)
        if textarea is None:
            warn("%s: pybox zonder code %s" % (self.name, box.get("id")))
            return
        if "facultative" in cls:
            return self.example(box, parent, title_el if has_title else None, kind)
        return self.coding_exercise(box, parent, title_el if has_title else None)

    def description_nodes(self, box):
        """Een kopie van de pybox met alleen de beschrijving (zonder bedieningselementen)."""
        b = copy.deepcopy(box)
        for sel in ["heading", "pycheck", "helpOuter", "pyboxTextwrap", "flexcontain", "pyboxbuttons",
                    "pbresults", "epilogue", "get-problem-source", "pyscramble", "slugwarn"]:
            for x in b.find_class(sel):
                x.drop_tree()
        for x in b.xpath(".//*[@name='pyinput'] | .//select | .//label | .//input | .//script"):
            x.drop_tree()
        return b

    def title_into(self, title_el, parent):
        if title_el is None:
            return
        t = ET.SubElement(parent, "title")
        self.inline(title_el, Inline(t))
        strip_para(t)

    def statement_from(self, box, parent_ex):
        st = ET.SubElement(parent_ex, "statement")
        self.blocks(self.description_nodes(box), st)
        if len(st) == 0:
            ET.SubElement(st, "p")
        return st

    def example(self, box, parent, title_el, kind, code=None):
        if code is None:
            code = code_of(box)
        self.example_count += 1
        label = "%s-vb-%d" % (self.chapter_id, self.example_count)
        desc = self.description_nodes(box)
        console = kind == "Console"
        holder = ET.Element("tmp")
        self.blocks(desc, holder)
        if (len(holder) or title_el is not None) and parent.tag in DIVISIONS:
            ex = ET.SubElement(parent, "example")
            self.title_into(title_el, ex)
            for c in holder:
                ex.append(c)
            target = ex
        else:
            if title_el is not None:
                p = ET.SubElement(parent, "p")
                a = ET.SubElement(p, "alert")
                self.inline(title_el, Inline(a))
                strip_para(a)
            for c in holder:
                parent.append(c)
            target = parent
        prog = ET.SubElement(target, "program", {"interactive": "activecode", "language": "python",
                                                "label": label})
        c = ET.SubElement(prog, "code")
        c.text = "\n" + code + "\n" if code.strip() else "\n\n"

    def begin_exercise(self, parent, slug, title_el, kind):
        ex = ET.SubElement(parent, "exercise")
        if not slug and title_el is not None:
            slug = self.derived_slug(title_el)
        if slug:
            ex.set("label", slug_to_label(slug))
        else:
            self.example_count += 1
            ex.set("label", "%s-oef-%d" % (self.chapter_id, self.example_count))
            warn("%s: oefening zonder slug (%s)" % (self.name, kind))
        self.title_into(title_el, ex)
        self.current_exercise_hints = []
        return ex

    def end_exercise(self, ex):
        for title, hint in self.current_exercise_hints:
            h = ET.Element("hint")
            if title and re.match(r"^[A-Z#]", title) and not re.search(r"(?i)klik", title) and \
                    not re.match(r"(?i)^(hint|tip)\.?$", title):
                ET.SubElement(h, "title").text = title
            self.current_exercise_hints_guard = True
            saved = self.current_exercise_hints
            self.current_exercise_hints = None
            self.blocks(hint, h)
            self.current_exercise_hints = saved
            if len(h):
                insert_hint(ex, h)
        self.current_exercise_hints = None

    def derived_slug(self, title_el):
        """Volgorde-oefeningen hebben op CS Circles geen slug; maak er een van les en titel."""
        title = re.sub(r"[^a-z0-9]+", "-", normalize_space(title_el.text_content()).lower()).strip("-")
        return "%s.%s" % (self.chapter_id.replace("les-", "").lstrip("0") or "0", title)

    def coding_exercise(self, box, parent, title_el):
        slug = slug_of(box)
        ex = self.begin_exercise(parent, slug, title_el, "code")
        self.statement_from(box, ex)
        code = code_of(box)
        spec = toetsen.get(slug)
        prog = ET.SubElement(ex, "program", {"interactive": "activecode", "language": "python",
                                            "label": slug_to_label(slug) + "-code"})
        if spec and spec.get("tijdslimiet"):
            prog.set("timelimit", str(spec["tijdslimiet"]))
        if spec is None:
            warn("%s: geen toetsen voor %s" % (self.name, slug))
            spec = {}
        voorcode = harnas_voorcode(spec) if spec else None
        if voorcode:
            pre = ET.SubElement(prog, "preamble", {"visible": "no"})
            pre.text = "\n" + voorcode.strip("\n") + "\n"
        start = spec.get("startcode", code)
        c = ET.SubElement(prog, "code")
        c.text = "\n" + start.strip("\n") + "\n" if start.strip() else "\n\n"
        if spec:
            t = ET.SubElement(prog, "tests")
            t.text = "\n" + maak_tests(slug, spec, start) + "\n"
        self.end_exercise(ex)

    def scramble(self, box, parent, title_el):
        slug = slug_of(box) or (self.derived_slug(title_el) if title_el is not None else None)
        ex = self.begin_exercise(parent, slug, title_el, "scramble")
        ex.set("language", "python")
        self.statement_from(box, ex)
        lines = [li.text_content() for li in box.xpath(".//li[contains(@class,'pyscramble')]")]
        lines = [ln.replace(" ", " ") for ln in lines]
        spec = toetsen.get(slug) or {}
        order = spec.get("volgorde")
        if order is None:
            warn("%s: geen volgorde voor scramble %s" % (self.name, slug))
            order = list(range(len(lines)))
        if sorted(order) != list(range(len(lines))):
            warn("%s: volgorde van %s klopt niet met %d regels" % (self.name, slug, len(lines)))
        blocks = ET.SubElement(ex, "blocks")
        deps = spec.get("afhankelijk")  # {index: [indices]} voor meerdere juiste volgordes
        for i in order:
            attrs = {}
            if deps is not None:
                attrs["name"] = "r%d" % i
                if deps.get(i):
                    attrs["depends"] = " ".join("r%d" % d for d in deps[i])
            b = ET.SubElement(blocks, "block", attrs)
            ET.SubElement(b, "cline").text = lines[i].rstrip() if lines[i].strip() else " "
        self.end_exercise(ex)

    def multiscramble(self, box, parent, title_el):
        slug = slug_of(box)
        ex = self.begin_exercise(parent, slug, title_el, "multiscramble")
        self.statement_from(box, ex)
        items = box.xpath(".//li[starts-with(@id,'pyli')]")
        items.sort(key=lambda li: int(li.get("id").split("_")[-1]))
        blocks = ET.SubElement(ex, "blocks")
        for li in items:
            b = ET.SubElement(blocks, "block")
            p = ET.SubElement(b, "p")
            self.inline(li, Inline(p))
            strip_para(p)
        self.end_exercise(ex)

    def multiple_choice(self, box, parent, title_el):
        slug = slug_of(box)
        ex = self.begin_exercise(parent, slug, title_el, "multi")
        self.statement_from(box, ex)
        choices = ET.SubElement(ex, "choices", {"randomize": "yes"})
        epilogue = box.find_class("epilogue")
        for opt in box.xpath(".//select[starts-with(@id,'pyselect')]/option"):
            if opt.get("value") == "d":
                continue
            ch = ET.SubElement(choices, "choice")
            if opt.get("value") == "r":
                ch.set("correct", "yes")
            st = ET.SubElement(ch, "statement")
            p = ET.SubElement(st, "p")
            self.inline(opt, Inline(p))
            strip_para(p)
            if opt.get("value") == "r" and epilogue:
                fb = ET.SubElement(ch, "feedback")
                self.blocks(epilogue[0], fb)
                if len(fb) == 0:
                    ch.remove(fb)
        self.end_exercise(ex)

    def short_answer(self, box, parent, title_el):
        slug = slug_of(box)
        ex = self.begin_exercise(parent, slug, title_el, "short")
        st = self.statement_from(box, ex)
        typ = box.xpath(".//input[@name='type']/@value")
        typ = typ[0] if typ else "trimmableString"
        answer = box.xpath(".//input[@name='correct']/@value")[0]
        mode = "number" if typ == "number" else "string"
        p = ET.SubElement(st, "p")
        p.text = "Jouw antwoord: "
        attrs = {"mode": mode, "answer": answer, "width": "12"}
        ET.SubElement(p, "fillin", attrs)
        ev = ET.SubElement(ex, "evaluation")
        e = ET.SubElement(ev, "evaluate")
        test = ET.SubElement(e, "test")
        cmp_el = ET.SubElement(test, "numcmp" if mode == "number" else "strcmp", {"use-answer": "yes"})
        epilogue = box.find_class("epilogue")
        fb = ET.SubElement(test, "feedback")
        if epilogue:
            self.blocks(epilogue[0], fb)
        if len(fb) == 0:
            ET.SubElement(fb, "p").text = "Correct!"
        # Volgorde volgens het schema: statement, evaluation, hints
        ex.remove(ev)
        ex.insert(list(ex).index(st) + 1, ev)
        self.end_exercise(ex)

    # ---------------- structuur ----------------

    deferred_images = []

    def convert(self):
        self.deferred_images = []
        content = self.doc.find_class("entry-content")[0]
        chapter = ET.Element("chapter")
        chapter.set("{http://www.w3.org/XML/1998/namespace}id", self.chapter_id)
        ET.SubElement(chapter, "title").text = self.info["titel"]

        # Splits de inhoud op in stukken per <h2> (secties) en <h3> (subsecties).
        pieces = split_on_headings(content)
        self.build_division(chapter, pieces, level=2)
        if self.pending_hints:
            warn("%s: %d losse hints buiten oefeningen" % (self.name, len(self.pending_hints)))
        return chapter

    def build_division(self, div, pieces, level):
        """pieces: lijst van (kop-element of None, [nodes]) voor dit niveau."""
        intro_nodes = pieces[0][1] if pieces and pieces[0][0] is None else []
        subs = pieces[1:] if pieces and pieces[0][0] is None else pieces
        if not subs:
            self.fill(div, intro_nodes)
            return
        if any_content(intro_nodes):
            intro = ET.SubElement(div, "introduction")
            self.fill(intro, intro_nodes)
            if len(intro) == 0:
                div.remove(intro)
            elif intro.find(".//exercise") is not None:
                # Oefeningen in een introduction worden door PreTeXt niet interactief weergegeven;
                # maak er dan een gewone eerste (sub)sectie van.
                intro.tag = "section" if level == 2 else "subsection"
                intro.set("{http://www.w3.org/XML/1998/namespace}id", "%s-%s0" % (div.get(
                    "{http://www.w3.org/XML/1998/namespace}id"), "s" if level == 2 else "ss"))
                t = ET.Element("title")
                t.text = "Inleiding"
                intro.insert(0, t)
        subtag = "section" if level == 2 else "subsection"
        for n, (head, nodes) in enumerate(subs, 1):
            sec = ET.SubElement(div, subtag)
            sec.set("{http://www.w3.org/XML/1998/namespace}id", "%s-%s%d" % (div.get(
                "{http://www.w3.org/XML/1998/namespace}id"), "s" if level == 2 else "ss", n))
            t = ET.SubElement(sec, "title")
            self.inline(head, Inline(t))
            strip_para(t)
            if level == 2:
                subpieces = split_nodes_on(nodes, "h3")
                self.build_division(sec, subpieces, 3)
            else:
                self.fill(sec, nodes)

    def fill(self, div, nodes):
        wrapper = lxml.html.Element("div")
        for n in nodes:
            if isinstance(n, str):
                if len(wrapper):
                    wrapper[-1].tail = (wrapper[-1].tail or "") + n
                else:
                    wrapper.text = (wrapper.text or "") + n
            else:
                wrapper.append(n)
        self.blocks(wrapper, div)
        for title, hint in self.pending_hints:
            rem = ET.SubElement(div, "remark")
            ET.SubElement(rem, "title").text = title or "Tip"
            self.blocks(hint, rem)
        self.pending_hints = []


# --------------------------------------------------------------------------
# Hulpfuncties
# --------------------------------------------------------------------------

def image_width(path):
    """Breedte in pixels van een PNG- of JPEG-bestand (zonder extra bibliotheken)."""
    import struct
    try:
        with open(path, "rb") as f:
            data = f.read()
    except OSError:
        return None
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">I", data[16:20])[0]
    if data[:2] == b"\xff\xd8":
        i = 2
        while i < len(data) - 9:
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            length = struct.unpack(">H", data[i + 2:i + 4])[0]
            if marker in (0xC0, 0xC1, 0xC2):
                return struct.unpack(">H", data[i + 7:i + 9])[0]
            i += 2 + length
    return None


def has_blocks(el):
    return bool(el.xpath(".//form|.//div|.//pre|.//p|.//ul|.//ol|.//table|.//iframe|.//h2|.//h3"))


def any_content(nodes):
    for n in nodes:
        if isinstance(n, str):
            if n.strip():
                return True
        elif n.tag not in ("script",) and (n.text_content().strip() or n.xpath(".//img|.//iframe")):
            return True
    return False


def split_on_headings(content):
    """Maak een platte lijst van top-level nodes, waarbij <h2>'s die in een <p> zitten naar boven komen."""
    return split_nodes_on(flatten(content), "h2")


def flatten(content):
    nodes = []
    if content.text and content.text.strip():
        nodes.append(content.text)
    for child in content:
        if not isinstance(child.tag, str):
            if child.tail and child.tail.strip():
                nodes.append(child.tail)
            continue
        tail = child.tail
        child.tail = None
        if child.tag == "p" and child.xpath("./h2|./h3"):
            p = lxml.html.Element("p")
            if child.text:
                p.text = child.text
            for c in list(child):
                if c.tag in ("h2", "h3"):
                    nodes.append(p)
                    t = c.tail
                    c.tail = None
                    nodes.append(c)
                    p = lxml.html.Element("p")
                    p.text = t
                else:
                    p.append(c)
            nodes.append(p)
        else:
            nodes.append(child)
        if tail and tail.strip():
            nodes.append(tail)
    return nodes


def split_nodes_on(nodes, tag):
    pieces = [(None, [])]
    for n in nodes:
        if not isinstance(n, str) and n.tag == tag:
            pieces.append((n, []))
        else:
            pieces[-1][1].append(n)
    if not any_content(pieces[0][1]) and len(pieces) > 1:
        pieces = pieces[1:]
    return pieces


def insert_hint(ex, hint):
    """Voeg een hint toe op de juiste plek (na statement/program/blocks/choices/evaluation)."""
    idx = len(ex)
    for i, c in enumerate(ex):
        if c.tag in ("answer", "solution"):
            idx = i
            break
    ex.insert(idx, hint)


def strip_para(el):
    """Haal witruimte aan begin en eind van een inline-container weg."""
    if el.text:
        el.text = el.text.lstrip()
    if len(el):
        last = el[-1]
        if last.tail:
            last.tail = last.tail.rstrip()
    elif el.text:
        el.text = el.text.rstrip()
    if el.text == "":
        el.text = None


def pre_text(el):
    parts = []

    def walk(n):
        if n.text:
            parts.append(n.text)
        for c in n:
            if isinstance(c.tag, str) and c.tag == "br":
                parts.append("\n")
            elif isinstance(c.tag, str):
                walk(c)
            if c.tail:
                parts.append(c.tail)
    walk(el)
    return "".join(parts).replace(" ", " ").replace("\r", "")


def code_of(box):
    ta = box.find(".//textarea")
    if ta is None:
        return ""
    code = (ta.text or "").replace("\r", "")
    if code.startswith("\n"):
        code = code[1:]
    lines = [ln for ln in code.split("\n") if ln.strip() != AUTOCOMMENT]
    return "\n".join(lines).rstrip()


def slug_of(box):
    s = box.xpath(".//input[@name='slug']/@value")
    if s and s[0] != "NULL":
        return s[0]
    for attr in box.xpath(".//*[@onclick]/@onclick | .//*[@data-pbonclick]/@data-pbonclick"):
        m = re.search(r"historyClick\(\d+,'([^']+)'\)", attr)
        if m:
            return m.group(1)
    return None


def unarchive(url):
    m = re.match(r"^(?:https?://web\.archive\.org)?/web/\d+[a-z_]*/(.*)$", url)
    if m:
        url = m.group(1)
    return url


def pretty_url(href):
    return re.sub(r"^https?://", "", href).rstrip("/")


MIXED = {"p", "title", "cell", "alert", "em", "delete", "url", "xref", "c", "cline", "shortdescription",
         "m", "caption", "code", "pre", "tests", "preamble", "feedback-text"}


def indent(el, level=0):
    """Zoals ET.indent, maar zonder witruimte toe te voegen in gemengde inhoud (alinea's, titels, ...)."""
    if el.tag in MIXED or not len(el):
        return
    if (el.text or "").strip():
        return
    if any((c.tail or "").strip() for c in el):
        return
    pad = "\n" + "  " * (level + 1)
    el.text = pad
    for c in el:
        indent(c, level + 1)
        c.tail = pad
    el[-1].tail = "\n" + "  " * level


def merge_tables(root):
    """CS Circles gebruikte soms een aparte tabel voor de kop en een scrollende tabel voor de rest."""
    for tab in list(root.iter("tabular")):
        nxt = tab.getnext()
        rows = tab.findall("row")
        if nxt is not None and nxt.tag == "tabular" and rows and all(r.get("header") == "yes" for r in rows):
            for r in nxt.findall("row"):
                tab.append(r)
            nxt.getparent().remove(nxt)


def write_chapter(chapter, path):
    merge_tables(chapter)
    indent(chapter)
    fix_code_whitespace(chapter)
    data = ET.tostring(chapter, encoding="unicode")
    with open(path, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write("<!-- Gegenereerd door tools/convert.py uit archief/ ; niet met de hand bewerken. -->\n")
        f.write(data)
        f.write("\n")


def fix_code_whitespace(root):
    """ET.indent verandert geen tekst in <code>, maar wel de tail; zorg dat code netjes eindigt."""
    for el in root.iter("code", "preamble", "tests", "pre"):
        if el.text and not el.text.endswith("\n"):
            el.text += "\n"


def write_main():
    chapters = []
    appendices = []
    for info in lessen.PAGINAS:
        if not os.path.exists(os.path.join(ROOT, "source", info["id"] + ".ptx")):
            continue
        line = '      <xi:include href="./%s.ptx" />' % info["id"]
        (appendices if info.get("soort") == "appendix" else chapters).append(line)
    with open(os.path.join(ROOT, "source", "main.ptx"), "w", encoding="utf-8") as f:
        f.write(MAIN % ("\n".join(chapters), "\n".join(appendices)))


MAIN = """<?xml version="1.0" encoding="utf-8"?>
<!-- Gegenereerd door tools/convert.py ; niet met de hand bewerken. -->
<pretext xml:lang="nl-NL" xmlns:xi="http://www.w3.org/2001/XInclude">
  <xi:include href="./docinfo.ptx" />

  <book xml:id="cscircles-nl">
    <title>Computer Science Circles</title>
    <subtitle>Programmeren in Python</subtitle>

    <xi:include href="./frontmatter.ptx" />

%s

    <backmatter xml:id="backmatter">
      <title>Bijlagen</title>
%s
    </backmatter>
  </book>
</pretext>
"""


def main():
    only = sys.argv[1:]
    os.makedirs(os.path.join(ROOT, "source"), exist_ok=True)
    all_images = set()
    for info in lessen.PAGINAS:
        if only and info["naam"] not in only:
            continue
        path = os.path.join(ROOT, "archief", info["naam"] + ".html")
        if not os.path.exists(path):
            warn("ontbreekt: " + path)
            continue
        page = Page(info)
        chapter = page.convert()
        if info.get("soort") == "appendix":
            chapter.tag = "appendix"
        write_chapter(chapter, os.path.join(ROOT, "source", info["id"] + ".ptx"))
        all_images |= page.images
    write_main()
    with open(os.path.join(ROOT, "tools", "afbeeldingen.txt"), "w") as f:
        for fname, src in sorted(all_images):
            f.write("%s %s\n" % (fname, src))
    print("%d waarschuwingen" % len(WARNINGS))


if __name__ == "__main__":
    main()
