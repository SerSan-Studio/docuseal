#!/usr/bin/env python3
"""SerSan: le modifiche di testo del marchio sul codice di DocuSeal (vedi SERSAN.md).

Piccole e isolate, perché gli aggiornamenti da upstream restino facili. Ogni sostituzione controlla di trovare
il testo originale una volta sola. Se il testo è già quello SerSan, la salta (si può rilanciare). Se non trova
né l'uno né l'altro, si ferma: dopo un aggiornamento da upstream vuol dire che quel punto è cambiato, e va
guardato a mano.

Uso, dalla cartella del repository:  python3 sersan/applica-marchio.py
"""
import sys
from pathlib import Path

FORK = "https://github.com/SerSan-Studio/docuseal"
# Versione delle icone negli indirizzi: le icone hanno 180 giorni di cache nei browser, quindi quando cambiano
# logo o icone si cambia questa, e i browser le riscaricano (come fa sersan.io con favicon.svg?v=13).
ICONE = "?v=sersan2"

# (file, testo originale, testo SerSan)
MODIFICHE = [
    # Nome del prodotto: una costante, usata da manifest, email di sistema, intestazioni, PDF.
    ("lib/docuseal.rb", "  PRODUCT_NAME = 'DocuSeal'\n", "  PRODUCT_NAME = 'SerSan Sign'\n"),
    # Codice sorgente (AGPL): i link "GitHub" dell'interfaccia vanno al nostro fork.
    ("lib/docuseal.rb", "  GITHUB_URL = 'https://github.com/docusealco/docuseal'\n", f"  GITHUB_URL = '{FORK}'\n"),

    # Titoli e meta: il nome dalla costante.
    ("app/views/layouts/_head_tags.html.erb",
     "(signed_in? ? 'DocuSeal' : 'DocuSeal | Open Source Document Signing')",
     "Docuseal.product_name"),
    ("app/views/shared/_meta.html.erb",
     "(signed_in? ? 'DocuSeal' : 'DocuSeal | Open Source Document Signing')",
     "Docuseal.product_name"),
    ("app/views/shared/_meta.html.erb",
     '<meta property="og:site_name" content="DocuSeal">',
     '<meta property="og:site_name" content="<%= Docuseal.product_name %>">'),
    ("app/views/shared/_meta.html.erb",
     '<meta name="twitter:creator" content="@docusealco">\n<meta name="twitter:site" content="@docusealco">\n',
     ''),
    ("app/views/shared/_html_title.html.erb", '"#{title} | DocuSeal"', '"#{title} | #{Docuseal.product_name}"'),
    # Nella barra in alto: "SerSan" pieno e "Sign" nel blu del marchio (classe sersan-sign, app/javascript/sersan.css).
    ("app/views/shared/_title.html.erb", "<span>DocuSeal</span>",
     '<span class="tracking-tight">SerSan <span class="sersan-sign">Sign</span></span>'),
    ("app/views/start_form/_docuseal_logo.html.erb",
     '<h1 class="text-5xl font-bold text-center">DocuSeal</h1>',
     '<h1 class="text-5xl font-bold text-center"><%= Docuseal.product_name %></h1>'),

    # Logo: il marchio di sersan.io (public/sersan-logo.svg, da sersan/genera-icone.sh) al posto di quello di DocuSeal.
    ("app/views/shared/_logo.html.erb", None,
     f'<img src="/sersan-logo.svg{ICONE}" alt="SerSan" class="<%= local_assigns[:class] %>" '
     'height="<%= local_assigns.fetch(:height, \'37\') %>" width="<%= local_assigns.fetch(:width, \'37\') %>">\n'),
    ("app/javascript/template_builder/logo.vue", None,
     f'<template>\n  <img\n    src="/sersan-logo.svg{ICONE}"\n    alt="SerSan"\n    height="40"\n    width="40"\n  >\n</template>\n\n'
     "<script>\nexport default {\n  name: 'ProjectLogo'\n}\n</script>\n"),
    # Icone e anteprima con la versione nell'indirizzo (vedi ICONE in cima), anche nel manifest dell'app.
    *[("app/views/shared/_meta.html.erb", f'href="/{f}">', f'href="/{f}{ICONE}">')
      for f in ("apple-icon-180x180.png", "favicon-32x32.png", "favicon-96x96.png", "favicon-16x16.png", "favicon.svg")],
    ("app/views/shared/_meta.html.erb", '"#{root_url}preview.png"', f'"#{{root_url}}preview.png{ICONE}"', 2),
    ("app/views/pwa/manifest.json.erb", '"src": "/favicon.svg",', f'"src": "/favicon.svg{ICONE}",'),
    ("app/views/pwa/manifest.json.erb", '"src": "/apple-touch-icon.png",', f'"src": "/apple-touch-icon.png{ICONE}",'),
    ("app/views/pwa/manifest.json.erb", '"#FAF7F4"', '"#F7F9FC"', 2),
    # Le iniziali dell'utente in alto a destra: ciano invece del viola di DocuSeal.
    ("app/views/shared/_navbar.html.erb", "bg-base-content text-purple-300 rounded-full",
     "bg-base-content text-cyan-300 rounded-full"),

    # Attribuzione (licenza, termini aggiuntivi): resta "DocuSeal", anche se la costante ora dice SerSan.
    # Accanto, il link al nostro codice sorgente.
    ("app/views/shared/_powered_by.html.erb",
     'class="underline"><%= Docuseal.product_name %></a> - <%= t(\'open_source_documents_software\') %>',
     'class="underline">DocuSeal</a> - <%= t(\'open_source_documents_software\') %>'
     ' · <a href="<%= Docuseal::GITHUB_URL %>" class="underline" target="_blank" rel="noopener">'
     "<%= t('sersan_source_code') %></a>"),
    ("app/views/templates_share_link_qr/_branding.html.erb",
     'rel="noopener"><%= Docuseal.product_name %></a>',
     'rel="noopener">DocuSeal</a>'),
    ("app/views/shared/_email_attribution.html.erb", "product_name: Docuseal.product_name) %>",
     "product_name: 'DocuSeal') %>", 3),
    ("app/javascript/submission_form/completed.vue",
     "      >DocuSeal</a> - {{ t('open_source_documents_software') }}\n",
     "      >DocuSeal</a> - {{ t('open_source_documents_software') }} ·\n"
     f"      <a\n        href=\"{FORK}\"\n        target=\"_blank\"\n        class=\"underline\"\n      >{{{{ t('sersan_source_code') }}}}</a>\n"),
    # La scritta del link al codice sorgente, nella lingua di chi firma (lato server: config/locales/sersan.yml).
    ("app/javascript/submission_form/i18n.js", "  open_source_documents_software: 'open source documents software',\n",
     "  open_source_documents_software: 'open source documents software',\n  sersan_source_code: 'Source code',\n"),
    ("app/javascript/submission_form/i18n.js", "  open_source_documents_software: 'software di documenti open source',\n",
     "  open_source_documents_software: 'software di documenti open source',\n  sersan_source_code: 'Codice sorgente',\n"),

    # Mittente predefinito delle email di sistema (con SMTP_FROM nudo resta questo nome).
    ("app/mailers/application_mailer.rb", "default from: 'DocuSeal <info@docuseal.com>'",
     "default from: 'SerSan Sign <sign@sersan.io>'"),

    # PDF: testo accanto al logo nel registro di firma e motivo della firma digitale.
    ("lib/submissions/generate_audit_trail.rb", "      column.formatted_text([{ text: 'DocuSeal',",
     "      column.formatted_text([{ text: Docuseal.product_name,"),
    ("lib/submissions/generate_audit_trail.rb", "      'Signed with DocuSeal.com'\n",
     "      \"Signed with #{Docuseal.product_name}\"\n"),
    ("lib/submissions/generate_result_attachments.rb", "    SIGN_REASON = 'Signed with DocuSeal.com'\n",
     "    SIGN_REASON = \"Signed with #{Docuseal.product_name}\".freeze\n"),

    # Colori di sersan.io: testo e pulsanti nel navy del marchio, blu e ciano per gli accenti, sfondi chiari freddi
    # invece del beige di DocuSeal. Caratteri e ritocchi in app/javascript/sersan.css, importato dai due fogli di stile.
    ("tailwind.config.js",
     "          primary: '#e4e0e1',\n          secondary: '#ef9fbc',\n          accent: '#eeaf3a',\n"
     "          neutral: '#291334',\n          'base-100': '#faf7f5',\n          'base-200': '#efeae6',\n"
     "          'base-300': '#e7e2df',\n          'base-content': '#291334',\n",
     "          primary: '#e3eaf3',\n          secondary: '#2280dc',\n          accent: '#3de2ff',\n"
     "          neutral: '#132741',\n          'base-100': '#f7f9fc',\n          'base-200': '#edf1f7',\n"
     "          'base-300': '#e1e7f0',\n          'base-content': '#132741',\n"),
    # Scritte dei pulsanti come sul sito (maiuscola solo all'inizio), non tutte maiuscole.
    ("tailwind.config.js", "          '--rounded-btn': '1.9rem',\n",
     "          '--rounded-btn': '1.9rem',\n          '--btn-text-case': 'none',\n"),
    ("tailwind.dynamic.config.js",
     "        'base-100': '#faf7f5',\n        'base-200': '#efeae6',\n        'base-300': '#e7e2df',\n"
     "        'base-content': '#291334'\n",
     "        'base-100': '#f7f9fc',\n        'base-200': '#edf1f7',\n        'base-300': '#e1e7f0',\n"
     "        'base-content': '#132741'\n"),
    ("app/javascript/application.js", "      backgroundColor: '#faf7f5',\n", "      backgroundColor: '#f7f9fc',\n"),
    ("app/javascript/application.scss", '@import "tailwindcss/utilities";\n',
     '@import "tailwindcss/utilities";\n@import "./sersan.css";\n'),
    ("app/javascript/form.scss", '@import "tailwindcss/utilities";\n',
     '@import "tailwindcss/utilities";\n@import "./sersan.css";\n'),

    # Niente "Developer Newsletters" di DocuSeal dopo il primo accesso: si va dritti al cruscotto.
    # (Controller, vista e test della newsletter sono cancellati: vedi CANCELLATI qui sotto.)
    ("app/controllers/setup_controller.rb", "      redirect_to newsletter_path\n", "      redirect_to root_path\n"),
    ("config/routes.rb", "  resource :newsletter, only: %i[show update]\n", ""),

    # Italiano: lingua predefinita dei conti nuovi; per chi firma resta quella del browser, e se il browser
    # ha una lingua che DocuSeal non conosce si va sull'italiano invece che sull'inglese.
    ("app/models/account.rb", "  attribute :locale, :string, default: 'en-US'\n",
     "  attribute :locale, :string, default: 'it-IT'\n"),
    ("app/controllers/application_controller.rb", "        locale.split('-').first.presence || 'en-GB'\n",
     "        locale.split('-').first.presence || 'it'\n"),
    ("app/controllers/application_controller.rb", "    locale = 'en-GB' unless I18n.locale_available?(locale)\n",
     "    locale = 'it' unless I18n.locale_available?(locale)\n"),
    ("spec/system/setup_spec.rb", "      expect(user.account.locale).to eq('en-US')\n",
     "      expect(user.account.locale).to eq('it-IT')\n"),

    # Russo. Le traduzioni stanno in file nostri (config/locales/ru.yml, i18n_ru.js), qui solo gli elenchi.
    ("config/application.rb", "%i[en en-US en-GB es-ES fr-FR pt-PT de-DE it-IT nl-NL\n",
     "%i[en en-US en-GB es-ES fr-FR pt-PT de-DE it-IT nl-NL ru-RU\n"),
    ("config/application.rb", "es it de fr nl pl uk cs pt he ar ko ja]\n", "es it de fr nl pl uk cs pt he ar ko ja ru]\n"),
    ("app/controllers/accounts_controller.rb", "    'nl-NL' => 'Nederlands'\n",
     "    'nl-NL' => 'Nederlands',\n    'ru-RU' => 'Русский'\n"),
    ("app/views/devise/shared/_links.html.erb", "%i[en pt-PT de-DE fr-FR it-IT es-ES nl-NL]",
     "%i[en pt-PT de-DE fr-FR it-IT es-ES nl-NL ru-RU]"),
    ("app/javascript/submission_form/i18n.js", "const en = {\n", "import ru from './i18n_ru'\n\nconst en = {\n"),
    ("app/javascript/submission_form/i18n.js", "const i18n = { en, es, it, de, fr, pl, uk, cs, pt, he, nl, ar, ko, ja }",
     "const i18n = { en, es, it, de, fr, pl, uk, cs, pt, he, nl, ar, ko, ja, ru }"),
    ("app/javascript/template_builder/i18n.js", "const en = {\n", "import ru from './i18n_ru'\n\nconst en = {\n"),
    ("app/javascript/template_builder/i18n.js", "export { en, es, it, pt, fr, de, nl }",
     "export { en, es, it, pt, fr, de, nl, ru }"),
    ("app/javascript/template_builder/builder.vue", "        'es-ES': 'DD/MM/YYYY'\n",
     "        'es-ES': 'DD/MM/YYYY',\n        'ru-RU': 'DD.MM.YYYY'\n"),
    ("app/javascript/template_builder/field_settings.vue",
     "const spaceLocales = ['fr-FR', 'es-ES', 'pt-PT', 'de-DE', 'it-IT', 'nl-NL']",
     "const spaceLocales = ['fr-FR', 'es-ES', 'pt-PT', 'de-DE', 'it-IT', 'nl-NL', 'ru-RU']"),
    ("app/javascript/template_builder/dynamic_variable.vue",
     "const spaceLocales = ['fr-FR', 'es-ES', 'pt-PT', 'de-DE', 'it-IT', 'nl-NL']",
     "const spaceLocales = ['fr-FR', 'es-ES', 'pt-PT', 'de-DE', 'it-IT', 'nl-NL', 'ru-RU']"),
]

