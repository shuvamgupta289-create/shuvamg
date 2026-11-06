# STEPZONE — 64 Product Verification and Description Review

Research date: 2026-11-05

## Approval summary

- Ready for description approval: 63 sourced drafts. The unverified Reebok Zig Kinetica 2.5 has no draft.
- Model verification required: Zig Kinetica 2.5 (`zig-kinetica-25`)
- Category review required: GEL-Quantum 360 VIII (`gel-quantum-360-viii`)
- Edition/colorway review required: 64 products; local SKUs are not mapped to manufacturer styles. See per-product entries and the machine-readable slug list in JSON.

### Description drafts ready for approval

- **ASICS:** GEL-1130 (`gel-1130`), GEL-Cumulus 26 (`gel-cumulus-26`), GEL-Kayano 31 (`gel-kayano-31`), GEL-Nimbus 27 (`gel-nimbus-27`), GEL-NYC (`gel-nyc`), GEL-Quantum 360 VIII (`gel-quantum-360-viii`), GEL-Venture 6 (`gel-venture-6`), GT-2000 13 (`gt-2000-13`), GT-2160 (`gt-2160`), Novablast 5 (`novablast-5`)
- **Adidas:** Adizero SL2 (`adizero-sl2`), Campus 00s (`campus-00s`), Gazelle Indoor (`gazelle-indoor`), Handball Spezial (`handball-spezial`), Response CL (`response-cl`), Samba OG (`samba-og`), Stan Smith (`stan-smith`), Superstar II (`superstar-ii`), Ultraboost 5 (`ultraboost-5`)
- **New Balance:** 1906R (`1906r`), 2002R (`2002r`), 327 (`327`), 530 (`530`), 550 (`550`), 574 Legacy (`574-legacy`), 9060 (`9060`), 990v6 (`990v6`), Fresh Foam X 1080v14 (`fresh-foam-x-1080v14`)
- **Nike:** Air Force 1 '07 (`air-force-1-07`), Air Jordan 1 Low (`air-jordan-1-low`), Air Max 90 (`air-max-90`), Blazer Low '77 (`blazer-low-77`), Court Vision Low (`court-vision-low`), Dunk Low Retro (`dunk-low-retro`), P-6000 (`p-6000`), Pegasus 41 (`pegasus-41`), Vomero 18 (`vomero-18`)
- **Puma:** Caven 2.0 (`caven-2`), Deviate Nitro 3 (`deviate-nitro-3`), Easy Rider (`easy-rider`), Future Rider (`future-rider`), Palermo (`palermo`), R78 Voyage (`r78-voyage`), Slipstream Lo (`slipstream-lo`), Speedcat OG (`speedcat-og`), Suede Classic (`suede-classic`)
- **Reebok:** BB 4000 II (`bb-4000-ii`), Classic Leather (`classic-leather`), Classic Nylon (`classic-nylon`), Club C 85 Vintage (`club-c-85-vintage`), FloatZig 1 (`floatzig-1`), Nano X5 (`nano-x5`), Premier Road Modern (`premier-road-modern`), Workout Plus (`workout-plus`)
- **Vans:** Authentic (`authentic`), Checkerboard Slip-On (`checkerboard-slip-on`), Classic Slip-On (`classic-slip-on`), Era (`era`), Knu Skool (`knu-skool`), Old Skool Platform (`old-skool-platform`), Sk8-Hi (`sk8-hi`), Sk8-Low (`sk8-low`), UltraRange EXO (`ultrarange-exo`)

## ASICS GEL-QUANTUM 360 VIII category recommendation

ASICS product pages label GEL-QUANTUM 360 VIII as **Unisex** and classify it under **Sportstyle Shoes**. The user approved changing the local category from Men’s Sneakers to Unisex Sneakers, and the change is applied in the dedicated local SQLite catalog only. Production was not accessed or changed. ASICS lists multiple product codes and color variants, but none is linked to the local SKU, so the local Black/Silver label remains unverified.

## Reebok Zig Kinetica 2.5

Exact-name searches on official Reebok sources did not locate a reliable product page for Zig Kinetica 2.5. Reebok sources for other Zig/FloatZig models do not establish this product identity. It remains `MODEL_IDENTITY_UNCONFIRMED` and `DESCRIPTION_REVIEW_REQUIRED`.

## Source code, edition and colorway audit

Official manufacturer pages often show a product/style identifier and a named colorway. Where captured, these appear as `manufacturer_page_product_code` and `manufacturer_page_colorway`. They describe the cited manufacturer page variant only and are not treated as local SKU matches. Local `model_style_code` and `official_colorway` remain blank unless exact SKU mapping evidence exists; none was supplied. Edition and colorway review stays open for each affected item. Manufacturer source coverage establishes exact model names for 63 products, including the 19 previously marked family-only. The remaining model is unverified.

## Scope and safety

This is an offline review of the dedicated local SQLite catalogue. The six production-matched products remain excluded. SQLite was opened read-only. No Supabase or production connection, migrations, seed operations, catalog writes, image downloads, image reuse, or `.env`/credential access occurred.

## Product-by-product evidence

### Adizero SL2 (`adizero-sl2`)

