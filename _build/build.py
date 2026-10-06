#!/usr/bin/env python3
"""Generates the vXv Barber's static site into ../docs. Edit this file, not the HTML."""
import json, os, html
from urllib.parse import quote
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs")
IMG = os.path.join(OUT, "assets", "img")
BASE = "https://welcometothenextlevel.github.io/vxvbarbers/"
V = "10"  # cache-buster for css/js

WA_NUM = "41767578636"
WA = "https://wa.me/" + WA_NUM
def wa(text):
    return WA + "?text=" + quote(text)

TIKTOK = "https://www.tiktok.com/@vxvbarbers"
IG = "https://www.instagram.com/vxvbarbers/"
IG_VEVEY = "https://www.instagram.com/vxvvevey/"

# ------------------------------------------------------------------ data
WEEK_STD = [None, ["10:00", "19:00"], ["10:00", "19:00"], ["10:00", "19:00"], ["10:00", "19:00"], ["10:00", "19:00"], ["08:00", "18:00"]]
WEEK_VEV = [None, ["10:00", "19:00"], ["10:00", "19:00"], ["10:00", "19:00"], ["10:00", "19:00"], ["10:00", "19:00"], ["10:00", "19:00"]]
SALONS = [
    dict(key="crissier", name="Crissier", n="01", street="Rue du Jura 11", city="1023 Crissier", locality="Crissier", zip="1023",
         phone="076 757 86 36", tel="+41767578636", hours=WEEK_STD, rating="4,6", count=224,
         pid="ChIJTa0I34cxjEcRKLLp_NP-2lk", cid="6474767600733237800", lat=46.5394724, lng=6.5784301,
         img="crissier-salle", imgs=["neon-close", "lounge"], video="assets/video/hero.mp4",
         text="L’adresse historique, entièrement refaite : plafond lumineux en nid d’abeille, sol en marbre, mur végétal et nos néons. Plusieurs fauteuils en parallèle pour que l’attente reste courte."),
    dict(key="blecherette", name="Blécherette", n="02", street="Route des Plaines-du-Loup 55", city="1018 Lausanne", locality="Lausanne", zip="1018",
         phone="076 669 36 00", tel="+41766693600", hours=WEEK_STD, rating="5,0", count=53,
         pid="ChIJrwco4I8xjEcRTlv9IjlqdOw", cid="17038360083882138446", lat=46.5408039, lng=6.620091,
         img="blecherette", imgs=["blecherette-salle", "blecherette-entree"], video=None,
         text="La nouvelle adresse, dans le quartier des Plaines-du-Loup. Marbre noir veiné d’or, verdure suspendue sous un plafond lumineux — et déjà 5,0 sur Google."),
    dict(key="vevey", name="Vevey", n="03", street="Avenue Général-Guisan 52", city="1800 Vevey", locality="Vevey", zip="1800",
         phone="078 973 14 14", tel="+41789731414", hours=WEEK_VEV, rating="5,0", count=5,
         pid="ChIJqzCxVt2djkcR466f8EjNs-E", cid="16263568392523329251", lat=46.4663417, lng=6.8373042,
         img="vevey-fauteuil", imgs=["vevey", "vevey-tondeuse"], video=None,
         text="Le salon de la Riviera. Même équipe, mêmes gestes, mêmes finitions — et ouvert jusqu’à 19h le samedi."),
]
TOTAL_REVIEWS = sum(s["count"] for s in SALONS)
DAYS = ["Dimanche", "Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"]

def gmaps(s):
    return "https://www.google.com/maps/search/?api=1&query=" + quote("vXv Barber's " + s["street"] + " " + s["city"]) + "&query_place_id=" + s["pid"]
def greviews(s):
    return "https://search.google.com/local/reviews?placeid=" + s["pid"]
def gwrite(s):
    return "https://search.google.com/local/writereview?placeid=" + s["pid"]
def gembed(s):
    return "https://maps.google.com/maps?q=" + quote(s["street"] + ", " + s["city"]) + "&z=16&output=embed"
def hsum(s):
    h = s["hours"]
    f = lambda t: t.replace(":00", "h").lstrip("0")
    if h[6] == h[1]:
        return "Lun – Sam · %s – %s" % (f(h[1][0]), f(h[1][1]))
    return "Lun – Ven · %s – %s<br>Sam · %s – %s" % (f(h[1][0]), f(h[1][1]), f(h[6][0]), f(h[6][1]))

PRICES = [
    ("Coupe", "25", "Ciseaux ou tondeuse, dégradé, contours nets et coiffage.", "coupe-skin"),
    ("Coupe enfant", "22", "Même soin, même précision — pour les plus jeunes.", "coupe-frange"),
    ("Barbe", "15", "Taille, dégradé de barbe et contours à la lame.", "coupe-barbe"),
    ("Point noir", "7", "Soin express du visage contre les points noirs.", "portrait-nb"),
]

