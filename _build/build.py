#!/usr/bin/env python3
"""Generates the vXv Barber's static site into ../docs. Edit this file, not the HTML."""
import json, os, html
from urllib.parse import quote
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs")
IMG = os.path.join(OUT, "assets", "img")
BASE = "https://welcometothenextlevel.github.io/vxvbarbers/"
V = "4"  # cache-buster for css/js

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
         img="crissier-salle", imgs=["neon-close", "lounge"],
         short="Plafond en nid d’abeille, sol en marbre, mur végétal et néons VXV.",
         text="L’adresse historique, entièrement repensée. Un plafond lumineux en nid d’abeille, du marbre au sol, un mur végétal signé de nos néons — et des fauteuils alignés pour que l’attente reste courte."),
    dict(key="blecherette", name="Blécherette", n="02", street="Route des Plaines-du-Loup 55", city="1018 Lausanne", locality="Lausanne", zip="1018",
         phone="076 669 36 00", tel="+41766693600", hours=WEEK_STD, rating="5,0", count=53,
         pid="ChIJrwco4I8xjEcRTlv9IjlqdOw", cid="17038360083882138446", lat=46.5408039, lng=6.620091,
         img="blecherette", imgs=["blecherette-salle", "blecherette-entree"],
         short="Marbre noir veiné d’or, plafond lumineux et verdure suspendue.",
         text="La nouvelle adresse, au cœur du quartier des Plaines-du-Loup. Marbre noir veiné d’or, verdure suspendue sous un plafond lumineux : le même standard que Crissier, côté Lausanne."),
    dict(key="vevey", name="Vevey", n="03", street="Avenue Général-Guisan 52", city="1800 Vevey", locality="Vevey", zip="1800",
         phone="078 973 14 14", tel="+41789731414", hours=WEEK_VEV, rating="5,0", count=5,
         pid="ChIJqzCxVt2djkcR466f8EjNs-E", cid="16263568392523329251", lat=46.4663417, lng=6.8373042,
         img="vevey", imgs=["vevey-fauteuil", "vevey-tondeuse"],
         short="La dernière-née, sur la Riviera. Ouvert jusqu’à 19h le samedi.",
         text="La petite dernière, sur la Riviera. Même équipe, mêmes gestes, mêmes finitions — avec un samedi ouvert jusqu’à 19h."),
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
def hours_summary(s):
    h = s["hours"]
    if h[6] == h[1]:
        return "Lu–Sa " + h[1][0].replace(":00", "h") + "–" + h[1][1].replace(":00", "h")
    return "Lu–Ve " + h[1][0].replace(":00", "h") + "–" + h[1][1].replace(":00", "h") + " · Sa " + h[6][0].replace(":00", "h").lstrip("0") + "–" + h[6][1].replace(":00", "h")

PRICES = [
    ("Coupe", "25", "Ciseaux ou tondeuse, dégradé, contours nets et coiffage. On écoute d’abord, on coupe ensuite.", "coupe-skin"),
    ("Coupe enfant", "22", "Même soin, même précision — pour les plus jeunes.", "coupe-frange"),
    ("Barbe", "15", "Taille, dégradé de barbe et contours dessinés à la lame.", "coupe-barbe"),
    ("Point noir", "7", "Soin express du visage contre les points noirs.", "portrait-nb"),
]

REVIEWS = [
    ("Valentin F.", "crissier", "Je n'ai jamais été déçu en 2 ans ! Les prix sont extrêmement compétitifs et tous les barbiers sont à la pointe de leur métier. L'ambiance est très accueillante, l'attente est rarement longue. Bref, vous trouverez difficilement un meilleur salon en région lausannoise. Je recommande à 100 % !"),
    ("Erkin O.", "crissier", "Super expérience chez VXV Barber ! L’équipe est accueillante, professionnelle et vraiment à l’écoute. La coupe est impeccable, le dégradé est net et précis. On sent qu’ils prennent leur temps pour bien faire les choses. Je recommande à 100 %."),
    ("Nolf N.", "crissier", "Franchement, rien à redire. Très bon accueil, barber sympa et à l’écoute. La coupe et la barbe sont réalisées avec beaucoup de soin et de précision. On voit qu’ils aiment leur métier. Je recommande les yeux fermés !"),
    ("Javier M.", "blecherette", "Je suis entièrement satisfait de mon expérience chez VXV Barber à la Blécherette. Dès mon arrivée, j’ai été très bien accueilli par une équipe chaleureuse et professionnelle."),
    ("Club Pro", "blecherette", "Super expérience dans ce salon ! Très bon accueil, équipe professionnelle et à l’écoute. Je suis vraiment satisfait du résultat, on sent qu’ils prennent le temps de bien faire. Je recommande sans hésiter."),
    ("Tobias", "crissier", "Les gens qui y travaillent sont très gentils et polis, l'accueil est parfait, le salon est magnifique avec beaucoup d'espace. Les demandes sont toujours respectées. Vous repartez avec une belle coupe garantie. Foncez."),
    ("Luca A.", "crissier", "Très bonne expérience avec Moha. Personne sérieuse, professionnelle et à l’écoute. Le travail a été fait avec soin et tout s’est déroulé parfaitement du début à la fin. Je recommande sans hésitation."),
    ("Anwar L.", "blecherette", "Le traitement sur place était incroyable et le salon est très propre. Et le service est de grande qualité, je recommande fortement !"),
    ("Izi B.", "blecherette", "Un très beau salon, classe, propre. Je n’ai pas eu à attendre longtemps et la coupe m’a plu. Le barber était sympa, à l’écoute et pro. Allez-y en toute confiance."),
    ("Nas K.", "blecherette", "Bel accueil et service au top. Équipe professionnelle. De plus, un prix compétitif."),
    ("Ruben T.", "crissier", "Ils se préoccupent du bien-être des clients, ils sont très accueillants et leurs coupes sont toujours bien réussies 🔥🔥"),
    ("Bilel M.", "vevey", "Les coiffeurs sont incroyablement qualifiés, je recommande. Une expérience unique et rapide !"),
    ("Matteo G.", "blecherette", "Des coiffeurs compétents, professionnels et très à l’aise à la discussion avec le client."),
    ("Antonio S.", "crissier", "Mon fils a voulu aller chez eux car ses copains en parlaient. Je n'ai qu'un mot à dire : EXCELLENCE."),
    ("Nurdin P.", "blecherette", "Très bon coiffeur, très propre, il sait ce qu’il fait. Première fois que j’y vais et vraiment pas déçu. Foncez !"),
    ("Jack L.", "vevey", "Coiffeur très fort, merci pour la prestation."),
    ("Ylian S.", "crissier", "Coiffeur extrêmement gentil et soigneux, service au top. Je recommande !"),
    ("Elsin M.", "blecherette", "Super accueil, coupe au propre, parfait comme on aime 😉"),
    ("Jean-Claude P.", "blecherette", "Endroit convivial, très sympathique et au service de sa clientèle."),
    ("Ilias D.", "crissier", "10/10, rien à redire. Surtout la personne à l'accueil, qui était grave sympa."),
    ("Rayan P.", "crissier", "Incroyable, pas cher et très bon coiffeur."),
    ("Jefferson C.", "blecherette", "Bon coiffeur et bonne ambiance."),
]
SALON_NAME = {s["key"]: s["name"] for s in SALONS}

