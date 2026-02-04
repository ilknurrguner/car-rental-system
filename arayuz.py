from tkinter import *
import fonksiyonlar
import json

#kullanılacak renk paleti
PALETTE = {
    "bg_main": "#e9ecf5",
    "appbar": "#f3f5fb",          
    "toolbar": "#7e8fc8",         
    "panel": "#ede4ff",    
    "card": "#EDE7FF",     
    "card_border": "#c7cfdf",
    "chip_bg": "#d7efe9",
    "chip_fg": "#0e6a63",
    "accent": "#ffa928",
    "accent_hover": "#f09118",
    "secondary": "#e9e2ff",
    "secondary_hover": "#603ae4",
    "danger": "#ff5d5d",
    "line": "#cfd6e4", 
    "text": "#2b2b2b",
    "muted": "#5a6374",
    "link": "#5b57db",
    "cardsag" : "#d4ddfb"
}
#"#4d68c1" "#d4ddfb"
#kullanılacak fontlar
BASE_FONT = ("Segoe UI", 11) 
TITLE_FONT = ("Segoe UI Semibold", 16)
SUBTITLE_FONT = ("Segoe UI", 10)
SECTION_TITLE_FONT = ("Segoe UI Semibold", 14) # +1
LABEL_FONT = ("Segoe UI Semibold", 12)
BTN_FONT = ("Segoe UI Semibold", 11)
HEADER_BTN_FONT = ("Segoe UI", 10)
RIGHT_HEADER_FONT = ("Segoe UI Semibold", 14)
LIST_ROW_FONT = ("Segoe UI", 12)


window = Tk()
window.title("Araç Kiralama Uygulaması")
window.geometry("1500x900")
window.configure(bg=PALETTE["bg_main"])

#üst uygulama çubuğu
appbar = Frame(window, bg=PALETTE["appbar"], highlightthickness=1, highlightbackground=PALETTE["line"])
appbar.place(relx=0.02, rely=0.03, relwidth=0.96, relheight=0.06)

app_icon = Label(appbar, text="🚗", bg=PALETTE["appbar"], fg=PALETTE["text"], font=("Segoe UI Emoji", 16))
app_icon.pack(side=LEFT, padx=(12, 6))

app_title = Label(appbar, text="Araç Kiralama", bg=PALETTE["appbar"], fg=PALETTE["text"], font=TITLE_FONT)
app_title.pack(side=LEFT, padx=(4, 8))

app_subtitle = Label(appbar, text="Filtrele • Listele • Kirala", bg=PALETTE["appbar"], fg=PALETTE["muted"], font=SUBTITLE_FONT)
app_subtitle.pack(side=LEFT, padx=4)

#filtreleme üst paneli
frame_ust_container = Frame(window, bg=PALETTE["panel"], highlightthickness=0)
frame_ust_container.place(relx=0.02, rely=0.10, relwidth=0.96, relheight=0.12)
frame_ust = Frame(frame_ust_container, bg=PALETTE["toolbar"], highlightthickness=1,highlightbackground=PALETTE["line"])
frame_ust.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=1.0)
frame_sol_container = Frame(window, bg=PALETTE["panel"], highlightthickness=0)
frame_sol_container.place(relx=0.02, rely=0.22, relwidth=0.23, relheight=0.75)

#sol ve sağ kartlar
frame_sag_container = Frame(window, bg=PALETTE["panel"], highlightthickness=0)
frame_sag_container.place(relx=0.25, rely=0.22, relwidth=0.73, relheight=0.75)
frame_sol = Frame(frame_sol_container, bg=PALETTE["card"], highlightthickness=1,highlightbackground=PALETTE["line"])
frame_sol.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=1.0)
frame_sag = Frame(frame_sag_container, bg=PALETTE["cardsag"], highlightthickness=1,highlightbackground=PALETTE["line"])
frame_sag.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=1.0)
frame_sag.grid_rowconfigure(12, weight=1)
frame_sag.grid_columnconfigure(1, weight=1)

#sağ liste başlık şeridi
list_header = Frame(frame_sag, bg="#fff2dc", highlightthickness=0)
list_header.grid(row=9, column=1, columnspan=7, sticky="ew", padx=0, pady=(0, 0))
list_header_label = Label(list_header, text="📋 Araç Listesi", bg=list_header["bg"], fg=PALETTE["text"], font=SECTION_TITLE_FONT)
list_header_label.pack(side=LEFT, padx=12, pady=6)

