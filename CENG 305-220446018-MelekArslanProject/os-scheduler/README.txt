================================================================================
CS 305 - Operating Systems
Process Scheduling Simulator
Student: Melek Arslan
Student ID: 220446018
================================================================================

PROJE AÇIKLAMASI:
-----------------
Bu proje, işletim sistemlerinde kullanılan process scheduling algoritmalarını
simüle eden bir uygulamadır. FCFS, SJF, Round Robin ve Priority Scheduling
algoritmalarını görselleştirir ve karşılaştırır.

KULLANIM:
---------

1. GUI UYGULAMASI (Önerilen):
   - ProcessScheduler.exe dosyasını çift tıklayarak çalıştırın
   - "Load Input File" butonuna tıklayıp processes.txt dosyasını seçin
   - Quantum ve Speed ayarlarını yapın
   - "Run Simulation" butonuna tıklayın
   - Sonuçları sekmelerde inceleyin
   - PDF veya CSV olarak export edebilirsiniz

2. KOMUT SATIRI:
   - Python yüklü olmalı
   - Terminal'de: python scheduler.py processes.txt [time_quantum]
   - Örnek: python scheduler.py processes.txt 3

DOSYA YAPISI:
-------------
os-scheduler/
├── ProcessScheduler.exe    # Ana uygulama (GUI)
├── scheduler.py             # Komut satırı arayüzü
├── main.py                  # GUI giriş noktası
├── processes.txt            # Örnek input dosyası
│
├── algorithms/              # Scheduling algoritmaları
│   ├── fcfs.py              # First-Come First-Served
│   ├── sjf.py               # Shortest Job First
│   ├── round_robin.py       # Round Robin
│   └── priority.py          # Priority Scheduling
│
├── utils/                   # Yardımcı fonksiyonlar
│   ├── file_parser.py       # Dosya okuma
│   ├── formatters.py        # Formatlama
│   └── calculations.py      # Hesaplamalar
│
└── gui/                     # GUI bileşenleri
    ├── app.py               # Ana uygulama
    ├── components.py        # UI bileşenleri
    └── visualizations.py    # Görselleştirmeler

INPUT DOSYASI FORMATI:
----------------------
process_id, arrival_time, burst_time, priority

Örnek:
P1, 0, 5, 3
P2, 1, 3, 1
P3, 2, 8, 2

ÖZELLİKLER:
-----------
- 4 farklı scheduling algoritması (FCFS, SJF, RR, Priority)
- Gantt chart görselleştirmesi
- Detaylı metrikler (Turnaround Time, Waiting Time, CPU Utilization)
- Karşılaştırmalı analiz grafikleri
- PDF ve CSV export
- Modern ve kullanıcı dostu arayüz

GEREKSINIMLER (Komut satırı için):
----------------------------------
- Python 3.x
- tkinter (genellikle Python ile birlikte gelir)

NOTLAR:
-------
- EXE dosyası bağımsız çalışır, Python yüklü olmasına gerek yoktur
- processes.txt dosyası örnek input dosyasıdır
- Tüm algoritmalar ödev gereksinimlerine uygun şekilde implement edilmiştir

================================================================================