GALLERY = [  # (image, caption, tags)
    ("coupe-coeur", "Motif cœur", "coupes"), ("mur-vegetal", "Crissier — le mur végétal", "salons"),
    ("coupe-texture", "Texture & taper", "coupes"), ("coupe-skin", "Skin fade", "coupes"),
    ("crissier-salle", "Crissier", "salons"), ("coupe-twists", "Twists", "coupes"),
    ("coupe-raie", "Raie rasée", "coupes"), ("portrait-nb", "Le résultat", "coupes"),
    ("blecherette", "Blécherette", "salons"), ("coupe-barbe", "Barbe & contours", "coupes"),
    ("coupe-blond", "Blond & motif", "coupes"), ("coupe-volume", "Volume & dégradé", "coupes"),
    ("etagere-or", "Crissier — les produits", "salons"), ("blecherette-salle", "Blécherette", "salons"), ("coupe-boucles", "Boucles & barbe", "coupes"),
    ("coupe-design", "Undercut", "coupes"), ("vevey", "Vevey", "salons coupes"),
    ("coupe-nuque", "La nuque", "coupes"), ("coupe-waves", "Waves", "coupes"),
    ("lounge", "Crissier — le salon d’attente", "salons"), ("coupe-motif", "Motif rasé", "coupes"),
    ("coupe-chignon", "Man bun & barbe", "coupes"), ("comptoir", "Crissier — le comptoir", "salons"), ("vevey-fauteuil", "Vevey", "salons"),
    ("coupe-degrade", "Mid fade", "coupes"), ("coupe-afro", "Afro & taper", "coupes"),
    ("miroir", "Dans le miroir", "coupes"), ("coupe-frange", "Frange & dégradé", "coupes"),
    ("neon-close", "Néons VXV", "salons"),
]
HSCROLL = [("coupe-coeur", "Motif cœur"), ("coupe-texture", "Texture & taper"), ("coupe-skin", "Skin fade"),
           ("coupe-twists", "Twists"), ("coupe-raie", "Raie rasée"), ("coupe-barbe", "Barbe & contours"),
           ("coupe-blond", "Blond & motif"), ("coupe-boucles", "Boucles & barbe"), ("portrait-nb", "Le résultat")]

# ------------------------------------------------------------------ icons
I = dict(
    wa='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M17.47 14.38c-.3-.15-1.76-.87-2.03-.97-.27-.1-.47-.15-.67.15-.2.3-.77.97-.94 1.17-.17.2-.35.22-.64.07-.3-.15-1.26-.46-2.4-1.48-.89-.79-1.49-1.77-1.66-2.07-.17-.3-.02-.46.13-.6.13-.13.3-.35.45-.52.15-.17.2-.3.3-.5.1-.2.05-.37-.03-.52-.07-.15-.67-1.62-.92-2.22-.24-.58-.49-.5-.67-.51h-.57c-.2 0-.52.07-.8.37-.27.3-1.04 1.02-1.04 2.48s1.07 2.88 1.21 3.08c.15.2 2.1 3.2 5.08 4.49.71.31 1.26.49 1.69.63.71.22 1.36.19 1.87.12.57-.09 1.76-.72 2.01-1.41.25-.7.25-1.29.17-1.41-.07-.13-.27-.2-.57-.35zM12.05 21.5h-.01a9.4 9.4 0 0 1-4.8-1.31l-.34-.2-3.56.93.95-3.47-.22-.36a9.42 9.42 0 0 1-1.44-5.02c0-5.2 4.24-9.44 9.45-9.44a9.38 9.38 0 0 1 6.68 2.77 9.38 9.38 0 0 1 2.76 6.68c0 5.21-4.24 9.44-9.44 9.44zm8.04-17.48A11.3 11.3 0 0 0 12.05.7C5.79.7.69 5.8.69 12.07c0 2 .52 3.96 1.52 5.68L.6 23.6l6-1.57a11.33 11.33 0 0 0 5.44 1.38h.01c6.26 0 11.36-5.1 11.36-11.36 0-3.04-1.18-5.89-3.32-8.03z"/></svg>',
    ig='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2.2c3.2 0 3.58 0 4.85.07 3.25.15 4.77 1.69 4.92 4.92.06 1.27.07 1.65.07 4.85s-.01 3.58-.07 4.85c-.15 3.23-1.66 4.77-4.92 4.92-1.27.06-1.65.07-4.85.07s-3.58-.01-4.85-.07c-3.26-.15-4.77-1.7-4.92-4.92C2.17 15.58 2.16 15.2 2.16 12s.01-3.58.07-4.85C2.38 3.92 3.9 2.38 7.15 2.23 8.42 2.17 8.8 2.16 12 2.16zM12 0C8.74 0 8.33.01 7.05.07 2.7.27.27 2.69.07 7.05.01 8.33 0 8.74 0 12s.01 3.67.07 4.95c.2 4.36 2.62 6.78 6.98 6.98C8.33 23.99 8.74 24 12 24s3.67-.01 4.95-.07c4.35-.2 6.78-2.62 6.98-6.98.06-1.28.07-1.69.07-4.95s-.01-3.67-.07-4.95c-.2-4.35-2.62-6.78-6.98-6.98C15.67.01 15.26 0 12 0zm0 5.84a6.16 6.16 0 1 0 0 12.32 6.16 6.16 0 0 0 0-12.32zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.4-11.85a1.44 1.44 0 1 0 0 2.88 1.44 1.44 0 0 0 0-2.88z"/></svg>',
    tt='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-5.2 1.74 2.89 2.89 0 0 1 2.31-4.64c.3 0 .59.04.88.13V9.4a6.84 6.84 0 0 0-1-.05A6.33 6.33 0 0 0 5 20.1a6.34 6.34 0 0 0 10.86-4.43v-7a8.16 8.16 0 0 0 4.77 1.52v-3.4a4.85 4.85 0 0 1-1-.1z"/></svg>',
    arr='<svg class="arr" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M4 12h15M13 6l6 6-6 6"/></svg>',
    ne='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M7 17 17 7M8 7h9v9"/></svg>',
    pin='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/></svg>',
    tel='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M5 3h4l2 5-2.5 1.5a11 11 0 0 0 6 6L16 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 5a2 2 0 0 1 2-2z"/></svg>',
    star='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="m12 3 2.8 5.7 6.2.9-4.5 4.4 1.1 6.2L12 17.3 6.4 20.2l1.1-6.2L3 9.6l6.2-.9z"/></svg>',
    x='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg>',
    prev='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg>',
    next='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M9 5l7 7-7 7"/></svg>',
)
MARK_POLY = '<polygon points="2,34 12.5,34 17,50 21.5,34 32,34 21.5,68 12.5,68"/><polygon points="38,2 52,2 82,68 68,68"/><polygon points="68,2 82,2 52,68 38,68"/><polygon points="88,34 98.5,34 103,50 107.5,34 118,34 107.5,68 98.5,68"/>'
MARK = '<svg viewBox="0 0 120 70" aria-hidden="true">' + MARK_POLY + '</svg>'

