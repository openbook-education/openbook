#!/usr/bin/env python
"""
OpenBook: Interactive Online Textbooks
© 2026 Dennis Schulmeister-Zimolong <dennis@wpvs.de>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.
"""

import argparse, os

from fontTools.ttLib import TTFont
from typing          import Any, Optional, TypedDict, Union

class FontMetadata(TypedDict, total=False):
    """
    Structured font metadata for CSS generation and inspection.

    Properties:
        family:        Font family name (e.g., 'Roboto').
        src:           File name or path for CSS src (e.g., 'Roboto.woff2').
        format:        Font format for CSS (e.g., 'woff2', 'truetype').
        is_variable:   True if the font is a variable font (has axes).
        axes:          Dictionary of variable font axes (tag to axis object).
        weight:        Numeric weight for static fonts (e.g., 400, 700), or None.
        weight_range:  Tuple (min, max) for variable font weights, or None.
        style:         CSS font-style value (e.g., 'normal', 'italic', 'oblique').
        style_comment: Additional style info or comments, or None.
    """
    family:        str
    src:           str
    format:        str
    is_variable:   bool
    axes:          dict[str, Any]
    weight:        Union[int, None]
    weight_range:  Union[tuple[int, int], None]
    style:         str
    style_comment: Union[str, None]

def parse_font_metadata(
    input_path:  str,
    font_family: Optional[str] = None,
    font_path:   Optional[str] = None
) -> FontMetadata:
    """
    Parse font metadata and return a structured description for CSS generation.

    :param input_path: Path to the input font file
    :param font_family: Font family name to use (if None, auto-detect)
    :param font_path: Path to the font file for the CSS src URL (if None, uses input_path)
    :return: Dictionary with font metadata (family, src, format, weight, style, is_variable, axes, etc.)
    """
    font     = TTFont(input_path)
    src_path = font_path or input_path
    ext      = os.path.splitext(src_path)[1].lower()

    result: FontMetadata = {
        "family":        None,
        "src":           os.path.basename(src_path),
        "format":        None,
        "is_variable":   False,
        "axes":          {},
        "weight":        None,
        "weight_range":  None,
        "style":         "normal",
        "style_comment": None,
    }

    # Font family detection
    if font_family is None:
        name_table = font["name"]
        family     = None

        for record in name_table.names:
            if record.nameID == 1 and (record.platformID, record.langID) in [(3, 1033), (1, 0)]:
                try:
                    family = record.string.decode(record.getEncoding())
                except Exception:
                    family = record.string.decode(errors='ignore')
                break

        result["family"] = family or "CustomFont"
    else:
        result["family"] = font_family

    match ext:
        case ".eot":
            result["format"] = "embedded-opentype"
        case ".woff2":
            result["format"] = "woff2"
        case ".woff":
            result["format"] = "woff"
        case (".otc" | ".ttc"):
            result["format"] = "collection"
        case ".ttf":
            result["format"] = "truetype"
        case ".otf":
            result["format"] = "opentype"
        case _:
            result["format"] = "unknown"

    result["is_variable"] = "fvar" in font

    if result["is_variable"]:
        result["axes"] = {axis.axisTag: axis for axis in font["fvar"].axes}

        if "wght" in result["axes"]:
            min_wght = int(result["axes"]["wght"].minValue)
            max_wght = int(result["axes"]["wght"].maxValue)
            result["weight_range"] = (min_wght, max_wght)

        if "ital" in result["axes"]:
            if result["axes"]["ital"].maxValue > 0:
                result["style"] = "oblique 0deg 20deg"  # Variable italic axis, range is a guess
            else:
                result["style"] = "normal"
        elif "slnt" in result["axes"]:
            result["style"] = "oblique"
        else:
            result["style_comment"] = "normal (no ital/slnt axis)"
    else:
        # Static font: try to detect weight and style from OS/2 and name tables
        if "OS/2" in font:
            result["weight"] = getattr(font["OS/2"], "usWeightClass", None)

            fsSelection = getattr(font["OS/2"], "fsSelection", 0)
            if fsSelection & 0x01:
                result["style"] = "italic"
            elif fsSelection & 0x200:
                result["style"] = "oblique"

        if result["style"] == "normal" and "name" in font:
            for record in font["name"].names:
                if record.nameID == 2:
                    try:
                        subfamily = record.string.decode(record.getEncoding()).lower()
                        if "italic" in subfamily:
                            result["style"] = "italic"
                        elif "oblique" in subfamily:
                            result["style"] = "oblique"
                    except (UnicodeDecodeError, LookupError, AttributeError):
                        # Ignore malformed/unsupported name records and continue best-effort style detection.
                        continue

    return result