# Google reviews, copied verbatim from the three Google Business profiles (5-star only)
REVIEWS = [
    ("Valentin Faessler", "crissier", "Je n'ai jamais deçu en 2 ans ! Les prix sont extrement compétitifs et tout les barbiers sont a la pointe de leur métier. L'ambiance est très accueillante, l'attente est rarement longue. Bref, vous trouverez difficilement un meilleur salon en region Lausannoise. Je recommande à 100% !"),
    ("Nas K", "blecherette", "Bel accueil et service au top. 💯👍 Équipe professionnelle. 👏 De plus, un prix compétitif. 💰"),
    ("Erkin Ozcan", "crissier", "Super expérience chez VXV Barber ! L’équipe est accueillante, professionnelle et vraiment à l’écoute. La coupe est impeccable, le dégradé est net et précis. On sent qu’ils prennent leur temps pour bien faire les choses. Je recommande à 100 %, c’est clairement le meilleurs barbiers du coin !"),
    ("Bilel Maghraoui", "vevey", "Les coiffeurs sont incroyablement qualifié je recommande une expérience unique et rapide !!!🙏🏽🙏🏽"),
    ("Nolf Nolf", "crissier", "Franchement, rien à redire. Très bon accueil, barber sympa et à l’écoute. La coupe et la barbe sont réalisées avec beaucoup de soin et de précision. On voit qu’ils aiment leur métier. Je suis ressorti très satisfait et je reviendrai avec plaisir. Je recommande les yeux fermés !"),
    ("Club pro", "blecherette", "Super expérience dans ce salon ! Très bon accueil, équipe professionnelle et à l’écoute. Je suis vraiment satisfait du résultat, on sent qu’ils prennent le temps de bien faire. Je recommande sans hésiter"),
    ("Tobias", "crissier", "Les gens qui y travaillent sont très gentils et poli , l'accueil est parfait, le salon est Magnifique avec beaucoup d'espace. Les demandes sont toujours respectées. Vous repartez avec une belle coupe garantie. Foncez."),
    ("Javier Moreno", "blecherette", "Je suis entièrement satisfait de mon expérience chez VXV Barber à la Blécherette. Dès mon arrivée, j’ai été très bien accueilli par une équipe chaleureuse et professionnelle."),
    ("Luca Alls", "crissier", "Très bonne expérience avec Moha Personne sérieuse, professionnelle et à l’écoute. Le travail a été fait avec soin et tout s’est déroulé parfaitement du début à la fin. Je suis très satisfait et je recommande sans hésitation."),
    ("Anwar Lutangu", "blecherette", "Le traitement sur place était incroyable et le salon est très propre. Et le service est de grande qualité je recommande fortement!"),
    ("Jack L'horaire", "vevey", "Coiffeur très fort, merci pour la prestation"),
    ("Izi bos", "blecherette", "J’y suis allé c’est un très beau salon classe, propre. J’ai pas eu à attendre longtemps et la coupe m’a plu le barber était sympa à l’écoute et pro. Allez y en toute confiance"),
    ("Ruben Tv", "crissier", "Ils se préoccupent du bien-être des client ils sont très accueillant et leur coupe sont toujours bien réussi 🔥🔥"),
    ("Nurdin Pezic", "blecherette", "très bon coiffeur très propre il sait ce qu’il fait n’hésitez pas première fois que j’y vais est vraiment pas déçu foncez !"),
    ("Fikri Omb", "crissier", "Bonjour, pour ma part qui as tester beaucoup de salon de coiffure.. celle ci c’est la meuilleur ! Très professionnel et a l’écoute de la demande du client :) !"),
    ("Matteo Gaudiuso", "blecherette", "Des coiffeurs compétent, professionnel et très à l’aise à la discussion avec le client"),
    ("Ylian Sfar", "crissier", "Coiffeur extrêmement gentil et soigneux, service au top. Je recommande !!!"),
    ("Elsin Memedov", "blecherette", "Super accueil, coupe au propre parfait comme ont aiment 😉"),
    ("Antonio Sousa", "crissier", "Mon fils à voulut aller chez eux car ses copains en parlait. Je n'ai qu'un mot a dire: EXCELLENCE"),
    ("jean-claude pellissier", "blecherette", "Endroit, convivial, très sympathique et au service de sa clientèle"),
    ("Ilias Djalo", "crissier", "10/10 rien à redire, surtout le personne à l'accueil qui était grave sympa"),
    ("Jefferson Castillo", "blecherette", "Bon coiffeur et bonne ambiance"),
    ("Rayan Parente", "crissier", "Incroyable pas cher est très bon coiffeur"),
]
AV_COLORS = ["#5e35b1", "#00897b", "#e64a19", "#3949ab", "#c2185b", "#00796b", "#6d4c41", "#1e88e5", "#7cb342", "#f4511e", "#546e7a", "#8e24aa"]

GALLERY = [  # (image, caption, tags)
    ("coupe-coeur", "Motif cœur", "coupes"), ("mur-vegetal", "Crissier — le mur végétal", "salons"),
    ("coupe-texture", "Texture & taper", "coupes"), ("coupe-skin", "Skin fade", "coupes"),
    ("crissier-salle", "Crissier", "salons"), ("coupe-twists", "Twists", "coupes"),
    ("coupe-raie", "Raie rasée", "coupes"), ("portrait-nb", "Le résultat", "coupes"),
    ("blecherette", "Blécherette", "salons"), ("coupe-barbe", "Barbe & contours", "coupes"),
    ("coupe-blond", "Blond & motif", "coupes"), ("coupe-volume", "Volume & dégradé", "coupes"),
    ("etagere-or", "Crissier — les produits", "salons"), ("blecherette-salle", "Blécherette", "salons"),
    ("coupe-boucles", "Boucles & barbe", "coupes"), ("coupe-design", "Undercut", "coupes"),
    ("vevey", "Vevey", "salons coupes"), ("coupe-nuque", "La nuque", "coupes"), ("coupe-waves", "Waves", "coupes"),
    ("lounge", "Crissier — l’attente", "salons"), ("coupe-motif", "Motif rasé", "coupes"),
    ("coupe-chignon", "Man bun & barbe", "coupes"), ("comptoir", "Crissier — le comptoir", "salons"),
    ("vevey-fauteuil", "Vevey", "salons"), ("coupe-degrade", "Mid fade", "coupes"), ("coupe-afro", "Afro & taper", "coupes"),
    ("miroir", "Dans le miroir", "coupes"), ("coupe-frange", "Frange & dégradé", "coupes"), ("neon-close", "Néons vXv", "salons"),
]
HSCROLL = [("coupe-coeur", "Motif cœur"), ("coupe-texture", "Texture & taper"), ("coupe-skin", "Skin fade"),
           ("coupe-twists", "Twists"), ("coupe-raie", "Raie rasée"), ("coupe-barbe", "Barbe & contours"),
           ("coupe-blond", "Blond & motif"), ("coupe-boucles", "Boucles & barbe"), ("portrait-nb", "Le résultat"),
           ("coupe-volume", "Volume & dégradé")]