def esc(s):
    return html.escape(s, quote=True)

_dims = {}
def dims(name):
    if name not in _dims:
        with Image.open(os.path.join(IMG, name + ".jpg")) as im:
            _dims[name] = im.size
    return _dims[name]

def pic(name, alt, lazy=True, cls="", extra=""):
    w, h = dims(name)
    return ('<picture><source type="image/webp" srcset="assets/img/%s.webp">'
            '<img src="assets/img/%s.jpg" alt="%s" width="%d" height="%d"%s decoding="async"%s%s></picture>'
            % (name, name, esc(alt), w, h, ' loading="lazy"' if lazy else ' fetchpriority="high"',
               ' class="%s"' % cls if cls else "", extra))

def lines(txt, tag="h2", cls="display h-l", d=0, attrs=""):
    """txt uses | for line breaks; *word* becomes serif italic."""
    out = []
    txt = txt.replace(" ?", "\u00a0?").replace(" !", "\u00a0!")
    for i, ln in enumerate(txt.split("|")):
        parts = ln.split("*")
        inner = "".join(("<em>%s</em>" % p) if k % 2 else p for k, p in enumerate(parts))
        out.append('<span class="ln"><span style="--i:%d">%s</span></span>' % (i, inner))
    return '<%s class="%s" data-lines style="--d:%ss"%s>%s</%s>' % (tag, cls, d, attrs, "".join(out), tag)

# ------------------------------------------------------------------ chrome
NAV = [("salons", "Salons"), ("prestations", "Prestations"), ("galerie", "Galerie"), ("avis", "Avis"), ("reseaux", "Réseaux")]

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
<meta name="theme-color" content="#0a0a0b">
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
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:ital,wdth,wght@0,62..125,300..900;1,100,400&family=Bodoni+Moda:ital,opsz,wght@1,6..96,400..500&display=swap">
<link rel="stylesheet" href="assets/css/site.css?v=%(v)s">
<script>document.documentElement.classList.add("js");(function(p){if(p.slice(-5)===".html"){history.replaceState(null,"",p.slice(-11)==="/index.html"?p.slice(0,-10):p.slice(0,-5)+location.search+location.hash)}})(location.pathname)</script>
%(extra)s</head>
""" % dict(title=esc(title), desc=esc(desc), url=url, base=BASE, v=V, extra=extra)

def header(slug):
    links = "".join('<a href="%s"%s>%s</a>' % (k, ' aria-current="page"' if k == slug else "", t) for k, t in NAV)
    mlinks = "".join('<li><a href="%s" style="--i:%d">%s<small>0%d</small></a></li>' % (k, i, t, i + 1) for i, (k, t) in enumerate([("./", "Accueil")] + NAV))
    return """<a class="skip" href="#main">Aller au contenu</a>
<header class="hdr"><div class="wrap hdr-in">
<a class="logo" href="./" aria-label="vXv Barber's — accueil">%(mark)s<span>BARBER'S</span></a>
<nav class="nav" aria-label="Navigation principale">%(links)s</nav>
<div class="hdr-cta"><a class="btn btn-line" href="%(wa)s" target="_blank" rel="noopener">%(waico)s WhatsApp</a>
<button class="burger" type="button" aria-label="Ouvrir le menu" aria-expanded="false" aria-controls="mnav"><i></i><i></i></button></div>
</div></header>
<div class="mnav" id="mnav"><ol>%(mlinks)s</ol>
<div class="mnav-foot"><a class="btn btn-wa" href="%(wa)s" target="_blank" rel="noopener">%(waico)s Écrire sur WhatsApp</a>
<div class="row"><a href="%(ig)s" target="_blank" rel="noopener">Instagram</a><a href="%(tt)s" target="_blank" rel="noopener">TikTok</a><span>Sans rendez-vous · Lu–Sa</span></div></div></div>
""" % dict(mark=MARK, links=links, mlinks=mlinks, wa=WA, waico=I["wa"], ig=IG, tt=TIKTOK)

def footer():
    sal = "".join('<li><a href="%s" target="_blank" rel="noopener">%s<br><span class="muted">%s, %s</span></a></li>' % (gmaps(s), s["name"], s["street"], s["city"]) for s in SALONS)
    pages = "".join('<li><a href="%s">%s</a></li>' % (k, t) for k, t in NAV)
    return """<footer class="ftr"><div class="wrap">
<div class="ftr-top">
<div><a class="logo" href="./" aria-label="vXv Barber's — accueil">%(mark)s<span>BARBER'S</span></a>
<p class="muted" style="margin-top:22px;max-width:22em">Barbershop sans rendez-vous à Crissier, Lausanne-Blécherette et Vevey.</p></div>
<div><h4>Salons</h4><ul>%(sal)s</ul></div>
<div><h4>Pages</h4><ul><li><a href="./">Accueil</a></li>%(pages)s</ul></div>
<div><h4>Suivre</h4><ul><li><a href="%(ig)s" target="_blank" rel="noopener">Instagram @vxvbarbers</a></li><li><a href="%(igv)s" target="_blank" rel="noopener">Instagram @vxvvevey</a></li><li><a href="%(tt)s" target="_blank" rel="noopener">TikTok @vxvbarbers</a></li><li><a href="%(wa)s" target="_blank" rel="noopener">WhatsApp</a></li></ul></div>
</div>
<div class="ftr-big" aria-hidden="true">vXv<em>barber’s</em></div>
<div class="ftr-bot"><span>© <span data-year>2026</span> vXv Barber’s</span><span>Sans rendez-vous · du lundi au samedi</span></div>
</div></footer>
""" % dict(mark=MARK, sal=sal, pages=pages, ig=IG, igv=IG_VEVEY, tt=TIKTOK, wa=WA)

def wa_widget():
    q = [("Combien d’attente en ce moment ?", "Bonjour vXv, combien d’attente en ce moment au salon de "),
         ("Une question sur un tarif", "Bonjour vXv, j’ai une question sur vos tarifs : "),
         ("Autre demande", "Bonjour vXv, ")]
    quick = "".join('<a href="%s" target="_blank" rel="noopener">%s</a>' % (wa(t), lab) for lab, t in q)
    return """<div class="wa">