# File di DocuSeal che SerSan toglie del tutto (la newsletter per sviluppatori di DocuSeal).
CANCELLATI = [
    "app/controllers/newsletters_controller.rb",
    "app/views/newsletters/show.html.erb",
    "spec/system/newsletters_spec.rb",
]


def main() -> int:
    errori = 0
    for voce in MODIFICHE:
        file, vecchio, nuovo = voce[:3]
        volte = voce[3] if len(voce) > 3 else 1
        p = Path(file)
        testo = p.read_text()
        if vecchio is None:  # file sostituito per intero
            if testo == nuovo:
                print(f"già fatto: {file}")
            else:
                p.write_text(nuovo)
                print(f"sostituito: {file}")
            continue
        gia = bool(nuovo) and testo.count(nuovo) >= volte
        if gia and vecchio in nuovo:  # aggiunta (il testo nuovo contiene il vecchio): non rifarla
            print(f"già fatto: {file}")
        elif testo.count(vecchio) == volte:
            p.write_text(testo.replace(vecchio, nuovo))
            print(f"fatto: {file}")
        elif gia or (not nuovo and vecchio not in testo):
            print(f"già fatto: {file}")
        else:
            print(f"DA GUARDARE: {file}: trovato {testo.count(vecchio)} volte su {volte}: {vecchio[:60]!r}")
            errori += 1
    for file in CANCELLATI:
        p = Path(file)
        if p.exists():
            p.unlink()
            print(f"cancellato: {file}")
        else:
            print(f"già fatto: {file}")
    return 1 if errori else 0


if __name__ == "__main__":
    sys.exit(main())