# ------------------------------------------------------------------ icons
I = dict(
    wa='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M17.47 14.38c-.3-.15-1.76-.87-2.03-.97-.27-.1-.47-.15-.67.15-.2.3-.77.97-.94 1.17-.17.2-.35.22-.64.07-.3-.15-1.26-.46-2.4-1.48-.89-.79-1.49-1.77-1.66-2.07-.17-.3-.02-.46.13-.6.13-.13.3-.35.45-.52.15-.17.2-.3.3-.5.1-.2.05-.37-.03-.52-.07-.15-.67-1.62-.92-2.22-.24-.58-.49-.5-.67-.51h-.57c-.2 0-.52.07-.8.37-.27.3-1.04 1.02-1.04 2.48s1.07 2.88 1.21 3.08c.15.2 2.1 3.2 5.08 4.49.71.31 1.26.49 1.69.63.71.22 1.36.19 1.87.12.57-.09 1.76-.72 2.01-1.41.25-.7.25-1.29.17-1.41-.07-.13-.27-.2-.57-.35zM12.05 21.5h-.01a9.4 9.4 0 0 1-4.8-1.31l-.34-.2-3.56.93.95-3.47-.22-.36a9.42 9.42 0 0 1-1.44-5.02c0-5.2 4.24-9.44 9.45-9.44a9.38 9.38 0 0 1 6.68 2.77 9.38 9.38 0 0 1 2.76 6.68c0 5.21-4.24 9.44-9.44 9.44zm8.04-17.48A11.3 11.3 0 0 0 12.05.7C5.79.7.69 5.8.69 12.07c0 2 .52 3.96 1.52 5.68L.6 23.6l6-1.57a11.33 11.33 0 0 0 5.44 1.38h.01c6.26 0 11.36-5.1 11.36-11.36 0-3.04-1.18-5.89-3.32-8.03z"/></svg>',
    ig='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2.2c3.2 0 3.58 0 4.85.07 3.25.15 4.77 1.69 4.92 4.92.06 1.27.07 1.65.07 4.85s-.01 3.58-.07 4.85c-.15 3.23-1.66 4.77-4.92 4.92-1.27.06-1.65.07-4.85.07s-3.58-.01-4.85-.07c-3.26-.15-4.77-1.7-4.92-4.92C2.17 15.58 2.16 15.2 2.16 12s.01-3.58.07-4.85C2.38 3.92 3.9 2.38 7.15 2.23 8.42 2.17 8.8 2.16 12 2.16zM12 0C8.74 0 8.33.01 7.05.07 2.7.27.27 2.69.07 7.05.01 8.33 0 8.74 0 12s.01 3.67.07 4.95c.2 4.36 2.62 6.78 6.98 6.98C8.33 23.99 8.74 24 12 24s3.67-.01 4.95-.07c4.35-.2 6.78-2.62 6.98-6.98.06-1.28.07-1.69.07-4.95s-.01-3.67-.07-4.95c-.2-4.35-2.62-6.78-6.98-6.98C15.67.01 15.26 0 12 0zm0 5.84a6.16 6.16 0 1 0 0 12.32 6.16 6.16 0 0 0 0-12.32zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.4-11.85a1.44 1.44 0 1 0 0 2.88 1.44 1.44 0 0 0 0-2.88z"/></svg>',
    tt='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-5.2 1.74 2.89 2.89 0 0 1 2.31-4.64c.3 0 .59.04.88.13V9.4a6.84 6.84 0 0 0-1-.05A6.33 6.33 0 0 0 5 20.1a6.34 6.34 0 0 0 10.86-4.43v-7a8.16 8.16 0 0 0 4.77 1.52v-3.4a4.85 4.85 0 0 1-1-.1z"/></svg>',
    g='<svg viewBox="0 0 48 48" aria-hidden="true"><path fill="#FFC107" d="M43.6 20.1H42V20H24v8h11.3C33.7 32.7 29.2 36 24 36c-6.6 0-12-5.4-12-12s5.4-12 12-12c3.1 0 5.8 1.2 7.9 3l5.7-5.7C34 6.1 29.3 4 24 4 12.9 4 4 12.9 4 24s8.9 20 20 20 20-8.9 20-20c0-1.3-.1-2.6-.4-3.9z"/><path fill="#FF3D00" d="m6.3 14.7 6.6 4.8C14.7 15.1 19 12 24 12c3.1 0 5.8 1.2 7.9 3l5.7-5.7C34 6.1 29.3 4 24 4 16.3 4 9.7 8.3 6.3 14.7z"/><path fill="#4CAF50" d="M24 44c5.2 0 9.9-2 13.4-5.2l-6.2-5.2C29.2 35.1 26.7 36 24 36c-5.2 0-9.6-3.3-11.3-7.9l-6.5 5C9.5 39.6 16.2 44 24 44z"/><path fill="#1976D2" d="M43.6 20.1H42V20H24v8h11.3c-.8 2.2-2.2 4.2-4.1 5.6l6.2 5.2C37 39.2 44 34 44 24c0-1.3-.1-2.6-.4-3.9z"/></svg>',
    arr='<svg class="arr" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M4 12h15M13 6l6 6-6 6"/></svg>',
    ne='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M7 17 17 7M8 7h9v9"/></svg>',
    pin='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/></svg>',
    tel='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M5 3h4l2 5-2.5 1.5a11 11 0 0 0 6 6L16 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 5a2 2 0 0 1 2-2z"/></svg>',
    star='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="m12 3 2.8 5.7 6.2.9-4.5 4.4 1.1 6.2L12 17.3 6.4 20.2l1.1-6.2L3 9.6l6.2-.9z"/></svg>',
    x='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg>',
    prev='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg>',
    next='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M9 5l7 7-7 7"/></svg>',
)
I["arr2"] = I["ne"].replace("<svg ", '<svg class="arr2" ')
MARK_POLY = '<polygon points="2,34 12.5,34 17,50 21.5,34 32,34 21.5,68 12.5,68"/><polygon points="38,2 52,2 82,68 68,68"/><polygon points="68,2 82,2 52,68 38,68"/><polygon points="88,34 98.5,34 103,50 107.5,34 118,34 107.5,68 98.5,68"/>'
MARK = '<svg viewBox="0 0 120 70" aria-hidden="true">' + MARK_POLY + '</svg>'
GWORD = '<span style="font-weight:600;letter-spacing:-.01em"><span style="color:#4285F4">G</span><span style="color:#EA4335">o</span><span style="color:#FBBC05">o</span><span style="color:#4285F4">g</span><span style="color:#34A853">l</span><span style="color:#EA4335">e</span></span>'

def esc(s):
    return html.escape(s, quote=True)

_dims = {}
def dims(name):
    if name not in _dims:
        with Image.open(os.path.join(IMG, name + ".jpg")) as im:
            _dims[name] = im.size
    return _dims[name]

def pic(name, alt, lazy=True):
    w, h = dims(name)
    return ('<picture><source type="image/webp" srcset="assets/img/%s.webp"><img src="assets/img/%s.jpg" alt="%s" width="%d" height="%d"%s decoding="async"></picture>'
            % (name, name, esc(alt), w, h, ' loading="lazy"' if lazy else ""))

def H(txt, tag="h2", cls="d d-l", attrs=""):
    """Heading split into masked lines. '|' breaks a line, a leading '~' greys that line."""
    txt = txt.replace(" ?", " ?").replace(" !", " !")
    out = []
    for ln in txt.split("|"):
        soft = ln.startswith("~")
        out.append('<span class="line"><span%s>%s</span></span>' % (' class="soft"' if soft else "", ln.lstrip("~")))
    return '<%s class="%s" data-lines%s>%s</%s>' % (tag, cls, attrs, "".join(out), tag)

def socials():
    return ('<div class="socials"><a class="soc ig" href="%s" target="_blank" rel="noopener" aria-label="Instagram @vxvbarbers">%s</a>'
            '<a class="soc tt" href="%s" target="_blank" rel="noopener" aria-label="TikTok @vxvbarbers">%s</a>'
            '<a class="soc wa" href="%s" target="_blank" rel="noopener" aria-label="WhatsApp">%s</a></div>') % (IG, I["ig"], TIKTOK, I["tt"], WA, I["wa"])

def stars():
    return '<span class="stars" aria-label="5 étoiles sur 5">★★★★★</span>'

# ------------------------------------------------------------------ chrome
NAV = [("salons", "Salons"), ("prestations", "Prestations"), ("galerie", "Galerie"), ("avis", "Avis")]