<div class="wa-teaser">Une question ? Écrivez-nous.</div>
<div class="wa-panel" role="dialog" aria-label="Contacter vXv Barber's sur WhatsApp" id="wa-panel">
<div class="wa-head"><span class="wa-av">%(mark)s</span><div><b>vXv Barber’s</b><span>Écrivez-nous, on vous répond dès que possible</span></div></div>
<div class="wa-body"><div class="wa-msg">Salut 👋 Une question sur un salon, un tarif ou l’attente du moment ? Écrivez-nous directement ici.<time></time></div>
<div class="wa-quick">%(quick)s</div></div>
<div class="wa-foot"><a class="btn btn-wa" href="%(wa)s" target="_blank" rel="noopener">%(ico)s Ouvrir WhatsApp</a></div>
</div>
<button class="wa-btn" type="button" aria-label="Contacter sur WhatsApp" aria-expanded="false" aria-controls="wa-panel">%(ico)s<span class="x">%(x)s</span></button>
</div>""" % dict(mark=MARK, quick=quick, wa=wa("Bonjour vXv, "), ico=I["wa"], x=I["x"])

def page(slug, title, desc, main, extra_head="", loader=False):
    ld = ""
    if loader:
        ld = """<div class="loader" aria-hidden="true"><svg class="loader-mark" viewBox="0 0 120 70">%s</svg>
<div class="loader-meta"><span>Crissier · Blécherette · Vevey</span><span class="loader-pct">000</span></div><i class="loader-bar"></i></div>
""" % MARK_POLY
    return (head(slug, title, desc, extra_head) + "<body>\n" + ld + header(slug) +
            '<main id="main">\n' + main + "\n</main>\n" + footer() + wa_widget() +
            '\n<div class="curtain" aria-hidden="true"></div>\n<script src="assets/js/site.js?v=%s" defer></script>\n</body>\n</html>\n' % V)

def stars(r):
    return '<span class="stars" aria-hidden="true">★★★★★</span>'

def jsonld():
    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    shops = []
    for s in SALONS:
        spec = []
        for i, h in enumerate(s["hours"]):
            if h:
                spec.append({"@type": "OpeningHoursSpecification", "dayOfWeek": days[i], "opens": h[0], "closes": h[1]})
        shops.append({
            "@type": "BarberShop", "name": "vXv Barber's " + s["name"], "url": BASE + "salons#" + s["key"],
            "image": BASE + "assets/img/" + s["img"] + ".jpg", "telephone": s["tel"], "priceRange": "CHF 7–25",
            "address": {"@type": "PostalAddress", "streetAddress": s["street"], "postalCode": s["zip"], "addressLocality": s["locality"], "addressRegion": "VD", "addressCountry": "CH"},
            "geo": {"@type": "GeoCoordinates", "latitude": s["lat"], "longitude": s["lng"]},
            "hasMap": "https://maps.google.com/?cid=" + s["cid"], "openingHoursSpecification": spec,
            "parentOrganization": {"@id": BASE + "#org"}})
    data = {"@context": "https://schema.org", "@graph": [
        {"@type": "Organization", "@id": BASE + "#org", "name": "vXv Barber's", "url": BASE, "logo": BASE + "assets/img/apple-touch-icon.png",
         "sameAs": [IG, IG_VEVEY, TIKTOK]}] + shops}
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + "</script>\n"

# ------------------------------------------------------------------ pages
def salon_card(s, d):
    return """<article class="salon" data-rv style="--d:%(d)ss" data-hours='%(hours)s'>
<a class="frame" href="salons#%(key)s" data-cursor="Voir" aria-label="Le salon de %(name)s">%(pic)s</a>
<div class="salon-body">
<div class="salon-top"><h3>%(name)s</h3><span class="rate">%(stars)s %(rating)s · %(count)d avis</span></div>
<address>%(street)s<br>%(city)s</address>
<span class="ostat">Horaires</span>
<p class="muted" style="margin:0;font-size:15px">%(short)s</p>
<div class="salon-links"><a class="chip" href="%(map)s" target="_blank" rel="noopener">%(pin)s Itinéraire</a><a class="chip" href="tel:%(tel)s">%(telico)s Appeler</a></div>
</div></article>""" % dict(d=d, hours=json.dumps(s["hours"]), key=s["key"], name=s["name"], pic=pic(s["img"], "Intérieur du salon vXv Barber's à " + s["name"]),
                           stars=stars(5), rating=s["rating"], count=s["count"], street=s["street"], city=s["city"], short=s["short"],
                           map=gmaps(s), pin=I["pin"], tel=s["tel"], telico=I["tel"])

def index():
    hs = "".join('<figure class="hgal-item"><div class="frame mask" data-cursor="Galerie" style="--d:%ss"><a href="galerie" tabindex="-1">%s</a></div><figcaption><span>%s</span><i>%02d</i></figcaption></figure>'
                 % (round(min(i, 4) * .08, 2), pic(n, cap), cap, i + 1) for i, (n, cap) in enumerate(HSCROLL))
    prices = "".join('<li class="price" data-img="%s" data-rv style="--d:%ss"><span class="price-n">%02d</span><div><h3>%s</h3><p>%s</p></div><span class="price-v"><small>CHF</small>%s.–</span></li>'
                     % (img, i * .08, i + 1, n, desc, v) for i, (n, v, desc, img) in enumerate(PRICES))
    hover = '<div class="hover-img" aria-hidden="true">' + "".join('<img src="assets/img/%s.jpg" data-k="%s" alt="" loading="lazy">' % (img, img) for _, _, _, img in PRICES) + "</div>"
    quotes = REVIEWS[:5]
    qhtml = "".join('<figure class="quote"><blockquote>%s</blockquote><footer><b>%s</b><span>%s · %s · Avis Google</span></footer></figure>'
                    % (esc(t), esc(n), stars(5), SALON_NAME[k]) for n, k, t in quotes)
    qdots = "".join('<button class="qdot" type="button" aria-label="Avis %d"></button>' % (i + 1) for i in range(len(quotes)))
    cards = "".join(salon_card(s, i * .1) for i, s in enumerate(SALONS))
    main = """
<section class="hero">
<div class="hero-bgword" aria-hidden="true">vXv</div>
<div class="wrap">
<div class="hero-grid">
<div class="hero-text">
<span class="eyebrow" data-rv>Barbershop · Crissier · Blécherette · Vevey</span>
%(h1)s
<p class="lead" data-rv style="--d:.35s">Coupes, dégradés et barbe dans trois salons, de Lausanne à la Riviera. Sans rendez-vous, du lundi au samedi.</p>
<div class="hero-actions" data-rv style="--d:.45s"><a class="btn btn-solid" href="salons">Trouver un salon %(arr)s</a><a class="btn btn-line" href="%(wa)s" target="_blank" rel="noopener">%(waico)s WhatsApp</a></div>
</div>
<div class="hero-side">
<div class="hero-media mask" style="--d:.1s">
<video data-auto autoplay muted loop playsinline preload="auto" poster="assets/img/neon-close.jpg" src="assets/video/hero.mp4" aria-label="Le salon vXv de Crissier en vidéo"></video>
</div>
<div class="badge" aria-hidden="true"><svg viewBox="0 0 100 100"><defs><path id="c" d="M50 50m-38 0a38 38 0 1 1 76 0a38 38 0 1 1-76 0"/></defs><text textLength="236" lengthAdjust="spacing"><textPath href="#c" textLength="236" lengthAdjust="spacing">SANS RENDEZ-VOUS · SANS RENDEZ-VOUS · </textPath></text></svg><b><svg viewBox="0 0 24 24"><path d="M7 17 17 7M8 7h9v9"/></svg></b></div>
</div>
</div>
<div class="hero-foot" data-rv style="--d:.6s"><span>%(stars)s <strong>%(total)d avis Google</strong> sur nos trois salons</span><span><strong>215,6K</strong> j’aime sur TikTok</span><span class="scroll-cue">Défiler <i></i></span></div>
</div>
</section>

