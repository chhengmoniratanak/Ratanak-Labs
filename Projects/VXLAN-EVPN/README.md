# BGP EVPN VXLAN Fabric Implementation

A production-grade, multi-tenant BGP EVPN VXLAN data center fabric deployed and verified in EVE-NG. This project implements a modern control-plane-driven EVPN architecture, replacing traditional flood-and-learn mechanisms.

## 🏗️ Topology & Architecture

The network follows a classic spine-leaf design consisting of a centralized core router (`CS1`) acting as an OSPF underlay router and BGP EVPN Route Reflector, paired with two Cisco Nexus 9000v leaf switches (`9K1`, `9K-2`) and Cisco IOS-on-Unix (IOL) edge host nodes.

* **Spine / Core (`CS1`)**: Manages OSPF Area 0 underlay reachability and MP-BGP route reflection.
* **Leaf 1 (`9K1`) & Leaf 2 (`9K-2`)**: NX-OS VTEP nodes handling Layer 2 VNIs, Distributed Anycast Gateways, and the Layer 3 transit VNI (`333333`).
* **Hosts (`PC4`, `PC5`, `PC6`, `PC7`)**: IOL Layer 3 router nodes serving as edge endpoints across multiple VLANs.

---

## 🚀 Key Features

* **MP-BGP EVPN Control Plane**: Dynamically exchanges Type-2 (MAC/IP bindings) and Type-5 (IP prefix) routes.
* **Distributed Anycast Gateways**: Provides consistent default gateway redundancy across all leaf nodes using a shared virtual MAC (`000a.000a.000a`).
* **ARP Suppression & Ingress Replication**: Optimizes BUM (Broadcast, Unknown-Unicast, Multicast) traffic handling and eliminates broadcast storms across the fabric.
* **Symmetric IRB**: Achieves efficient inter-subnet routing via a dedicated Layer 3 transit VNI.

---

## 📂 Repository Structure

```text
bgp-evpn-vxlan-fabric/
├── README.md               # Project overview and documentation
├── BGP_EVPN_VXLAN_Project_Doc.pdf
└── configs/
    ├── vxlan.txt            # Core/Spine running configuration
    ├── evpn.txt            # Leaf 1 running configuration
    └── l3vni.txt           # Leaf 2 running configuration

```

---

## ✅ Verification & Results

* **Intra-Subnet (Same VLAN across VTEPs)**: Verified with 100% ping success (`PC4` to `PC6`) using BGP Ingress Replication and ARP Suppression.
* **Inter-Subnet (Cross-VLAN across Fabric)**: Verified with 100% ping success (`PC5` to `PC7`) via the L3 transit VNI (`333333`) and Distributed Anycast Gateways.