def head(slug, title, desc, extra=""):
    url = BASE + ("" if slug == "index" else slug)
    return """<!doctype html>
<html lang="fr-CH">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>%(title)s</title>
<meta name="description" content="%(desc)s">
<link rel="canonical" href="%(url)s">
<meta name="theme-color" content="#ffffff">
<meta property="og:type" content="website">
<meta property="og:locale" content="fr_CH">
<meta property="og:site_name" content="vXv Barber's">
<meta property="og:title" content="%(title)s">
<meta property="og:description" content="%(desc)s">
<meta property="og:url" content="%(url)s">
<meta property="og:image" content="%(base)sassets/img/og.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
<link rel="icon" href="assets/img/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="assets/img/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@700;800;900&family=Instrument+Sans:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="assets/css/site.css?v=%(v)s">
<script>document.documentElement.classList.add("js");(function(p){if(p.slice(-5)===".html"){history.replaceState(null,"",p.slice(-11)==="/index.html"?p.slice(0,-10):p.slice(0,-5)+location.search+location.hash)}})(location.pathname)</script>
%(extra)s</head>
""" % dict(title=esc(title), desc=esc(desc), url=url, base=BASE, v=V, extra=extra)

def header(slug):
    links = "".join('<a href="%s"%s>%s</a>' % (k, ' aria-current="page"' if k == slug else "", t) for k, t in NAV)
    ml = [("./", "Accueil", "index")] + [(k, t, k) for k, t in NAV]
    mlinks = "".join('<li><a href="%s" style="--i:%d"%s>%s<small>0%d</small></a></li>' % (h, i, ' aria-current="page"' if s == slug else "", t, i + 1) for i, (h, t, s) in enumerate(ml))
    return """<a class="skip" href="#main">Aller au contenu</a>
<header class="hdr"><div class="wrap hdr-in">
<a class="logo" href="./" aria-label="vXv Barber's — accueil">%(mark)s<span>BARBER'S</span></a>
<nav class="nav" aria-label="Navigation principale">%(links)s</nav>
<div class="hdr-r">%(soc)s<a class="btn btn-ink" href="%(wa)s" target="_blank" rel="noopener" aria-label="WhatsApp">%(waico)s<span class="lbl">WhatsApp</span></a>
<button class="burger" type="button" aria-label="Ouvrir le menu" aria-expanded="false" aria-controls="mnav"><i></i><i></i></button></div>
</div></header>
<div class="mnav" id="mnav"><ol>%(mlinks)s</ol>
<div class="mnav-foot"><a class="btn btn-wa" href="%(wa)s" target="_blank" rel="noopener">%(waico)s Écrire sur WhatsApp</a>%(soc)s</div></div>
""" % dict(mark=MARK, links=links, mlinks=mlinks, wa=WA, waico=I["wa"], soc=socials())

def footer():
    sal = "".join('<li><a href="salons#%s"><b>%s</b><br><span class="muted">%s, %s</span></a></li>' % (s["key"], s["name"], s["street"], s["city"]) for s in SALONS)
    pages = "".join('<li><a href="%s">%s</a></li>' % (k, t) for k, t in [("./", "Accueil")] + NAV)
    tels = "".join('<li><a href="tel:%s">%s · %s</a></li>' % (s["tel"], s["name"], s["phone"]) for s in SALONS)
    word = "".join("<span>%s</span>" % c for c in "VXVBARBER'S")
    return """<footer class="ftr"><div class="wrap">
<div class="ftr-grid">
<div><a class="logo" href="./" aria-label="vXv Barber's — accueil">%(mark)s<span>BARBER'S</span></a>
<p class="muted" style="margin-top:20px;max-width:24em">Barbershop sans rendez-vous à Crissier, Lausanne-Blécherette et Vevey.</p>%(soc)s</div>
<div><h4>Salons</h4><ul>%(sal)s</ul></div>
<div><h4>Contact</h4><ul><li><a href="%(wa)s" target="_blank" rel="noopener">WhatsApp · +41 76 757 86 36</a></li>%(tels)s</ul></div>
<div><h4>Pages</h4><ul>%(pages)s</ul></div>
</div>
<div class="ftr-word" aria-hidden="true">%(word)s</div>
<div class="ftr-bot"><span>© <span data-year>2026</span> vXv Barber’s</span><span>Sans rendez-vous · du lundi au samedi</span></div>
</div></footer>
""" % dict(mark=MARK, soc=socials(), sal=sal, wa=WA, tels=tels, pages=pages, word=word)

def wa_widget():
    q = [("Combien d’attente en ce moment ?", "Bonjour vXv, combien d’attente en ce moment au salon de "),
         ("Une question sur un tarif", "Bonjour vXv, j’ai une question sur vos tarifs : "),
         ("Autre demande", "Bonjour vXv, ")]
    quick = "".join('<a href="%s" target="_blank" rel="noopener">%s</a>' % (wa(t), lab) for lab, t in q)
    return """<div class="waw">
<div class="waw-tease">Une question ? Écrivez-nous 👋</div>
<div class="waw-panel" id="waw-panel" role="dialog" aria-label="Contacter vXv Barber's sur WhatsApp">
<div class="waw-head"><span class="waw-av">%(mark)s</span><div><b>vXv Barber’s</b><span>Réponse sur WhatsApp</span></div></div>
<div class="waw-body"><div class="waw-msg">Salut 👋 Une question sur un salon, un tarif ou l’attente du moment ? Écrivez-nous directement.<time></time></div>
<div class="waw-quick">%(quick)s</div></div>
<div class="waw-foot"><a class="btn btn-wa" href="%(wa)s" target="_blank" rel="noopener">%(ico)s Ouvrir WhatsApp</a></div>
</div>
<button class="waw-btn" type="button" aria-label="Contacter sur WhatsApp" aria-expanded="false" aria-controls="waw-panel">%(ico)s<span class="x">%(x)s</span></button>
</div>""" % dict(mark=MARK, quick=quick, wa=wa("Bonjour vXv, "), ico=I["wa"], x=I["x"])

def page(slug, title, desc, main, extra_head="", loader=False):
    ld = ""
    if loader:
        ld = '<div class="loader" aria-hidden="true"><svg viewBox="0 0 120 70">%s</svg><span class="loader-city">Crissier · Blécherette · Vevey</span><span class="loader-count">0</span></div>\n' % MARK_POLY
    scripts = "".join('<script src="assets/js/vendor/%s"></script>\n' % s for s in ["gsap.min.js", "ScrollTrigger.min.js", "lenis.min.js"])
    return (head(slug, title, desc, extra_head) + "<body>\n" + ld + header(slug) +
            '<main id="main">\n' + main + "\n</main>\n" + footer() + wa_widget() +
            '\n<div class="curtain" aria-hidden="true">%s</div>\n' % MARK + scripts +
            '<script src="assets/js/site.js?v=%s"></script>\n</body>\n</html>\n' % V)

