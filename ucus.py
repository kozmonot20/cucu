# -*- coding: utf-8 -*-
# kozmonot20 - Glass Cockpit Flight Simulator v4.0 GUI Edition
import sys
import random
import math
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout
from PyQt6.QtCore import QTimer, Qt, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QKeyEvent

class GlassCockpitPanel(QWidget):
    def __init__(self, sim_engine, parent=None):
        super().__init__(parent)
        self.sim = sim_engine
        self.setMinimumSize(700, 450)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Arka plan kaplama (Karanlık Kokpit Modu)
        painter.setBrush(QBrush(QColor(18, 18, 18)))
        painter.drawRect(self.rect())
        
        # Panel başlığı ve Skor paneli
        painter.setPen(QColor(0, 255, 127))
        painter.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
        painter.drawText(20, 30, f"🛸 KOZMONOT20 SİBER-JET FLIGHT PANEL v4.0 GUI 🛸")
        painter.setPen(Qt.GlobalColor.white)
        painter.drawText(480, 30, f"SKOR: {self.sim.skor} | YAKIT: %{self.sim.yakit:.1f}")

        # Sol Panel: Hız ve Gaz
        self.draw_vertical_bar(painter, 20, 60, 80, 250, "IAS HIZI", self.sim.hiz, 0, 250, "Kt")
        self.draw_vertical_bar(painter, 120, 60, 40, 250, "GAZ", self.sim.gaz, 0, 100, "%", QColor(255, 140, 0))

        # Merkez Panel: Yapay Ufuk (Primary Flight Display)
        self.draw_pfd(painter, 190, 60, 320, 250)

        # Sağ Panel: İrtifa ve Dikey Hız
        self.draw_vertical_bar(painter, 530, 60, 80, 250, "İRTİFA", self.sim.irtifa, 0, 10000, "Ft")
        self.draw_vertical_bar(painter, 630, 60, 50, 250, "VSI", self.sim.dikey_hiz, -2000, 2000, "f/m", QColor(0, 206, 209))

        # Alt Panel: Telsiz ve ILS Göstergeleri
        self.draw_bottom_systems(painter, 20, 330, 660, 100)

    def draw_vertical_bar(self, painter, x, y, w, h, label, val, min_v, max_v, unit, color=QColor(0, 255, 0)):
        # Kutu Arka Planı
        painter.setBrush(QBrush(QColor(30, 30, 30)))
        painter.setPen(QPen(QColor(70, 70, 70), 2))
        painter.drawRect(x, y, w, h)

        # Doluluk Oranı Çizimi
        pct = (val - min_v) / (max_v - min_v) if (max_v - min_v) != 0 else 0
        pct = max(0.0, min(1.0, pct))
        fill_h = int(h * pct)
        
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(x + 2, y + h - fill_h, w - 3, fill_h)

        # Yazılar
        painter.setPen(Qt.GlobalColor.white)
        painter.setFont(QFont("Arial", 8, QFont.Weight.Bold))
        painter.drawText(x, y - 8, label)
        painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        painter.drawText(x + 5, y + h - 10, f"{int(val)}")
        painter.setFont(QFont("Arial", 7))
        painter.drawText(x + 5, y + h - 25, unit)

    def draw_pfd(self, painter, x, y, w, h):
        painter.save()
        # Göstergeyi sınırla (Klip)
        painter.setClipRect(x, y, w, h)
        painter.translate(x + w/2, y + h/2)

        # Hücum açısına göre yapay ufuk yanal hareket simülasyonu
        # 1 derece hücum açısı = 4 piksel kayma simüle edelim
        pitch_offset = (self.sim.hucum_acisi - 2.5) * 6
        
        # Gökyüzü (Mavi)
        painter.setBrush(QBrush(QColor(24, 116, 205)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(-w, -h*2 + int(pitch_offset), w*2, h*2)

        # Yeryüzü (Kahverengi)
        painter.setBrush(QBrush(QColor(128, 64, 0)))
        painter.drawRect(-w, int(pitch_offset), w*2, h*2)

        # Ufuk Çizgisi
        painter.setPen(QPen(Qt.GlobalColor.white, 3))
        painter.drawLine(-w, int(pitch_offset), w, int(pitch_offset))

        # Sabit Uçak Sembolü (Kokpite referanslı merkeze çizilir)
        painter.setPen(QPen(QColor(255, 215, 0), 4))
        painter.drawLine(-40, 0, -15, 0)
        painter.drawLine(-15, 0, -15, 10)
        painter.drawLine(15, 0, 40, 0)
        painter.drawLine(15, 0, 15, 10)
        painter.setBrush(QBrush(QColor(255, 215, 0)))
        painter.drawEllipse(QPointF(0, 0), 4, 4)

        # Bilgi Etiketleri
        painter.restore()
        painter.setPen(Qt.GlobalColor.white)
        painter.setFont(QFont("Arial", 8))
        painter.drawText(x + 10, y + 20, f"AOA: {self.sim.hucum_acisi:.1f}°")

    def draw_bottom_systems(self, painter, x, y, w, h):
        # Arka plan paneli
        painter.setBrush(QBrush(QColor(25, 25, 25)))
        painter.setPen(QPen(QColor(80, 80, 80), 2))
        painter.drawRect(x, y, w, h)

        # Telsiz Bilgileri
        painter.setPen(QColor(0, 255, 255))
        painter.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        painter.drawText(x + 20, y + 30, f"📡 COM1 (KULE) : {self.sim.com1_frekans:.1f} MHz")
        painter.drawText(x + 20, y + 55, f"📻 NAV1 (ILS)  : {self.sim.nav1_frekans:.1f} MHz")

        # ILS Görsel Matris Çizimi
        painter.setPen(Qt.GlobalColor.white)
        painter.drawText(x + 320, y + 30, "📐 ILS PİST HİZALAMA")
        
        # ILS Artı Çizelgesi Çizimi
        cx, cy = x + 400, y + 60
        painter.setPen(QPen(QColor(100, 100, 100), 1, Qt.PenStyle.DashLine))
        painter.drawLine(cx - 50, cy, cx + 50, cy)
        painter.drawLine(cx, cy - 25, cx, cy + 25)

        # ILS Hareketli Sapma Noktası (Localizer sapmasını yatayda çarpıyoruz)
        ils_x = cx + (self.sim.ils_localizer * 13)
        gs_text = "HİZADA"
        gs_color = QColor(0, 255, 0)
        if self.sim.ils_glideslope > 0:
            gs_text = "YÜKSEK"; gs_color = QColor(255, 69, 0)
        elif self.sim.ils_glideslope < 0:
            gs_text = "ALÇAK"; gs_color = QColor(255, 69, 0)

        painter.setBrush(QBrush(QColor(255, 255, 0)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(ils_x, cy), 6, 6)
        
        painter.setPen(gs_color)
        painter.drawText(x + 470, y + 65, f"G-Slope: {gs_text}")

        # Sistem İkaz Mesajı Alanı
        msg_color = QColor(0, 255, 127) if "✅" in self.sim.hata_mesaji or "TEMİZ" in self.sim.hata_mesaji else QColor(255, 0, 0)
        painter.setPen(msg_color)
        painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        painter.drawText(x + 20, y + 85, f"🚨 İKAZ: {self.sim.hata_mesaji}")

class MainWindow(QMainWindow):
    def __init__(self, sim_engine):
        super().__init__()
        self.sim = sim_engine
        self.setWindowTitle("KOZMONOT20 SİBER-JET FLIGHT PANEL v4.0 GUI")
        self.setStyleSheet("background-color: #121212;")
        
        self.panel = GlassCockpitPanel(self.sim)
        self.setCentralWidget(self.panel)

        # Oyun Döngüsü Zamanlayıcısı (0.18 saniyede bir tetiklenir)
        self.timer = QTimer()
        self.timer.timeout.connect(self.game_loop)
        self.timer.start(180)

    def keyPressEvent(self, event: QKeyEvent):
        # Klavye Kontrollerinin Yakalanması
        key = event.text().lower()
        if key == 'w': self.sim.hucum_acisi = min(15.0, self.sim.hucum_acisi + 1.5)
        elif key == 's': self.sim.hucum_acisi = max(-10.0, self.sim.hucum_acisi - 1.5)
        elif key == 'd': self.sim.gaz = min(100, self.sim.gaz + 5)
        elif key == 'a': self.sim.gaz = max(0, self.sim.gaz - 5)
        elif key == 'r':
            self.sim.com1_frekans = 118.1 if self.sim.com1_frekans == 121.5 else 121.5
        elif key == 'q':
            self.sim.oyun_bitti = True
            self.close()
        self.panel.update()

    def game_loop(self):
        if not self.sim.oyun_bitti:
            self.sim.ucus_fizigi_guncelle()
            self.panel.update()
        else:
            self.timer.stop()

# Konsoldaki Sınıfın Yapısını Koruyoruz (Görsel panele veri akışı sağlaması için modifiye edildi)
class GelişmisUcakSimuGUIed:
    def __init__(self):
        self.irtifa, self.hiz, self.dikey_hiz, self.yakit, self.gaz = 5000, 140, 0, 100.0, 65
        self.hucum_acisi, self.skor, self.oyun_bitti = 2.5, 0, False
        self.hata_mesaji = "✅ HAVA SAHASI TEMİZ"
        self.ils_glideslope = 0   
        self.ils_localizer = 0    
        self.com1_frekans = 121.5  
        self.nav1_frekans = 110.3  

    def ucus_fizigi_guncelle(self):
        self.skor += 1
        self.yakit -= (self.gaz * 0.002)
        self.hiz += ((self.gaz * 2.2) - self.hiz) * 0.1
        self.irtifa += int(self.dikey_hiz / 60)
        self.dikey_hiz = int((self.hucum_acisi - 2.5) * self.hiz * 0.5)
        
        if random.randint(1, 100) < 25:
            self.ils_localizer = max(-3, min(3, self.ils_localizer + random.choice([-1, 1])))
            self.ils_glideslope = max(-3, min(3, self.ils_glideslope + random.choice([-1, 1])))
            self.hata_mesaji = "⚠️ ILS SİNYALİNDE SAPMA VAR! PİSTİ HIZALA!"
        else:
            self.hata_mesaji = "✅ HAVA SAHASI TEMİZ"

        if self.irtifa <= 0: self.hata_mesaji = "💥 ÇAKILDI: Yere çarptınız!"; self.oyun_bitti = True
        elif self.yakit <= 0: self.hata_mesaji = "⛽ MOTOR SUSTU: Yakıt bitti!"; self.oyun_bitti = True
        elif self.hiz < 60: self.hata_mesaji = "🛑 STALL: Uçak havada tutunamadı!"; self.oyun_bitti = True

if __name__ == "__main__":
    app = QApplication(sys.argv)
    sim = GelişmisUcakSimuGUIed()
    window = MainWindow(sim)
    window.show()
    sys.exit(app.exec())