<div class="marquee" aria-hidden="true"><div class="marquee-track">%(mq)s%(mq)s</div></div>

<section class="sec"><div class="wrap">
<div class="manifesto">
<div><span class="eyebrow" data-rv>La maison</span></div>
<p class="manifesto-text">Ici, on ne coupe pas à la chaîne. On s’assoit, on écoute, on regarde — puis on taille. Net, propre, <em>au millimètre.</em> Du marbre au sol, de la lumière au plafond, et une équipe qui aime vraiment son métier.</p>
</div>
<div class="stats">
<div class="stat" data-rv><b><span data-count="%(total)d">%(total)d</span></b><span>avis Google, trois salons</span></div>
<div class="stat" data-rv style="--d:.08s"><b><span data-count="5.0">5,0</span><sup>★</sup></b><span>note de la Blécherette</span></div>
<div class="stat" data-rv style="--d:.16s"><b><span data-count="3">3</span></b><span>adresses, sans rendez-vous</span></div>
<div class="stat" data-rv style="--d:.24s"><b><span data-count="215.6">215,6</span><sup>K</sup></b><span>j’aime sur TikTok</span></div>
</div>
</div></section>

<section class="hgal" aria-label="Le travail">
<div class="hgal-sticky">
<div class="wrap hgal-mhead" style="margin-bottom:28px">%(hgm)s</div>
<div class="hgal-track">
<div class="hgal-intro"><span class="eyebrow" data-rv>Le travail</span>%(hgh)s<p class="lead" data-rv style="margin-top:22px">Dégradés, motifs, textures, barbes. Tout sort de nos fauteuils — rien n’est retouché.</p><a class="link-u" href="galerie" style="margin-top:18px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;font-size:13px">Toute la galerie →</a></div>
%(hs)s
</div>
<div class="hgal-progress"><i></i></div>
</div>
</section>

<section class="sec"><div class="wrap">
<div class="sec-head"><div><span class="eyebrow" data-rv>Prestations</span>%(ph)s</div><p class="lead" data-rv>Des prix clairs, affichés. Pas de rendez-vous à prendre : vous passez, on s’occupe du reste.</p></div>
<ul class="prices">%(prices)s</ul>
<p class="note" data-rv>Tarifs du salon de Crissier, indicatifs. <a class="link-u" href="prestations">Voir les prestations</a></p>
%(hover)s
</div></section>

<section class="sec" style="padding-top:0"><div class="wrap">
<div class="sec-head"><div><span class="eyebrow" data-rv>Avant · Après</span>%(bah)s</div><p class="lead" data-rv>Une transformation complète, filmée dans notre salon. Du volume à la coupe nette, avec la raie dessinée.</p></div>
<div class="ba">
<div class="frame mask"><span class="tag">Avant</span>%(avant)s</div>
<div class="frame mask" style="--d:.12s"><span class="tag">Après</span>%(apres)s</div>
<div class="frame mask" style="--d:.24s"><video data-auto muted loop playsinline preload="none" poster="assets/img/avant.jpg" data-src="assets/video/transfo.mp4" aria-label="Vidéo de la transformation"></video><span class="frame-cap">La transformation · 10 s</span></div>
</div>
</div></section>

<section class="sec" style="padding-top:0"><div class="wrap">
<div class="sec-head"><div><span class="eyebrow" data-rv>Nos salons</span>%(sh)s</div><a class="btn btn-line" href="salons" data-rv>Horaires & accès %(arr)s</a></div>
<div class="salons">%(cards)s</div>
</div></section>

<section class="sec" style="padding-top:0"><div class="wrap">
<span class="rule" style="margin-bottom:clamp(56px,7vw,96px)"></span>
<div class="sec-head" style="margin-bottom:40px"><div><span class="eyebrow" data-rv>Ils en parlent</span></div><a class="link-u" href="avis" data-rv style="font-weight:600;letter-spacing:.14em;text-transform:uppercase;font-size:13px">Tous les avis →</a></div>
<div class="quote-stage" data-rv>%(qhtml)s</div>
<div class="quote-nav">%(qdots)s</div>
</div></section>

<section class="cta">
<div class="cta-bg"><img data-par="0.12" src="assets/img/mur-vegetal.jpg" alt="" loading="lazy"></div>
<div class="wrap">
<span class="eyebrow" data-rv>Sans rendez-vous</span>
%(ctah)s
<div class="hero-actions" data-rv><a class="btn btn-solid" href="salons">Trouver un salon %(arr)s</a><a class="btn btn-wa" href="%(wa)s" target="_blank" rel="noopener">%(waico)s Écrire sur WhatsApp</a></div>
</div>
</section>
""" % dict(
        h1=lines("Le dégradé,|*au millimètre.*", "h1", "display h-xl", .15),
        arr=I["arr"], wa=WA, waico=I["wa"], stars=stars(5), total=TOTAL_REVIEWS,
        mq="".join("<span>%s</span>" % t for t in ["Sans rendez-vous", "Dégradés", "<em>Barbe</em>", "Coupe enfant", "Crissier", "<em>Blécherette</em>", "Vevey", "Motifs"]),
        hgh=lines("Le travail|parle *pour nous.*", "h2", "display h-m"),
        hgm='<span class="eyebrow">Le travail</span>' + lines("Le travail|parle *pour nous.*", "h2", "display h-m"),
        hs=hs, ph=lines("Simple.|*Affiché.*", "h2", "display h-l"), prices=prices, hover=hover,
        bah=lines("Dix secondes,|*une autre tête.*", "h2", "display h-l"),
        avant=pic("avant-salon", "Avant la coupe : cheveux longs et volumineux"), apres=pic("apres", "Après la coupe : dégradé net et raie dessinée"),
        sh=lines("Trois adresses.|*Un seul standard.*", "h2", "display h-l"), cards=cards,
        qhtml=qhtml, qdots=qdots, ctah=lines("Passez quand|*vous voulez.*", "h2", "display h-xl"))
    return page("index", "vXv Barber’s — Barbershop à Crissier, Lausanne & Vevey",
                "Barbershop sans rendez-vous à Crissier, Lausanne-Blécherette et Vevey. Dégradés, coupes, barbe. %d avis Google." % TOTAL_REVIEWS,
                main, jsonld() + '<link rel="preload" as="video" href="assets/video/hero.mp4" type="video/mp4">\n', loader=True)

def salons():
    secs = []
    for i, s in enumerate(SALONS):
        rows = "".join('<tr data-day="%d"><td>%s</td><td>%s</td></tr>' % (k, DAYS[k], ("%s – %s" % tuple(s["hours"][k])) if s["hours"][k] else "Fermé") for k in [1, 2, 3, 4, 5, 6, 0])
        secs.append("""<section class="sdetail" id="%(key)s" data-hours='%(hours)s'>
