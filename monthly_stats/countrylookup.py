"""
countrylookup.py — ISO 3166-1 alpha-2 country code → English name

Used by the Monthly Stats notebooks to display readable country names in
chart labels and dropdown menus instead of raw two-letter codes.

Resolution order
----------------
1. pycountry (most accurate; install with ``pip install pycountry``)
2. restcountries.com public API (fetched once, cached to
   ``cache/country_names.json`` relative to the working directory)
3. Built-in dict covering all 249 ISO 3166-1 alpha-2 codes + XK (Kosovo)

Public API
----------
cc_name(code)   → str   e.g. "US" → "United States"
cc_label(code)  → str   e.g. "US" → "United States (US)"
"""

from __future__ import annotations

import json
from pathlib import Path

try:
    import requests as _requests
except ImportError:
    _requests = None  # type: ignore[assignment]

# ---------------------------------------------------------------------------
# Short-form overrides for codes whose ISO official name is long or obscure
# ---------------------------------------------------------------------------
_CC_OVERRIDES: dict[str, str] = {
    "BO": "Bolivia",
    "BQ": "Bonaire / St. Eustatius",
    "CD": "DR Congo",
    "IR": "Iran",
    "KP": "North Korea",
    "KR": "South Korea",
    "FM": "Micronesia",
    "MD": "Moldova",
    "PS": "Palestine",
    "RU": "Russia",
    "SH": "St. Helena",
    "SY": "Syria",
    "TW": "Taiwan",
    "TZ": "Tanzania",
    "VE": "Venezuela",
    "VG": "British Virgin Islands",
    "VI": "U.S. Virgin Islands",
    "VN": "Vietnam",
    "XK": "Kosovo",          # not in ISO standard; used by MaxMind / M-Lab
}