#scrollable liste alanı
liste_container = Frame(frame_sag, bg=PALETTE["card"])
liste_container.grid(row=12, column=1, columnspan=7, sticky="nsew")
canvas = Canvas(liste_container, bg="white", highlightthickness=0)
canvas.pack(side=LEFT, fill=BOTH, expand=True)
scrollbar = Scrollbar(liste_container, orient=VERTICAL, command=canvas.yview)
scrollbar.pack(side=RIGHT, fill=Y)
canvas.configure(yscrollcommand=scrollbar.set)

#canvas içine gerçek frame
frame_liste = Frame(canvas, bg=PALETTE["card"])
canvas_frame_id = canvas.create_window((0, 0), window=frame_liste, anchor="nw")

def on_canvas_configure(event): #pencere genişlediğinde frame_liste de sağa doğru genişler
    canvas.itemconfig(canvas_frame_id, width=event.width)

def on_frame_configure(event): #içerik eklendikçe scroll bölgesi güncellenir
    canvas.configure(scrollregion=canvas.bbox("all"))

canvas.bind("<Configure>", on_canvas_configure)
frame_liste.bind("<Configure>", on_frame_configure)

def _on_mousewheel(event): #mouse wheel scroll
    if event.num == 4 or event.delta > 0:
        canvas.yview_scroll(-1, "units")
    elif event.num == 5 or event.delta < 0:
        canvas.yview_scroll(1, "units")

canvas.bind_all("<MouseWheel>", _on_mousewheel)   # Windows & Mac
canvas.bind_all("<Button-4>", _on_mousewheel)     # Linux scroll up
canvas.bind_all("<Button-5>", _on_mousewheel)     # Linux scroll down

#model listesi için
selected_marka = StringVar(value="Marka")
selected_model = StringVar(value="Tümü")

try:
    with open("modelListesi.json", 'r', encoding='utf-8') as f:
        modeller = json.load(f)
except FileNotFoundError:
    print("Hata: 'modelListesi.json' dosyası bulunamadı.")
    modeller = []

#hover efekt fonksiyonları
def hover_btn(widget, enter_bg, enter_fg, leave_bg, leave_fg):
    widget.bind("<Enter>", lambda e: widget.config(bg=enter_bg, fg=enter_fg))
    widget.bind("<Leave>", lambda e: widget.config(bg=leave_bg, fg=leave_fg))

def hover_btn_fg(widget, enter_fg, leave_fg):
    widget.bind("<Enter>", lambda e: widget.config(fg=enter_fg))
    widget.bind("<Leave>", lambda e: widget.config(fg=leave_fg))

def menu_hover(widget, enter_bg, leave_bg):
    widget.bind("<Enter>", lambda e: widget.config(bg=enter_bg))
    widget.bind("<Leave>", lambda e: widget.config(bg=leave_bg))

#menüden marka seçimi
def marka_Sec(marka):
    selected_marka.set(marka)
    model_menu.delete(0, "end")
    model_menu.add_command(label="Tümü", command=lambda: model_Sec("Tümü")) #model menüsünü seçilen markaya göre güncelleme
    selected_model.set("Tümü")
    if marka == "Tümü":
        return
    for m in modeller[marka]:
        model_menu.add_command(label=m, command=lambda x=m: model_Sec(x))

def model_Sec(model):
    selected_model.set(model)

#menubutton ve menü görünüm ayarları
menu_btn_style = {"relief": "flat", "bg": PALETTE["toolbar"], "activebackground": PALETTE["toolbar"], "fg": PALETTE["text"], "font": HEADER_BTN_FONT, "bd": 0, "width": 16, "cursor": "hand2", "highlightthickness": 0, "padx": 6, "pady": 6}
menu_style = {"tearoff": 0, "bg": "#ffffff", "fg": PALETTE["text"], "activebackground": "#e6ebff", "activeforeground": PALETTE["text"], "bd": 0}

marka_menuBtn = Menubutton(frame_ust, textvariable=selected_marka, **menu_btn_style)
marka_menu = Menu(marka_menuBtn, **menu_style)
marka_menu.add_command(label="Tümü", command=lambda: marka_Sec("Tümü"))
for marka in modeller:
    marka_menu.add_command(label=marka, command=lambda m=marka: marka_Sec(m))