<div class="sd-media">
<div class="frame mask">%(p0)s</div>
<div class="frame mask" style="--d:.1s">%(p1)s</div>
<div class="frame mask" style="--d:.2s">%(p2)s</div>
</div>
<div class="sd-info">
<span class="num" data-rv>%(n)s</span>
%(h)s
<p class="lead" data-rv>%(text)s</p>
<span class="ostat" data-rv>Horaires</span>
<table class="hours" data-rv><caption class="sr">Horaires d'ouverture — %(name)s</caption>%(rows)s</table>
<dl class="facts" data-rv>
<dt>Adresse</dt><dd>%(street)s, %(city)s</dd>
<dt>Téléphone</dt><dd><a href="tel:%(tel)s">%(phone)s</a></dd>
<dt>Avis Google</dt><dd>%(stars)s %(rating)s sur 5 · %(count)d avis</dd>
</dl>
<div class="salon-links" data-rv style="margin-top:26px"><a class="chip" href="%(map)s" target="_blank" rel="noopener">%(pin)s Itinéraire</a><a class="chip" href="tel:%(tel)s">%(telico)s Appeler</a><a class="chip" href="%(rev)s" target="_blank" rel="noopener">%(star)s Avis</a></div>
<div class="map" data-map="%(embed)s" data-title="Carte — vXv Barber's %(name)s" data-rv><button type="button">%(pin)s Afficher la carte</button></div>
</div>
</section>""" % dict(key=s["key"], hours=json.dumps(s["hours"]), n=s["n"], name=s["name"],
                     h=lines(s["name"], "h2", "display h-l"), text=s["text"], rows=rows,
                     p0=pic(s["img"], "Le salon vXv Barber's à " + s["name"]), p1=pic(s["imgs"][0], "vXv Barber's " + s["name"]), p2=pic(s["imgs"][1], "vXv Barber's " + s["name"]),
                     street=s["street"], city=s["city"], tel=s["tel"], phone=s["phone"], stars=stars(5), rating=s["rating"], count=s["count"],
                     map=gmaps(s), pin=I["pin"], telico=I["tel"], rev=greviews(s), star=I["star"], embed=esc(gembed(s))))
    main = """<section class="phead"><div class="wrap">
<nav class="crumbs" aria-label="Fil d'Ariane" data-rv><a href="./">Accueil</a><span>/</span><span>Salons</span></nav>
%s
<p class="lead" data-rv style="--d:.3s">Crissier, Lausanne-Blécherette et Vevey. Trois salons sans rendez-vous, ouverts du lundi au samedi. Passez quand vous voulez — ou écrivez-nous sur WhatsApp pour connaître l’attente.</p>
</div></section>
<div class="wrap">%s</div>
""" % (lines("Trois adresses.|*Un seul standard.*", "h1", "display h-xl", .1), "".join(secs))
    return page("salons", "Nos salons — Crissier, Blécherette, Vevey | vXv Barber’s",
                "Adresses, horaires et accès des trois salons vXv Barber's : Rue du Jura 11 à Crissier, Route des Plaines-du-Loup 55 à Lausanne, Avenue Général-Guisan 52 à Vevey.",
                main, jsonld())

def prestations():
    prices = "".join('<li class="price" data-img="%s" data-rv style="--d:%ss"><span class="price-n">%02d</span><div><h3>%s</h3><p>%s</p></div><span class="price-v"><small>CHF</small>%s.–</span></li>'
                     % (img, i * .08, i + 1, n, desc, v) for i, (n, v, desc, img) in enumerate(PRICES))
    hover = '<div class="hover-img" aria-hidden="true">' + "".join('<img src="assets/img/%s.jpg" data-k="%s" alt="" loading="lazy">' % (img, img) for _, _, _, img in PRICES) + "</div>"
    steps = [("Vous passez", "Pas de rendez-vous. Choisissez le salon le plus proche et entrez — ou écrivez-nous avant pour connaître l’attente."),
             ("On écoute", "Photo, idée précise ou envie de changer : on prend le temps de comprendre avant de toucher à la tondeuse."),
             ("On finit", "Contours à la lame, dégradé fondu, coiffage. Vous repartez prêt, pas « presque ».")]
    st = "".join('<div class="stat" data-rv style="--d:%ss"><b class="num" style="font-weight:400;font-size:clamp(2rem,3vw,2.6rem)">0%d</b><h3 class="h-s display" style="margin:18px 0 12px">%s</h3><p class="muted" style="font-size:15px">%s</p></div>' % (i * .1, i + 1, t, p) for i, (t, p) in enumerate(steps))
    main = """<section class="phead"><div class="wrap">
<nav class="crumbs" aria-label="Fil d'Ariane" data-rv><a href="./">Accueil</a><span>/</span><span>Prestations</span></nav>
%(h1)s
<p class="lead" data-rv style="--d:.3s">Quatre prestations, des prix affichés, aucune surprise. Le reste, c’est du savoir-faire.</p>
</div></section>
<section class="sec" style="padding-top:0"><div class="wrap">
<ul class="prices">%(prices)s</ul>
<p class="note" data-rv>Tarifs affichés pour le salon de Crissier, à titre indicatif. Ils peuvent varier légèrement selon l’adresse — demandez-nous sur WhatsApp.</p>
%(hover)s
</div></section>
<section class="sec" style="padding-top:0"><div class="wrap">
<div class="split">
<div class="frame mask" style="aspect-ratio:4/5"><video data-auto muted loop playsinline preload="none" poster="assets/img/miroir.jpg" data-src="assets/video/miroir.mp4" aria-label="Un client dans le miroir après sa coupe"></video></div>
<div><span class="eyebrow" data-rv>Comment ça se passe</span>%(h2)s
<div class="stats" style="grid-template-columns:1fr;margin-top:40px;border-top:0">%(steps)s</div></div>
</div>
</div></section>
<section class="cta">
<div class="cta-bg"><img data-par="0.12" src="assets/img/lounge.jpg" alt="" loading="lazy"></div>
<div class="wrap"><span class="eyebrow" data-rv>Une question ?</span>%(ctah)s
<div class="hero-actions" data-rv><a class="btn btn-wa" href="%(wa)s" target="_blank" rel="noopener">%(waico)s Écrire sur WhatsApp</a><a class="btn btn-line" href="salons">Nos salons %(arr)s</a></div></div>
</section>
""" % dict(h1=lines("Simple.|*Affiché.*", "h1", "display h-xl", .1), prices=prices, hover=hover,
           h2=lines("Trois temps,|*zéro attente inutile.*", "h2", "display h-m"), steps=st,
           ctah=lines("On vous|*répond.*", "h2", "display h-xl"), wa=wa("Bonjour vXv, j’ai une question : "), waico=I["wa"], arr=I["arr"])
    return page("prestations", "Prestations & tarifs — vXv Barber’s",
                "Coupe CHF 25, coupe enfant CHF 22, barbe CHF 15, soin point noir CHF 7. Sans rendez-vous à Crissier, Lausanne-Blécherette et Vevey.", main)

def galerie():
    items = []
    for i, (n, cap, tags) in enumerate(GALLERY):
        items.append('<figure class="gitem" data-tags="%s" data-cap="%s" data-full="assets/img/%s.jpg" data-cursor="Voir" data-rv style="--d:%ss">%s</figure>'
                     % (tags, esc(cap), n, round((i % 4) * .06, 2), pic(n, cap)))
        if i == 5:
            items.append('<figure class="gitem" data-tags="videos" data-cap="La transformation" data-rv><video data-auto muted loop playsinline preload="none" poster="assets/img/avant.jpg" data-src="assets/video/transfo.mp4" aria-label="Vidéo : transformation complète"></video></figure>')
        if i == 13:
            items.append('<figure class="gitem" data-tags="videos" data-cap="Crissier en mouvement" data-rv><video data-auto muted loop playsinline preload="none" poster="assets/img/neon-close.jpg" data-src="assets/video/hero.mp4" aria-label="Vidéo : le salon de Crissier"></video></figure>')
        if i == 20:
            items.append('<figure class="gitem" data-tags="videos" data-cap="Dans le miroir" data-rv><video data-auto muted loop playsinline preload="none" poster="assets/img/miroir.jpg" data-src="assets/video/miroir.mp4" aria-label="Vidéo : un client dans le miroir"></video></figure>')
    main = """<section class="phead" style="padding-bottom:40px"><div class="wrap">