# ---------------------------------------------------------------------------
# Built-in fallback — all 249 ISO 3166-1 alpha-2 codes, offline-safe
# ---------------------------------------------------------------------------
_CC_BUILTIN: dict[str, str] = {
    "AD":"Andorra","AE":"United Arab Emirates","AF":"Afghanistan",
    "AG":"Antigua and Barbuda","AI":"Anguilla","AL":"Albania",
    "AM":"Armenia","AO":"Angola","AQ":"Antarctica",
    "AR":"Argentina","AS":"American Samoa","AT":"Austria",
    "AU":"Australia","AW":"Aruba","AX":"Åland Islands",
    "AZ":"Azerbaijan","BA":"Bosnia and Herzegovina","BB":"Barbados",
    "BD":"Bangladesh","BE":"Belgium","BF":"Burkina Faso",
    "BG":"Bulgaria","BH":"Bahrain","BI":"Burundi",
    "BJ":"Benin","BL":"Saint Barthélemy","BM":"Bermuda",
    "BN":"Brunei Darussalam","BO":"Bolivia, Plurinational State of","BQ":"Bonaire, Sint Eustatius and Saba",
    "BR":"Brazil","BS":"Bahamas","BT":"Bhutan",
    "BV":"Bouvet Island","BW":"Botswana","BY":"Belarus",
    "BZ":"Belize","CA":"Canada","CC":"Cocos (Keeling) Islands",
    "CD":"Congo, The Democratic Republic of the","CF":"Central African Republic","CG":"Congo",
    "CH":"Switzerland","CI":"Côte d'Ivoire","CK":"Cook Islands",
    "CL":"Chile","CM":"Cameroon","CN":"China",
    "CO":"Colombia","CR":"Costa Rica","CU":"Cuba",
    "CV":"Cabo Verde","CW":"Curaçao","CX":"Christmas Island",
    "CY":"Cyprus","CZ":"Czechia","DE":"Germany",
    "DJ":"Djibouti","DK":"Denmark","DM":"Dominica",
    "DO":"Dominican Republic","DZ":"Algeria","EC":"Ecuador",
    "EE":"Estonia","EG":"Egypt","EH":"Western Sahara",
    "ER":"Eritrea","ES":"Spain","ET":"Ethiopia",
    "FI":"Finland","FJ":"Fiji","FK":"Falkland Islands (Malvinas)",
    "FM":"Micronesia, Federated States of","FO":"Faroe Islands","FR":"France",
    "GA":"Gabon","GB":"United Kingdom","GD":"Grenada",
    "GE":"Georgia","GF":"French Guiana","GG":"Guernsey",
    "GH":"Ghana","GI":"Gibraltar","GL":"Greenland",
    "GM":"Gambia","GN":"Guinea","GP":"Guadeloupe",
    "GQ":"Equatorial Guinea","GR":"Greece","GS":"South Georgia and the South Sandwich Islands",
    "GT":"Guatemala","GU":"Guam","GW":"Guinea-Bissau",
    "GY":"Guyana","HK":"Hong Kong","HM":"Heard Island and McDonald Islands",
    "HN":"Honduras","HR":"Croatia","HT":"Haiti",
    "HU":"Hungary","ID":"Indonesia","IE":"Ireland",
    "IL":"Israel","IM":"Isle of Man","IN":"India",
    "IO":"British Indian Ocean Territory","IQ":"Iraq","IR":"Iran, Islamic Republic of",
    "IS":"Iceland","IT":"Italy","JE":"Jersey",
    "JM":"Jamaica","JO":"Jordan","JP":"Japan",
    "KE":"Kenya","KG":"Kyrgyzstan","KH":"Cambodia",
    "KI":"Kiribati","KM":"Comoros","KN":"Saint Kitts and Nevis",
    "KP":"Korea, Democratic People's Republic of","KR":"Korea, Republic of","KW":"Kuwait",
    "KY":"Cayman Islands","KZ":"Kazakhstan","LA":"Lao People's Democratic Republic",
    "LB":"Lebanon","LC":"Saint Lucia","LI":"Liechtenstein",
    "LK":"Sri Lanka","LR":"Liberia","LS":"Lesotho",
    "LT":"Lithuania","LU":"Luxembourg","LV":"Latvia",
    "LY":"Libya","MA":"Morocco","MC":"Monaco",
    "MD":"Moldova, Republic of","ME":"Montenegro","MF":"Saint Martin (French part)",
    "MG":"Madagascar","MH":"Marshall Islands","MK":"North Macedonia",
    "ML":"Mali","MM":"Myanmar","MN":"Mongolia",
    "MO":"Macao","MP":"Northern Mariana Islands","MQ":"Martinique",
    "MR":"Mauritania","MS":"Montserrat","MT":"Malta",
    "MU":"Mauritius","MV":"Maldives","MW":"Malawi",
    "MX":"Mexico","MY":"Malaysia","MZ":"Mozambique",
    "NA":"Namibia","NC":"New Caledonia","NE":"Niger",
    "NF":"Norfolk Island","NG":"Nigeria","NI":"Nicaragua",
    "NL":"Netherlands","NO":"Norway","NP":"Nepal",
    "NR":"Nauru","NU":"Niue","NZ":"New Zealand",
    "OM":"Oman","PA":"Panama","PE":"Peru",
    "PF":"French Polynesia","PG":"Papua New Guinea","PH":"Philippines",
    "PK":"Pakistan","PL":"Poland","PM":"Saint Pierre and Miquelon",
    "PN":"Pitcairn","PR":"Puerto Rico","PS":"Palestine, State of",
    "PT":"Portugal","PW":"Palau","PY":"Paraguay",
    "QA":"Qatar","RE":"Réunion","RO":"Romania",
    "RS":"Serbia","RU":"Russian Federation","RW":"Rwanda",
    "SA":"Saudi Arabia","SB":"Solomon Islands","SC":"Seychelles",
    "SD":"Sudan","SE":"Sweden","SG":"Singapore",
    "SH":"Saint Helena, Ascension and Tristan da Cunha","SI":"Slovenia","SJ":"Svalbard and Jan Mayen",
    "SK":"Slovakia","SL":"Sierra Leone","SM":"San Marino",
    "SN":"Senegal","SO":"Somalia","SR":"Suriname",
    "SS":"South Sudan","ST":"Sao Tome and Principe","SV":"El Salvador",
    "SX":"Sint Maarten (Dutch part)","SY":"Syrian Arab Republic","SZ":"Eswatini",
    "TC":"Turks and Caicos Islands","TD":"Chad","TF":"French Southern Territories",
    "TG":"Togo","TH":"Thailand","TJ":"Tajikistan",
    "TK":"Tokelau","TL":"Timor-Leste","TM":"Turkmenistan",
    "TN":"Tunisia","TO":"Tonga","TR":"Türkiye",
    "TT":"Trinidad and Tobago","TV":"Tuvalu","TW":"Taiwan, Province of China",
    "TZ":"Tanzania, United Republic of","UA":"Ukraine","UG":"Uganda",
    "UM":"United States Minor Outlying Islands","US":"United States","UY":"Uruguay",
    "UZ":"Uzbekistan","VA":"Holy See (Vatican City State)","VC":"Saint Vincent and the Grenadines",
    "VE":"Venezuela, Bolivarian Republic of","VG":"Virgin Islands, British","VI":"Virgin Islands, U.S.",
    "VN":"Viet Nam","VU":"Vanuatu","WF":"Wallis and Futuna",
    "WS":"Samoa","YE":"Yemen","YT":"Mayotte",
    "ZA":"South Africa","ZM":"Zambia","ZW":"Zimbabwe",
}