marka_menuBtn["menu"] = marka_menu
marka_menuBtn.pack(side=LEFT, padx=20, pady=8)
menu_hover(marka_menuBtn, "#ccd7fb", PALETTE["toolbar"])

model_menuBtn = Menubutton(frame_ust, textvariable=selected_model, **menu_btn_style)
model_menu = Menu(model_menuBtn, **menu_style)
model_menu.add_command(label="Tümü", command=lambda: model_Sec("Tümü"))
model_menuBtn["menu"] = model_menu
model_menuBtn.pack(side=LEFT, padx=20, pady=8)
menu_hover(model_menuBtn, "#ccd7fb", PALETTE["toolbar"])

def menu_guncelle(): #yeni marka eklendiğinde menüyü güncelle
    global marka_menu
    marka_menu.delete(0, 'end')
    marka_menu.add_command(label="Tümü", command=lambda: marka_Sec("Tümü"))
    for marka in sorted(modeller.keys()):
        marka_menu.add_command(label=marka, command=lambda m=marka: marka_Sec(m))
    marka_Sec("Tümü")

def kayitButonu(): #yeni araç ekleme kısmının kaydet butonu fonksiyonu
    global modeller
    marka = marka_var.get().strip()
    model = model_var.get().strip()

    kayit_basarili = fonksiyonlar.yeniAracEkle(plaka_var, marka_var, model_var, ucret_var, "aracListesi.json")
    if kayit_basarili:
        fonksiyonlar.aracListele(frame_liste, "aracListesi.json")
        if marka not in modeller.keys(): #yeni marka ve model eklenmişse modelListesi.json dosyasına kaydet
            modeller[marka] = [model]
        else:
            if model not in modeller[marka]:
                modeller[marka].append(model)
        try:
            with open("modelListesi.json", 'w', encoding='utf-8') as f:
                json.dump(modeller, f, indent=4, ensure_ascii=False)
        except Exception:
            return
        menu_guncelle() #kayıt işleminden sonra menüyü güncelle

durum_menuBtn = Menubutton(frame_ust, text="Kira Durumu", **menu_btn_style)
durum_menu = Menu(durum_menuBtn, **menu_style)
durum_menu.add_command(label="Bakımda", command=lambda: durum_menuBtn.config(text="Bakımda"))
durum_menu.add_command(label="Kirada", command=lambda: durum_menuBtn.config(text="Kirada"))
durum_menu.add_command(label="Müsait", command=lambda: durum_menuBtn.config(text="Müsait"))
durum_menu.add_command(label="Tümü", command=lambda: durum_menuBtn.config(text="Tümü"))
durum_menuBtn["menu"] = durum_menu
durum_menuBtn.pack(side=LEFT, padx=20, pady=8)
menu_hover(durum_menuBtn, "#ccd7fb", PALETTE["toolbar"])

ucret_menuBtn = Menubutton(frame_ust, text="Günlük Ücret", **menu_btn_style)
ucret_menu = Menu(ucret_menuBtn, **menu_style)
ucret_menu.add_command(label="<500 TL", command=lambda: ucret_menuBtn.config(text="<500 TL"))
ucret_menu.add_command(label="501-1000 TL", command=lambda: ucret_menuBtn.config(text="501-1000 TL"))
ucret_menu.add_command(label="1001-1500 TL", command=lambda: ucret_menuBtn.config(text="1001-1500 TL"))
ucret_menu.add_command(label="1501-2000 TL", command=lambda: ucret_menuBtn.config(text="1501-2000 TL"))
ucret_menu.add_command(label=">2001 TL", command=lambda: ucret_menuBtn.config(text=">2001 TL"))
ucret_menu.add_command(label="Tümü", command=lambda: ucret_menuBtn.config(text="Tümü"))
ucret_menuBtn["menu"] = ucret_menu
ucret_menuBtn.pack(side=LEFT, padx=20, pady=8)
menu_hover(ucret_menuBtn, "#ccd7fb", PALETTE["toolbar"])

