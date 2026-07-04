#!/usr/bin/env python3

from pathlib import Path
import argparse
import csv

from PIL import Image, ImageCms


def find_default_cmyk_profile():
    """Look for a generic CMYK profile on macOS."""

    candidates = [
        "/System/Library/ColorSync/Profiles/Generic CMYK Profile.icc",
        "./sRGB.icc",
        "/Library/ColorSync/Profiles/USWebCoatedSWOP.icc",
    ]

    for path in candidates:
        if Path(path).exists():
            return path

    raise FileNotFoundError(
        "No CMYK ICC profile found. Specify one with --cmyk-profile."
    )


class ColorConverter:

    def __init__(self, cmyk_profile, rgb_profile):

        self.transform = ImageCms.buildTransform(
            ImageCms.getOpenProfile(cmyk_profile),
            ImageCms.getOpenProfile(rgb_profile),
            "CMYK",
            "RGB",
        )

    def convert(self, c, m, y, k):

        pixel = (
            round(c * 255 / 100),
            round(m * 255 / 100),
            round(y * 255 / 100),
            round(k * 255 / 100),
        )

        img = Image.new("CMYK", (1, 1), pixel)
        rgb = ImageCms.applyTransform(img, self.transform)

        return rgb.getpixel((0, 0))


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("input_csv")
    parser.add_argument("output_csv")
    parser.add_argument("rgb_profile")

    parser.add_argument(
        "--cmyk-profile",
        default=None,
    )

    args = parser.parse_args()

    cmyk_profile = (
        args.cmyk_profile
        if args.cmyk_profile
        else find_default_cmyk_profile()
    )

    converter = ColorConverter(
        cmyk_profile,
        args.rgb_profile,
    )

    with open(args.input_csv, newline="", encoding="utf-8") as infile, \
         open(args.output_csv, "w", newline="", encoding="utf-8") as outfile:

        reader = csv.DictReader(infile)

        fieldnames = reader.fieldnames + [
            "R",
            "G",
            "B",
            "Hex",
        ]

        writer = csv.DictWriter(
            outfile,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for row in reader:

            r, g, b = converter.convert(
                float(row["C"]),
                float(row["M"]),
                float(row["Y"]),
                float(row["K"]),
            )

            row["R"] = r
            row["G"] = g
            row["B"] = b
            row["Hex"] = "#{:02X}{:02X}{:02X}".format(r, g, b)

            writer.writerow(row)

    print(f"Wrote {args.output_csv}")


if __name__ == "__main__":
    main()
