# DMVPN Lab — Phase 2 (CCNP ENCOR/SCOR)

## What I built
DMVPN Phase 2 lab: 1 hub (R1/HQ) + 3 spokes (R2-R4/branches) instead of 3 separate GRE-over-IPsec tunnels. Hub uses one mGRE interface for all spokes; spokes build direct tunnels to each other via NHRP instead of hairpinning through HQ. Stack: mGRE + NHRP + IPsec (tunnel protection) + EIGRP, BGP on the underlay.

## Topology
- **R1 (Hub)** — Tunnel 10.0.0.1/24, WAN 192.0.2.2/30
- **R2/R3/R4 (Spokes)** — Tunnel 10.0.0.2-4/24, WAN 172.16.0.1/30, 203.0.113.1/30, 198.51.100.1/30
- All tunnels share overlay 10.0.0.0/24; ISP router in the middle default-routes everyone via BGP

## Key config
Hub — mGRE is what makes it DMVPN, not plain GRE:
```
interface Tunnel0
 tunnel mode gre multipoint
 ip nhrp network-id 1
 ip nhrp map multicast dynamic
 tunnel protection ipsec profile DMVPN-PROFILE
```
Spoke — NHS + static bootstrap map so it can reach the hub before registering:
```
interface Tunnel0
 tunnel mode gre multipoint
 ip nhrp nhs 10.0.0.1
 ip nhrp map 10.0.0.1 192.0.2.2
 tunnel protection ipsec profile DMVPN-PROFILE
```
EIGRP on hub tunnel needs split-horizon off, or spoke routes never propagate to other spokes:
```
interface Tunnel0
 no ip split-horizon eigrp 100
```

## Gotchas I ran into
- **Split-horizon on the hub** — tunnel comes up, NHRP registers fine, but spokes never learn each other's routes until this is disabled.
- **Static `ip nhrp map` on spokes** — without it, a spoke can't send its first NHRP registration (chicken-and-egg: doesn't know hub's physical IP yet).
- **MTU/MSS** — GRE+IPsec overhead means pings work but big transfers silently fragment. Fixed with `ip mtu 1400` / `ip tcp adjust-mss 1360`.
- **First spoke-to-spoke ping fails** — expected, that's NHRP resolving. Second ping goes direct.
- **Multicast mapping** (`ip nhrp map multicast`) needed on both ends or EIGRP hellos never cross the tunnel, even though NHRP itself looks healthy.

## Proof it works
Verified bottom-up: IPsec SAs active → NHRP registrations on hub → Tunnel0 up/up → EIGRP neighbors formed → spoke routes in routing table → `R2# ping 3.3.3.3 source lo0` succeeds on 2nd try with `show ip nhrp` showing R3 as a `dynamic` (direct) entry, confirming spoke-to-spoke bypasses the hub.

*(Note: source doc gives expected verification output, not captured screenshots — swap in real output/pcaps here if you ran this live.)*

## What I'd do differently / next steps
- Move to **Phase 3** (NHRP redirect/shortcut) and compare NHRP table behavior vs Phase 2.
- Try **OSPF** instead of EIGRP to hit the network-type gotchas.
- Add a **second hub** for redundancy.
- Script the verification checks instead of running them per-device by hand.