def _build_cc_names() -> dict[str, str]:
    # 1. pycountry — most accurate; install with: pip install pycountry
    try:
        import pycountry
        names = {c.alpha_2: c.name for c in pycountry.countries}
        names.update(_CC_OVERRIDES)
        return names
    except ImportError:
        pass

    # 2. restcountries.com public API, cached to disk, with robust validation
    cache_path = Path("cache/country_names.json")
    data = None

    if cache_path.exists():
        try:
            loaded = json.loads(cache_path.read_text())
            if isinstance(loaded, list) and loaded and isinstance(loaded[0], dict):
                data = loaded
            else:
                cache_path.unlink()   # stale or corrupted — delete and re-fetch
        except Exception:
            cache_path.unlink(missing_ok=True)

    if data is None and _requests is not None:
        try:
            print("[countrylookup] downloading country names from restcountries.com ...")
            r = _requests.get(
                "https://restcountries.com/v3.1/all?fields=name,cca2",
                timeout=15,
            )
            r.raise_for_status()
            fetched = r.json()
            if isinstance(fetched, list) and fetched and isinstance(fetched[0], dict):
                data = fetched
                cache_path.parent.mkdir(parents=True, exist_ok=True)
                cache_path.write_text(r.text)
        except Exception as exc:
            print(f"[countrylookup] restcountries unavailable ({exc}); using built-in names")

    if data is not None:
        try:
            names = {
                c["cca2"]: c["name"]["common"]
                for c in data
                if "cca2" in c and "name" in c
            }
            names.update(_CC_OVERRIDES)
            return names
        except Exception:
            pass

    # 3. Built-in fallback — always works offline
    names = dict(_CC_BUILTIN)
    names.update(_CC_OVERRIDES)
    return names


_CC_NAMES: dict[str, str] = _build_cc_names()


def cc_name(code: str) -> str:
    """Return the short English country name for an ISO 3166-1 alpha-2 code.

    Falls back to the raw code if the code is unknown.

    >>> cc_name("US")
    'United States'
    >>> cc_name("ZZ")
    'ZZ'
    """
    return _CC_NAMES.get(code, code)


def cc_label(code: str) -> str:
    """Return 'Name (XX)' for dropdown options and chart legends.

    >>> cc_label("US")
    'United States (US)'
    """
    name = cc_name(code)
    return f"{name} ({code})" if name != code else code
