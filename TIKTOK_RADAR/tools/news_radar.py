#!/usr/bin/env python3
"""
TIKTOK RADAR · Módulo de Ingesta y Monitoreo de Noticias (News Scout)
Rastrea fuentes reconocidas (Xataka, agencias oficiales y tecnológicas)
y categoriza las noticias para producción automatizada de video vertical.
"""

import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Any

FEEDS = [
    {
        "id": "xataka",
        "name": "Xataka Tecnología & Ciencia",
        "url": "https://www.xataka.com/feedburner.xml",
        "type": "Especializada / Análisis contrastado",
        "weight": 1.0,
    },
    {
        "id": "bbc_mundo",
        "name": "BBC Mundo (Internacional / Impacto)",
        "url": "https://feeds.bbci.co.uk/mundo/rss.xml",
        "type": "Generalista / Corroborada global",
        "weight": 1.2,
    },
    {
        "id": "elpais_tec",
        "name": "El País Tecnología",
        "url": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/tecnologia/portada",
        "type": "Medio de referencia",
        "weight": 0.9,
    },
]


def fetch_feed(feed_info: Dict[str, Any], max_items: int = 5) -> List[Dict[str, Any]]:
    items = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        req = urllib.request.Request(feed_info["url"], headers=headers)
        with urllib.request.urlopen(req, timeout=8) as response:
            xml_data = response.read()
        root = ET.fromstring(xml_data)
        
        # Soportar RSS y Atom
        xml_items = root.findall(".//item")
        if not xml_items:
            xml_items = root.findall(".//{http://www.w3.org/2005/Atom}entry")
            
        for item in xml_items[:max_items]:
            title_node = item.find("title")
            if title_node is None:
                title_node = item.find("{http://www.w3.org/2005/Atom}title")

            link_node = item.find("link")
            if link_node is None:
                link_node = item.find("{http://www.w3.org/2005/Atom}link")

            desc_node = item.find("description")
            if desc_node is None:
                desc_node = item.find("{http://www.w3.org/2005/Atom}summary")

            date_node = item.find("pubDate")
            if date_node is None:
                date_node = item.find("{http://www.w3.org/2005/Atom}updated")

            title = title_node.text.strip() if (title_node is not None and title_node.text) else "Sin título"
            
            link = ""
            if link_node is not None:
                link = link_node.text.strip() if link_node.text else link_node.attrib.get("href", "")
                
            desc = desc_node.text.strip() if (desc_node is not None and desc_node.text) else ""
            # Limpiar etiquetas HTML simples si existen
            if "<" in desc and ">" in desc:
                import re
                desc = re.sub(r"<[^>]+>", "", desc).strip()
                
            pub_date = date_node.text.strip() if (date_node is not None and date_node.text) else ""

            # Determinar potencial de recreación dramática (presencia de eventos físicos, vuelos, colapsos, gadgets, descubrimientos)
            has_action = any(k in title.lower() for k in ["avión", "accidente", "ia", "robot", "cohete", "espacial", "fallo", "alerta", "crisis", "golpe", "viral"])
            
            items.append({
                "source_id": feed_info["id"],
                "source_name": feed_info["name"],
                "source_type": feed_info["type"],
                "title": title,
                "link": link,
                "summary": desc[:250] + ("..." if len(desc) > 250 else ""),
                "pub_date": pub_date,
                "needs_dramatic_recreation": has_action,
            })
    except Exception as e:
        print(f"[Error consultando {feed_info['name']}]: {e}")
    return items


def scan_all_sources(max_per_source: int = 4) -> List[Dict[str, Any]]:
    all_news = []
    for f in FEEDS:
        all_news.extend(fetch_feed(f, max_items=max_per_source))
    return all_news


if __name__ == "__main__":
    news = scan_all_sources(max_per_source=3)
    print(f"=== TIKTOK RADAR · NOTICIAS DETECTADAS ({len(news)} titulares) ===")
    for idx, n in enumerate(news, 1):
        mode = "🎬 RECREACIÓN 3D DRAMÁTICA" if n["needs_dramatic_recreation"] else "📊 INFOGRAFÍA 3D DINÁMICA"
        print(f"\n{idx}. [{n['source_name']}]")
        print(f"   Título: {n['title']}")
        print(f"   Tipo: {n['source_type']} | Enfoque visual: {mode}")
        print(f"   Link: {n['link']}")