<nav class="crumbs" aria-label="Fil d'Ariane" data-rv><a href="./">Accueil</a><span>/</span><span>Galerie</span></nav>
%(h1)s
<p class="lead" data-rv style="--d:.3s">Des coupes sorties de nos fauteuils et nos trois salons, tels quels. Pour la suite, c’est sur <a class="link-u" href="%(ig)s" target="_blank" rel="noopener">Instagram</a> et <a class="link-u" href="%(tt)s" target="_blank" rel="noopener">TikTok</a>.</p>
</div></section>
<section style="padding-bottom:clamp(88px,12vw,160px)"><div class="wrap">
<div class="gfilters"><div class="filters" data-filter-group=".gitem" style="margin:0">
<button type="button" data-f="all" aria-pressed="true">Tout</button><button type="button" data-f="coupes" aria-pressed="false">Coupes</button><button type="button" data-f="salons" aria-pressed="false">Salons</button><button type="button" data-f="videos" aria-pressed="false">Vidéos</button>
</div></div>
<div class="masonry" style="margin-top:20px">%(items)s</div>
</div></section>
<div class="lb" aria-hidden="true" role="dialog" aria-label="Galerie en plein écran">
<div class="lb-top"><span class="lb-count"></span><button class="lb-x" type="button" aria-label="Fermer">%(x)s</button></div>
<div class="lb-stage"><img alt=""></div>
<div class="lb-bot"><button class="lb-prev" type="button" aria-label="Précédente">%(prev)s</button><span class="lb-cap"></span><button class="lb-next" type="button" aria-label="Suivante">%(next)s</button></div>
</div>
""" % dict(h1=lines("Le travail|*parle.*", "h1", "display h-xl", .1), items="".join(items), ig=IG, tt=TIKTOK, x=I["x"], prev=I["prev"], next=I["next"])
    return page("galerie", "Galerie — coupes et salons | vXv Barber’s",
                "Dégradés, motifs, barbes et nos salons de Crissier, Blécherette et Vevey en photos et vidéos.", main)

def avis():
    scores = "".join("""<div class="score" data-rv style="--d:%ss"><h3>%s</h3><b>%s</b>%s<span>%d avis Google</span>
<div class="salon-links" style="padding-top:0"><a class="chip" href="%s" target="_blank" rel="noopener">Lire %s</a><a class="chip" href="%s" target="_blank" rel="noopener">%s Laisser un avis</a></div></div>"""
                     % (i * .1, s["name"], s["rating"], stars(5), s["count"], greviews(s), I["ne"], gwrite(s), I["star"]) for i, s in enumerate(SALONS))
    cards = "".join('<article class="rcard" data-tags="%s" data-rv style="--d:%ss">%s<p>%s</p><footer><span class="av">%s</span><span><b>%s</b>%s · Google</span></footer></article>'
                    % (k, round((i % 3) * .08, 2), stars(5), esc(t), esc(n[0]), esc(n), SALON_NAME[k]) for i, (n, k, t) in enumerate(REVIEWS))
    main = """<section class="phead"><div class="wrap">
<nav class="crumbs" aria-label="Fil d'Ariane" data-rv><a href="./">Accueil</a><span>/</span><span>Avis</span></nav>
%(h1)s
<p class="lead" data-rv style="--d:.3s">%(total)d avis Google sur nos trois salons. Voici ce qu’en disent ceux qui sortent du fauteuil — mot pour mot.</p>
</div></section>
<section style="padding-bottom:clamp(88px,12vw,160px)"><div class="wrap">
<div class="scores">%(scores)s</div>
<div class="filters" data-filter-group=".rcard" data-rv>
<button type="button" data-f="all" aria-pressed="true">Tous</button><button type="button" data-f="crissier" aria-pressed="false">Crissier</button><button type="button" data-f="blecherette" aria-pressed="false">Blécherette</button><button type="button" data-f="vevey" aria-pressed="false">Vevey</button>
</div>
<div class="rcards">%(cards)s</div>
</div></section>
<section class="cta">
<div class="cta-bg"><img data-par="0.12" src="assets/img/mur-vegetal.jpg" alt="" loading="lazy"></div>
<div class="wrap"><span class="eyebrow" data-rv>Passé chez nous ?</span>%(ctah)s
<div class="hero-actions" data-rv>%(write)s</div></div>
</section>
""" % dict(h1=lines("Ils sortent|*du fauteuil.*", "h1", "display h-xl", .1), total=TOTAL_REVIEWS, scores=scores, cards=cards,
           ctah=lines("Dites-le|*aux autres.*", "h2", "display h-xl"),
           write="".join('<a class="btn %s" href="%s" target="_blank" rel="noopener">%s %s</a>' % ("btn-solid" if i == 0 else "btn-line", gwrite(s), I["star"], s["name"]) for i, s in enumerate(SALONS)))
    return page("avis", "Avis clients — vXv Barber’s",
                "%d avis Google sur les salons vXv Barber's de Crissier (4,6), Lausanne-Blécherette (5,0) et Vevey (5,0)." % TOTAL_REVIEWS, main)

def reseaux():
    main = """<section class="phead"><div class="wrap">
