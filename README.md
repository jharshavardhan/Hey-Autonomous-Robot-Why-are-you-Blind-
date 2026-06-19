# 🤖 Hey Autonomous Vacuum Cleaner! Why Are You Blind?
### AI-Powered Visual Dirt Detection for Robot Vacuums

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)
![YOLOv8](https://img.shields.io/badge/YOLOv8s-mAP50%3A90%25-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Platform](https://img.shields.io/badge/Hardware-Jetson%20Nano-76b900?logo=nvidia)
![Framework](https://img.shields.io/badge/Framework-ROS2-orange)

> A real-time computer vision system that gives robot vacuums the ability to **see and understand** floor-level dirt — enabling zone-targeted, adaptive cleaning instead of blind scheduled sweeps.

---

## 📌 Overview

Modern autonomous vacuum cleaners excel at navigation, but they are fundamentally **blind** — they clean on a schedule, not on demand. They cannot detect what they're cleaning, distinguish dirt types, or adapt their behavior accordingly.

This project solves that by training and comparing three deep learning models (MobileNetV2, ResNet50, and YOLOv8s) on real floor images to detect 4 dirt classes in real time, and integrating the winning model into a full robotic pipeline on NVIDIA Jetson Nano with ROS2.

---

## 🧠 The Problem

| Limitation | Impact |
|---|---|
| Fixed Schedule | Wastes energy cleaning already-clean floors |
| No Dirt Detection | Cannot adapt cleaning mode to dirt type |
| No Localization | Cleans entire floor instead of dirty zones only |
| Liquid Blindness | Risks vacuuming liquid — permanently damages motor |
| No Adaptive Suction | Full power even on clean floors (20–40% battery wasted) |
| No Learning | Repeats the same path every session |

---

## ✅ Solution

**YOLOv8s object detection** trained on real floor images to detect dirt with bounding boxes, enabling:
- Precise **zone-targeted cleaning**
- **Adaptive suction control** based on dirt class
- **Real-time inference** (<100ms per frame on Jetson Nano)

---

## 📊 Dataset

- **Source:** [Kaggle — alyyan/trash-detection](https://www.kaggle.com/datasets/alyyan/trash-detection)
- Real floor images captured from a vacuum camera perspective
- **4 dirt classes:** Dirt, Liquid, Marks, Trash
- **1 clean class:** Nothing detected
- Varied surfaces: tiles, wood, carpet
- Varied lighting conditions and camera angles
- Used for YOLOv8s bounding box training AND ResNet50/MobileNetV2 classification comparison

---

## 🏗️ Model Comparison

| Metric | MobileNetV2 | ResNet50 | YOLOv8s |
|---|---|---|---|
| Stability | ⚠️ Dip at Phase 2 | ❌ Catastrophic crash | ✅ Smooth throughout |
| Final Accuracy | ✅ 93% val | ⚠️ ~90% but erratic | ✅ 95% mAP50 |
| Overfitting | ✅ None | ❌ Unstable | ✅ None |
| Detects Location | ❌ | ❌ | ✅ |
| Deployment Ready | ⚠️ Maybe | ❌ No | ✅ Yes |

### Key Findings

**MobileNetV2** — ~35% accuracy overall. Significant overfitting; minority classes (liquid, marks) near 0% recall. Transfer learning from ImageNet doesn't generalize to floor dirt.

**ResNet50** — ~29% accuracy. Class collapse observed — model converges to predicting the dominant class only. Too heavy for embedded real-time inference on Jetson Nano.

**YOLOv8s** — mAP50: ~90%. Detects all 4 dirt classes with bounding boxes. Each class achieves F1 ≈ 0.90. Real-time capable and selected as the final deployment model.

---

## 🔧 Hardware Architecture

| Component | Description |
|---|---|
| **Vision Sensor** | CSI camera mounted at the vacuum front, angled at the floor |
| **Dust Sensor** | PPD42NS optical sensor in the air intake for fine particle detection |
| **Processing Unit** | NVIDIA Jetson Nano — runs YOLOv8s in <15ms, hosts ROS2 nodes |
| **Vacuum Base** | iRobot Create 3 — physical movement via ROS2, BFS/A* path commands |
| **Motor Driver** | DRV8880 — controls suction via PWM (OFF: liquid, LOW: clean, HIGH: dirt/trash) |
| **Power System** | Li-ion battery — 5V compute, 24V motors. Auto-docks below 20% |

---

## 🔄 System Pipeline

