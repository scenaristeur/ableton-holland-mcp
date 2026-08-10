from __future__ import annotations

import html as html_lib
import re
from html.parser import HTMLParser


class TableCapture(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.out: list[str] = []
        self.in_script = 0
        self.in_style = 0
        self.current_header: str | None = None
        self.capture_heading = False
        self.heading_buf: list[str] = []
        # table state
        self.table_depth = 0
        self.in_table = False
        self.in_th = False
        self.in_td = False
        self.cell_buf: list[str] = []
        self.cell_code = False
        self.rows: list[list[str]] = []
        self.cur_row: list[str] = []
        self.is_header_row = False
        # prose paragraph capture
        self.para_depth = 0
        self.in_p = False
        self.p_buf: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag == "script":
            self.in_script += 1
        elif tag == "style":
            self.in_style += 1
        elif tag in ("th", "td"):
            self.cell_buf = []
            if tag == "th":
                self.in_th = True
            else:
                self.in_td = True
        elif tag == "tr":
            self.cur_row = []
        elif tag == "table" and self.current_header:
            self.in_table = True
            self.rows = []
        elif tag == "h2" or tag == "h3":
            self.capture_heading = True
            self.heading_buf = []
        elif tag == "h1":
            self.current_header = None
            self.capture_heading = True
            self.heading_buf = []
        elif tag == "p" and not self.in_table:
            self.in_p = True
            self.p_buf = []
        elif tag == "br" and self.in_p and not self.in_table:
            self.p_buf.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            self.in_script -= 1
        elif tag == "style":
            self.in_style -= 1
        elif tag == "th":
            self.in_th = False
            self.cur_row.append(self._clean_cell())
        elif tag == "td":
            self.in_td = False
            self.cur_row.append(self._clean_cell())
        elif tag == "tr" and self.in_table:
            if self.cur_row:
                self.rows.append(self.cur_row)
        elif tag == "table" and self.in_table:
            self.in_table = False
            self._emit_table()
        elif tag in ("h2", "h3", "h1"):
            self.capture_heading = False
            hdr = " ".join(self.heading_buf).strip()
            self.current_header = hdr or self.current_header
            if hdr:
                lvl = (
                    2
                    if tag in ("h2", "h3") and tag == "h2"
                    else 3
                    if tag == "h3"
                    else 1
                )
                if hdr not in ("Surge XT", "Surge FX") or tag == "h1":
                    self.out.append(f"\n## {hdr}\n" if lvl == 2 else f"\n### {hdr}\n")
        elif tag == "p" and not self.in_table:
            self.in_p = False
            text = " ".join(self.p_buf).strip()
            if text and not self._is_ui_only(text):
                self.out.append(text + "\n")

    def handle_data(self, data: str) -> None:
        if self.in_script or self.in_style:
            return
        if self.capture_heading:
            self.heading_buf.append(data)
            return
        if self.in_th or self.in_td:
            self.cell_buf.append(data)
            return
        if self.in_table:
            return
        if self.in_p:
            self.p_buf.append(data)

    def _clean_cell(self) -> str:
        text = html_lib.unescape(" ".join(self.cell_buf)).strip()
        text = re.sub(r"\s+", " ", text)
        return text.replace("|", "\\|")

    def _is_ui_only(self, text: str) -> bool:
        return any(k in text.lower() for k in ("os? coll", "surge xt", "<a name"))
        return False

    def _emit_table(self) -> None:
        if not self.rows:
            return
        ncols = max(len(r) for r in self.rows)
        if ncols < 2:
            return
        header = self.rows[0]
        header = header + [""] * (ncols - len(header))
        self.out.append("")
        self.out.append("| " + " | ".join(header) + " |")
        self.out.append("|" + "|".join(["---"] * ncols) + "|")
        for r in self.rows[1:]:
            r = r + [""] * (ncols - len(r))
            if sum(1 for c in r if c) <= 1:
                continue
            self.out.append("| " + " | ".join(r) + " |")
        self.out.append("")


def main() -> None:
    with open("doc_surge/surge_OSC.html", encoding="utf-8") as f:
        src = f.read()
    p = TableCapture()
    p.feed(src)
    md = (
        "# Surge XT (and FX) 1.3 — OSC Specification\n\n"
        "OSC messages use the exact (case-sensitive) entry in the **Address** column.\n"
        "Form: `/<address> <value>`. Values can be:\n"
        "- a float between **0.0** and **1.0** bounding the parameter range (use `.`, never `,`)\n"
        "- an integer\n"
        "- a boolean (0=false, 1=true)\n"
        "- a file path\n"
        "- contextual (int or float depending on loaded oscillator/effect)\n\n"
        "Out-of-range values are clipped.\n\n"
        "> **Important:** all numeric values must be sent over OSC as **floating point** numbers,\n"
        "> even for int/bool typed parameters (the 'Appropriate Values' column describes how Surge uses the data).\n\n"
        "**OSC Output:** parameter/patch/tuning/modulation changes are reported to OSC out when enabled;\n"
        "floats reported 0.0-1.0 followed by a display string. Errors go to `/error`.\n"
        "**Examples are shown in red** in the original and marked `ex:` here.\n\n"
        + "\n".join(p.out)
        + "\n"
    )
    with open("doc_surge/surge_OSC.md", "w", encoding="utf-8") as f:
        f.write(md)


if __name__ == "__main__":
    main()