def jsonld():
    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    shops = []
    for s in SALONS:
        spec = [{"@type": "OpeningHoursSpecification", "dayOfWeek": days[i], "opens": h[0], "closes": h[1]} for i, h in enumerate(s["hours"]) if h]
        shops.append({"@type": "BarberShop", "name": "vXv Barber's " + s["name"], "url": BASE + "salons#" + s["key"],
            "image": BASE + "assets/img/" + s["img"] + ".jpg", "telephone": s["tel"], "priceRange": "CHF 7–25",
            "address": {"@type": "PostalAddress", "streetAddress": s["street"], "postalCode": s["zip"], "addressLocality": s["locality"], "addressRegion": "VD", "addressCountry": "CH"},
            "geo": {"@type": "GeoCoordinates", "latitude": s["lat"], "longitude": s["lng"]},
            "hasMap": "https://maps.google.com/?cid=" + s["cid"], "openingHoursSpecification": spec, "parentOrganization": {"@id": BASE + "#org"}})
    data = {"@context": "https://schema.org", "@graph": [{"@type": "Organization", "@id": BASE + "#org", "name": "vXv Barber's", "url": BASE,
            "logo": BASE + "assets/img/apple-touch-icon.png", "sameAs": [IG, IG_VEVEY, TIKTOK]}] + shops}
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + "</script>\n"

# ------------------------------------------------------------------ components
def rcard(i, r, hidden=False):
    name, key, text = r
    s = next(x for x in SALONS if x["key"] == key)
    return ('<article class="rcard" data-tags="%s"%s><div class="rcard-h"><span class="av" style="background:%s">%s</span><div><b>%s</b><span>Avis Google</span></div>%s</div>'
            '%s<p>%s</p><div class="rsrc"><span>vXv Barber’s %s</span><a href="%s" target="_blank" rel="noopener"%s>Voir sur Google</a></div></article>'
            % (key, ' aria-hidden="true"' if hidden else "", AV_COLORS[i % len(AV_COLORS)], esc(name[0].upper()), esc(name), I["g"].replace("<svg ", '<svg class="g" '),
               stars(), esc(text), s["name"], greviews(s), ' tabindex="-1"' if hidden else ""))

def rev_rows(n_rows=2):
    rows = []
    for k in range(n_rows):
        idx = list(range(len(REVIEWS)))[k::n_rows]
        a = "".join(rcard(i, REVIEWS[i]) for i in idx)
        b = "".join(rcard(i, REVIEWS[i], hidden=True) for i in idx)
        rows.append('<div class="rev-row%s" style="--dur:%ds"><div class="rev-track">%s%s</div></div>' % (" rev" if k % 2 else "", 75 + k * 12, a, b))
    return '<div class="rev-rows">%s</div>' % "".join(rows)

def g_summary():
    sc = "".join('<div class="meta"><b style="color:var(--ink)">%s</b> %s<br>%s · %d avis</div>' % (s["rating"], stars(), s["name"], s["count"]) for s in SALONS)
    return ('<div class="g-summary" data-rv><span style="display:flex;align-items:center;gap:12px">%s<span style="font-size:24px">%s</span></span>'
            '<div class="score"><b>%d</b><span class="meta">avis Google<br>sur trois salons</span></div>%s<span class="sp"></span>'
            '<a class="btn btn-line" href="avis">Tous les avis %s</a><a class="btn btn-ink" href="%s" target="_blank" rel="noopener">Laisser un avis</a></div>'
            % (I["g"].replace("<svg ", '<svg class="glogo" '), GWORD, TOTAL_REVIEWS, sc, I["arr"], gwrite(SALONS[0])))

def prices_html():
    rows = "".join('<li class="price" data-img="%s" data-rv><span class="n">0%d</span><div><h3>%s</h3><p>%s</p></div><span class="v"><small>CHF</small>%s.–</span></li>'
                   % (img, i + 1, n, desc, v) for i, (n, v, desc, img) in enumerate(PRICES))
    pf = '<div class="pfloat" aria-hidden="true">' + "".join('<img src="assets/img/%s.jpg" data-k="%s" alt="" loading="lazy">' % (p[3], p[3]) for p in PRICES) + "</div>"
    return '<ul class="prices">%s</ul>%s' % (rows, pf)

def follow():
    cards = [(IG, "ig", I["ig"], "Instagram", "@vxvbarbers · 3K abonnés"),
             (TIKTOK, "tt", I["tt"], "TikTok", "@vxvbarbers · 215,6K j’aime"),
             (IG_VEVEY, "ig", I["ig"], "Instagram Vevey", "@vxvvevey · 527 abonnés"),
             (WA, "wa", I["wa"], "WhatsApp", "+41 76 757 86 36")]
    return '<div class="follow">%s</div>' % "".join(
        '<a class="fcard" href="%s" target="_blank" rel="noopener" data-rv><span class="ic %s">%s</span><span><b>%s</b><span>%s</span></span>%s</a>' % (u, c, ic, t, sub, I["arr2"]) for u, c, ic, t, sub in cards)

def bigcta(title, lead, img="lounge", extra_btn=""):
    return """<section class="sec tight"><div class="wrap"><div class="bigcta">
<div class="bg"><img data-par="6" src="assets/img/%s.jpg" alt="" loading="lazy"></div>
<span class="kicker">Sans rendez-vous · Lun – Sam</span>
%s
<p class="lead">%s</p>
<div class="hero-cta">%s<a class="btn btn-wa" href="%s" target="_blank" rel="noopener">%s Écrire sur WhatsApp</a><a class="btn btn-line" href="salons">Nos salons %s</a></div>
</div></div></section>""" % (img, H(title, "h2", "d d-xl"), lead, extra_btn, wa("Bonjour vXv, "), I["wa"], I["arr"])

def phead(crumb, title, lead):
    return """<section class="phead"><div class="wrap">
<nav class="crumbs" aria-label="Fil d'Ariane" data-rv><a href="./">Accueil</a><span>/</span><span>%s</span></nav>
%s
<p class="lead" data-rv>%s</p>
</div></section>""" % (crumb, H(title, "h1", "d d-xl"), lead)