list_Btn = Button(frame_ust,text="Listele",height=1, width=10,font=BTN_FONT,fg=PALETTE["text"],bg=PALETTE["accent"],activebackground=PALETTE["accent_hover"],activeforeground=PALETTE["text"],highlightthickness=0,bd=0, cursor="hand2",command=lambda: fonksiyonlar.filtreKirala(selected_marka.get(),selected_model.get(),durum_menuBtn.cget("text"),ucret_menuBtn.cget("text"), frame_liste))
list_Btn.pack(side=RIGHT, padx=20, pady=8)
hover_btn(list_Btn, PALETTE["accent_hover"], PALETTE["text"], PALETTE["accent"], PALETTE["text"])

def filtreTemizle_custom(): #filtre seçimini varsayılana döndürme
    selected_marka.set("Tümü")
    selected_model.set("Tümü")
    durum_menuBtn.config(text="Tümü")
    ucret_menuBtn.config(text="Tümü")
    fonksiyonlar.siralama_kriteri = None
    fonksiyonlar.siralama_yonu = "asc"
    PlakaBtn.config(text="Plaka")
    MarkaBtn.config(text="Marka")
    ModelBtn.config(text="Model")
    KiraBtn.config(text="Kira Durumu")
    UcretBtn.config(text="Günlük Ücret")
    fonksiyonlar.aracListele(frame_liste, "aracListesi.json")

temizleBtn = Label(frame_ust,text="🧹 Temizle",bg=PALETTE["toolbar"],fg=PALETTE["secondary"],font=BTN_FONT,cursor="hand2")
temizleBtn.pack(side=RIGHT, padx=15, pady=8)
temizleBtn.bind("<Button-1>", lambda e: filtreTemizle_custom())
temizleBtn.bind("<Enter>", lambda e: header_hover_in(temizleBtn))
temizleBtn.bind("<Leave>", lambda e: header_hover_out(temizleBtn))
hover_btn_fg(temizleBtn, PALETTE["secondary_hover"], PALETTE["secondary"])

#sol araç ekleme başlık şeridi
section_head = Frame(frame_sol, bg="#fff2dc", highlightthickness=0)
section_head.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0, pady=(0, 0))
head_label = Label(section_head, text="➕ Araç Ekle", bg=section_head["bg"], fg=PALETTE["text"], font=SECTION_TITLE_FONT)
head_label.pack(side=LEFT, padx=12, pady=6)

frame_sol.grid_columnconfigure(0, weight=1)
frame_sol.grid_columnconfigure(1, weight=1)

#form alanları
plaka_var = StringVar()
marka_var = StringVar()
model_var = StringVar()
ucret_var = StringVar()

def make_label(parent, text): #label oluşturma arayüz elemanları
    return Label(parent, text=text, bg=PALETTE["card"], fg=PALETTE["text"], font=LABEL_FONT)

def make_entry(parent, textvariable): #entry oluşturma arayüz elemanları
    e = Entry(parent, textvariable=textvariable,width=18,font=BASE_FONT,fg=PALETTE["text"],bg="#ffffff",relief="flat",insertbackground=PALETTE["text"],highlightthickness=1,highlightbackground=PALETTE["line"],highlightcolor=PALETTE["link"])
    return e

make_label(frame_sol, "Plaka:").grid(row=1, column=0, sticky="w", padx=12, pady=10)
plaka_entry = make_entry(frame_sol, plaka_var)
plaka_entry.grid(row=1, column=1, pady=10, padx=12, sticky="ew")

make_label(frame_sol, "Marka:").grid(row=2, column=0, sticky="w", padx=12, pady=10)
marka_entry = make_entry(frame_sol, marka_var)
marka_entry.grid(row=2, column=1, pady=10, padx=12, sticky="ew")

make_label(frame_sol, "Model:").grid(row=3, column=0, sticky="w", padx=12, pady=10)
model_entry = make_entry(frame_sol, model_var)
model_entry.grid(row=3, column=1, pady=10, padx=12, sticky="ew")

make_label(frame_sol, "Günlük Ücret:").grid(row=4, column=0, sticky="w", padx=12, pady=10)
ucret_entry = make_entry(frame_sol, ucret_var)
ucret_entry.grid(row=4, column=1, pady=10, padx=12, sticky="ew")

