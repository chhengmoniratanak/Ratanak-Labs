# LISP IPv4 Standalone Deployment (IOS-XE 17.3.x)

## What I built
A three-router LISP overlay that separates endpoint IPs (EIDs) from the underlay transport (RLOCs) per RFC 6830. R1 and R3 are edge xTRs hosting each site's EID space; R2 is the core, doubling as Map Server/Map Resolver and OSPF underlay router. EID prefixes never touch the OSPF core — they're only visible through LISP's control plane.

## Topology
- **R1 (Site A xTR)** — Lo0 192.168.1.1/24 (EID), Gi1 10.12.12.1/24 (RLOC to R2)
- **R2 (Core MS/MR)** — Gi1 10.12.12.2/24, Gi2 10.23.23.2/24, no EIDs — just underlay + control plane
- **R3 (Site B xTR)** — Lo0 192.168.3.3/24 (EID), Gi1 10.23.23.3/24 (RLOC to R2)
- Underlay (RLOC): 10.12.12.0/24, 10.23.23.0/24 — routed via OSPF
- Overlay (EID): 192.168.1.0/24, 192.168.3.0/24 — never appears in OSPF, only in the LISP map-cache

## Key config
xTR (R1) — locator-set, database-mapping, and pointer to the MS/MR:
```
router lisp
 locator-set RLOC_R1
  10.12.12.1 priority 1 weight 100
 exit-locator-set
 instance-id 0
  service ipv4
   eid-table default
    database-mapping 192.168.1.0/24 locator-set RLOC_R1
    itr map-resolver 10.12.12.2
    itr
    etr map-server 10.12.12.2 key cisco123
    etr
```
Core (R2) — authorized sites + activating MS/MR roles:
```
router lisp
 site SITE_A
  authentication-key cisco123
  eid-prefix 192.168.1.0/24
 site SITE_B
  authentication-key cisco123
  eid-prefix 192.168.3.0/24
 ipv4 map-server
 ipv4 map-resolver
```
Underlay OSPF (R2) — RLOCs only, EIDs intentionally excluded:
```
router ospf 1
 network 10.12.12.0 0.0.0.255 area 0
 network 10.23.23.0 0.0.0.255 area 0
```

## Gotchas I ran into
- **EID prefixes must never be redistributed into OSPF** — that's the entire point of LISP. If 192.168.x.x shows up in `show ip route ospf` on R2, the separation is broken; check for accidental redistribution on the xTRs.
- **The auth key (`cisco123`) has to match exactly** between each xTR's `etr map-server ... key` and R2's `authentication-key` per site. A mismatch shows up as `Up: no` in `show lisp site` with no other obvious error.
- **`show lisp site` "Up: no" isn't always an auth problem** — it can also mean the xTR's RLOC isn't reachable from R2 over OSPF. Check underlay reachability before assuming the key is wrong.
- **Map-cache is populated by traffic, not by config** — nothing shows in `show ip lisp map-cache` until a packet actually triggers a map-request/map-reply exchange. First ping resolves it; that's expected, not a failure.
- **`database-mapping` prefix must exactly match the `eid-prefix` configured under the site on R2** — a mismatch here means the ETR registers fine but the MS won't validate/accept it correctly.
- **`instance-id 0` must be consistent across all routers** — mismatched instance-IDs are a documented cause of registration loops.

## Proof it works
Verified bottom-up: `show ip route ospf` on R2 shows only 10.12.12.0/24 and 10.23.23.0/24 (EIDs absent) → `show lisp site` on R2 shows both SITE_A and SITE_B as `Up: yes` → `ping 192.168.3.3 source loopback 0` from R1 succeeds (first packet triggers map-request/map-reply, encapsulation follows) → `show ip lisp map-cache` on R1 shows a dynamic entry for 192.168.3.0/24 via RLOC 10.23.23.3.

*(Reflects the guide's documented verification sequence, not a captured live run — swap in real command output if executed.)*

## What I'd do differently / next steps
- Add a **second RLOC per site** (multi-homed xTR) to exercise priority/weight load balancing instead of the single-locator setup here.
- Test **EID mobility** — move a host's EID registration between sites and watch the map-cache update, which is one of LISP's core value props over static routing.
- Split MS and MR onto **separate devices** instead of collapsing both roles onto R2, closer to a real deployment.
- Script `show lisp site` / `show ip lisp map-cache` checks into a single verification pass instead of running them per-step manually.
