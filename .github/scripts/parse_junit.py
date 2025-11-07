from __future__ import annotations

import os
import sys
import xml.etree.ElementTree as ET


def main():
    p = 'report.xml'
    if not os.path.exists(p):
        print(f"JUnit report not found at {p}")
        return 1
    tree = ET.parse(p)
    root = tree.getroot()
    # Handle <testsuite> or <testsuites>
    if root.tag == 'testsuite':
        ts = root
        tests = int(ts.attrib.get('tests', 0))
        failures = int(ts.attrib.get('failures', 0))
        errors = int(ts.attrib.get('errors', 0))
        skipped = int(ts.attrib.get('skipped', 0))
    else:
        tests = failures = errors = skipped = 0
        for ts in root.findall('testsuite'):
            tests += int(ts.attrib.get('tests', 0))
            failures += int(ts.attrib.get('failures', 0))
            errors += int(ts.attrib.get('errors', 0))
            skipped += int(ts.attrib.get('skipped', 0))
    passed = tests - failures - errors - skipped
    rate = 0.0 if tests == 0 else round(100.0 * passed / tests, 2)
    out_path = os.environ.get('GITHUB_OUTPUT')
    if out_path:
        with open(out_path, 'a') as f:
            f.write(f"tests={tests}\n")
            f.write(f"passed={passed}\n")
            f.write(f"failures={failures}\n")
            f.write(f"errors={errors}\n")
            f.write(f"skipped={skipped}\n")
            f.write(f"passrate={rate}\n")
    else:
        print(f"tests={tests}")
        print(f"passed={passed}")
        print(f"failures={failures}")
        print(f"errors={errors}")
        print(f"skipped={skipped}")
        print(f"passrate={rate}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