kaydetBtn = Button(frame_sol,text="Kaydet",command=lambda: kayitButonu(),bg=PALETTE["secondary"],fg=PALETTE["text"],font=BTN_FONT,height=1, width=12,highlightthickness=0,bd=0,activebackground=PALETTE["secondary_hover"],activeforeground=PALETTE["text"],cursor="hand2")
kaydetBtn.grid(row=5, column=1, sticky="e", padx=12, pady=10)
hover_btn(kaydetBtn, PALETTE["secondary_hover"], PALETTE["text"], PALETTE["secondary"], PALETTE["text"])

row_baslik = 10 #başlık satırının oynamaması için sabit değişken

def baslik_tikla(kriter, btn):
    fonksiyonlar.sirala_ve_goster(frame_liste, "aracListesi.json", kriter)
    fonksiyonlar.guncelle_siralama_gostergesi(PlakaBtn, MarkaBtn, ModelBtn, KiraBtn, UcretBtn)

#başlık stili
header_label_style = {"bg": PALETTE["card"], "fg": PALETTE["text"], "font": RIGHT_HEADER_FONT, "cursor": "hand2"}

def header_hover_in(w):
    w.config(fg=PALETTE["link"])
def header_hover_out(w):
    w.config(fg=PALETTE["text"])

#başlıklar buton gibi davranıyor (sıralama için)
PlakaBtn = Label(frame_sag, text="Plaka", bg=PALETTE["cardsag"])
PlakaBtn.grid(row=row_baslik, column=1, padx=70, pady=12)
PlakaBtn.bind("<Button-1>", lambda e: baslik_tikla("plaka", PlakaBtn))
PlakaBtn.bind("<Enter>", lambda e: header_hover_in(PlakaBtn))
PlakaBtn.bind("<Leave>", lambda e: header_hover_out(PlakaBtn))

MarkaBtn = Label(frame_sag, text="Marka", bg=PALETTE["cardsag"])
MarkaBtn.grid(row=row_baslik, column=2, padx=(55,70), pady=12)
MarkaBtn.bind("<Button-1>", lambda e: baslik_tikla("marka", MarkaBtn))
MarkaBtn.bind("<Enter>", lambda e: header_hover_in(MarkaBtn))
MarkaBtn.bind("<Leave>", lambda e: header_hover_out(MarkaBtn))

ModelBtn = Label(frame_sag, text="Model", bg=PALETTE["cardsag"])
ModelBtn.grid(row=row_baslik, column=3, padx=55, pady=12)
ModelBtn.bind("<Button-1>", lambda e: baslik_tikla("model", ModelBtn))
ModelBtn.bind("<Enter>", lambda e: header_hover_in(ModelBtn))
ModelBtn.bind("<Leave>", lambda e: header_hover_out(ModelBtn))

KiraBtn = Label(frame_sag, text="Kira Durumu", bg=PALETTE["cardsag"])
KiraBtn.grid(row=row_baslik, column=4, padx=(45, 30), pady=12)
KiraBtn.bind("<Button-1>", lambda e: baslik_tikla("durum", KiraBtn))
KiraBtn.bind("<Enter>", lambda e: header_hover_in(KiraBtn))
KiraBtn.bind("<Leave>", lambda e: header_hover_out(KiraBtn))

UcretBtn = Label(frame_sag, text="Günlük Ücret", bg=PALETTE["cardsag"])
UcretBtn.grid(row=row_baslik, column=5, padx=(30, 0), pady=12)
UcretBtn.bind("<Button-1>", lambda e: baslik_tikla("ucret", UcretBtn))
UcretBtn.bind("<Enter>", lambda e: header_hover_in(UcretBtn))
UcretBtn.bind("<Leave>", lambda e: header_hover_out(UcretBtn))


frame_sag.grid_columnconfigure(1, weight=0)
frame_sag.grid_columnconfigure(2, weight=0)
frame_sag.grid_columnconfigure(3, weight=0)
frame_sag.grid_columnconfigure(4, weight=0)
frame_sag.grid_columnconfigure(5, weight=0)
frame_sag.grid_columnconfigure(6, weight=1)
frame_sag.grid_rowconfigure(12, weight=1)

#başlıkları ayıran çizgi
cizgi = Frame(frame_sag, height=1, bg=PALETTE["line"])
cizgi.grid(row=11, column=1, columnspan=7, sticky="ew", padx=0, pady=(0, 0))

#başlangıçta tüm araçları listele
fonksiyonlar.aracListele(frame_liste, "aracListesi.json")

window.mainloop()