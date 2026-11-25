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
    ("app/views/shared/_title.html.erb", "<span>DocuSeal</span>", "<span><%= Docuseal.product_name %></span>"),
    ("app/views/start_form/_docuseal_logo.html.erb",
     '<h1 class="text-5xl font-bold text-center">DocuSeal</h1>',
     '<h1 class="text-5xl font-bold text-center"><%= Docuseal.product_name %></h1>'),

    # Logo: il marchio SerSan (public/sersan-logo.png) al posto dell'SVG di DocuSeal.
    ("app/views/shared/_logo.html.erb", None,
     '<img src="/sersan-logo.png" alt="SerSan" class="<%= local_assigns[:class] %>" '
     'height="<%= local_assigns.fetch(:height, \'37\') %>" width="<%= local_assigns.fetch(:width, \'37\') %>">\n'),
    ("app/javascript/template_builder/logo.vue", None,
     '<template>\n  <img\n    src="/sersan-logo.png"\n    alt="SerSan"\n    height="40"\n    width="40"\n  >\n</template>\n\n'
     "<script>\nexport default {\n  name: 'ProjectLogo'\n}\n</script>\n"),

    # Attribuzione (licenza, termini aggiuntivi): resta "DocuSeal", anche se la costante ora dice SerSan.
    # Accanto, il link al nostro codice sorgente.
    ("app/views/shared/_powered_by.html.erb",
     'class="underline"><%= Docuseal.product_name %></a> - <%= t(\'open_source_documents_software\') %>',
     'class="underline">DocuSeal</a> - <%= t(\'open_source_documents_software\') %>'
     ' · <a href="<%= Docuseal::GITHUB_URL %>" class="underline" target="_blank" rel="noopener">Codice sorgente</a>'),
    ("app/views/templates_share_link_qr/_branding.html.erb",
     'rel="noopener"><%= Docuseal.product_name %></a>',
     'rel="noopener">DocuSeal</a>'),
    ("app/views/shared/_email_attribution.html.erb", "product_name: Docuseal.product_name) %>",
     "product_name: 'DocuSeal') %>", 3),
    ("app/javascript/submission_form/completed.vue",
     "      >DocuSeal</a> - {{ t('open_source_documents_software') }}\n",
     "      >DocuSeal</a> - {{ t('open_source_documents_software') }} ·\n"
     f"      <a\n        href=\"{FORK}\"\n        target=\"_blank\"\n        class=\"underline\"\n      >Codice sorgente</a>\n"),

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

    # Colori SerSan sui pulsanti (neutral), più rosa e blu del marchio. Sfondi e testo restano quelli di DocuSeal.
    ("tailwind.config.js", "          secondary: '#ef9fbc',\n          accent: '#eeaf3a',\n          neutral: '#291334',\n",
     "          secondary: '#ff1a8c',\n          accent: '#2b45ff',\n          neutral: '#3b1d9a',\n"),

    # Italiano: lingua predefinita dei conti nuovi; per chi firma resta quella del browser, e se il browser
    # ha una lingua che DocuSeal non conosce si va sull'italiano invece che sull'inglese.
    ("app/models/account.rb", "  attribute :locale, :string, default: 'en-US'\n",
     "  attribute :locale, :string, default: 'it-IT'\n"),
    ("app/controllers/application_controller.rb", "        locale.split('-').first.presence || 'en-GB'\n",
     "        locale.split('-').first.presence || 'it'\n"),
    ("app/controllers/application_controller.rb", "    locale = 'en-GB' unless I18n.locale_available?(locale)\n",
     "    locale = 'it' unless I18n.locale_available?(locale)\n"),
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
        if testo.count(vecchio) == volte:
            p.write_text(testo.replace(vecchio, nuovo))
            print(f"fatto: {file}")
        elif (nuovo and testo.count(nuovo) >= volte) or (not nuovo and vecchio not in testo):
            print(f"già fatto: {file}")
        else:
            print(f"DA GUARDARE: {file}: trovato {testo.count(vecchio)} volte su {volte}: {vecchio[:60]!r}")
            errori += 1
    return 1 if errori else 0


if __name__ == "__main__":
    sys.exit(main())