<nav class="crumbs" aria-label="Fil d'Ariane" data-rv><a href="./">Accueil</a><span>/</span><span>Réseaux</span></nav>
%(h1)s
<p class="lead" data-rv style="--d:.3s">Les coupes du jour, les coulisses, les concours et les nouvelles adresses : tout passe d’abord par nos réseaux.</p>
</div></section>
<section style="padding-bottom:clamp(88px,12vw,140px)"><div class="wrap">
<div class="socials">
<a class="soc" href="%(tt)s" target="_blank" rel="noopener" data-rv data-cursor="Suivre">
<div class="soc-bg"><video data-auto muted loop playsinline preload="none" poster="assets/img/miroir.jpg" data-src="assets/video/miroir.mp4"></video></div>
<span class="soc-ico">%(ttico)s</span><span class="go">%(ne)s</span>
<div><h3>TikTok</h3><div class="handle">@vxvbarbers</div>
<div class="soc-stats"><div><b>10,7K</b><span>abonnés</span></div><div><b>215,6K</b><span>j’aime</span></div><div><b>506K</b><span>vues, une vidéo</span></div></div></div>
</a>
<a class="soc" href="%(ig)s" target="_blank" rel="noopener" data-rv style="--d:.1s" data-cursor="Suivre">
<div class="soc-bg">%(p1)s</div>
<span class="soc-ico">%(igico)s</span><span class="go">%(ne)s</span>
<div><h3>Instagram</h3><div class="handle">@vxvbarbers · Crissier & Blécherette</div>
<div class="soc-stats"><div><b>3K</b><span>abonnés</span></div><div><b>96</b><span>publications</span></div></div></div>
</a>
<a class="soc" href="%(igv)s" target="_blank" rel="noopener" data-rv style="--d:.2s" data-cursor="Suivre">
<div class="soc-bg">%(p2)s</div>
<span class="soc-ico">%(igico)s</span><span class="go">%(ne)s</span>
<div><h3>Instagram Vevey</h3><div class="handle">@vxvvevey</div>
<div class="soc-stats"><div><b>527</b><span>abonnés</span></div><div><b>28</b><span>publications</span></div></div></div>
</a>
</div>
</div></section>
<section class="sec" style="padding-top:0"><div class="wrap">
<div class="split">
<div><span class="eyebrow" data-rv>WhatsApp</span>%(h2)s
<p class="lead" data-rv>L’attente du moment, un tarif, une coupe que vous avez vue sur TikTok ? Envoyez-nous un message — c’est le plus rapide.</p>
<div class="hero-actions" data-rv style="margin-top:30px"><a class="btn btn-wa" href="%(wa)s" target="_blank" rel="noopener">%(waico)s +41 76 757 86 36</a></div></div>
<div class="frame mask" style="aspect-ratio:4/5"><video data-auto muted loop playsinline preload="none" poster="assets/img/neon-close.jpg" data-src="assets/video/hero.mp4" aria-label="Le salon de Crissier en vidéo"></video><span class="frame-cap">Crissier · en direct du salon</span></div>
</div>
</div></section>
""" % dict(h1=lines("Suivez|*le fauteuil.*", "h1", "display h-xl", .1), tt=TIKTOK, ig=IG, igv=IG_VEVEY, ttico=I["tt"], igico=I["ig"], ne=I["ne"],
           p1=pic("lounge", ""), p2=pic("vevey", ""), h2=lines("Une question ?|*Un message.*", "h2", "display h-l"),
           wa=wa("Bonjour vXv, "), waico=I["wa"])
    return page("reseaux", "Réseaux — TikTok, Instagram, WhatsApp | vXv Barber’s",
                "Suivez vXv Barber's sur TikTok (@vxvbarbers, 215K j'aime) et Instagram (@vxvbarbers, @vxvvevey), ou écrivez-nous sur WhatsApp.", main)

def sitemap():
    urls = [BASE] + [BASE + k for k, _ in NAV]
    return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join("<url><loc>%s</loc></url>\n" % u for u in urls) + "</urlset>\n"

def icons():
    from PIL import ImageDraw, ImageFilter
    polys = [[(2,34),(12.5,34),(17,50),(21.5,34),(32,34),(21.5,68),(12.5,68)],[(38,2),(52,2),(82,68),(68,68)],[(68,2),(82,2),(52,68),(38,68)],[(88,34),(98.5,34),(103,50),(107.5,34),(118,34),(107.5,68),(98.5,68)]]
    def mark(im, cx, cy, w, col):
        k = w / 120.0; dr = ImageDraw.Draw(im)
        for pg in polys:
            dr.polygon([(cx - w / 2 + x * k, cy - 35 * k + y * k) for x, y in pg], fill=col)
    for size, name in [(180, "apple-touch-icon.png"), (32, "favicon-32.png")]:
        S = size * 4; im = Image.new("RGB", (S, S), (10, 10, 11)); mark(im, S / 2, S / 2, S * .7, (236, 230, 220))
        im.resize((size, size), Image.LANCZOS).save(os.path.join(IMG, name))
    with open(os.path.join(IMG, "favicon.svg"), "w") as f:
        f.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="-14 -36 148 148"><rect x="-14" y="-36" width="148" height="148" rx="30" fill="#0a0a0b"/><g fill="#ece6dc">' + MARK_POLY + '</g></svg>')
    bg = Image.open(os.path.join(IMG, "mur-vegetal.jpg")).convert("RGB")
    W, H = 1200, 630; r = max(W / bg.width, H / bg.height); bg = bg.resize((int(bg.width * r), int(bg.height * r)), Image.LANCZOS)
    bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2 - 40, (bg.width - W) // 2 + W, (bg.height - H) // 2 - 40 + H))
    ov = Image.new("RGB", (W, H), (10, 10, 11)); bg = Image.blend(bg, ov, .55)
    mark(bg, W / 2, H / 2 - 20, 360, (236, 230, 220))
    bg.save(os.path.join(IMG, "og.jpg"), quality=84)

if __name__ == "__main__":
    icons()
    pages = dict(index=index(), salons=salons(), prestations=prestations(), galerie=galerie(), avis=avis(), reseaux=reseaux())
    for k, v in pages.items():
        with open(os.path.join(OUT, k + ".html"), "w", encoding="utf-8") as f:
            f.write(v)
    with open(os.path.join(OUT, "sitemap.xml"), "w") as f:
        f.write(sitemap())
    with open(os.path.join(OUT, "robots.txt"), "w") as f:
        f.write("User-agent: *\nAllow: /\nSitemap: %ssitemap.xml\n" % BASE)
    open(os.path.join(OUT, ".nojekyll"), "w").close()
    with open(os.path.join(OUT, "404.html"), "w", encoding="utf-8") as f:
        f.write(page("404", "Page introuvable — vXv Barber’s", "Cette page n'existe pas.",
                     '<section class="phead" style="min-height:80svh"><div class="wrap">%s<p class="lead" data-rv>Cette page n’existe pas — mais nos fauteuils, si.</p><div class="hero-actions" data-rv><a class="btn btn-solid" href="./">Accueil %s</a></div></div></section>'
                     % (lines("Coupe|*ratée.*", "h1", "display h-xl"), I["arr"])).replace("<head>\n", '<head>\n<base href="/vxvbarbers/">\n', 1))
    print("built", ", ".join(pages))
