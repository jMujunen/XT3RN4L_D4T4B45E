#!/usr/bin/env python3

# HTML_VIEW.py - Test file for viewing HTML in PySimpleGUI

from dataclasses import dataclass, field

import markdown
import PySimpleGUI as sg
from tkhtmlview import html_parser


@dataclass
class HTML_VIEWER:
    parser: html_parser.HTMLTextParser = field(default_factory=html_parser.HTMLTextParser)

    def set_html(self, widget, html, strip=True) -> None:
        prev_state = widget.cget("state")
        widget.config(state=sg.tk.NORMAL)
        widget.delete("1.0", sg.tk.END)
        widget.tag_delete(widget.tag_names)
        self.parser.w_set_html(widget, html, strip=strip)
        widget.config(state=prev_state)

    def markdown2html(self, markdown_content) -> str:
        return markdown.markdown(str(markdown_content))


# Example

if __name__ == "__main__":
    html = """
<h1>EQC-144-397-819</h1>
<hr />
<ul>
<li>lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt. lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt. lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt. </li>
<li>lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. </li>
<li>lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. </li>
<li>lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</li>
</ul>
"""

    sg.theme("Dark Gray 2")

    layout_notes = [
        [
            sg.Multiline(
                size=(70, 40),
                border_width=2,
                text_color="black",
                background_color="white",
                disabled=True,
                key="-NOTES-",
            )
        ],
    ]

    layout = [
        [sg.Frame("-NOTES-", layout_notes)],
    ]
    window = sg.Window("Title", layout, finalize=True, use_default_focus=False)
    for element in window.key_dict.values():
        element.block_focus()

    notes = window["-NOTES-"].Widget

    HTML_OBJ = HTML_VIEWER()
    parsed_html = HTML_OBJ.set_html(notes, html)

    width, height = notes.winfo_width(), notes.winfo_height()

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "Exit"):
            break
        print(event, values)

    window.close()
