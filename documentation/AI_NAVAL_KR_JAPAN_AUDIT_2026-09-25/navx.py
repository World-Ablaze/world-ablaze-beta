"""Extract per-save naval data: every country's fleets/task forces (mission id raw +
ship definitions at ship depth 1) and war pairs. Output: one JSON per save."""
import sys, os, json, re, collections, time
sys.path.insert(0, r"E:\Projets\HOI4\WA\world-ablaze-beta\.claude\skills\wa-savegame-analysis\scripts")
import savegame as sg

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "navjson")
os.makedirs(OUT, exist_ok=True)


def parse_fleets_raw(units_lines):
    # copy of sg._parse_fleets but keeps the raw mission id
    fleets = []
    fleet = tf = None
    fdepth = tdepth = sdepth = mdepth = None
    in_regions = False
    for line in units_lines:
        st = line.strip()
        delta = line.count("{") - line.count("}")
        if fleet is None:
            if not st.startswith("fleet={"):
                continue
            fleet = {"name": None, "leader": False, "regions": [], "tfs": []}
            fleets.append(fleet)
            fdepth = 0
            in_regions = False
        elif sdepth is not None:
            if sdepth == 1 and st.startswith("definition="):
                tf["ships"][st.split("=", 1)[1]] += 1
        elif tf is not None:
            if st.startswith("ship={"):
                sdepth = 0
            elif mdepth is not None:
                if st.startswith("mission="):
                    tf["mission"] = st.split("=")[1]
            elif st.startswith("mission={"):
                mdepth = 0
            elif st.startswith("name=") and tf["name"] is None:
                tf["name"] = st.split("=", 1)[1].strip('"')
        else:
            if st.startswith("task_force={"):
                tf = {"mission": None, "name": None, "ships": collections.Counter()}
                fleet["tfs"].append(tf)
                tdepth = 0
            elif st.startswith("leader={"):
                fleet["leader"] = True
            elif st.startswith("name=") and fleet["name"] is None:
                fleet["name"] = st.split("=", 1)[1].strip('"')
            elif st.startswith("strategic_region={"):
                in_regions = True
            elif in_regions:
                if st.startswith("}"):
                    in_regions = False
                else:
                    fleet["regions"] += st.replace("}", "").split()
        fdepth += delta
        if mdepth is not None:
            mdepth += delta
            if mdepth <= 0:
                mdepth = None
        if sdepth is not None:
            sdepth += delta
            if sdepth <= 0:
                sdepth = None
        if tdepth is not None:
            tdepth += delta
            if tdepth <= 0:
                tdepth = tf = None
        if fdepth <= 0:
            fdepth = fleet = None
    return fleets


def units_by_country(fh):
    """One pass over countries={}: yield (tag, units_lines)."""
    for line in fh:
        if line.startswith("countries={"):
            break
    depth = 1
    tag = None
    buf = None
    udepth = None
    for line in fh:
        d = line.count("{") - line.count("}")
        if buf is not None:
            buf.append(line)
            udepth += d
            depth += d
            if udepth <= 0:
                yield tag, buf
                buf = None
            continue
        if tag is None and depth == 1:
            m = re.match(r"^\t([A-Z][A-Z0-9]{2})=\{", line)
            if m:
                tag = m.group(1)
        elif tag is not None and depth == 2 and line.startswith("\t\tunits={"):
            buf = [line]
            udepth = d
            depth += d
            if udepth <= 0:
                yield tag, buf
                buf = None
            continue
        depth += d
        if tag is not None and depth <= 1:
            tag = None
        if depth <= 0:
            return


def main(files):
    for f in files:
        p = sg.resolve(f)
        base = os.path.basename(p)
        outp = os.path.join(OUT, base + ".json")
        if os.path.exists(outp):
            continue
        t0 = time.time()
        meta = sg.read_meta(p)
        res = {"file": base, "date": meta.get("date"), "campaign": meta.get("game_unique_id"),
               "countries": {}, "wars": []}
        with sg.open_save(p) as fh:
            for tag, lines in units_by_country(fh):
                fl = parse_fleets_raw(lines)
                if not fl:
                    continue
                res["countries"][tag] = [
                    {"name": x["name"], "leader": x["leader"], "regions": x["regions"],
                     "tfs": [{"mission": t["mission"], "name": t["name"], "ships": dict(t["ships"])}
                             for t in x["tfs"]]} for x in fl]
        wars = set()
        with sg.open_save(p) as fh:
            for owner, cp, kind, fields in sg.iter_relations(fh):
                if kind == "war_relation":
                    wars.add(tuple(sorted((owner, cp))))
                    a, b = fields.get("first"), fields.get("second")
                    if a and b and {a, b} != {owner, cp}:
                        res.setdefault("war_mismatch", []).append([owner, cp, a, b])
        res["wars"] = sorted(wars)
        json.dump(res, open(outp, "w"))
        print(base, res["date"], len(res["countries"]), len(res["wars"]), "%.1fs" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