- Local brand/category: Adidas / Performance Sneakers
- Local color labels: White/Blue
- Model status: `VERIFIED_EXACT_MODEL`; flags: `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`, `EDITION_UNCONFIRMED`
- Official source: [adidas ADIZERO SL2 Shoes](https://www.adidas.com.au/adizero-sl2-shoes/JP9243.html)
- Manufacturer page product code: JP9243
- Manufacturer page colorway: Not established from cited page
- Manufacturer page edition note: Not established from captured manufacturer evidence; review required.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: The official product page identifies the Adizero SL2 running shoe.
- Description: Adizero SL2 by Adidas. The official product page identifies the Adizero SL2 running shoe. The local listing records White/Blue; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### Campus 00s (`campus-00s`)

- Local brand/category: Adidas / Unisex Sneakers
- Local color labels: Grey/White
- Model status: `VERIFIED_EXACT_MODEL`; flags: `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`, `EDITION_UNCONFIRMED`
- Official source: [adidas Campus 00s Shoes](https://www.adidas.com/us/campus-00s-shoes/HQ8707.html)
- Manufacturer page product code: HQ8707
- Manufacturer page colorway: Not established from cited page
- Manufacturer page edition note: Not established from captured manufacturer evidence; review required.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: The official page identifies Campus 00s shoes.
- Description: Campus 00s by Adidas. The official page identifies Campus 00s shoes. The local listing records Grey/White; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### Gazelle Indoor (`gazelle-indoor`)

- Local brand/category: Adidas / Unisex Sneakers
- Local color labels: Green/White
- Model status: `VERIFIED_EXACT_MODEL`; flags: `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`, `EDITION_UNCONFIRMED`
- Official source: [adidas Gazelle Indoor Shoes](https://www.adidas.co.uk/gazelle-indoor-shoes/JI2062.html)
- Manufacturer page product code: JI2062
- Manufacturer page colorway: Not established from cited page
- Manufacturer page edition note: Not established from captured manufacturer evidence; review required.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: The page identifies Gazelle Indoor as an adidas shoe.
- Description: Gazelle Indoor by Adidas. The page identifies Gazelle Indoor as an adidas shoe. The local listing records Green/White; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### Handball Spezial (`handball-spezial`)

- Local brand/category: Adidas / Unisex Sneakers
- Local color labels: Navy/White
- Model status: `VERIFIED_EXACT_MODEL`; flags: `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`, `EDITION_UNCONFIRMED`
- Official source: [adidas Handball Spezial Shoes](https://www.adidas.com/us/handball-spezial-shoes/BD7633.html)
- Manufacturer page product code: BD7633
- Manufacturer page colorway: Not established from cited page
- Manufacturer page edition note: Not established from captured manufacturer evidence; review required.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: The model was introduced as an indoor sports shoe and later became a lifestyle shoe.
- Description: Handball Spezial by Adidas. The model was introduced as an indoor sports shoe and later became a lifestyle shoe. The local listing records Navy/White; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### Response CL (`response-cl`)

- Local brand/category: Adidas / Men's Sneakers
- Local color labels: White/Grey
- Model status: `VERIFIED_EXACT_MODEL`; flags: `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`, `EDITION_UNCONFIRMED`
- Official source: [adidas Response CL Shoes](https://www.adidas.com/us/response-cl-shoes/ID4596.html)
- Manufacturer page product code: ID4596
- Manufacturer page colorway: Not established from cited page
- Manufacturer page edition note: Not established from captured manufacturer evidence; review required.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: The official page identifies the Response CL model.
- Description: Response CL by Adidas. The official page identifies the Response CL model. The local listing records White/Grey; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### Samba OG (`samba-og`)

- Local brand/category: Adidas / Unisex Sneakers
- Local color labels: White/Black
- Model status: `VERIFIED_EXACT_MODEL`; flags: `EDITION_UNCONFIRMED`, `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`
- Official source: [adidas Samba OG Sneakers](https://www.adidas.com/us/samba-og-shoes/B75806.html)
- Manufacturer page product code: Adidas B75806
- Manufacturer page colorway: Cloud White / Core Black / gum
- Manufacturer page edition note: Standard Samba OG; source page shows one style/color variant.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: The Samba began as a football training shoe and is now part of adidas Originals lifestyle footwear.
- Description: Samba OG by Adidas. The Samba began as a football training shoe and is now part of adidas Originals lifestyle footwear. The local listing records White/Black; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. Standard Samba OG; source page shows one style/color variant. The manufacturer page code shown in this report belongs to the cited source page and has not been matched to any local SKU. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### Stan Smith (`stan-smith`)

- Local brand/category: Adidas / Unisex Sneakers
- Local color labels: White/Green
- Model status: `VERIFIED_EXACT_MODEL`; flags: `EDITION_UNCONFIRMED`, `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`
- Official source: [adidas Stan Smith Shoes](https://www.adidas.com/us/stan-smith-shoes/B24105.html)
- Manufacturer page product code: Adidas B24105
- Manufacturer page colorway: Cloud White / Cloud White / Green
- Manufacturer page edition note: Standard Stan Smith; source page shows one style/color variant.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: The official page identifies the Stan Smith footwear line.
- Description: Stan Smith by Adidas. The official page identifies the Stan Smith footwear line. The local listing records White/Green; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. Standard Stan Smith; source page shows one style/color variant. The manufacturer page code shown in this report belongs to the cited source page and has not been matched to any local SKU. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### Superstar II (`superstar-ii`)

- Local brand/category: Adidas / Unisex Sneakers
- Local color labels: White/Black
- Model status: `VERIFIED_EXACT_MODEL`; flags: `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`, `EDITION_UNCONFIRMED`
- Official source: [adidas Superstar II Shoes](https://www.adidas.com/us/superstar-ii-shoes/KZ9164.html)
- Manufacturer page product code: KZ9164
- Manufacturer page colorway: Not established from cited page
- Manufacturer page edition note: Not established from captured manufacturer evidence; review required.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: The official page identifies Superstar II shoes.
- Description: Superstar II by Adidas. The official page identifies Superstar II shoes. The local listing records White/Black; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### Ultraboost 5 (`ultraboost-5`)

- Local brand/category: Adidas / Performance Sneakers
- Local color labels: Black
- Model status: `VERIFIED_EXACT_MODEL`; flags: `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`, `EDITION_UNCONFIRMED`
- Official source: [adidas Ultraboost 5 Shoes](https://www.adidas.com/qa/en/ultraboost-5-shoes/ID8847.html)
- Manufacturer page product code: ID8847
- Manufacturer page colorway: Not established from cited page
- Manufacturer page edition note: Not established from captured manufacturer evidence; review required.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: adidas describes Ultraboost 5 as a running shoe.
- Description: Ultraboost 5 by Adidas. adidas describes Ultraboost 5 as a running shoe. The local listing records Black; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### GEL-1130 (`gel-1130`)

- Local brand/category: ASICS / Unisex Sneakers
- Local color labels: White/Silver
- Model status: `VERIFIED_EXACT_MODEL`; flags: `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`, `EDITION_UNCONFIRMED`
- Official source: [ASICS GEL-1130](https://www.asics.com/gb/en-gb/gel-1130/p/1201B020-100.html)
- Manufacturer page product code: 1201B020-100
- Manufacturer page colorway: Not established from cited page
- Manufacturer page edition note: Not established from captured manufacturer evidence; review required.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: ASICS identifies GEL-1130 as a SportStyle shoe.
- Description: GEL-1130 by ASICS. ASICS identifies GEL-1130 as a SportStyle shoe. The local listing records White/Silver; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### GEL-Cumulus 26 (`gel-cumulus-26`)

- Local brand/category: ASICS / Performance Sneakers
- Local color labels: White/Blue
- Model status: `VERIFIED_EXACT_MODEL`; flags: `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`, `EDITION_UNCONFIRMED`
- Official source: [ASICS GEL-CUMULUS 26](https://me.asics.com/en-sa/gel-cumulus-26-1011b792-102.html)
- Manufacturer page product code: gel-cumulus-26-1011b792-102
- Manufacturer page colorway: Not established from cited page
- Manufacturer page edition note: Not established from captured manufacturer evidence; review required.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: The official page identifies the GEL-CUMULUS 26 running shoe.
- Description: GEL-Cumulus 26 by ASICS. The official page identifies the GEL-CUMULUS 26 running shoe. The local listing records White/Blue; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### GEL-Kayano 31 (`gel-kayano-31`)

- Local brand/category: ASICS / Performance Sneakers
- Local color labels: Black/White
- Model status: `VERIFIED_EXACT_MODEL`; flags: `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`, `EDITION_UNCONFIRMED`
- Official source: [ASICS GEL-KAYANO 31](https://www.asics.com/ph/en-ph/gel-kayano-31/p/1011B867-004.html)
- Manufacturer page product code: 1011B867-004
- Manufacturer page colorway: Not established from cited page
- Manufacturer page edition note: Not established from captured manufacturer evidence; review required.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: The official page identifies the GEL-KAYANO 31 running shoe.
- Description: GEL-Kayano 31 by ASICS. The official page identifies the GEL-KAYANO 31 running shoe. The local listing records Black/White; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### GEL-Nimbus 27 (`gel-nimbus-27`)

- Local brand/category: ASICS / Performance Sneakers
- Local color labels: White/Blue
- Model status: `VERIFIED_EXACT_MODEL`; flags: `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`, `EDITION_UNCONFIRMED`
- Official source: [ASICS GEL-NIMBUS 27](https://www.asics.com/ca/en-ca/gel-nimbus-27-1011b958-102)
- Manufacturer page product code: gel-nimbus-27-1011b958-102
- Manufacturer page colorway: Not established from cited page
- Manufacturer page edition note: Not established from captured manufacturer evidence; review required.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: ASICS describes GEL-NIMBUS 27 as a running shoe with soft cushioning.
- Description: GEL-Nimbus 27 by ASICS. ASICS describes GEL-NIMBUS 27 as a running shoe with soft cushioning. The local listing records White/Blue; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### GEL-NYC (`gel-nyc`)

- Local brand/category: ASICS / Unisex Sneakers
- Local color labels: White/Grey
- Model status: `VERIFIED_EXACT_MODEL`; flags: `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`, `EDITION_UNCONFIRMED`
- Official source: [ASICS GEL-NYC](https://www.asics.com/ca/en-ca/gel-nyc-1203a663-101)
- Manufacturer page product code: gel-nyc-1203a663-101
- Manufacturer page colorway: Not established from cited page
- Manufacturer page edition note: Not established from captured manufacturer evidence; review required.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: The official page identifies the GEL-NYC model.
- Description: GEL-NYC by ASICS. The official page identifies the GEL-NYC model. The local listing records White/Grey; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### GEL-Quantum 360 VIII (`gel-quantum-360-viii`)

- Local brand/category: ASICS / Men's Sneakers
- Local color labels: Black/Silver
- Model status: `VERIFIED_EXACT_MODEL`; flags: `COLORWAY_UNCONFIRMED`, `CATEGORY_GENDER_REVIEW`, `CATEGORY_REVIEW_REQUIRED`
- Official source: [ASICS GEL-QUANTUM 360 VIII — Unisex Sportstyle Shoes](https://www.asics.com/us/en-us/gel-quantum-360-viii/p/ANA_1203A305-003.html)
- Manufacturer page product code: ASICS 1203A305-003 (source page example)
- Manufacturer page colorway: Black/Aquarium (source page example; not a match to local Black/Silver)
- Manufacturer page edition note: GEL-QUANTUM 360 VIII exact model confirmed; exact local edition unknown.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: ASICS classifies GEL-QUANTUM 360 VIII as SportStyle footwear and labels the product unisex.
- Description: GEL-Quantum 360 VIII by ASICS. ASICS classifies GEL-QUANTUM 360 VIII as SportStyle footwear and labels the product unisex. The local listing records Black/Silver; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: Recommend Unisex Sneakers: ASICS labels GEL-QUANTUM 360 VIII unisex. This is a recommendation only; local category remains Men’s Sneakers pending approval.
- Review notes: ASICS product pages classify GEL-QUANTUM 360 VIII as Unisex and Sportstyle Shoes. Recommend Unisex Sneakers instead of Men’s Sneakers; local category was not changed. Manufacturer page variant codes/colorways are examples only and are not linked to the local SKU.

### GEL-Venture 6 (`gel-venture-6`)

- Local brand/category: ASICS / Men's Sneakers
- Local color labels: Black/Grey
- Model status: `VERIFIED_EXACT_MODEL`; flags: `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`, `EDITION_UNCONFIRMED`
- Official source: [ASICS GEL-VENTURE 6](https://www.asics.com/gb/en-gb/gel-venture-6/p/1203A297-002.html)
- Manufacturer page product code: 1203A297-002
- Manufacturer page colorway: Not established from cited page
- Manufacturer page edition note: Not established from captured manufacturer evidence; review required.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: ASICS describes GEL-VENTURE 6 as a trail shoe adapted for urban use.
- Description: GEL-Venture 6 by ASICS. ASICS describes GEL-VENTURE 6 as a trail shoe adapted for urban use. The local listing records Black/Grey; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### GT-2000 13 (`gt-2000-13`)

- Local brand/category: ASICS / Performance Sneakers
- Local color labels: Black/Blue
- Model status: `VERIFIED_EXACT_MODEL`; flags: `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`, `EDITION_UNCONFIRMED`
- Official source: [ASICS GT-2000 13](https://www.asics.com/ph/en-ph/gt-2000-13/p/1011B861-001.html)
- Manufacturer page product code: 1011B861-001
- Manufacturer page colorway: Not established from cited page
- Manufacturer page edition note: Not established from captured manufacturer evidence; review required.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: ASICS describes GT-2000 13 as a stability running shoe.
- Description: GT-2000 13 by ASICS. ASICS describes GT-2000 13 as a stability running shoe. The local listing records Black/Blue; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### GT-2160 (`gt-2160`)

- Local brand/category: ASICS / Unisex Sneakers
- Local color labels: White/Grey
- Model status: `VERIFIED_EXACT_MODEL`; flags: `EDITION_UNCONFIRMED`, `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`
- Official source: [ASICS GT-2160](https://www.asics.com/us/en-us/gt-2160/p/ANA_1203A320-116.html)
- Manufacturer page product code: ASICS 1203A320-116
- Manufacturer page colorway: White/Concrete
- Manufacturer page edition note: GT-2160 product page; this source page variant is not tied to local SKU.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: The official ASICS collection identifies the GT-2160 model.
- Description: GT-2160 by ASICS. The official ASICS collection identifies the GT-2160 model. The local listing records White/Grey; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. GT-2160 product page; this source page variant is not tied to local SKU. The manufacturer page code shown in this report belongs to the cited source page and has not been matched to any local SKU. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### Novablast 5 (`novablast-5`)

- Local brand/category: ASICS / Performance Sneakers
- Local color labels: Black/Orange
- Model status: `VERIFIED_EXACT_MODEL`; flags: `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`, `EDITION_UNCONFIRMED`
- Official source: [ASICS NOVABLAST 5](https://www.asics.com/us/en-us/product/novablast--5/p/ANA_1011B974-002.html)
- Manufacturer page product code: ANA_1011B974-002
- Manufacturer page colorway: Not established from cited page
- Manufacturer page edition note: Not established from captured manufacturer evidence; review required.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: ASICS describes NOVABLAST 5 as a running shoe.
- Description: Novablast 5 by ASICS. ASICS describes NOVABLAST 5 as a running shoe. The local listing records Black/Orange; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### 1906R (`1906r`)

- Local brand/category: New Balance / Men's Sneakers
- Local color labels: White/Silver
- Model status: `VERIFIED_EXACT_MODEL`; flags: `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`, `EDITION_UNCONFIRMED`
- Official source: [New Balance 1906R](https://www.newbalance.com/pd/1906r/M1906RER-D-11.html)
- Manufacturer page product code: M1906RER-D-11
- Manufacturer page colorway: Not established from cited page
- Manufacturer page edition note: Not established from captured manufacturer evidence; review required.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: The official page identifies the 1906R model.
- Description: 1906R by New Balance. The official page identifies the 1906R model. The local listing records White/Silver; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### 2002R (`2002r`)

- Local brand/category: New Balance / Men's Sneakers
- Local color labels: Grey/Blue
- Model status: `VERIFIED_EXACT_MODEL`; flags: `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`, `EDITION_UNCONFIRMED`
- Official source: [New Balance 2002R](https://www.newbalance.com/pd/2002r/M2002RST-D-14.html)
- Manufacturer page product code: M2002RST-D-14
- Manufacturer page colorway: Not established from cited page
- Manufacturer page edition note: Not established from captured manufacturer evidence; review required.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: New Balance describes the 2002R as a men’s sneaker drawing on 2000s running designs.
- Description: 2002R by New Balance. New Balance describes the 2002R as a men’s sneaker drawing on 2000s running designs. The local listing records Grey/Blue; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### 327 (`327`)

- Local brand/category: New Balance / Unisex Sneakers
- Local color labels: White/Blue
- Model status: `VERIFIED_EXACT_MODEL`; flags: `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`, `EDITION_UNCONFIRMED`
- Official source: [New Balance 327](https://www.newbalance.com/pd/327/WS327FE-B-08.html)
- Manufacturer page product code: WS327FE-B-08
- Manufacturer page colorway: Not established from cited page
- Manufacturer page edition note: Not established from captured manufacturer evidence; review required.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: New Balance says the 327 draws inspiration from its 1970s running shoes.
- Description: 327 by New Balance. New Balance says the 327 draws inspiration from its 1970s running shoes. The local listing records White/Blue; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### 530 (`530`)

- Local brand/category: New Balance / Unisex Sneakers
- Local color labels: White/Silver
- Model status: `VERIFIED_EXACT_MODEL`; flags: `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`, `EDITION_UNCONFIRMED`
- Official source: [New Balance 530](https://www.newbalance.com/pd/530/MR530CK-D-055.html)
- Manufacturer page product code: MR530CK-D-055
- Manufacturer page colorway: Not established from cited page
- Manufacturer page edition note: Not established from captured manufacturer evidence; review required.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: New Balance describes the 530 as drawing on turn-of-the-millennium running-shoe design.
- Description: 530 by New Balance. New Balance describes the 530 as drawing on turn-of-the-millennium running-shoe design. The local listing records White/Silver; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### 550 (`550`)

- Local brand/category: New Balance / Unisex Sneakers
- Local color labels: White/Green
- Model status: `VERIFIED_EXACT_MODEL`; flags: `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`, `EDITION_UNCONFIRMED`
- Official source: [New Balance 550](https://www.newbalance.com/pd/550/BB550V1-52598.html)
- Manufacturer page product code: BB550V1-52598
- Manufacturer page colorway: Not established from cited page
- Manufacturer page edition note: Not established from captured manufacturer evidence; review required.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: New Balance says the 550 was reintroduced in 2020 and returned to its full-time lineup in 2021.
- Description: 550 by New Balance. New Balance says the 550 was reintroduced in 2020 and returned to its full-time lineup in 2021. The local listing records White/Green; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### 574 Legacy (`574-legacy`)

- Local brand/category: New Balance / Unisex Sneakers
- Local color labels: Navy/Grey
- Model status: `VERIFIED_EXACT_MODEL`; flags: `EDITION_UNCONFIRMED`, `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`
- Official source: [New Balance 574 Legacy](https://www.newbalance.com.hk/default/gender-neutral/shoes/U574LGV1-35533.html)
- Manufacturer page product code: New Balance U574LGV1-35533
- Manufacturer page colorway: Not established from cited page
- Manufacturer page edition note: 574 Legacy exact model page; the local variant color and style code mapping remain unknown.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: The manufacturer’s 574 line is documented; this source does not establish the exact Legacy edition.
- Description: 574 Legacy by New Balance. The manufacturer’s 574 line is documented; this source does not establish the exact Legacy edition. The local listing records Navy/Grey; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. 574 Legacy exact model page; the local variant color and style code mapping remain unknown. The manufacturer page code shown in this report belongs to the cited source page and has not been matched to any local SKU. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### 9060 (`9060`)

- Local brand/category: New Balance / Unisex Sneakers
- Local color labels: Grey
- Model status: `VERIFIED_EXACT_MODEL`; flags: `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`, `EDITION_UNCONFIRMED`
- Official source: [New Balance 9060](https://www.newbalance.com/pd/9060/U9060V1-50899-PMG-NA-CCB.html)
- Manufacturer page product code: U9060V1-50899-PMG-NA-CCB
- Manufacturer page colorway: Not established from cited page
- Manufacturer page edition note: Not established from captured manufacturer evidence; review required.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: New Balance describes the 9060 as a new expression of the 99X series design.
- Description: 9060 by New Balance. New Balance describes the 9060 as a new expression of the 99X series design. The local listing records Grey; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### 990v6 (`990v6`)

- Local brand/category: New Balance / Men's Sneakers
- Local color labels: Grey
- Model status: `VERIFIED_EXACT_MODEL`; flags: `EDITION_UNCONFIRMED`, `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`
- Official source: [New Balance Made in USA 990v6](https://www.newbalance.com/pd/made-in-usa-990v6/M990GL6-4E-14.html)
- Manufacturer page product code: New Balance M990GL6-4E-14
- Manufacturer page colorway: Not established from cited page
- Manufacturer page edition note: Manufacturer page is a Made in USA 990v6 variant; local edition is not specified.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: The page identifies the Made in USA 990v6. The local catalog does not establish a style code or made-in-USA variant.
- Description: 990v6 by New Balance. The page identifies the Made in USA 990v6. The local catalog does not establish a style code or made-in-USA variant. The local listing records Grey; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. Manufacturer page is a Made in USA 990v6 variant; local edition is not specified. The manufacturer page code shown in this report belongs to the cited source page and has not been matched to any local SKU. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### Fresh Foam X 1080v14 (`fresh-foam-x-1080v14`)

- Local brand/category: New Balance / Performance Sneakers
- Local color labels: Black/White
- Model status: `VERIFIED_EXACT_MODEL`; flags: `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`, `EDITION_UNCONFIRMED`
- Official source: [New Balance Fresh Foam X 1080v14](https://www.newbalance.com/pd/fresh-foam-x-1080v14/M1080V14-47512-PMG-NA-PR.html)
- Manufacturer page product code: M1080V14-47512-PMG-NA-PR
- Manufacturer page colorway: Not established from cited page
- Manufacturer page edition note: Not established from captured manufacturer evidence; review required.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: New Balance describes the shoe for running, walking and all-day wear; the v14 page documents a triple jacquard mesh upper and Fresh Foam X midsole.
- Description: Fresh Foam X 1080v14 by New Balance. New Balance describes the shoe for running, walking and all-day wear; the v14 page documents a triple jacquard mesh upper and Fresh Foam X midsole. The local listing records Black/White; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### Air Force 1 '07 (`air-force-1-07`)

- Local brand/category: Nike / Unisex Sneakers
- Local color labels: White
- Model status: `VERIFIED_EXACT_MODEL`; flags: `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`, `EDITION_UNCONFIRMED`
- Official source: [Nike Air Force 1 '07](https://www.nike.com/t/air-force-1-07-mens-shoes-XVPIszaq)
- Manufacturer page product code: air-force-1-07-mens-shoes-XVPIszaq
- Manufacturer page colorway: Not established from cited page
- Manufacturer page edition note: Not established from captured manufacturer evidence; review required.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: Nike identifies the Air Force 1 '07; the listing does not identify the local color's style code. Nike states the AF1 debuted in 1982 and was the first basketball shoe to house Nike Air.
- Description: Air Force 1 '07 by Nike. Nike identifies the Air Force 1 '07; the listing does not identify the local color's style code. The local listing records White; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### Air Jordan 1 Low (`air-jordan-1-low`)

- Local brand/category: Nike / Men's Sneakers
- Local color labels: White/Red
- Model status: `VERIFIED_EXACT_MODEL`; flags: `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`, `EDITION_UNCONFIRMED`
- Official source: [Air Jordan 1 Low](https://www.nike.com/t/air-jordan-1-low-mens-shoes-w9HO9jOz)
- Manufacturer page product code: air-jordan-1-low-mens-shoes-w9HO9jOz
- Manufacturer page colorway: Not established from cited page
- Manufacturer page edition note: Not established from captured manufacturer evidence; review required.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: Nike describes the Air Jordan 1 Low and documents Nike Air cushioning on the product page.
- Description: Air Jordan 1 Low by Nike. Nike describes the Air Jordan 1 Low and documents Nike Air cushioning on the product page. The local listing records White/Red; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### Air Max 90 (`air-max-90`)

- Local brand/category: Nike / Men's Sneakers
- Local color labels: White/Grey
- Model status: `VERIFIED_EXACT_MODEL`; flags: `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`, `EDITION_UNCONFIRMED`
- Official source: [Nike Air Max 90](https://www.nike.com/t/air-max-90-mens-shoes-bAZ6AeHT)
- Manufacturer page product code: air-max-90-mens-shoes-bAZ6AeHT
- Manufacturer page colorway: Not established from cited page
- Manufacturer page edition note: Not established from captured manufacturer evidence; review required.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: The official Nike page identifies the Air Max 90 model.
- Description: Air Max 90 by Nike. The official Nike page identifies the Air Max 90 model. The local listing records White/Grey; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### Blazer Low '77 (`blazer-low-77`)

- Local brand/category: Nike / Unisex Sneakers
- Local color labels: White/Black
- Model status: `VERIFIED_EXACT_MODEL`; flags: `EDITION_UNCONFIRMED`, `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`
- Official source: [Nike Blazer Low '77 Premium](https://www.nike.com/launch/t/blazer-low-77-premium-coconut-milk)
- Manufacturer page product code: Nike SNKRS product page identifier not displayed
- Manufacturer page colorway: Coconut Milk
- Manufacturer page edition note: Premium edition shown on the source page; local edition/colorway is not linked.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: Nike identifies a Blazer Low '77 silhouette; the cited page is a Premium colorway, not proof of the local edition.
- Description: Blazer Low '77 by Nike. Nike identifies a Blazer Low '77 silhouette; the cited page is a Premium colorway, not proof of the local edition. The local listing records White/Black; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. Premium edition shown on the source page; local edition/colorway is not linked. The manufacturer page code shown in this report belongs to the cited source page and has not been matched to any local SKU. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### Court Vision Low (`court-vision-low`)

- Local brand/category: Nike / Men's Sneakers
- Local color labels: White/Navy
- Model status: `VERIFIED_EXACT_MODEL`; flags: `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`, `EDITION_UNCONFIRMED`
- Official source: [Nike Court Vision Low](https://www.nike.com/t/court-vision-low-mens-shoes-FpEqIQ3A)
- Manufacturer page product code: court-vision-low-mens-shoes-FpEqIQ3A
- Manufacturer page colorway: Not established from cited page
- Manufacturer page edition note: Not established from captured manufacturer evidence; review required.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: The official Nike page identifies Court Vision Low.
- Description: Court Vision Low by Nike. The official Nike page identifies Court Vision Low. The local listing records White/Navy; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### Dunk Low Retro (`dunk-low-retro`)

- Local brand/category: Nike / Unisex Sneakers
- Local color labels: White/Black
- Model status: `VERIFIED_EXACT_MODEL`; flags: `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`, `EDITION_UNCONFIRMED`
- Official source: [Nike Dunk Low Retro](https://www.nike.com/t/dunk-low-retro-mens-shoes-RrfSUR27/IO1616-002)
- Manufacturer page product code: IO1616-002
- Manufacturer page colorway: Not established from cited page
- Manufacturer page edition note: Not established from captured manufacturer evidence; review required.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: The official Nike page identifies Dunk Low Retro.
- Description: Dunk Low Retro by Nike. The official Nike page identifies Dunk Low Retro. The local listing records White/Black; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### P-6000 (`p-6000`)

- Local brand/category: Nike / Men's Sneakers
- Local color labels: Silver/White
- Model status: `VERIFIED_EXACT_MODEL`; flags: `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`, `EDITION_UNCONFIRMED`
- Official source: [Nike P-6000](https://www.nike.com/t/p-6000-mens-shoes-nX3hJMZg)
- Manufacturer page product code: p-6000-mens-shoes-nX3hJMZg
- Manufacturer page colorway: Not established from cited page
- Manufacturer page edition note: Not established from captured manufacturer evidence; review required.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: The official Nike page identifies the P-6000 model.
- Description: P-6000 by Nike. The official Nike page identifies the P-6000 model. The local listing records Silver/White; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### Pegasus 41 (`pegasus-41`)

- Local brand/category: Nike / Performance Sneakers
- Local color labels: Black/White
- Model status: `VERIFIED_EXACT_MODEL`; flags: `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`, `EDITION_UNCONFIRMED`
- Official source: [Nike Pegasus 41](https://about.nike.com/en-GB/newsroom/releases/this-summer-the-nike-pegasus-41-gives-runners-more-energy-return-than-ever)
- Manufacturer page product code: this-summer-the-nike-pegasus-41-gives-runners-more-energy-return-than-ever
- Manufacturer page colorway: Not established from cited page
- Manufacturer page edition note: Not established from captured manufacturer evidence; review required.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: Nike identifies Pegasus 41 as a road-running shoe. The cited page describes ReactX foam and Air Zoom in that model.
- Description: Pegasus 41 by Nike. Nike identifies Pegasus 41 as a road-running shoe. The cited page describes ReactX foam and Air Zoom in that model. The local listing records Black/White; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### Vomero 18 (`vomero-18`)

- Local brand/category: Nike / Performance Sneakers
- Local color labels: White/Blue
- Model status: `VERIFIED_EXACT_MODEL`; flags: `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`, `EDITION_UNCONFIRMED`
- Official source: [Nike Vomero 18](https://www.nike.com/t/vomero-18-mens-road-running-shoes-NzWnvcC8)
- Manufacturer page product code: vomero-18-mens-road-running-shoes-NzWnvcC8
- Manufacturer page colorway: Not established from cited page
- Manufacturer page edition note: Not established from captured manufacturer evidence; review required.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: Nike identifies Vomero 18 as a road-running shoe.
- Description: Vomero 18 by Nike. Nike identifies Vomero 18 as a road-running shoe. The local listing records White/Blue; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### Caven 2.0 (`caven-2`)

- Local brand/category: Puma / Men's Sneakers
- Local color labels: White/Black
- Model status: `VERIFIED_EXACT_MODEL`; flags: `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`, `EDITION_UNCONFIRMED`
- Official source: [PUMA Caven 2.0](https://us.puma.com/us/en/pd/caven-20-sneakers/392290)
- Manufacturer page product code: 392290
- Manufacturer page colorway: Not established from cited page
- Manufacturer page edition note: Not established from captured manufacturer evidence; review required.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: The official PUMA page identifies Caven 2.0 sneakers.
- Description: Caven 2.0 by Puma. The official PUMA page identifies Caven 2.0 sneakers. The local listing records White/Black; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### Deviate Nitro 3 (`deviate-nitro-3`)

- Local brand/category: Puma / Performance Sneakers
- Local color labels: Black/Yellow
- Model status: `VERIFIED_EXACT_MODEL`; flags: `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`, `EDITION_UNCONFIRMED`
- Official source: [PUMA Deviate NITRO 3](https://us.puma.com/us/en/pd/deviate-nitro-3-womens-road-running-shoes/309708)
- Manufacturer page product code: 309708
- Manufacturer page colorway: Not established from cited page
- Manufacturer page edition note: Not established from captured manufacturer evidence; review required.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: PUMA classifies Deviate NITRO 3 as road-running footwear.
- Description: Deviate Nitro 3 by Puma. PUMA classifies Deviate NITRO 3 as road-running footwear. The local listing records Black/Yellow; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### Easy Rider (`easy-rider`)

- Local brand/category: Puma / Unisex Sneakers
- Local color labels: Green/White
- Model status: `VERIFIED_EXACT_MODEL`; flags: `EDITION_UNCONFIRMED`, `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`
- Official source: [PUMA Easy Rider Vintage](https://us.puma.com/us/en/pd/easy-rider-vintage-sneakers/197670530040.html)
- Manufacturer page product code: PUMA 197670530040
- Manufacturer page colorway: Not established from cited page
- Manufacturer page edition note: Easy Rider Vintage product page confirms the base model; local vintage edition is not confirmed.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: PUMA says Easy Rider originated as a 1970s running shoe.
- Description: Easy Rider by Puma. PUMA says Easy Rider originated as a 1970s running shoe. The local listing records Green/White; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. Easy Rider Vintage product page confirms the base model; local vintage edition is not confirmed. The manufacturer page code shown in this report belongs to the cited source page and has not been matched to any local SKU. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### Future Rider (`future-rider`)

- Local brand/category: Puma / Men's Sneakers
- Local color labels: White/Blue
- Model status: `VERIFIED_EXACT_MODEL`; flags: `EDITION_UNCONFIRMED`, `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`
- Official source: [PUMA Future Rider Play On](https://us.puma.com/us/en/pd/future_rider_play_on_sneakers/393473)
- Manufacturer page product code: PUMA 393473_17
- Manufacturer page colorway: Cobalt Glaze-Pelé Yellow
- Manufacturer page edition note: Play On edition on source page; this colorway does not match the local broad white/blue label conclusively.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: The official PUMA page identifies Future Rider Play On; the local catalog does not establish the Play On edition.
- Description: Future Rider by Puma. The official PUMA page identifies Future Rider Play On; the local catalog does not establish the Play On edition. The local listing records White/Blue; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. Play On edition on source page; this colorway does not match the local broad white/blue label conclusively. The manufacturer page code shown in this report belongs to the cited source page and has not been matched to any local SKU. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### Palermo (`palermo`)

- Local brand/category: Puma / Unisex Sneakers
- Local color labels: White/Green
- Model status: `VERIFIED_EXACT_MODEL`; flags: `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`, `EDITION_UNCONFIRMED`
- Official source: [PUMA Palermo](https://us.puma.com/us/en/pd/palermo_sneakers/396463)
- Manufacturer page product code: 396463
- Manufacturer page colorway: Not established from cited page
- Manufacturer page edition note: Not established from captured manufacturer evidence; review required.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: PUMA describes Palermo as a terrace-style model from its archives, debuting in the early 1980s.
- Description: Palermo by Puma. PUMA describes Palermo as a terrace-style model from its archives, debuting in the early 1980s. The local listing records White/Green; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### R78 Voyage (`r78-voyage`)

- Local brand/category: Puma / Women's Sneakers
- Local color labels: White/Pink
- Model status: `VERIFIED_EXACT_MODEL`; flags: `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`, `EDITION_UNCONFIRMED`
- Official source: [PUMA R78 Voyage](https://us.puma.com/us/en/pd/r78-voyage-womens-sneakers/380729)
- Manufacturer page product code: 380729
- Manufacturer page colorway: Not established from cited page
- Manufacturer page edition note: Not established from captured manufacturer evidence; review required.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: The official PUMA page identifies R78 Voyage as a women’s sneaker.
- Description: R78 Voyage by Puma. The official PUMA page identifies R78 Voyage as a women’s sneaker. The local listing records White/Pink; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### Slipstream Lo (`slipstream-lo`)

- Local brand/category: Puma / Unisex Sneakers
- Local color labels: White/Blue
- Model status: `VERIFIED_EXACT_MODEL`; flags: `EDITION_UNCONFIRMED`, `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`
- Official source: [PUMA x TROPHY HUNTING Slipstream Lo](https://us.puma.com/us/en/pd/puma-x-trophy-hunting-slipstream-lo-womens-sneakers/394174)
- Manufacturer page product code: PUMA 394174_01
- Manufacturer page colorway: Frosted Ivory-Eggnog
- Manufacturer page edition note: Collaboration edition on source page; local edition/colorway not linked.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: PUMA states the Slipstream began in 1987 as a basketball sneaker; the cited page is a collaboration and does not identify the local edition.
- Description: Slipstream Lo by Puma. PUMA states the Slipstream began in 1987 as a basketball sneaker; the cited page is a collaboration and does not identify the local edition. The local listing records White/Blue; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. Collaboration edition on source page; local edition/colorway not linked. The manufacturer page code shown in this report belongs to the cited source page and has not been matched to any local SKU. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### Speedcat OG (`speedcat-og`)

- Local brand/category: Puma / Unisex Sneakers
- Local color labels: Black/White
- Model status: `VERIFIED_EXACT_MODEL`; flags: `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`, `EDITION_UNCONFIRMED`
- Official source: [PUMA Speedcat OG](https://us.puma.com/us/en/pd/speedcat-og-sneakers/398846)
- Manufacturer page product code: 398846
- Manufacturer page colorway: Not established from cited page
- Manufacturer page edition note: Not established from captured manufacturer evidence; review required.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: PUMA identifies Speedcat as a model associated with motorsport/racing culture.
- Description: Speedcat OG by Puma. PUMA identifies Speedcat as a model associated with motorsport/racing culture. The local listing records Black/White; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### Suede Classic (`suede-classic`)

- Local brand/category: Puma / Unisex Sneakers
- Local color labels: Black/White
- Model status: `VERIFIED_EXACT_MODEL`; flags: `EDITION_UNCONFIRMED`, `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`
- Official source: [PUMA Suede Classic](https://us.puma.com/us/en/pd/sneakers-suede-classic/399781?swatch=01)
- Manufacturer page product code: PUMA 399781
- Manufacturer page colorway: PUMA Black-PUMA White
- Manufacturer page edition note: Suede Classic product page; this source variant is not linked to local SKU.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: The source is a PUMA Classics collection and does not identify the exact Suede Classic edition.
- Description: Suede Classic by Puma. The source is a PUMA Classics collection and does not identify the exact Suede Classic edition. The local listing records Black/White; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. Suede Classic product page; this source variant is not linked to local SKU. The manufacturer page code shown in this report belongs to the cited source page and has not been matched to any local SKU. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### BB 4000 II (`bb-4000-ii`)

- Local brand/category: Reebok / Unisex Sneakers
- Local color labels: White/Green
- Model status: `VERIFIED_EXACT_MODEL`; flags: `EDITION_UNCONFIRMED`, `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`
- Official source: [Reebok BB 4000 II Shoes](https://www.reebok.com/collections/90s-classic-basketball-shoes-0afz00a/products/reebok-bb-4000-ii-shoes-core-black-white-pure-grey-7-108031)
- Manufacturer page product code: Reebok 7-108031
- Manufacturer page colorway: Core Black/Ftwr White/Pure Grey
- Manufacturer page edition note: BB 4000 II basketball-inspired shoe; source page is black/white/grey, not local white/green.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: Reebok describes BB 4000 II as a basketball-inspired shoe with an 1980s heritage.
- Description: BB 4000 II by Reebok. Reebok describes BB 4000 II as a basketball-inspired shoe with an 1980s heritage. The local listing records White/Green; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. BB 4000 II basketball-inspired shoe; source page is black/white/grey, not local white/green. The manufacturer page code shown in this report belongs to the cited source page and has not been matched to any local SKU. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### Classic Leather (`classic-leather`)

- Local brand/category: Reebok / Unisex Sneakers
- Local color labels: White
- Model status: `VERIFIED_EXACT_MODEL`; flags: `EDITION_UNCONFIRMED`, `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`
- Official source: [Reebok Classic Leather Shoes](https://www.reebok.com/products/reebok-classic-leather-shoes-core-black-core-black-pure-grey-5-107421)
- Manufacturer page product code: Reebok 5-107421
- Manufacturer page colorway: Core Black/Core Black/Pure Grey
- Manufacturer page edition note: Classic Leather product page; source color does not match local white label.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: Reebok identifies the Classic Leather model; the cited color variant is not a match proof for the local listing.
- Description: Classic Leather by Reebok. Reebok identifies the Classic Leather model; the cited color variant is not a match proof for the local listing. The local listing records White; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. Classic Leather product page; source color does not match local white label. The manufacturer page code shown in this report belongs to the cited source page and has not been matched to any local SKU. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### Classic Nylon (`classic-nylon`)

- Local brand/category: Reebok / Men's Sneakers
- Local color labels: Navy/White
- Model status: `VERIFIED_EXACT_MODEL`; flags: `EDITION_UNCONFIRMED`, `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`
- Official source: [Reebok Classic Nylon Shoes](https://www.reebok.com/collections/mens-classics/products/reebok-classic-nylon-shoes-core-black-core-black-pure-grey-7-107056)
- Manufacturer page product code: Reebok 7-107056
- Manufacturer page colorway: Core Black/Core Black/Pure Grey
- Manufacturer page edition note: Classic Nylon product page; source color does not match local navy/white label.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: Reebok identifies Classic Nylon shoes and lists nylon as part of the model name; cited color does not verify local colorway.
- Description: Classic Nylon by Reebok. Reebok identifies Classic Nylon shoes and lists nylon as part of the model name; cited color does not verify local colorway. The local listing records Navy/White; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. Classic Nylon product page; source color does not match local navy/white label. The manufacturer page code shown in this report belongs to the cited source page and has not been matched to any local SKU. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### Club C 85 Vintage (`club-c-85-vintage`)

- Local brand/category: Reebok / Unisex Sneakers
- Local color labels: Chalk/Green
- Model status: `VERIFIED_EXACT_MODEL`; flags: `EDITION_UNCONFIRMED`, `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`
- Official source: [Reebok Club C 85 Vintage Shoes](https://www.reebok.com/products/reebok-club-c-85-vintage-shoes-chalk-paperwhite-glen-green-103162)
- Manufacturer page product code: Reebok 103162
- Manufacturer page colorway: Chalk/Paperwhite/Glen Green
- Manufacturer page edition note: Club C 85 Vintage exact product page; local chalk/green is a broad label and SKU match is unproven.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: Reebok identifies Club C 85 Vintage as court-inspired footwear.
- Description: Club C 85 Vintage by Reebok. Reebok identifies Club C 85 Vintage as court-inspired footwear. The local listing records Chalk/Green; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. Club C 85 Vintage exact product page; local chalk/green is a broad label and SKU match is unproven. The manufacturer page code shown in this report belongs to the cited source page and has not been matched to any local SKU. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### FloatZig 1 (`floatzig-1`)

- Local brand/category: Reebok / Performance Sneakers
- Local color labels: White/Orange
- Model status: `VERIFIED_EXACT_MODEL`; flags: `EDITION_UNCONFIRMED`, `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`
- Official source: [Reebok FloatZig 1](https://www.reebok.eu/collections/floatzig-1)
- Manufacturer page product code: No product style code on cited collection page
- Manufacturer page colorway: Not established from cited page
- Manufacturer page edition note: Official Reebok page names Floatzig 1 and identifies it as a daily trainer; no specific color variant is established.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: Reebok describes FloatZig 1 as an all-around daily trainer.
- Description: FloatZig 1 by Reebok. Reebok describes FloatZig 1 as an all-around daily trainer. The local listing records White/Orange; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. Official Reebok page names Floatzig 1 and identifies it as a daily trainer; no specific color variant is established. The manufacturer page code shown in this report belongs to the cited source page and has not been matched to any local SKU. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### Nano X5 (`nano-x5`)

- Local brand/category: Reebok / Performance Sneakers
- Local color labels: Black/White
- Model status: `VERIFIED_EXACT_MODEL`; flags: `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`, `EDITION_UNCONFIRMED`
- Official source: [Reebok Nano X5](https://www.reebok.com/products/reebok-nano-x5-training-shoes-black-grey-6-172449)
- Manufacturer page product code: reebok-nano-x5-training-shoes-black-grey-6-172449
- Manufacturer page colorway: Not established from cited page
- Manufacturer page edition note: Not established from captured manufacturer evidence; review required.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: Reebok identifies Nano X5 as a training shoe.
- Description: Nano X5 by Reebok. Reebok identifies Nano X5 as a training shoe. The local listing records Black/White; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### Premier Road Modern (`premier-road-modern`)

- Local brand/category: Reebok / Men's Sneakers
- Local color labels: White/Grey
- Model status: `VERIFIED_EXACT_MODEL`; flags: `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`, `EDITION_UNCONFIRMED`
- Official source: [Reebok Premier Road Modern](https://www.reebok.com/products/reebok-premier-road-modern-black-cherry-midnite-tide-heritage-green)
- Manufacturer page product code: reebok-premier-road-modern-black-cherry-midnite-tide-heritage-green
- Manufacturer page colorway: Not established from cited page
- Manufacturer page edition note: Not established from captured manufacturer evidence; review required.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: Reebok identifies Premier Road Modern; the local catalog does not establish an exact color/style variant.
- Description: Premier Road Modern by Reebok. Reebok identifies Premier Road Modern; the local catalog does not establish an exact color/style variant. The local listing records White/Grey; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### Workout Plus (`workout-plus`)

- Local brand/category: Reebok / Unisex Sneakers
- Local color labels: White/Chalk
- Model status: `VERIFIED_EXACT_MODEL`; flags: `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`, `EDITION_UNCONFIRMED`
- Official source: [Reebok Workout Plus](https://www.reebok.com/products/reebok-workout-plus-shoes-chalk-chalk-black-146360)
- Manufacturer page product code: reebok-workout-plus-shoes-chalk-chalk-black-146360
- Manufacturer page colorway: Not established from cited page
- Manufacturer page edition note: Not established from captured manufacturer evidence; review required.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: Reebok describes Workout Plus as a classic workout shoe.
- Description: Workout Plus by Reebok. Reebok describes Workout Plus as a classic workout shoe. The local listing records White/Chalk; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### Zig Kinetica 2.5 (`zig-kinetica-25`)

- Local brand/category: Reebok / Men's Sneakers
- Local color labels: Black/Red
- Model status: `MODEL_IDENTITY_UNCONFIRMED`; flags: `MODEL_IDENTITY_UNCONFIRMED`, `DESCRIPTION_REVIEW_REQUIRED`
- Official source: None found for exact model
- Manufacturer page product code: Not captured / not provided by cited page
- Manufacturer page colorway: Not established from cited page
- Manufacturer page edition note: No qualifying official Reebok source was located for the exact name Zig Kinetica 2.5.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: None established
- Description: `DESCRIPTION_REVIEW_REQUIRED`
- Category recommendation: No change recommended from current evidence
- Review notes: Exact-name searches of official Reebok pages did not return a reliable product/model page for Zig Kinetica 2.5. Related Zig products were not treated as evidence for this name. Keep unverified pending a manufacturer source.

### Authentic (`authentic`)

- Local brand/category: Vans / Unisex Sneakers
- Local color labels: Black
- Model status: `VERIFIED_EXACT_MODEL`; flags: `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`, `EDITION_UNCONFIRMED`
- Official source: [Vans Authentic Shoe](https://www.vans.com/en-us/p/shoes/icons/authentic-5310/authentic-shoe-VN000D7YBZW)
- Manufacturer page product code: authentic-shoe-VN000D7YBZW
- Manufacturer page colorway: Not established from cited page
- Manufacturer page edition note: Not established from captured manufacturer evidence; review required.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: Vans identifies Authentic as an original silhouette.
- Description: Authentic by Vans. Vans identifies Authentic as an original silhouette. The local listing records Black; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### Checkerboard Slip-On (`checkerboard-slip-on`)

- Local brand/category: Vans / Unisex Sneakers
- Local color labels: Checkerboard
- Model status: `VERIFIED_EXACT_MODEL`; flags: `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`, `EDITION_UNCONFIRMED`
- Official source: [Vans Classic Slip-On Checkerboard Shoe](https://www.vans.com/en-us/p/shoes/icons/classic-slip-on-5315/classic-slip-on-checkerboard-shoe-VN000EYE276)
- Manufacturer page product code: classic-slip-on-checkerboard-shoe-VN000EYE276
- Manufacturer page colorway: Not established from cited page
- Manufacturer page edition note: Not established from captured manufacturer evidence; review required.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: Vans identifies the checkerboard Classic Slip-On model.
- Description: Checkerboard Slip-On by Vans. Vans identifies the checkerboard Classic Slip-On model. The local listing records Checkerboard; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### Classic Slip-On (`classic-slip-on`)

- Local brand/category: Vans / Unisex Sneakers
- Local color labels: Black/White Checkerboard
- Model status: `VERIFIED_EXACT_MODEL`; flags: `EDITION_UNCONFIRMED`, `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`
- Official source: [Vans Classic Slip-On Shoe](https://www.vans.com/en-us/p/shoes/icons/classic-slip-on-5315/classic-slip-on-checkerboard-shoe-VN000EYE276)
- Manufacturer page product code: Vans VN000EYE276
- Manufacturer page colorway: Checkerboard
- Manufacturer page edition note: Official checkerboard Classic Slip-On page; exact local color/style SKU mapping remains unconfirmed.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: Vans identifies Classic Slip-On; the cited black solid version does not confirm local black-and-white checkerboard variant.
- Description: Classic Slip-On by Vans. Vans identifies Classic Slip-On; the cited black solid version does not confirm local black-and-white checkerboard variant. The local listing records Black/White Checkerboard; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. Official checkerboard Classic Slip-On page; exact local color/style SKU mapping remains unconfirmed. The manufacturer page code shown in this report belongs to the cited source page and has not been matched to any local SKU. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### Era (`era`)

- Local brand/category: Vans / Unisex Sneakers
- Local color labels: Navy/White
- Model status: `VERIFIED_EXACT_MODEL`; flags: `EDITION_UNCONFIRMED`, `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`
- Official source: [Vans Era](https://www.vans.com/en-us/p/shoes/icons/era-5320/skate-era-VN000ECRBA2)
- Manufacturer page product code: Vans VN000ECRBA2
- Manufacturer page colorway: Black/White
- Manufacturer page edition note: Official Skate Era product page confirms the Era model family; the local navy/white label is not this source variant.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: Vans describes Era as an original skate shoe.
- Description: Era by Vans. Vans describes Era as an original skate shoe. The local listing records Navy/White; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. Official Skate Era product page confirms the Era model family; the local navy/white label is not this source variant. The manufacturer page code shown in this report belongs to the cited source page and has not been matched to any local SKU. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### Knu Skool (`knu-skool`)

- Local brand/category: Vans / Unisex Sneakers
- Local color labels: Black/White
- Model status: `VERIFIED_EXACT_MODEL`; flags: `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`, `EDITION_UNCONFIRMED`
- Official source: [Vans Knu Skool Shoe](https://www.vans.com/en-us/p/shoes/knu-skool-5840/knu-skool-VN000EE6BPA)
- Manufacturer page product code: knu-skool-VN000EE6BPA
- Manufacturer page colorway: Not established from cited page
- Manufacturer page edition note: Not established from captured manufacturer evidence; review required.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: Vans identifies the Knu Skool model.
- Description: Knu Skool by Vans. Vans identifies the Knu Skool model. The local listing records Black/White; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### Old Skool Platform (`old-skool-platform`)

- Local brand/category: Vans / Women's Sneakers
- Local color labels: Black/White
- Model status: `VERIFIED_EXACT_MODEL`; flags: `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`, `EDITION_UNCONFIRMED`
- Official source: [Vans Old Skool Platform Shoe](https://www.vans.com/en-us/p/shoes/icons/old-skool-5205/old-skool-stackform-shoe-VN0A7Q5MBKA)
- Manufacturer page product code: old-skool-stackform-shoe-VN0A7Q5MBKA
- Manufacturer page colorway: Not established from cited page
- Manufacturer page edition note: Not established from captured manufacturer evidence; review required.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: Vans identifies Old Skool Platform and describes it as a platform variation of the Old Skool.
- Description: Old Skool Platform by Vans. Vans identifies Old Skool Platform and describes it as a platform variation of the Old Skool. The local listing records Black/White; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### Sk8-Hi (`sk8-hi`)

- Local brand/category: Vans / Unisex Sneakers
- Local color labels: Black/White
- Model status: `VERIFIED_EXACT_MODEL`; flags: `EDITION_UNCONFIRMED`, `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`
- Official source: [Vans Sk8-Hi Shoe](https://www.vans.com/en-us/p/shoes/icons/sk8-hi-5325/sk8-hi-shoe-VN000D5IB8C)
- Manufacturer page product code: Vans VN000D5IB8C
- Manufacturer page colorway: Black/White
- Manufacturer page edition note: Official Sk8-Hi product page; local broad color is similar but SKU-to-style match is unproven.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: Vans identifies Sk8-Hi as a high-top model.
- Description: Sk8-Hi by Vans. Vans identifies Sk8-Hi as a high-top model. The local listing records Black/White; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. Official Sk8-Hi product page; local broad color is similar but SKU-to-style match is unproven. The manufacturer page code shown in this report belongs to the cited source page and has not been matched to any local SKU. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### Sk8-Low (`sk8-low`)

- Local brand/category: Vans / Unisex Sneakers
- Local color labels: Black/White
- Model status: `VERIFIED_EXACT_MODEL`; flags: `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`, `EDITION_UNCONFIRMED`
- Official source: [Vans SK8-Low Shoe](https://www.vans.com/en-us/p/shoes-00081/sk8-low-shoe-VN0A4UUK6BT)
- Manufacturer page product code: sk8-low-shoe-VN0A4UUK6BT
- Manufacturer page colorway: Not established from cited page
- Manufacturer page edition note: Not established from captured manufacturer evidence; review required.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: Vans describes SK8-Low as a low-top version of the Sk8-Hi, with suede and canvas uppers, lace-up closure, reinforced toe caps, padded collars, and a rubber waffle outsole.
- Description: The Vans SK8-Low takes the Sk8-Hi silhouette into a low-top profile. Vans documents suede and canvas uppers, lace-up closure, reinforced toe caps, padded collars and a rubber waffle outsole. The local black-and-white color label is not matched to a manufacturer style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source confirms SK8-Low model details but does not establish that local inventory is the exact variant shown. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

### UltraRange EXO (`ultrarange-exo`)

- Local brand/category: Vans / Men's Sneakers
- Local color labels: Black/White
- Model status: `VERIFIED_EXACT_MODEL`; flags: `EDITION_UNCONFIRMED`, `COLORWAY_UNCONFIRMED`, `SOURCE_PRODUCT_CODE_NOT_LINKED_TO_LOCAL_SKU`
- Official source: [Vans UltraRange EXO Shoe](https://www.vans.com/en-us/p/shoes/ultrarange-5140/customs-ultrarange-exo-shoe-VN0A3VC1605)
- Manufacturer page product code: Vans VN0A3VC1605
- Manufacturer page colorway: Customs (customizable)
- Manufacturer page edition note: Official page identifies UltraRange EXO, sold as a customizable model; this does not establish local colors.
- Local SKU style mapping: Unconfirmed
- Local official colorway: Unconfirmed
- Verified specifications: Vans identifies the UltraRange footwear line; the cited collection is not specific to the EXO version.
- Description: UltraRange EXO by Vans. Vans identifies the UltraRange footwear line; the cited collection is not specific to the EXO version. The local listing records Black/White; the precise manufacturer colorway and edition have not been matched to a style code.
- Category recommendation: No change recommended from current evidence
- Review notes: Local color labels are broad inventory labels, not manufacturer colorway names. Do not infer the official colorway from them. Source page confirms the named model or family, but does not establish that local inventory is the exact variant shown. Official page identifies UltraRange EXO, sold as a customizable model; this does not establish local colors. The manufacturer page code shown in this report belongs to the cited source page and has not been matched to any local SKU. The manufacturer source page may show a product code and variant, recorded separately when captured. It is not linked to the local SKU. Do not infer a local colorway or edition from a broad catalog color label.

## Integrity validation

Reebok Zig Kinetica 2.5 is on `HOLD_MODEL_IDENTITY_UNVERIFIED`; it has no approved description and is excluded from import proposals.

The report stores audit snapshots of local prices, variant SKUs, sizes, colors, prices and stock. Validation compares those values with the earlier content manifest and read-only SQLite. No local product names, slugs, prices, SKUs, variant relationships or stock were modified.