# ------------------------------------------------------------------ pages
def index():
    panels = []
    for s in SALONS:
        media = ('<video data-auto autoplay muted loop playsinline preload="auto" poster="assets/img/neon-close.jpg" src="%s" aria-label="Le salon de %s en vidéo"></video>' % (s["video"], s["name"])
                 if s["video"] else pic(s["img"], "Le salon vXv Barber's à " + s["name"], lazy=False))
        panels.append("""<a class="panel" href="salons#%(key)s" data-hours='%(hours)s' data-cursor="Voir">
<div class="media">%(media)s</div>
<div class="panel-top"><span>%(n)s</span><span class="status" data-status>Horaires</span></div>
<div class="panel-body"><h2>%(name)s</h2><address>%(street)s<br>%(city)s</address><span class="go">%(ne)s</span></div>
</a>""" % dict(key=s["key"], hours=json.dumps(s["hours"]), media=media, n=s["n"], name=s["name"], street=s["street"], city=s["city"], ne=I["ne"]))
    hs = "".join('<figure class="hg-item"><a class="ph" href="galerie" data-cursor="Galerie" aria-label="%s — voir la galerie">%s</a><figcaption><span>%s</span><span>%02d</span></figcaption></figure>'
                 % (esc(c), pic(n, c, lazy=False), c, i + 1) for i, (n, c) in enumerate(HSCROLL))
    slist = "".join("""<div class="sitem" data-hours='%(hours)s' data-rv>
<div class="top"><h3>%(name)s</h3><span class="status light" data-status>Horaires</span></div>
<address>%(street)s<br>%(city)s</address>
<div class="hrs">%(hsum)s<br>Dimanche · fermé</div>
<div class="acts"><a class="chip" href="%(map)s" target="_blank" rel="noopener">%(pin)s Itinéraire</a><a class="chip" href="tel:%(tel)s">%(telico)s %(phone)s</a></div>
</div>""" % dict(hours=json.dumps(s["hours"]), name=s["name"], street=s["street"], city=s["city"], hsum=hsum(s), map=gmaps(s), pin=I["pin"], tel=s["tel"], telico=I["tel"], phone=s["phone"]) for s in SALONS)

    main = """
<section class="hero"><div class="wrap">
<div class="hero-top"><span class="kicker" data-in>Barbershop · Crissier · Lausanne · Vevey</span><span class="kicker" data-in>Sans rendez-vous · Lun – Sam</span></div>
%(h1)s
<div class="hero-row">
<p class="lead" data-in>Dégradés, coupes et barbe dans nos trois salons. Pas de rendez-vous à prendre : vous passez, on s’occupe du reste.</p>
<div class="hero-cta" data-in><a class="gbadge" href="avis"><span class="g">%(g)s</span><span><b>%(total)d avis Google</b> %(stars)s</span></a><a class="btn btn-ink" href="salons">Trouver un salon %(arr)s</a><a class="btn btn-wa" href="%(wa)s" target="_blank" rel="noopener">%(waico)s WhatsApp</a></div>
</div>
<div class="trip">%(panels)s</div>
</div></section>

<section class="sec"><div class="wrap">
<div class="intro">
<div class="intro-text">
<span class="kicker" data-rv><b>01</b> La maison</span>
%(ih)s
<p class="lead" data-rv>Trois salons entre Crissier, Lausanne et Vevey, une équipe de barbiers et une règle simple : on écoute ce que vous voulez, puis on le fait proprement. Dégradés, contours, barbe, coupes enfants — six jours sur sept.</p>
<a class="tlink" href="salons" data-rv>Découvrir nos salons %(ne)s</a>
</div>
<div class="intro-media">
<div class="ph tall" data-reveal>%(p1)s<span class="cap">Crissier</span></div>
<div class="ph mid" data-reveal>%(p2)s<span class="cap">Blécherette</span></div>
</div>
</div>
<div class="stats">
<div class="stat" data-rv><b data-count="%(total)d">%(total)d</b><span>avis Google sur nos trois salons</span></div>
<div class="stat" data-rv><b data-count="5.0">5,0</b><span>note Google de la Blécherette</span></div>
<div class="stat" data-rv><b data-count="3">3</b><span>salons, sans rendez-vous</span></div>
<div class="stat" data-rv><b><span data-count="215.6">215,6</span>K</b><span>j’aime sur TikTok</span></div>
</div>
</div></section>

<section class="hg stone">
<div class="wrap hg-head"><div><span class="kicker" data-rv><b>02</b> Le travail</span>%(hh)s</div><a class="tlink" href="galerie" data-rv>Toute la galerie %(ne)s</a></div>
<div class="hg-track">%(hs)s</div>
<div class="hg-bar"><i></i></div>
</section>

<section class="sec"><div class="wrap">
<div class="sec-head"><div><span class="kicker" data-rv><b>03</b> Tarifs</span>%(ph)s</div><p class="lead" data-rv>Affichés en salon, sans surprise.</p></div>
%(prices)s
<p class="note" data-rv>Tarifs du salon de Crissier, à titre indicatif. <a class="tlink" href="prestations" style="font-size:14px">Détails %(ne)s</a></p>
</div></section>

<section class="sec tight"><div class="wrap">
<div class="sec-head"><div><span class="kicker" data-rv><b>04</b> Avant · après</span>%(bh)s</div><p class="lead" data-rv>Une transformation complète, filmée dans notre salon.</p></div>
<div class="ba">
<div class="ph" data-reveal><span class="tag">Avant</span>%(avant)s</div>
<div class="ph big" data-reveal><span class="tag dark">En vidéo</span><video data-auto muted loop playsinline preload="none" poster="assets/img/avant.jpg" data-src="assets/video/transfo.mp4" aria-label="Vidéo de la transformation"></video></div>
<div class="ph" data-reveal><span class="tag">Après</span>%(apres)s</div>
</div>
</div></section>

<section class="sec stone"><div class="wrap">
<div class="sec-head"><div><span class="kicker" data-rv><b>05</b> Avis Google</span>%(rh)s</div></div>
%(gsum)s
</div>
%(rows)s
</section>

<section class="sec"><div class="wrap">
<div class="sec-head"><div><span class="kicker" data-rv><b>06</b> Adresses</span>%(sh)s</div><a class="tlink" href="salons" data-rv>Horaires & plans %(ne)s</a></div>
<div class="slist">%(slist)s</div>
</div></section>

<section class="sec tight"><div class="wrap">
<div class="sec-head"><div><span class="kicker" data-rv><b>07</b> Réseaux</span>%(fh)s</div></div>
%(follow)s
</div></section>

%(cta)s
""" % dict(
        h1=H("Coupes nettes,|~trois adresses.", "h1", "d d-hero"), g=I["g"], total=TOTAL_REVIEWS, stars=stars(), arr=I["arr"], wa=wa("Bonjour vXv, "), waico=I["wa"],
        panels="".join(panels), ih=H("Une coupe propre.|~À chaque fois.", "h2", "d d-l"), ne=I["ne"],
        p1=pic("neon-close", "Le mur végétal et les néons vXv du salon de Crissier"), p2=pic("blecherette-salle", "Le salon de la Blécherette"),
        hh=H("Sorti du fauteuil.", "h2", "d d-l"), hs=hs, ph=H("Des prix clairs.", "h2", "d d-l"), prices=prices_html(),
        bh=H("Avant. Après.", "h2", "d d-l"), avant=pic("avant-salon", "Avant la coupe"), apres=pic("apres", "Après la coupe : dégradé et raie dessinée"),
        rh=H("Ce qu’ils|~en disent.", "h2", "d d-l"), gsum=g_summary(), rows=rev_rows(2),
        sh=H("Trois salons.", "h2", "d d-l"), slist=slist, fh=H("Suivez-nous.", "h2", "d d-l"), follow=follow(),
        cta=bigcta("Passez quand|vous voulez.", "Pas de rendez-vous. Pour connaître l’attente du moment, écrivez-nous sur WhatsApp."))
    return page("index", "vXv Barber’s — Barbershop à Crissier, Lausanne & Vevey",
                "Barbershop sans rendez-vous à Crissier, Lausanne-Blécherette et Vevey. Dégradés, coupes, barbe. %d avis Google." % TOTAL_REVIEWS,
                main, jsonld() + '<link rel="preload" as="video" href="assets/video/hero.mp4" type="video/mp4">\n', loader=True)

