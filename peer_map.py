"""
Deep-Tech Analyst - Peer Map  (automatic competitor set for AI / deep-tech)
===========================================================================

Given ONE ticker, this returns a sensible peer set so the Market / News agents
have a comparison cohort without you hand-editing competitors.json every time.

It is a curated map of the AI value chain + adjacent deep-tech, because reliable
*automatic* peer discovery from scratch is noisy. You can always override with
`run_company.py <TICKER> --peers AMD AVGO TSM`.

Buckets cover: AI compute/accelerators, AI networking, foundry, memory/HBM,
advanced packaging (OSAT), semicap equipment, EDA, data-center infrastructure
(power/cooling/servers/REITs), optical/photonics, robotics, and quantum.
"""

# slug -> (human label, [ (ticker, name), ... ])
SECTORS = {
    "ai-compute": ("AI compute / accelerators", [
        ("NVDA", "NVIDIA Corporation"),
        ("AMD", "Advanced Micro Devices"),
        ("INTC", "Intel"),
        ("AVGO", "Broadcom"),
        ("MRVL", "Marvell Technology"),
        ("TSM", "TSMC"),
        ("QCOM", "Qualcomm"),
    ]),
    "ai-networking": ("AI / data-center networking", [
        ("AVGO", "Broadcom"),
        ("MRVL", "Marvell Technology"),
        ("ANET", "Arista Networks"),
        ("CSCO", "Cisco Systems"),
        ("NVDA", "NVIDIA Corporation"),
        ("CRDO", "Credo Technology"),
    ]),
    "foundry": ("Semiconductor foundry / IDM", [
        ("TSM", "TSMC"),
        ("INTC", "Intel"),
        ("UMC", "United Microelectronics"),
        ("GFS", "GlobalFoundries"),
        ("005930.KS", "Samsung Electronics"),
    ]),
    "memory-hbm": ("Memory / HBM", [
        ("MU", "Micron Technology"),
        ("000660.KS", "SK hynix"),
        ("005930.KS", "Samsung Electronics"),
    ]),
    "advanced-packaging-osat": ("Advanced packaging / OSAT", [
        ("AMKR", "Amkor Technology"),
        ("ASX", "ASE Technology Holding"),
        ("IMOS", "ChipMOS Technologies"),
        ("600584.SS", "JCET Group"),
        ("6239.TW", "Powertech Technology"),
        ("002156.SZ", "Tongfu Microelectronics"),
    ]),
    "semicap": ("Semiconductor equipment (semicap)", [
        ("ASML", "ASML Holding"),
        ("AMAT", "Applied Materials"),
        ("LRCX", "Lam Research"),
        ("KLAC", "KLA Corporation"),
        ("TER", "Teradyne"),
        ("ACMR", "ACM Research"),
    ]),
    "eda": ("EDA / chip design software", [
        ("SNPS", "Synopsys"),
        ("CDNS", "Cadence Design Systems"),
        ("ARM", "Arm Holdings"),
    ]),
    "data-center-infra": ("Data-center infrastructure (power / cooling / servers)", [
        ("VRT", "Vertiv Holdings"),
        ("ETN", "Eaton"),
        ("SMCI", "Super Micro Computer"),
        ("DELL", "Dell Technologies"),
        ("ABBV", "n/a"),  # placeholder kept out below
    ]),
    "data-center-reit": ("Data-center REITs / colocation", [
        ("EQIX", "Equinix"),
        ("DLR", "Digital Realty Trust"),
    ]),
    "optical-photonics": ("Optical / photonics interconnect", [
        ("COHR", "Coherent"),
        ("LITE", "Lumentum"),
        ("AAOI", "Applied Optoelectronics"),
        ("CRDO", "Credo Technology"),
    ]),
    "robotics": ("Robotics / automation", [
        ("SYM", "Symbotic"),
        ("TER", "Teradyne"),
        ("ISRG", "Intuitive Surgical"),
        ("ROK", "Rockwell Automation"),
    ]),
    "quantum": ("Quantum computing", [
        ("IONQ", "IonQ"),
        ("RGTI", "Rigetti Computing"),
        ("QBTS", "D-Wave Quantum"),
        ("QUBT", "Quantum Computing Inc."),
    ]),
    "compound-semi": ("Compound semiconductors / power / RF", [
        ("AXTI", "AXT Inc"),
        ("WOLF", "Wolfspeed"),
        ("QRVO", "Qorvo"),
        ("SWKS", "Skyworks Solutions"),
    ]),
}

# default broad AI basket when we can't classify a ticker
DEFAULT_BASKET = [
    ("NVDA", "NVIDIA Corporation"),
    ("AMD", "Advanced Micro Devices"),
    ("AVGO", "Broadcom"),
    ("TSM", "TSMC"),
    ("MU", "Micron Technology"),
    ("ASML", "ASML Holding"),
]


def _clean_members(members):
    return [(t, n) for (t, n) in members if n and n != "n/a"]


def name_for(ticker):
    """Best-effort human name for a ticker from the map (else None)."""
    tk = ticker.upper()
    for _, (_, members) in SECTORS.items():
        for t, n in members:
            if t.upper() == tk and n != "n/a":
                return n
    return None


def classify(ticker):
    """Return (sector_slug, sector_label) for the first bucket containing the
    ticker, else (None, None)."""
    tk = ticker.upper()
    for slug, (label, members) in SECTORS.items():
        if any(t.upper() == tk for t, _ in members):
            return slug, label
    return None, None


def peers_for(ticker, sector=None, max_peers=8):
    """Return (peers, sector_slug, sector_label, confidence).

    peers = [{"ticker","name","role"}], confidence in {"high","low"}.
    """
    tk = ticker.upper()
    if sector and sector in SECTORS:
        slug, (label, members) = sector, SECTORS[sector]
        confidence = "high"
    else:
        slug, label = classify(tk)
        if slug:
            members = SECTORS[slug][1]
            confidence = "high"
        else:
            members, label, slug = DEFAULT_BASKET, "AI broad (unclassified)", "ai-broad"
            confidence = "low"

    peers = [{"ticker": t, "name": n, "role": "competitor"}
             for (t, n) in _clean_members(members) if t.upper() != tk]
    return peers[:max_peers], slug, label, confidence


def list_sectors():
    return {slug: label for slug, (label, _) in SECTORS.items()}


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        tk = sys.argv[1].upper()
        peers, slug, label, conf = peers_for(tk)
        print(f"{tk}: sector={slug} ({label}), confidence={conf}")
        print("peers:", ", ".join(p["ticker"] for p in peers))
    else:
        print("Known sectors:")
        for slug, label in list_sectors().items():
            print(f"  {slug:<26} {label}")
