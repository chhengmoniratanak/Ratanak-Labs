# QoS — MQC Deep Dive (2-Node Lab)

## What I built
End-to-end MQC QoS policy on a single edge router (HQ-Edge), tested against a traffic-generator node (HQ-Core). Covers ingress classification/marking, LLQ+CBWFQ+WRED egress queuing, hierarchical shaping (HQoS) on a subrate WAN link, and ingress policing for scavenger traffic — the full ENCOR/ENARSI QoS toolkit in one compact topology.

## Topology
- **HQ-Core** — Eth0/0 10.1.1.2/24, traffic generator, default route → HQ-Edge
- **HQ-Edge** — Gi1 10.1.1.1/24 (LAN, ingress marking), Gi2 192.168.12.1/30 (WAN, egress shaping to a dummy unconnected next-hop)
- Traffic profile: Voice (UDP RTP → EF/LLQ), Video (source-IP match → AF41/CBWFQ 20%), Critical data (HTTP/S via NBAR2 → AF21/CBWFQ 30%+WRED), Scavenger (P2P/YouTube via NBAR2 → CS1, policed to 128 Kbps)

## Key config
Ingress marking + scavenger policing (Gi1):
```
policy-map MARKING-INGRESS
 class CM_VOICE
  set dscp ef
 class CM_SCAVENGER
  set dscp cs1
  police 128000 conform-action transmit exceed-action drop
interface GigabitEthernet1
 service-policy input MARKING-INGRESS
```
Egress queuing (child policy — LLQ/CBWFQ/WRED):
```
policy-map QUEUE-EGRESS
 class CM_WAN_VOICE
  priority percent 10
 class CM_WAN_CRITICAL
  bandwidth percent 30
  random-detect dscp-based
 class class-default
  fair-queue
```
Hierarchical shaping (parent, forces queues to engage on a 1G interface with a 10M contract):
```
policy-map SHAPE-10MBPS-PARENT
 class class-default
  shape average 10000000
  service-policy QUEUE-EGRESS
interface GigabitEthernet2
 service-policy output SHAPE-10MBPS-PARENT
```

## Gotchas I ran into
- **Physical vs. contracted bandwidth.** Gi2 is a 1 Gbps interface but the WAN contract is 10 Mbps — without the parent shaper, the router thinks it has 1 Gbps of headroom and the child queues never engage. HQoS (shape + nested service-policy) is what forces real congestion management.
- **A dummy static route is required to trigger egress queuing at all**, since Gi2 has no real neighbor — without traffic actually routing out that interface, the policy never activates.
- **Shaping vs. policing are not interchangeable.** Shaping (parent, WAN egress) buffers and smooths; policing (ingress, scavenger) hard-drops instantly. Used the wrong one on the wrong class and the design breaks.
- **CBWFQ `bandwidth` is a congestion-only guarantee**, not a ceiling — video can burst past 20% when the link is idle. The lab challenge fixes this with `police 2000000` nested inside the class to enforce a hard cap.
- **In EVE-NG/GNS3, egress counters can stay at zero even when ingress counters increment correctly.** Virtual interfaces lack real line-state signaling, so the CEF path can bypass the software queues entirely. This is expected — don't chase it as a misconfig if the syntax matches the guide.
- **`ping ... tos <value>`** needs the decimal ToS byte, not the DSCP name (e.g. EF = 184, AF41 = 136) — mixing these up gives you a policy that matches nothing during testing.

## Proof it works
Verified via `show policy-map interface GigabitEthernet2` on HQ-Edge while generating marked test streams from HQ-Core (`ping ... tos 184` for voice, `ping ... tos 72` large/repeated for critical-data WRED). Expect to see per-class packet counts under MARKING-INGRESS (ingress) and queue/drop stats under QUEUE-EGRESS (egress) — though see the virtual-environment caveat above regarding egress counters.

*(Not a captured live run — this reflects the guide's verification steps. Swap in real `show policy-map interface` output if you ran it.)*

## What I'd do differently / next steps
- Run this in a lab with **real physical or hypervisor-backed interfaces** to actually observe egress WRED drops and LLQ preemption, since virtual line-state limitations mask that here.
- Add the **lab challenge policer** (2 Mbps hard cap on video) as the default, not an optional add-on.
- Extend to a **3-node topology with a real WAN emulator** (e.g. a link-rate-limited switch) instead of a dummy static route, to validate shaping against actual provider-side drops.
- Script `show policy-map interface` diffs before/after each test stream to quantify conform/exceed/drop counts automatically.