def salons():
    secs = []
    for s in SALONS:
        rows = "".join('<tr data-day="%d"><td>%s</td><td>%s</td></tr>' % (k, DAYS[k], ("%s – %s" % tuple(s["hours"][k])) if s["hours"][k] else "Fermé") for k in [1, 2, 3, 4, 5, 6, 0])
        main_media = ('<video data-auto muted loop playsinline preload="none" poster="assets/img/%s.jpg" data-src="%s" aria-label="Le salon de %s en vidéo"></video>' % (s["img"], s["video"], s["name"])
                      if s["video"] else pic(s["img"], "Le salon vXv Barber's à " + s["name"]))
        secs.append("""<section class="sd" id="%(key)s" data-hours='%(hours)s'>
<div class="sd-media">
<div class="ph" data-reveal>%(m0)s</div>
<div class="ph" data-reveal>%(p1)s</div>
<div class="ph" data-reveal>%(p2)s</div>
</div>
<div class="sd-info">
<span class="num" data-rv>%(n)s / 03</span>
%(h)s
<p class="lead" data-rv>%(text)s</p>
<span class="status light" data-status data-rv>Horaires</span>
<table class="hours" data-rv><caption class="sr">Horaires — %(name)s</caption>%(rows)s</table>
<dl class="facts" data-rv><dt>Adresse</dt><dd>%(street)s, %(city)s</dd><dt>Téléphone</dt><dd><a href="tel:%(tel)s">%(phone)s</a></dd><dt>Google</dt><dd>%(rating)s %(stars)s · %(count)d avis</dd></dl>
<div class="sd-acts" data-rv><a class="btn btn-ink" href="%(map)s" target="_blank" rel="noopener">%(pin)s Itinéraire</a><a class="btn btn-line" href="tel:%(tel)s">%(telico)s Appeler</a><a class="chip" href="%(rev)s" target="_blank" rel="noopener">%(g)s Avis Google</a></div>
<div class="map" data-map="%(embed)s" data-title="Carte — vXv Barber's %(name)s" data-rv><button type="button">%(pin)s Afficher la carte</button></div>
</div>
</section>""" % dict(key=s["key"], hours=json.dumps(s["hours"]), m0=main_media, p1=pic(s["imgs"][0], "vXv Barber's " + s["name"]), p2=pic(s["imgs"][1], "vXv Barber's " + s["name"]),
                     n=s["n"], h=H(s["name"], "h2", "d d-l"), text=s["text"], name=s["name"], rows=rows, street=s["street"], city=s["city"], tel=s["tel"], phone=s["phone"],
                     rating=s["rating"], stars=stars(), count=s["count"], map=gmaps(s), pin=I["pin"], telico=I["tel"], rev=greviews(s), g=I["g"], embed=esc(gembed(s))))
    main = phead("Salons", "Trois salons.|~Un seul standard.", "Crissier, Lausanne-Blécherette et Vevey. Sans rendez-vous, du lundi au samedi — écrivez-nous sur WhatsApp pour connaître l’attente.") + \
        '<div class="wrap">%s</div>' % "".join(secs) + bigcta("Une question|avant de passer ?", "On vous répond sur WhatsApp.", "mur-vegetal")
    return page("salons", "Nos salons — Crissier, Blécherette, Vevey | vXv Barber’s",
                "Adresses, horaires et accès des trois salons vXv Barber's : Rue du Jura 11 à Crissier, Route des Plaines-du-Loup 55 à Lausanne, Avenue Général-Guisan 52 à Vevey.",
                main, jsonld())

def prestations():
    steps = [("Vous passez", "Pas de rendez-vous. Entrez dans le salon le plus proche — ou écrivez-nous avant pour connaître l’attente."),
             ("On écoute", "Photo, idée précise ou envie de changer : on prend le temps de comprendre avant de commencer."),
             ("On finit", "Contours à la lame, dégradé fondu, coiffage. Vous repartez prêt.")]
    st = "".join('<div class="step" data-rv><b>0%d</b><h3>%s</h3><p>%s</p></div>' % (i + 1, t, p) for i, (t, p) in enumerate(steps))
    main = phead("Prestations", "Des prix|~clairs.", "Quatre prestations, des prix affichés, aucune surprise.") + """
<section class="sec tight"><div class="wrap">%s
<p class="note" data-rv>Tarifs affichés pour le salon de Crissier, à titre indicatif. Ils peuvent varier légèrement selon l’adresse.</p></div></section>
<section class="sec stone"><div class="wrap">
<div class="intro">
<div class="ph" data-reveal style="aspect-ratio:4/5"><video data-auto muted loop playsinline preload="none" poster="assets/img/miroir.jpg" data-src="assets/video/miroir.mp4" aria-label="Un client dans le miroir après sa coupe"></video></div>
<div><span class="kicker" data-rv>Comment ça se passe</span>%s<div class="steps" style="grid-template-columns:1fr;margin-top:28px">%s</div></div>
</div></div></section>
%s""" % (prices_html(), H("En trois|~temps.", "h2", "d d-l", ' style="margin-top:16px"'), st,
         bigcta("Une question|sur un tarif ?", "Écrivez-nous, on vous répond sur WhatsApp."))
    return page("prestations", "Prestations & tarifs — vXv Barber’s",
                "Coupe CHF 25, coupe enfant CHF 22, barbe CHF 15, soin point noir CHF 7. Sans rendez-vous à Crissier, Lausanne-Blécherette et Vevey.", main)

def galerie():
    items = []
    vids = {5: ("transfo", "avant", "La transformation"), 13: ("hero", "neon-close", "Crissier en vidéo"), 21: ("miroir", "miroir", "Dans le miroir")}
    for i, (n, cap, tags) in enumerate(GALLERY):
        items.append('<figure class="gi" data-tags="%s" data-cap="%s" data-full="assets/img/%s.jpg" data-cursor="Voir" data-rv>%s<figcaption>%s</figcaption></figure>' % (tags, esc(cap), n, pic(n, cap), esc(cap)))
        if i in vids:
            v, p, c = vids[i]
            items.append('<figure class="gi vid" data-tags="videos" data-rv><video data-auto muted loop playsinline preload="none" poster="assets/img/%s.jpg" data-src="assets/video/%s.mp4" aria-label="%s"></video><figcaption>%s</figcaption></figure>' % (p, v, c, c))
    main = phead("Galerie", "Sorti du|~fauteuil.", "Des coupes réalisées dans nos salons, telles quelles. La suite est sur Instagram et TikTok.") + """
<section style="padding-bottom:clamp(80px,10vw,140px)"><div class="wrap">
<div class="gbar"><div class="chips" data-filter=".gi"><button type="button" data-f="all" aria-pressed="true">Tout</button><button type="button" data-f="coupes" aria-pressed="false">Coupes</button><button type="button" data-f="salons" aria-pressed="false">Salons</button><button type="button" data-f="videos" aria-pressed="false">Vidéos</button></div></div>
<div class="masonry">%s</div>
<div style="display:flex;flex-wrap:wrap;gap:10px;margin-top:36px"><a class="btn btn-ink" href="%s" target="_blank" rel="noopener">%s Plus sur Instagram</a><a class="btn btn-line" href="%s" target="_blank" rel="noopener">%s Plus sur TikTok</a></div>
</div></section>
<div class="lb" aria-hidden="true" role="dialog" aria-label="Photo en plein écran">
<div class="lb-top"><span class="lb-count"></span><button class="lb-x" type="button" aria-label="Fermer">%s</button></div>
<div class="lb-stage"><img alt=""></div>
<div class="lb-bot"><button class="lb-prev" type="button" aria-label="Précédente">%s</button><span class="lb-cap"></span><button class="lb-next" type="button" aria-label="Suivante">%s</button></div>
</div>""" % ("".join(items), IG, I["ig"].replace("<svg ", '<svg style="fill:currentColor" '), TIKTOK, I["tt"].replace("<svg ", '<svg style="fill:currentColor" '), I["x"], I["prev"], I["next"])
    return page("galerie", "Galerie — coupes et salons | vXv Barber’s",
                "Dégradés, motifs, barbes et nos salons de Crissier, Blécherette et Vevey en photos et vidéos.", main)