def convert_font(input_path: str, dest_format: str = "woff2", output_path: Optional[str] = None) -> None:
    """
    Convert TTF/OTF to the specified format using fontTools.

    :param input_path:  Path to the input font file (TTF/OTF/WOFF/WOFF2)
    :param dest_format: Destination format (e.g., 'woff2', 'woff', 'ttf', 'otf')
    :param output_path: Output file path (if None, auto-generated from input_path)
    """
    dest_format = dest_format.lower()

    if output_path is None:
        output_path = os.path.splitext(input_path)[0] + f".{dest_format}"

    font = TTFont(input_path)

    match dest_format:
        case "woff2":
            font.save(output_path)
        case "ttf":
            font.save(output_path)
        case "otf":
            font.save(output_path)
        case "woff":
            font.flavor = "woff"
            font.save(output_path)
        case _:
            print(f"Unsupported destination format: {dest_format}")
            return

    print(f"Converted {input_path} to {output_path}")

def inspect_variable_axes(input_path: str) -> None:
    """
    Print variable font axes if present.

    :param input_path: Path to the input font file
    """
    font = TTFont(input_path)

    if "fvar" in font:
        axes = font["fvar"].axes

        print("Variable font axes:")

        for axis in axes:
            print(f"  {axis.axisTag}: {axis.minValue}–{axis.maxValue} (default: {axis.defaultValue})")
    else:
        print("No variable axes found.")

def output_css_font_face(
    input_path: str,
    font_family: Optional[str] = None,
    font_path: Optional[str] = None
) -> None:
    """
    Output a CSS @font-face rule for the given font file.

    :param input_path:  Path to the input font file
    :param font_family: Font family name to use in CSS (if None, auto-detect)
    :param font_path:   Path to the font file for the CSS src URL (if None, uses input_path)
    """
    meta = parse_font_metadata(input_path, font_family, font_path)

    print()
    print(f"@font-face {{")
    print(f"    font-family: '{meta['family']}';")

    if meta["is_variable"]:
        print(f"    src: url('{meta['src']}') format({meta['format']}) tech(variations);")

        if meta["weight_range"]:
            min_wght, max_wght = meta["weight_range"]

            if min_wght == max_wght:
                print(f"    font-weight: {min_wght};")
            else:
                print(f"    font-weight: {min_wght} {max_wght};")
        else:
            print(f"    /* font-weight: unknown (no wght axis) */")
        if meta["style"]:
            print(f"    font-style: {meta['style']};")
        if meta["style_comment"]:
            print(f"    /* font-style: {meta['style_comment']} */")
    else:
        print(f"    src: url('{meta['src']}') format({meta['format']});")

        if meta["weight"]:
            print(f"    font-weight: {meta['weight']};")
        else:
            print(f"    /* font-weight: normal (unknown) */")
        print(f"    font-style: {meta['style']};")

    print(f"}}")

def main():
    parser = argparse.ArgumentParser(
        description = "Font utility: convert, inspect, and generate CSS for font files."
    )

    parser.add_argument(
        "fontfile",
        help = "Input font file (TTF/OTF/WOFF/WOFF2)"
    )

    parser.add_argument(
        "-t", "--to",
        nargs   = "?",
        const   = "woff2",
        default = None,
        metavar = "FORMAT",
        help    = "Convert to destination format (default: woff2). Supported: woff2, woff, ttf, otf"
    )

    parser.add_argument(
        "-i", "--inspect-axes",
        action = "store_true",
        help   = "Inspect variable font axes"
    )

    parser.add_argument(
        "-c", "--css",
        action = "store_true",
        help   = "Output CSS @font-face rule"
    )

    parser.add_argument(
        "-f", "--font-family",
        help = "Override font-family name for CSS output"
    )

    parser.add_argument(
        "-o", "--output",
        help = "Output file name for conversion"
    )

    args = parser.parse_args()

    if args.inspect_axes:
        inspect_variable_axes(args.fontfile)

    converted_path = None

    if args.to:
        out_path = args.output or os.path.splitext(args.fontfile)[0] + f".{args.to}"
        convert_font(args.fontfile, dest_format=args.to, output_path=out_path)
        converted_path = out_path

    if args.css:
        css_path = converted_path if converted_path else args.fontfile
        output_css_font_face(args.fontfile, font_family=args.font_family, font_path=css_path)

if __name__ == "__main__":
    main()
