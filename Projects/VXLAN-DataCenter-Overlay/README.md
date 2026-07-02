# Static VXLAN on Cisco Nexus 9000v (EVE-NG)

## What I built
A Layer 2 VXLAN overlay between two Nexus 9K leaf switches (VTEPs) using static ingress replication — no multicast, no BGP EVPN control plane. VLAN 10 on both switches maps to VNI 10010, so two end-hosts (VPC1, VPC2) on different physical switches sit in the same L2 domain across an L3 underlay. Built and validated in EVE-NG on NX-OS 9.x.

## Topology
- **Nexus-9K-01** — Lo0 1.1.1.1/32 (VTEP source), Eth1/1 10.1.1.1/30 (underlay), Eth1/2 → VLAN 10 → VPC1 (192.168.10.1/24)
- **Nexus-9K-02** — Lo0 2.2.2.2/32 (VTEP source), Eth1/1 10.1.1.2/30 (underlay), Eth1/2 → VLAN 10 → VPC2 (192.168.10.2/24)
- Switches connected back-to-back on Eth1/1; VLAN 10 on both sides is stretched over the overlay tunnel via VNI 10010

## Key config
TCAM carving (Phase 0, both switches, before anything else, reload required):
```
hardware access-list tcam region ing-copp 256
hardware access-list tcam region qos-ingress 256
```
Underlay — OSPF between the two loopbacks:
```
feature ospf
router ospf 1
interface Ethernet1/1
 no switchport
 ip address 10.1.1.1/30
 ip router ospf 1 area 0.0.0.0
interface Loopback0
 ip address 1.1.1.1/32
 ip router ospf 1 area 0.0.0.0
```
Overlay — VNI mapping + static ingress replication peer:
```
feature nv overlay
feature vn-segment-vlan-based
vlan 10
 vn-segment 10010
interface nve1
 no shutdown
 source-interface Loopback0
 member vni 10010
  ingress-replication protocol static
  peer-ip 2.2.2.2
```
Access port (required for NVE to come up at all):
```
interface Ethernet1/2
 switchport access vlan 10
 no shutdown
```

## Gotchas I ran into
- **TCAM carving isn't optional** — skip it and you get `ACLQOS_FAILED` at boot with unpredictable feature failures later. Has to be done before enabling features, and both switches need a reload after.
- **Active Attachment Circuit** — the NVE interface and VNI stay Down until at least one access port in the mapped VLAN is Up/Up. Config can be 100% correct and the tunnel still won't come up if the VPCs aren't powered on.
- **No control plane, so no peer adjacency until traffic flows** — `show nve peers` shows nothing until you actually send a ping. This looks like a misconfig but isn't.
- **First ping always fails** — it triggers ARP-broadcast encapsulation and MAC learning across the tunnel. Second ping succeeds. Don't chase this as a bug.
- **NX-OS 9.x syntax quirk** — `ingress-replication protocol static` / `peer-ip` nest under `member vni`, not directly under `interface nve1` like older releases. Easy to get wrong copying from older docs.
- **`no switchport` on Eth1/1** — needed to run OSPF on it as a routed underlay link; without it the interface stays L2 and OSPF won't come up.

## Proof it works
Verified in order: OSPF sees the remote loopback (`show ip route ospf` — 2.2.2.2/32 on SW1, 1.1.1.1/32 on SW2) → access ports Up/Up in VLAN 10 → ping VPC1 → VPC2 (first fails, second succeeds) → `show nve vni` shows State: Up, Mode: DP, Multicast-group: UnicastStatic → `show nve peers` shows the remote loopback State: Up → `show mac address-table vlan 10` shows the remote MAC reachable via nve1.

*(Optional stronger proof: packet capture on Eth1/1 filtered on UDP/4789, showing the 192.168.10.0/24 frames encapsulated between the two loopbacks — not captured in this run.)*

## What I'd do differently / next steps
- Move from **static ingress replication to BGP EVPN** control plane — removes the "first packet always fails" behavior and scales past 2 VTEPs without a full mesh of static peers.
- Add a **third VTEP** to see how static peering config grows linearly (n-1 peer statements per switch) vs. EVPN.
- Test **multicast underlay** ingress replication as a comparison point against static.
- Capture the actual UDP/4789 packet trace instead of relying on `show` command output alone.