def avis():
    scores = "".join("""<div class="gscore" data-rv><div class="top"><b>vXv Barber’s %s</b>%s</div><span class="num">%s</span>%s<span class="cnt">%d avis Google</span>
<div class="acts"><a class="chip" href="%s" target="_blank" rel="noopener">Lire sur Google %s</a><a class="chip" href="%s" target="_blank" rel="noopener">%s Laisser un avis</a></div></div>"""
                     % (s["name"], I["g"], s["rating"], stars(), s["count"], greviews(s), I["ne"], gwrite(s), I["star"]) for s in SALONS)
    grid = "".join(rcard(i, r) for i, r in enumerate(REVIEWS))
    gbtn = '<a class="btn btn-line" style="background:#fff;color:#0d0d0d;border-color:#fff" href="%s" target="_blank" rel="noopener">%s Laisser un avis Google</a>' % (gwrite(SALONS[0]), I["g"])
    main = phead("Avis", "Ce qu’ils|~en disent.", "%d avis Google sur nos trois salons. Voici de vrais avis de nos clients, tels qu’ils sont publiés sur Google." % TOTAL_REVIEWS) + """
<section class="sec tight"><div class="wrap"><div class="gscores">%s</div></div>
%s
</section>
<section class="sec stone"><div class="wrap">
<div class="sec-head"><div><span class="kicker" data-rv>Tous les avis</span>%s</div></div>
<div class="chips" data-filter=".rgrid .rcard" data-rv><button type="button" data-f="all" aria-pressed="true">Tous</button><button type="button" data-f="crissier" aria-pressed="false">Crissier</button><button type="button" data-f="blecherette" aria-pressed="false">Blécherette</button><button type="button" data-f="vevey" aria-pressed="false">Vevey</button></div>
<div class="rgrid">%s</div>
</div></section>
%s""" % (scores, rev_rows(2), H("Mot pour mot.", "h2", "d d-l"), grid,
         bigcta("Passé chez|nous ?", "Votre avis aide les autres à choisir leur barbier.", "mur-vegetal", gbtn))
    return page("avis", "Avis Google — vXv Barber’s",
                "%d avis Google sur les salons vXv Barber's de Crissier (4,6), Lausanne-Blécherette (5,0) et Vevey (5,0)." % TOTAL_REVIEWS, main)

def sitemap():
    urls = [BASE] + [BASE + k for k, _ in NAV]
    return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join("<url><loc>%s</loc></url>\n" % u for u in urls) + "</urlset>\n"

def icons():
    from PIL import ImageDraw
    polys = [[(2,34),(12.5,34),(17,50),(21.5,34),(32,34),(21.5,68),(12.5,68)],[(38,2),(52,2),(82,68),(68,68)],[(68,2),(82,2),(52,68),(38,68)],[(88,34),(98.5,34),(103,50),(107.5,34),(118,34),(107.5,68),(98.5,68)]]
    def mark(im, cx, cy, w, col):
        k = w / 120.0; dr = ImageDraw.Draw(im)
        for pg in polys:
            dr.polygon([(cx - w / 2 + x * k, cy - 35 * k + y * k) for x, y in pg], fill=col)
    for size, name in [(180, "apple-touch-icon.png"), (32, "favicon-32.png")]:
        S = size * 4; im = Image.new("RGB", (S, S), (255, 255, 255)); mark(im, S / 2, S / 2, S * .7, (13, 13, 13))
        im.resize((size, size), Image.LANCZOS).save(os.path.join(IMG, name))
    with open(os.path.join(IMG, "favicon.svg"), "w") as f:
        f.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="-14 -36 148 148"><rect x="-14" y="-36" width="148" height="148" rx="30" fill="#fff"/><g fill="#0d0d0d">' + MARK_POLY + '</g></svg>')
    W, Hh = 1200, 630
    og = Image.new("RGB", (W, Hh), (255, 255, 255))
    for i, n in enumerate(["crissier-salle", "blecherette", "vevey-fauteuil"]):
        im = Image.open(os.path.join(IMG, n + ".jpg")).convert("RGB")
        tw, th = 372, 430; r = max(tw / im.width, th / im.height); im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1), Image.LANCZOS)
        im = im.crop(((im.width - tw) // 2, (im.height - th) // 2, (im.width - tw) // 2 + tw, (im.height - th) // 2 + th))
        og.paste(im, (24 + i * 388, 176))
    mark(og, 112, 88, 150, (13, 13, 13))
    og.save(os.path.join(IMG, "og.jpg"), quality=86)

if __name__ == "__main__":
    icons()
    pages = dict(index=index(), salons=salons(), prestations=prestations(), galerie=galerie(), avis=avis())
    for k, v in pages.items():
        with open(os.path.join(OUT, k + ".html"), "w", encoding="utf-8") as f:
            f.write(v)
    old = os.path.join(OUT, "reseaux.html")
    if os.path.exists(old):
        os.remove(old)
    with open(os.path.join(OUT, "sitemap.xml"), "w") as f:
        f.write(sitemap())
    with open(os.path.join(OUT, "robots.txt"), "w") as f:
        f.write("User-agent: *\nAllow: /\nSitemap: %ssitemap.xml\n" % BASE)
    open(os.path.join(OUT, ".nojekyll"), "w").close()
    with open(os.path.join(OUT, "404.html"), "w", encoding="utf-8") as f:
        f.write(page("404", "Page introuvable — vXv Barber’s", "Cette page n'existe pas.",
                     '<section class="phead" style="min-height:70svh"><div class="wrap">%s<p class="lead" data-rv>Cette page n’existe pas — nos fauteuils, si.</p><a class="btn btn-ink" href="./">Accueil %s</a></div></section>'
                     % (H("Coupe|~ratée.", "h1", "d d-xl"), I["arr"])).replace("<head>\n", '<head>\n<base href="/vxvbarbers/">\n', 1))
    print("built", ", ".join(pages))
