"""Project 2 CLI. Usage: python project2.py {collect|analyze|build|all}

  collect  fetch documents listed in data/seed_urls.csv            (Spec 01)
  analyze  code documents, make review sample, aggregate findings  (Spec 02)
  build    regenerate validation / timeline / token site data      (Specs 04-05)
  all      collect + analyze + build
"""
import sys

from pipeline import analyze, code, collect
from tools import build_site, review_sample, token_usage

STEPS = {
    "collect": [collect.main],
    "analyze": [code.main, review_sample.main, analyze.main],
    "build": [token_usage.main, build_site.main],
}
STEPS["all"] = STEPS["collect"] + STEPS["analyze"] + STEPS["build"]


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1 or argv[0] not in STEPS:
        print(__doc__.strip())
        return 2
    for step in STEPS[argv[0]]:
        step()
    return 0


if __name__ == "__main__":
    sys.exit(main())
