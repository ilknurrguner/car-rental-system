from tkinter import *
import json
from tkinter import messagebox
from datetime import datetime
from PIL import Image, ImageTk
import os

siralama_kriteri = None #sıralama kriteri başlangıçta yok
siralama_yonu = "asc" #sıralama yönü başlangıçta artan

def araciKirala(plaka, frame_liste, dosya):
    try:
        with open(dosya, 'r', encoding='utf-8') as f:
            veri_listesi = json.load(f)
    except: return

    arac = next((a for a in veri_listesi if a.get("plaka") == plaka), None)

    kira_window = Toplevel(frame_liste.winfo_toplevel()) #araç kiralamak için pencere açacak
    kira_window.title(f"Araç Kirala: {plaka}")
    kira_window.geometry("300x350")
    kira_window.resizable(False, False)

    Label(kira_window, text=f"{plaka} - Kiralama İşlemi", font=("Arial", 12, "bold")).pack(pady=10)

    Label(kira_window, text="Kiralayan Ad Soyad:").pack(pady=2)
    kiralayan_ent = Entry(kira_window, justify="center")
    kiralayan_ent.pack(pady=5)

    Label(kira_window, text="Alış Tarihi (DD-MM-YYYY):").pack(pady=2)
    alis_ent = Entry(kira_window, justify="center")
    alis_ent.insert(0, datetime.now().strftime("%d-%m-%Y")) #bugünün tarihi varsayılan
    alis_ent.pack(pady=5)

    Label(kira_window, text="İade Tarihi (DD-MM-YYYY):").pack(pady=2)
    iade_ent = Entry(kira_window, justify="center")
    iade_ent.pack(pady=5)

    toplam_ucret_label = Label(kira_window, text="Toplam Ücret: 0 TL", font=("Arial", 10, "bold"), fg="green")
    toplam_ucret_label.pack(pady=10)

    def ucretHesapla(event=None):
        alis_str = alis_ent.get().strip()
        iade_str = iade_ent.get().strip()

        if len(alis_str) < 10 or len(iade_str) < 10:
            toplam_ucret_label.config(text="Toplam Ücret: --- TL", fg="blue")
            return -1
        try:
            d1 = datetime.strptime(alis_ent.get(), "%d-%m-%Y")
            d2 = datetime.strptime(iade_ent.get(), "%d-%m-%Y")
            gun_sayisi = (d2 - d1).days + 1 #toplam gün sayısı hesaplanır
            
            if gun_sayisi <= 0:
                toplam_ucret_label.config(text="Hata: Geçersiz tarih", fg="red")
                return -1
            
            birim_fiyat = int(arac.get("ucret", 0)) #jsondan alınan günlük ücret int'e çevrilir
            
            toplam = gun_sayisi * birim_fiyat
            toplam_ucret_label.config(text=f"Toplam Ücret: {toplam} TL ({gun_sayisi} Gün)", fg="green")
            return toplam
        except ValueError:
            toplam_ucret_label.config(text="Format: DD-MM-YYYY", fg="red")
            return -1
    alis_ent.bind("<KeyRelease>", ucretHesapla) #yazıldıkça ücret hesaplanır
    iade_ent.bind("<KeyRelease>", ucretHesapla)

    def kiralamayiTamamla():
        ad = kiralayan_ent.get().strip()
        alis = alis_ent.get().strip()
        iade = iade_ent.get().strip()
        toplam = ucretHesapla()

        if not ad or toplam <= 0:
            messagebox.showerror("Hata", "Lütfen bilgileri ve tarihleri kontrol edin.")
            return
        for a in veri_listesi: #durum kirada olarak güncellenir
            if a["plaka"] == plaka:
                a["durum"] = "Kirada"
                a["kiralayan"] = ad
                a["baslangic_tarihi"] = alis
                a["bitis_tarihi"] = iade
                break
        try:
            with open(dosya, 'w', encoding='utf-8') as f:
                json.dump(veri_listesi, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Başarılı", f"Araç {ad} adına kiralandı.\nToplam: {toplam} TL")
            kira_window.destroy()
            aracListele(frame_liste, dosya)
        except Exception as e:
            messagebox.showerror("Hata", f"Kaydedilemedi: {e}")
            
    Button(kira_window, text="Kiralamayı Onayla", command=kiralamayiTamamla, bg="green", width=20).pack(pady=10) #bilgiler onaylanır
    kira_window.grab_set()

def infoGetir(plaka, frame_liste, dosya):
    try:
        with open(dosya, 'r', encoding='utf-8') as f:
            veri_listesi = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return
    
    arac_verisi = next((arac for arac in veri_listesi if arac.get("plaka") == plaka), None)

    info_window = Toplevel(frame_liste.winfo_toplevel()) #bilgi penceresi açılır
    info_window.title(f"Kira Bilgisi")
    info_window.geometry("300x200")
    info_window.resizable(False, False)
    info_window.transient(frame_liste.winfo_toplevel())

    kiralayan_ad = arac_verisi.get("kiralayan", "Bilinmiyor")
    alis_tarihi = arac_verisi.get("baslangic_tarihi", "Belirtilmemiş")
    iade_tarihi = arac_verisi.get("bitis_tarihi", "Belirtilmemiş")
    
    info_frame = Frame(info_window)
    info_frame.pack(pady=10, padx=20)

    Label(info_frame, text=f"Plaka: {plaka}").grid(row=0, column=0, sticky="w", pady=2)
    Label(info_frame, text=f"Kiralayan: {kiralayan_ad}").grid(row=1, column=0, sticky="w", pady=2)
    Label(info_frame, text=f"Alış Tarihi: {alis_tarihi}").grid(row=2, column=0, sticky="w", pady=2)
    Label(info_frame, text=f"İade Tarihi: {iade_tarihi}").grid(row=3, column=0, sticky="w", pady=2)

    Button(info_window, text="Kapat", command=info_window.destroy, width=10).pack(pady=10)

    info_window.grab_set()

def aracBilgisiDuzenle(plaka, frame_liste, dosya):
    try:
        with open(dosya, 'r', encoding='utf-8') as f:
            veri_listesi = json.load(f)
    except: return

    arac = next((a for a in veri_listesi if a.get("plaka") == plaka), None)

    edit_window = Toplevel(frame_liste.winfo_toplevel()) #araç bilgisi düzenleme penceresi açılır
    edit_window.title(f"Düzenle: {plaka}")
    edit_window.geometry("350x250")
    edit_window.resizable(False, False)

    durum_var = StringVar(value=arac.get("durum", "Müsait"))
    ucret_var = StringVar(value=str(arac.get("ucret", "0")))

    Label(edit_window, text="Araç Durumu:").pack()

    durum_mbtn = Menubutton(edit_window, textvariable=durum_var, relief="raised", width=15)
    menu = Menu(durum_mbtn, tearoff=0)
    for secenek in ["Müsait", "Kirada", "Bakımda"]:
        menu.add_command(label=secenek, command=lambda s=secenek: durum_var.set(s))
    durum_mbtn["menu"] = menu
    durum_mbtn.pack(pady=5)

    Label(edit_window, text="Günlük Ücret (TL):").pack()
    ucret_ent = Entry(edit_window, textvariable=ucret_var, justify="center")
    ucret_ent.pack(pady=5)

    def guncelle():
        yeni_ucret = ucret_var.get().strip()
        yeni_durum = durum_var.get()
        if not yeni_ucret.isdigit():
            messagebox.showerror("Hata", "Ücret sadece sayı olmalıdır.")
            return

        for a in veri_listesi:
            if a["plaka"] == plaka:
                a["durum"] = durum_var.get()
                if a["durum"] == "Müsait" or "Bakımda":
                    a["kiralayan"] = ""
                    a["baslangic_tarihi"] = ""
                    a["bitis_tarihi"] = ""
                a["ucret"] = int(yeni_ucret)
                break

        try:
            with open(dosya, 'w', encoding='utf-8') as f:
                json.dump(veri_listesi, f, indent=4, ensure_ascii=False)
            if yeni_durum == "Kirada": #durum kirada yapılmış ise kiralama ekranına yönlendirilir
                messagebox.showinfo("Yönlendirme", "Araç durumu 'Kirada' olarak seçildi.\nKiralama bilgilerini girmek için kiralama ekranına yönlendiriliyorsunuz.")
                edit_window.destroy()
                araciKirala(plaka, frame_liste, dosya)
            else:
                messagebox.showinfo("Başarılı", "Araç bilgileri güncellendi.")
                edit_window.destroy()
                aracListele(frame_liste, dosya)
            
        except Exception as e:
            messagebox.showerror("Hata", f"Kaydedilemedi: {e}")

    Button(edit_window, text="Değişiklikleri Kaydet", command=guncelle, bg="#176985", fg="black").pack(pady=20)
    edit_window.grab_set()

def aracSil(plaka, frame_liste, dosya):
    onay_window = Toplevel(frame_liste.winfo_toplevel()) #silme onay penceresi açılır
    onay_window.title("Silme Onayı")
    onay_window.geometry("400x150")
    onay_window.resizable(False, False)
    onay_window.transient(frame_liste.winfo_toplevel())

    def Sil():
        onay_window.destroy()
        try:
            with open(dosya, 'r', encoding='utf-8') as f:
                veri_listesi = json.load(f)
        except FileNotFoundError:
            print(f"Hata: '{dosya}' dosyası bulunamadı.")
            veri_listesi = []
        except json.JSONDecodeError:
            print(f"Hata: '{dosya}' dosyası geçerli bir JSON formatında değil.")
            veri_listesi = []

        guncel_veri_listesi = [arac for arac in veri_listesi if arac.get("plaka") != plaka]

        try:
            with open(dosya, 'w', encoding='utf-8') as f:
                json.dump(guncel_veri_listesi, f, indent=4, ensure_ascii=False)
        except:
            return
        
        aracListele(frame_liste, dosya)
        
    def Vazgec(): #silinmeyecekse pencere kapanır ve değişiklik yapılmaz
        onay_window.destroy()

    Label(onay_window, text=f"{plaka} plakalı aracı silmek istediğinize emin misiniz? \n Bu işlem geri alınamaz.", padx=10, pady=10).pack(pady=15)
    frame_buton = Frame(onay_window)
    frame_buton.pack(pady=10)

    Button(frame_buton, text="Aracı Sil", command=Sil).pack(side=LEFT, padx=10)
    Button(frame_buton, text="Vazgeç", command=Vazgec).pack(side=RIGHT, padx=10)

    onay_window.grab_set()
    onay_window.wait_window()

def araciIadeEt(plaka, frame_liste, dosya):
    onay_window = Toplevel(frame_liste.winfo_toplevel()) #iade onay penceresi açılır
    onay_window.title("İade Onayı")
    onay_window.geometry("400x150")
    onay_window.resizable(False, False)
    onay_window.transient(frame_liste.winfo_toplevel())

    def iadeOnayla():
        onay_window.destroy()
        try:
            with open(dosya, 'r', encoding='utf-8') as f:
                veri_listesi = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return

        for arac in veri_listesi:
            if arac.get("plaka") == plaka:
                arac["durum"] = "Müsait" #durumu müsait yapmakla birlikte kiralama bilgileri de silinir
                arac["kiralayan"] = ""
                arac["baslangic_tarihi"] = ""
                arac["bitis_tarihi"] = ""
                break

        try:
            with open(dosya, 'w', encoding='utf-8') as f:
                json.dump(veri_listesi, f, indent=4, ensure_ascii=False)
            aracListele(frame_liste, dosya)
        except:
            return

    def Vazgec(): #iade edilmeyecekse pencere kapanır ve değişiklik yapılmaz
        onay_window.destroy()

    Label(onay_window, text=f"{plaka} plakalı aracın durumu 'Müsait' olarak değiştirilecek. \nOnaylıyor musunuz?", padx=10, pady=10).pack(pady=15)
    frame_buton = Frame(onay_window)
    frame_buton.pack(pady=10)

    Button(frame_buton, text="Onayla", command=iadeOnayla).pack(side=LEFT, padx=10)
    Button(frame_buton, text="Vazgeç", command=Vazgec).pack(side=RIGHT, padx=10)

    onay_window.grab_set()
    onay_window.wait_window()


def yeniAracEkle(plaka_var, marka_var, model_var, ucret_var, dosya):
    try:
        with open(dosya, 'r', encoding='utf-8') as f:
            veri_listesi = json.load(f)
    except FileNotFoundError:
        print(f"Hata: '{dosya}' dosyası bulunamadı.")
        veri_listesi = []
    except json.JSONDecodeError:
        print(f"Hata: '{dosya}' dosyası geçerli bir JSON formatında değil.")
        veri_listesi = []

    plaka = plaka_var.get().strip()
    marka = marka_var.get().strip()
    model = model_var.get().strip()
    ucret = ucret_var.get().strip()

    if not plaka or not marka or not model or not ucret: #boş alan kontrolü
        messagebox.showerror("Hata", "Lütfen tüm alanları doldurunuz.")
        return

    yeni_arac = {
        "plaka": plaka,
        "marka": marka,
        "model": model,
        "durum": "Müsait", 
        "ucret": int(ucret) if ucret.isdigit() else ucret 
    }

    veri_listesi.insert(0, yeni_arac) #yeni araç listenin başına eklenir ki arayüzde görünür olsun

    try:
        with open(dosya, 'w', encoding='utf-8') as f:
            json.dump(veri_listesi, f, indent=4, ensure_ascii=False)
        
        messagebox.showinfo("Başarılı", f"{plaka} plakalı araç başarıyla eklendi.")
        
        plaka_var.set("")
        marka_var.set("")
        model_var.set("")
        ucret_var.set("")

        return True

    except Exception as e:
        messagebox.showerror("Hata", "Araç kaydedilemedi. Lütfen tekrar deneyin.")
        return False

def aracListele(frame_liste, dosya):
    for widget in frame_liste.winfo_children():
        widget.destroy()

    frame_liste.grid_columnconfigure(0, weight=0, minsize=50)
    frame_liste.grid_columnconfigure(1, weight=1, minsize=100)
    frame_liste.grid_columnconfigure(2, weight=1, minsize=100)
    frame_liste.grid_columnconfigure(3, weight=1, minsize=100)
    frame_liste.grid_columnconfigure(4, weight=1, minsize=100) 
    frame_liste.grid_columnconfigure(5, weight=1, minsize=100) 
    frame_liste.grid_columnconfigure(6, weight=10)              
    frame_liste.grid_columnconfigure(7, weight=0, minsize=40)
    frame_liste.grid_columnconfigure(8, weight=0, minsize=110)

    if isinstance(dosya, str):  #dosya yolu geldiyse
        try:
            with open(dosya, 'r', encoding='utf-8') as f:
                veri_listesi = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            veri_listesi = []
    else:  #direkt liste geldiyse
        veri_listesi = dosya

    baslangic_satiri = 11  #başlık satırımız 10 olduğu için

    try:
        frame_liste.configure(bg="#ffffff")
    except Exception:
        pass

    if not veri_listesi:
        Label(frame_liste, text="Listelenecek araç bulunmamaktadır.", bg="#ffffff", fg="#5f6878", font=("Segoe UI", 16)).grid(row=baslangic_satiri, column=1, columnspan=5, sticky="w", padx=10, pady=12)
        return
    
    #butonlarda ikon kullanabilmek için olan kısım
    current_dir = os.path.dirname(os.path.abspath(__file__))
    delete_path = os.path.join(current_dir, "delete.png")
    edit_path = os.path.join(current_dir, "edit.png")

    try:
        img_delete = Image.open(delete_path)
        icon = ImageTk.PhotoImage(img_delete)

        img_edit = Image.open(edit_path)
        icon_e = ImageTk.PhotoImage(img_edit)
    except Exception as e:
        print(f"Resim yüklenirken hata oluştu: {e}")
        icon = None
        icon_e = None
    
    #arayüz için renkler
    row_bg_even = "#fbfcff"
    row_bg_odd  = "#f7f8fc"
    txt_color   = "#2b2b2b"
    muted_color = "#5f6878"

    for index, arac in enumerate(veri_listesi):
        current_row = index
        durum = arac.get("durum", "N/A")
        plaka = arac.get("plaka", "N/A")

        #zebra satır arka plan ve satır görünümü için arayüz elemanları
        bg_row = row_bg_even if index % 2 == 0 else row_bg_odd
        row_bg_frame = Frame(frame_liste, bg=bg_row, height=40)
        row_bg_frame.grid(row=index, column=0, columnspan=9, sticky="nsew")
        Label(row_bg_frame, text="", bg=bg_row).pack()

        silBtn = Button(frame_liste, image=icon, command=lambda p=plaka: aracSil(p, frame_liste, dosya), bg=bg_row, width=18, height=18, borderwidth=0, highlightthickness=0, cursor="hand2")
        silBtn.image = icon
        silBtn.grid(row=current_row, column=0, padx=(16, 0), pady=6)

        Label(frame_liste, text=plaka, bg=bg_row, fg=txt_color, font=("Segoe UI", 13, "bold")).grid(row=current_row, column=1, sticky="w", padx=(20, 40), pady=6)
        Label(frame_liste, text=arac.get("marka", "N/A"), bg=bg_row, fg=txt_color, font=("Segoe UI", 13)).grid(row=current_row, column=2, sticky="w", padx=40, pady=6)
        Label(frame_liste, text=arac.get("model", "N/A"), bg=bg_row, fg=txt_color, font=("Segoe UI", 13)).grid(row=current_row, column=3, sticky="w", padx=40, pady=6)
        Label(frame_liste, text=durum, bg=bg_row, fg=muted_color, font=("Segoe UI", 13)).grid(row=current_row, column=4, sticky="w", padx=40, pady=6)
        ucret = arac.get("ucret", "N/A")
        Label(frame_liste, text=f"{ucret} TL", bg=bg_row, fg=txt_color, font=("Segoe UI", 13)).grid(row=current_row, column=5, sticky="w", padx=40, pady=6)

        #duruma göre buton ekleme
        if durum == "Kirada":
            BilgiBtn = Label(frame_liste, text="i", bg=bg_row, fg="#4b5563",font=("Courier New", 14, "bold"), cursor="hand2")
            BilgiBtn.grid(row=current_row, column=7, sticky="e", padx=(6, 0), pady=6)
            BilgiBtn.bind("<Button-1>", lambda e, p=plaka: infoGetir(p, frame_liste, dosya))
            Button(frame_liste, text="İade Et", command=lambda p=plaka: araciIadeEt(p, frame_liste, dosya), bg="#d3f7f1", fg="#0d5f59", font=("Segoe UI", 9), highlightthickness=0, borderwidth=0, width=8, height=1, cursor="hand2",activebackground="#c2efe8", activeforeground="#0d5f59").grid(row=current_row, column=8, sticky="e", padx=(0, 10), pady=6)

        elif durum == "Müsait":
            editBtn = Button(frame_liste, image=icon_e, command=lambda p=plaka: aracBilgisiDuzenle(p, frame_liste, dosya), bg=bg_row, width=20, height=20, borderwidth=0, highlightthickness=0, cursor="hand2")
            editBtn.image = icon_e
            editBtn.grid(row=current_row, column=7, sticky="e", padx=(6, 0), pady=6)
            Button(frame_liste, text="Kirala", command=lambda p=plaka: araciKirala(p, frame_liste, dosya), bg="#ffe3b5", fg="#7b3f00", font=("Segoe UI", 9), highlightthickness=0, borderwidth=0, width=8, height=1, cursor="hand2", activebackground="#ffd899", activeforeground="#7b3f00").grid(row=current_row, column=8, sticky="e", padx=10, pady=6)

        else:
            editBtn = Button(frame_liste, image=icon_e, command=lambda p=plaka: aracBilgisiDuzenle(p, frame_liste, dosya), bg=bg_row, width=20, height=20,borderwidth=0, highlightthickness=0, cursor="hand2")
            editBtn.image = icon_e
            editBtn.grid(row=current_row, column=7, sticky="e", padx=(6, 0), pady=6)

#üst menüden yapılan seçimlere göre filtreleme yapılır

def filtreKirala(marka, model, durum, ucret, frame_liste):
    try:
        with open("aracListesi.json", "r", encoding="utf-8") as f:
            veri_listesi = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        veri_listesi = []

    filtrelenmis_liste = []
    
    for arac in veri_listesi:
        if marka not in ("Tümü", "Marka") and arac["marka"] != marka:
            continue

        if model != "Tümü" and arac["model"] != model:
            continue

        if durum not in ("Tümü", "Kira Durumu") and arac["durum"] != durum:
            continue

        if ucret not in ("Tümü", "Günlük Ücret"):
            u = int(arac["ucret"])
            if ucret == "<500 TL" and u >= 500: continue
            if ucret == "501-1000 TL" and not (501 <= u <= 1000): continue
            if ucret == "1001-1500 TL" and not (1001 <= u <= 1500): continue
            if ucret == "1501-2000 TL" and not (1501 <= u <= 2000): continue
            if ucret == ">2001 TL" and u <= 2000: continue

        filtrelenmis_liste.append(arac)

    if siralama_kriteri and veri_listesi:
        if siralama_kriteri == "plaka":
            filtrelenmis_liste.sort(key=lambda x: x.get("plaka",""), reverse=(siralama_yonu == "desc"))
        elif siralama_kriteri == "marka":
            filtrelenmis_liste.sort(key=lambda x: x.get("marka",""), reverse=(siralama_yonu == "desc"))
        elif siralama_kriteri == "model":
            filtrelenmis_liste.sort(key=lambda x: x.get("model",""), reverse=(siralama_yonu == "desc"))
        elif siralama_kriteri == "durum":
            filtrelenmis_liste.sort(key=lambda x: x.get("durum",""), reverse=(siralama_yonu == "desc"))
        elif siralama_kriteri == "ucret":
            filtrelenmis_liste.sort(key=lambda x: int(x.get("ucret",0)) if str(x.get("ucret","0")).isdigit() else 0, reverse=(siralama_yonu == "desc"))

    aracListele(frame_liste, filtrelenmis_liste)


#arayüzdeki butonlara tıklanınca o elemana göre sıralama yapılır
def sirala_ve_goster(frame_liste, dosya, kriter):
    global siralama_kriteri, siralama_yonu
    
    if siralama_kriteri == kriter: #aynı kritere tıklanırsa yön değiştirilir
        siralama_yonu = "desc" if siralama_yonu == "asc" else "asc"
    else:
        siralama_kriteri = kriter
        siralama_yonu = "asc"
    
    if isinstance(dosya, str):
        try:
            with open(dosya,'r',encoding='utf-8') as f:
                veri_listesi = json.load(f)
        except:
            veri_listesi = []
    else:
        veri_listesi = dosya
    
    if siralama_kriteri and veri_listesi:
        if siralama_kriteri == "plaka":
            veri_listesi.sort(key=lambda x: x.get("plaka",""), reverse=(siralama_yonu == "desc"))
        elif siralama_kriteri == "marka":
            veri_listesi.sort(key=lambda x: x.get("marka",""), reverse=(siralama_yonu == "desc"))
        elif siralama_kriteri == "model":
            veri_listesi.sort(key=lambda x: x.get("model",""), reverse=(siralama_yonu == "desc"))
        elif siralama_kriteri == "durum":
            veri_listesi.sort(key=lambda x: x.get("durum",""), reverse=(siralama_yonu == "desc"))
        elif siralama_kriteri == "ucret":
            veri_listesi.sort(key=lambda x: int(x.get("ucret",0)) if str(x.get("ucret","0")).isdigit() else 0, reverse=(siralama_yonu == "desc"))

    temp_dosya = "temp_sirali.json" #geçici dosyaya sıralanmış liste kaydedilir çünkü aracListele fonksiyonu dosya yolundan okur
    try:
        with open(temp_dosya, 'w', encoding='utf-8') as f:
            json.dump(veri_listesi, f, indent=4, ensure_ascii=False)
        aracListele(frame_liste, temp_dosya)
        
    except Exception as e:
        print(f"Sıralama dosyası kaydedilirken hata: {e}")  

#sıralama butonlarındaki sıralama yönünü gösteren ok işaretlerini günceller
def guncelle_siralama_gostergesi(plaka_btn, marka_btn, model_btn, durum_btn, ucret_btn): 
    global siralama_kriteri,siralama_yonu

    for btn in [plaka_btn,marka_btn,model_btn,durum_btn,ucret_btn]:
        current_text = btn.cget("text")
        if " ↑" in current_text:
            btn.config(text=current_text.replace(" ↑", ""))
        elif " ↓" in current_text:
            btn.config(text=current_text.replace(" ↓", ""))

    if siralama_kriteri:
        ok_isareti = " ↑" if siralama_yonu == "asc" else " ↓"

        if siralama_kriteri == "plaka":
            current_text = plaka_btn.cget("text")
            plaka_btn.config(text=f"{current_text}{ok_isareti}")
        elif siralama_kriteri == "marka":
            current_text = marka_btn.cget("text")
            marka_btn.config(text=f"{current_text}{ok_isareti}")
        elif siralama_kriteri == "model":
            current_text = model_btn.cget("text")
            model_btn.config(text=f"{current_text}{ok_isareti}")
        elif siralama_kriteri == "durum":
            current_text = durum_btn.cget("text")
            durum_btn.config(text=f"{current_text}{ok_isareti}")
        elif siralama_kriteri == "ucret":
            current_text = ucret_btn.cget("text")
            ucret_btn.config(text=f"{current_text}{ok_isareti}")