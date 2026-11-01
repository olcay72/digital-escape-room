
import json
import os
import random


KAYIT_DOSYASI = "kayit.json"
BASLANGIC_HAMLESI = 20


class Oda:
    def __init__(self, isim, acilma_esyasi, bulmaca, odul):
        self.isim = isim
        self.acilma_esyasi = acilma_esyasi
        self.bulmaca = bulmaca
        self.odul = odul


class KacisOdasi:
    def __init__(self):
        self.odalar = {}
        self.oyun_durumu = {}
        self.odalar_olustur()

    def bulmaca_olustur(self, oda_no):
        """Her oda için farklı türde bir bulmaca oluşturur."""

        if oda_no == 1:
            sayi = random.randint(10, 30)
            return {
                "soru": f"Güvenlik paneli: {sayi} + 7 = ?",
                "cevap": str(sayi + 7),
                "ipucu": "Toplama işlemini yap.",
            }

        elif oda_no == 2:
            sayi = random.randint(3, 9)
            return {
                "soru": f"Şifreyi çöz: {sayi} x {sayi} = ?",
                "cevap": str(sayi * sayi),
                "ipucu": "Sayıyı kendisiyle çarp.",
            }

        elif oda_no == 3:
            return {
                "soru": (
                    "Beni ne kadar çok alırsan, "
                    "arkanda o kadar çok bırakırsın. Neyim?"
                ),
                "cevap": "adim",
                "ipucu": "Yürümekle ilgilidir.",
            }

        elif oda_no == 4:
            baslangic = random.randint(1, 5)
            artis = random.randint(2, 5)
            dizi = [
                baslangic,
                baslangic + artis,
                baslangic + 2 * artis,
                baslangic + 3 * artis,
            ]
            return {
                "soru": (
                    f"Sayı dizisini tamamla: {dizi[0]}, "
                    f"{dizi[1]}, {dizi[2]}, {dizi[3]}, ?"
                ),
                "cevap": str(dizi[3] + artis),
                "ipucu": "Sayılar arasındaki farkı bul.",
            }

        else:
            return {
                "soru": (
                    "Üç anahtar var: kırmızı, mavi ve yeşil. "
                    "Doğru anahtar kırmızı değil, mavi de değil. "
                    "Hangi anahtar?"
                ),
                "cevap": "yesil",
                "ipucu": "Kırmızı ve maviyi ele.",
            }

    def odalar_olustur(self):
        ayarlar = [
            ("Giriş Odası", None, "Güvenlik Kartı"),
            ("Güvenlik Odası", "Güvenlik Kartı", "Laboratuvar Anahtarı"),
            ("Laboratuvar", "Laboratuvar Anahtarı", "Sunucu Anahtarı"),
            ("Sunucu Odası", "Sunucu Anahtarı", "Çıkış Anahtarı"),
            ("Çıkış Koridoru", "Çıkış Anahtarı", None),
        ]

        for no, (isim, gerekli_esya, odul) in enumerate(ayarlar, start=1):
            self.odalar[isim] = Oda(
                isim=isim,
                acilma_esyasi=gerekli_esya,
                bulmaca=self.bulmaca_olustur(no),
                odul=odul,
            )

    def yeni_oyun(self):
        self.oyun_durumu = {
            "mevcut_oda": "Giriş Odası",
            "envanter": [],
            "tamamlanan_odalar": [],
            "hamle": BASLANGIC_HAMLESI,
            "oyun_bitti": False,
            "kazanildi": False,
        }
        self.kaydet()
        print("\nLaboratuvarda uyandın. Kapılar kilitli!")
        print("Kaçmak için 20 hamlen var.\n")

    def kaydet(self):
        veri = {
            "oyun_durumu": self.oyun_durumu,
            "bulmacalar": {
                isim: oda.bulmaca
                for isim, oda in self.odalar.items()
            },
        }

        with open(KAYIT_DOSYASI, "w", encoding="utf-8") as dosya:
            json.dump(veri, dosya, ensure_ascii=False, indent=4)

    def yukle(self):
        if not os.path.exists(KAYIT_DOSYASI):
            return False

        try:
            with open(KAYIT_DOSYASI, "r", encoding="utf-8") as dosya:
                veri = json.load(dosya)

            self.oyun_durumu = veri["oyun_durumu"]

            # Kaydedilen bulmacaları koru.
            for isim, bulmaca in veri["bulmacalar"].items():
                if isim in self.odalar:
                    self.odalar[isim].bulmaca = bulmaca

            return True

        except (OSError, json.JSONDecodeError, KeyError, TypeError):
            print("Kayıt dosyası okunamadı.")
            return False

    def hamle_kullan(self):
        self.oyun_durumu["hamle"] -= 1

        if self.oyun_durumu["hamle"] <= 0:
            self.oyun_durumu["hamle"] = 0
            self.oyun_durumu["oyun_bitti"] = True
            self.oyun_durumu["kazanildi"] = False
            print("\nHamlelerin bitti! Laboratuvarda mahsur kaldın.")

        self.kaydet()

    def durum_goster(self):
        print("\n" + "=" * 40)
        print("Mevcut oda:", self.oyun_durumu["mevcut_oda"])
        print("Kalan hamle:", self.oyun_durumu["hamle"])
        print("Envanter:", self.oyun_durumu["envanter"] or "Boş")
        print(
            "Tamamlanan odalar:",
            len(self.oyun_durumu["tamamlanan_odalar"]),
            "/",
            len(self.odalar),
        )
        print("=" * 40)

    def bulmacayi_coz(self):
        oda_adi = self.oyun_durumu["mevcut_oda"]
        oda = self.odalar[oda_adi]

        if oda_adi in self.oyun_durumu["tamamlanan_odalar"]:
            print("Bu odanın bulmacasını zaten çözdün.")
            return

        print("\nBULMACA")
        print(oda.bulmaca["soru"])
        print("İpucu için 'ipucu' yazabilirsin.")
        cevap = input("Cevabın: ").strip().lower()

        if cevap == "ipucu":
            print("İpucu:", oda.bulmaca["ipucu"])
            return

        # Türkçe karakterleri cevap kontrolü için sadeleştir.
        cevap = cevap.translate(str.maketrans({
            "ı": "i",
            "ş": "s",
            "ğ": "g",
            "ü": "u",
            "ö": "o",
            "ç": "c",
        }))

        dogru_cevap = oda.bulmaca["cevap"].lower()

        if cevap == dogru_cevap:
            print("Doğru cevap! Bulmaca çözüldü.")
            self.oyun_durumu["tamamlanan_odalar"].append(oda_adi)

            if oda.odul:
                self.oyun_durumu["envanter"].append(oda.odul)
                print("Kazandığın eşya:", oda.odul)

            if len(self.oyun_durumu["tamamlanan_odalar"]) == len(self.odalar):
                self.oyun_durumu["oyun_bitti"] = True
                self.oyun_durumu["kazanildi"] = True
                print("\nTebrikler! Laboratuvardan kaçtın!")

            self.kaydet()

        else:
            print("Yanlış cevap! Bir hamle kaybettin.")
            self.hamle_kullan()

    def oda_degistir(self):
        mevcut = self.oyun_durumu["mevcut_oda"]

        if mevcut not in self.oyun_durumu["tamamlanan_odalar"]:
            print("Önce bu odanın bulmacasını çözmelisin.")
            return

        oda_sirasi = list(self.odalar.keys())
        indeks = oda_sirasi.index(mevcut)

        if indeks == len(oda_sirasi) - 1:
            print("Zaten son odadasın.")
            return

        sonraki_oda = self.odalar[oda_sirasi[indeks + 1]]

        if (
            sonraki_oda.acilma_esyasi
            and sonraki_oda.acilma_esyasi not in self.oyun_durumu["envanter"]
        ):
            print("Bu oda kilitli!")
            print("Gerekli eşya:", sonraki_oda.acilma_esyasi)
            return

        self.oyun_durumu["mevcut_oda"] = sonraki_oda.isim
        print("Yeni odaya girdin:", sonraki_oda.isim)
        self.kaydet()

    def oyunu_baslat(self):
        while not self.oyun_durumu["oyun_bitti"]:
            self.durum_goster()

            print("\n1. Bulmacayı çöz")
            print("2. Sonraki odaya geç")
            print("3. Envanteri göster")
            print("4. Oyunu kaydet ve çık")

            secim = input("Seçimin: ").strip()

            if secim == "1":
                self.bulmacayi_coz()

            elif secim == "2":
                self.oda_degistir()

            elif secim == "3":
                print("Envanter:", self.oyun_durumu["envanter"] or "Boş")

            elif secim == "4":
                self.kaydet()
                print("Oyun kaydedildi. Daha sonra devam edebilirsin.")
                return

            else:
                print("Geçersiz seçim.")

        self.kaydet()

        if self.oyun_durumu["kazanildi"]:
            print("OYUNU KAZANDIN!")
        else:
            print("OYUN BİTTİ. Yeni bir oyun başlatabilirsin.")

    def ana_menu(self):
        while True:
            print("\n=== DİJİTAL KAÇIŞ ODASI ===")
            print("1. Yeni oyun")
            print("2. Kaldığın yerden devam et")
            print("3. Çıkış")

            secim = input("Seçimin: ").strip()

            if secim == "1":
                self.yeni_oyun()
                self.oyunu_baslat()

            elif secim == "2":
                if self.yukle():
                    print("Kayıt yüklendi!")
                    if not self.oyun_durumu["oyun_bitti"]:
                        self.oyunu_baslat()
                    else:
                        print("Bu oyun zaten bitmiş. Yeni oyun başlatabilirsin.")
                else:
                    print("Kayıt bulunamadı veya okunamadı.")

            elif secim == "3":
                print("Görüşürüz!")
                break

            else:
                print("Geçersiz seçim.")


if __name__ == "__main__":
    oyun = KacisOdasi()
    oyun.ana_menu()
