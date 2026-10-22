# 🌐 VXLAN Flood-and-Learn Fabric (Multicast Underlay)

A clean, production-style runbook and architecture guide for deploying a 2-tier VXLAN Overlay network with a Multicast (PIM Sparse-Mode) IP Underlay across Cisco CSR1000V and Nexus 9000v platforms.

---

## 📐 Topology Architecture

```text
                  +-------------------+
                  |    CSR1 (Spine)   |
                  | Loopback0:        |
                  | 10.1.1.100/32     |
                  +---------+---------+
                            |
           Gi1 (10.0.0.1/30)| Gi2 (10.0.0.5/30)
                            |
         +------------------+------------------+
         |                                     |
 Eth1/1 (10.0.0.2/30)               Eth1/1 (10.0.0.6/30)
+--------+----------+              +-----------+-------+
|    9K1 (Leaf 1)   |   VXLAn      |    9K-2 (Leaf 2)   |
| Loopback0:        |====== Overlay =====| Loopback0:   |
| 10.1.1.1/32       |  (NVE Fabric)  | 10.1.2.2/32       |
+----+---------+----+              +----+---------+----+
     |         |                        |         |
Eth1/2 |  Eth1/3 |                 Eth1/2 |  Eth1/3 |
(VLAN 10) (VLAN 20)                (VLAN 10) (VLAN 20)
     |         |                        |         |
   [PC1]     [PC2]                    [PC3]     [PC4]
```

---

## 💡 Key Design & Components

* **IP Underlay Routing:** OSPF Area 0 ensures reachability for all VTEP Loopbacks and interface IP addresses.
* **BUM Replication:** Multicast **PIM Sparse-Mode** anchored to a central Rendezvous Point (**RP: 10.1.1.100**) for BUM (Broadcast, Unknown Unicast, Multicast) traffic handling.
* **Overlay Mapping:**
  * **VLAN 10** $\rightarrow$ **VNI 100000** $\rightarrow$ **Multicast Group 239.1.1.1**
  * **VLAN 20** $\rightarrow$ **VNI 200000** $\rightarrow$ **Multicast Group 239.1.1.2**
* **Hardware Allocations:** Includes Nexus TCAM carving optimizations for double-wide ARP/Ethernet entries.

---

## 🛠️ Addressing & Interface Summary

| Device | Role / Function | Loopback0 IP | Uplink Interface | Uplink IP | Connected To |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **CSR1** | Spine / PIM RP | `10.1.1.100/32` | Gi1 / Gi2 | `10.0.0.1/30` / `10.0.0.5/30` | 9K1 (Eth1/1) / 9K-2 (Eth1/1) |
| **9K1** | VTEP / Leaf 1 | `10.1.1.1/32` | Eth1/1 | `10.0.0.2/30` | CSR1 (Gi1) |
| **9K-2** | VTEP / Leaf 2 | `10.1.1.2/32` | Eth1/1 | `10.0.0.6/30` | CSR1 (Gi2) |

---

## 🔍 Verification Commands

### Check VNI Status and Multicast Mappings (Leaf Switches)
```bash
show nve vni
show vxlan
```

### Confirm PIM Multicast Route Table (Spine / RP)
```bash
show ip mroute
```

---
*Maintained as part of the Personal Engineering Library (CCNP ENCOR Network Fabric Studies).*