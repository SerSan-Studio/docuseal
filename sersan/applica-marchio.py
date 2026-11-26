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

# Blocchi interi dei componenti Vue che SerSan toglie (testo originale di DocuSeal 3.4.0).
FIELDS_TELEFONO = '      <div\n        v-else-if="type == \'phone\' && !nativePlatform && (fieldTypes.length === 0 || fieldTypes.includes(type))"\n        class="tooltip tooltip-bottom flex"\n        :class="{\'tooltip-bottom-end\': withPayment, \'tooltip-bottom\': !withPayment }"\n        :data-tip="t(\'unlock_sms_verified_phone_number_field_with_paid_plan_use_text_field_for_phone_numbers_without_verification\')"\n      >\n        <a\n          href="https://www.docuseal.com/pricing"\n          target="_blank"\n          class="opacity-50 flex items-center justify-center border border-dashed border-base-300 w-full rounded relative fields-grid-item"\n          :style="{ backgroundColor }"\n        >\n          <div class="w-0 absolute left-0">\n            <IconLock\n              width="18"\n              height="18"\n              stroke-width="1.5"\n            />\n          </div>\n          <div class="flex items-center flex-col px-2 py-2">\n            <component :is="icon" />\n            <span class="text-xs mt-1">\n              {{ fieldNames[type] }}\n            </span>\n          </div>\n        </a>\n      </div>\n'
FIELDS_QES = '      <div\n        v-else-if="withVerification === false && type == \'verification\' && (fieldTypes.length === 0 || fieldTypes.includes(type))"\n        class="tooltip tooltip-bottom flex tooltip-bottom-start"\n        :data-tip="t(\'obtain_qualified_electronic_signature_with_the_trusted_provider_click_to_learn_more\')"\n      >\n        <a\n          href="https://www.docuseal.com/qualified-electronic-signature"\n          target="_blank"\n          class="opacity-50 flex items-center justify-center border border-dashed border-base-300 w-full rounded relative fields-grid-item"\n          :style="{ backgroundColor }"\n        >\n          <div class="w-0 absolute left-0">\n            <IconLock\n              width="18"\n              height="18"\n              stroke-width="1.5"\n            />\n          </div>\n          <div class="flex items-center flex-col px-2 py-2">\n            <component :is="icon" />\n            <span class="text-xs mt-1">\n              {{ fieldNames[type] }}\n            </span>\n          </div>\n        </a>\n      </div>\n'
NAV_AIUTO = '    <% if Docuseal.multitenant? || cannot?(:manage, :tenants) %>\n      <div id="support_channels" class="mx-4 border-t border-base-300 <%= \'hidden md:block\' unless expanded %>">\n        <% unless turbo_native_app? %>\n          <div class="text-sm mt-3">\n            <%= t(\'need_help_ask_a_question_\') %>\n          </div>\n          <div class="flex mt-3 space-x-3">\n            <div class="tooltip tooltip-no-touch" data-tip="GitHub">\n              <a href="<%= Docuseal::GITHUB_URL %>" target="_blank" class="btn btn-circle btn-primary btn-md">\n                <%= svg_icon(\'brand_github\', class: \'w-8 h-8\') %>\n              </a>\n            </div>\n            <div class="tooltip tooltip-no-touch" data-tip="<%= t(\'discord_community\') %>">\n              <a href="<%= Docuseal::DISCORD_URL %>" target="_blank" class="btn btn-circle btn-primary btn-md">\n                <%= svg_icon(\'brand_discord\', class: \'w-8 h-8\') %>\n              </a>\n            </div>\n            <%= capture do %>\n              <div class="tooltip tooltip-no-touch" data-tip="<%= t(\'ai_assistant\') %>">\n                <a href="<%= Docuseal::CHATGPT_URL %>" target="_blank" class="btn btn-circle btn-primary btn-md">\n                  <%= svg_icon(\'message\', class: \'w-8 h-8\') %>\n                </a>\n              </div>\n            <% end %>\n          </div>\n        <% end %>\n        <a href="mailto:<%= Docuseal::SUPPORT_EMAIL %>" target="_blank" class="w-full block mt-4 underline">\n          <%= Docuseal::SUPPORT_EMAIL %>\n        </a>\n        <% if Docuseal.version.present? && !Docuseal.multitenant? && can?(:manage, EncryptedConfig) %>\n          <a href="https://github.com/docusealco/docuseal/releases" target="_blank" class="badge badge-outline text-xs block mx-auto mt-4">\n            v<%= Docuseal.version %>\n          </a>\n        <% end %>\n      </div>\n    <% end %>\n'
PAGAMENTI_BLOG = '      <div\n        v-if="isStripe && !stripeConnected"\n        class="px-1 pb-1.5"\n        @click.stop\n      >\n        <a\n          class="block link text-center text-xs"\n          href="https://www.docuseal.com/blog/accept-payments-and-request-signatures-with-ease"\n          target="_blank"\n          data-turbo="false"\n        >{{ t(\'learn_more\') }}</a>\n      </div>\n'
POWERED = '<%# SerSan: attribuzione a DocuSeal (licenza AGPL e termini aggiuntivi). Spenta finché non c\'è SERSAN_ATTRIBUZIONE=1 nel .env %>\n<% if ENV[\'SERSAN_ATTRIBUZIONE\'] == \'1\' %>\n  <div class="text-center px-2">\n    <% if local_assigns[:with_counter] %>\n      <% count = CompletedSubmitter.distinct.count(:submission_id) %>\n      <% if count > 1 %>\n        <%= t(\'count_documents_signed_with_html\', count:) %>\n      <% else %>\n        <%= t(\'powered_by\') %>\n      <% end %>\n    <% else %>\n      <%= t(\'powered_by\') %>\n    <% end %>\n    <a href="<%= Docuseal::PRODUCT_URL %><%= local_assigns[:link_path] %>" class="underline">DocuSeal</a> - <%= t(\'open_source_documents_software\') %> · <a href="<%= Docuseal::GITHUB_URL %>" class="underline" target="_blank" rel="noopener"><%= t(\'sersan_source_code\') %></a>\n  </div>\n<% end %>\n'
BRANDING = '<%# SerSan: attribuzione a DocuSeal, accesa con SERSAN_ATTRIBUZIONE=1 nel .env %>\n<% if ENV[\'SERSAN_ATTRIBUZIONE\'] == \'1\' %>\n  <%= t(\'powered_by\') %>\n  <a href="<%= Docuseal::PRODUCT_URL %>" target="_blank" rel="noopener">DocuSeal</a>\n<% end %>\n'

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

    # ---- Pulizia di DocuSeal (Michele, 2026-11-26: «elimina qualsiasi riferimento, pulsante, link, upgrade, repos,
    # chats, discord ecc, TUTTO»). Via: pulsanti e voci verso docuseal.com e la sua console, inviti a Pro,
    # GitHub/Discord/ChatGPT/email di supporto, avviso dell'app per telefono, pagina pubblicitaria di DocuSeal.
    # L'attribuzione «Powered by DocuSeal» resta nel codice ma spenta: si accende con SERSAN_ATTRIBUZIONE=1.
    ("app/views/shared/_powered_by.html.erb", None, POWERED),
    ("app/views/templates_share_link_qr/_branding.html.erb", None, BRANDING),
    ("app/views/submit_form/_submission_form.html.erb", 'data-attribution="<%= !turbo_native_app? %>"',
     "data-attribution=\"<%= ENV['SERSAN_ATTRIBUZIONE'] == '1' && !turbo_native_app? %>\""),
    ("app/views/shared/_email_attribution.html.erb", None, ""),
    ("app/views/shared/_github.html.erb", None, ""),
    ("app/views/shared/_mobile_app_alert.html.erb", None, ""),
    ("app/views/shared/_navbar_buttons.html.erb", None,
     "<% if signed_in? && current_user != true_user %>\n  <%= render 'shared/test_alert' %>\n<% end %>\n"),
    ("app/views/templates_code_modal/_placeholder.html.erb", None, ""),
    ("app/views/notifications_settings/_reminder_placeholder.html.erb", None, ""),
    ("app/views/sso_settings/_placeholder.html.erb", None, ""),
    ("app/views/sms_settings/_placeholder.html.erb", None, ""),
    ("app/views/personalization_settings/_logo_placeholder.html.erb", None, ""),
    ("app/views/submissions/_bulk_send_placeholder.html.erb", None, ""),
    ("app/views/submissions/_send_sms_button.html.erb", None, ""),
    ("app/views/esign_settings/_default_signature_row.html.erb", None, ""),
    ("app/views/users/_role_select.html.erb", None,
     "<div class=\"form-control\">\n  <%= f.label :role, class: 'label' %>\n  <%= f.select :role, nil, {}, class: 'base-select' do %>\n"
     "    <option value=\"admin\"><%= t('admin') %></option>\n  <% end %>\n</div>\n"),
    # chi non è entrato, su "/", vedeva la pagina pubblicitaria di DocuSeal: ora va all'accesso
    ("app/controllers/dashboard_controller.rb", "    render 'pages/landing'\n", "    redirect_to new_user_session_path\n"),
    ("app/controllers/errors_controller.rb", "'This feature is available in Pro Edition: https://www.docuseal.com/pricing'",
     "'This feature is not available'"),
    # menu dell'utente: niente "Console" (console.docuseal.com) e niente "Chiedi all'AI" (ChatGPT di DocuSeal)
    ("app/views/shared/_navbar.html.erb",
     "          <% if !Docuseal.demo? && can?(:manage, EncryptedConfig) %>\n            <li>\n"
     "              <%= link_to Docuseal.multitenant? ? console_redirect_index_path : Docuseal::CONSOLE_URL, data: { turbo_prefetch: false }, class: 'flex items-center' do %>\n"
     "                <%= svg_icon('terminal', class: 'w-5 h-5 flex-shrink-0 stroke-2') %>\n                <%= t('console') %>\n"
     "              <% end %>\n            </li>\n          <% end %>\n", ""),
    ("app/views/shared/_navbar.html.erb",
     "          <% if Docuseal.multitenant? || current_user.role == 'superadmin' %>\n            <li>\n"
     "              <%= link_to Docuseal::CHATGPT_URL, target: 'blank', class: 'flex items-center' do %>\n"
     "                <%= svg_icon('sparkles', class: 'w-5 h-5 flex-shrink-0 stroke-2') %>\n"
     "                <span class=\"mr-1 whitespace-nowrap\"><%= t('ask_ai') %></span>\n"
     "              <% end %>\n            </li>\n          <% end %>\n", ""),
    # impostazioni: niente "Piani Pro", "Console", né il riquadro con GitHub, Discord, ChatGPT, email e versione
    ("app/views/shared/_settings_nav.html.erb",
     "        <% if !Docuseal.demo? && !turbo_native_app? && can?(:manage, EncryptedConfig) && (current_user != true_user || !current_account.linked_account_account) %>\n"
     "          <li>\n"
     "            <%= content_for(:pro_link) || link_to(Docuseal.multitenant? ? console_redirect_index_path(redir: \"#{Docuseal::CONSOLE_URL}/plans\") : \"#{Docuseal::CLOUD_URL}/sign_up?#{{ redir: \"#{Docuseal::CONSOLE_URL}/on_premises\" }.to_query}\", class: 'text-base hover:bg-base-300', data: { turbo: false }) do %>\n"
     "              <%= t('plans') %>\n              <span class=\"badge badge-warning\"><%= t('pro') %></span>\n            <% end %>\n"
     "          </li>\n        <% end %>\n", ""),
    ("app/views/shared/_settings_nav.html.erb",
     "          <% unless turbo_native_app? %>\n            <li>\n"
     "              <%= link_to Docuseal.multitenant? ? console_redirect_index_path(redir: \"#{Docuseal::CONSOLE_URL}#{'/test' if current_account.testing?}/api\") : \"#{Docuseal::CONSOLE_URL}/on_premises\", class: 'text-base hover:bg-base-300', data: { turbo: false } do %>\n"
     "                <% if Docuseal.multitenant? %> API <% else %> <%= t('console') %> <% end %>\n"
     "              <% end %>\n            </li>\n          <% end %>\n", ""),
    ("app/views/shared/_settings_nav.html.erb", NAV_AIUTO, ""),
    ("app/views/api_settings/index.html.erb",
     "    <div class=\"text-center\">\n"
     "      <%= link_to t('open_full_api_reference'), \"#{Docuseal::PRODUCT_URL}/docs/api\", class: 'btn btn-warning text-base mt-4 px-8', target: '_blank', rel: 'noopener' %>\n"
     "    </div>\n", ""),
    ("app/views/templates/_embedding.html.erb",
     "        <%= link_to t('learn_more'), console_redirect_index_path(redir: \"#{Docuseal::CONSOLE_URL}/embedding/form\"), target: '_blank', data: { turbo: false }, class: 'btn btn-ghost text-gray-100 flex', rel: 'noopener' %>\n",
     "", 4),
    # PDF: niente docuseal.com nelle proprietà del file e nel registro di firma
    ("lib/submissions/generate_combined_attachment.rb", '"#{Docuseal.product_name} (#{Docuseal::PRODUCT_URL})"', "Docuseal.product_name"),
    ("lib/submissions/generate_audit_trail.rb", '"#{Docuseal.product_name} (#{Docuseal::PRODUCT_URL})"', "Docuseal.product_name"),
    ("lib/submissions/generate_result_attachments.rb", '"#{Docuseal.product_name} (#{Docuseal::PRODUCT_URL})"', "Docuseal.product_name"),
    ("lib/submissions/generate_audit_trail.rb", "                               link: Docuseal::PRODUCT_EMAIL_URL }],\n",
     "                               link: 'https://sersan.io' }],\n"),
    # editor dei modelli: niente caselle bloccate verso i prezzi di DocuSeal, niente formule e condizioni (sono Pro)
    ("app/javascript/template_builder/fields.vue", FIELDS_TELEFONO, ""),
    ("app/javascript/template_builder/fields.vue", FIELDS_QES, ""),
    ("app/javascript/template_builder/payment_settings.vue", 'v-if="withFormula || !nativePlatform"', 'v-if="withFormula"'),
    ("app/javascript/template_builder/payment_settings.vue", "(withConditions || !nativePlatform)", "withConditions"),
    ("app/javascript/template_builder/payment_settings.vue", PAGAMENTI_BLOG, ""),
    ("app/javascript/template_builder/field_settings.vue", "(withConditions || !nativePlatform)", "withConditions"),
    ("app/javascript/template_builder/field_settings.vue", "(withFormula || !nativePlatform)", "withFormula"),
    ("app/javascript/template_builder/selection_context_menu.vue", "(this.withConditions || !this.nativePlatform)", "this.withConditions"),
    ("app/javascript/template_builder/field_context_menu.vue", "(this.withConditions || !this.nativePlatform)", "this.withConditions"),
    ("app/javascript/template_builder/field_context_menu.vue", "(this.withFormula || !this.nativePlatform)", "this.withFormula"),

    # ---- Firma scritta (Michele, 2026-11-26: «non ti fa scrivere il tuo nome e via come su Google o DocuSign»).
    # Quando è permessa, la firma parte già scritta (con il nome, se il campo è obbligatorio) e si sceglie tra
    # tre stili (app/javascript/submission_form/sersan_signature_fonts.js, caratteri in public/sersan-firme/).
    # Disegnare resta possibile con il pulsante «Disegna».
    ("app/javascript/submission_form/signature_step.vue", "import { v4 } from 'uuid'\n",
     "import { v4 } from 'uuid'\nimport { SIGNATURE_FONTS, fontsFor, fontFor, fontSpec, loadSignatureFonts } from './sersan_signature_fonts'\n"),
    ("app/javascript/submission_form/signature_step.vue",
     "      isTextSignature: !this.signatureSrc && (!!this.signatureText || this.field.preferences?.format === 'typed' || this.field.preferences?.format === 'typed_or_upload'),\n",
     "      isTextSignature: !this.signatureSrc && (!!this.signatureText || this.field.preferences?.format === 'typed' || this.field.preferences?.format === 'typed_or_upload' ||\n"
     "        (this.withTypedSignature && !['drawn', 'drawn_or_upload', 'upload'].includes(this.field.preferences?.format))),\n"
     "      signatureFont: SIGNATURE_FONTS[0].family,\n"
     "      typedText: '',\n"),
    ("app/javascript/submission_form/signature_step.vue", "  computed: {\n    submitterSlug () {\n",
     "  computed: {\n    signatureFonts () {\n      return fontsFor(this.typedText)\n    },\n"
     "    signaturePreviewText () {\n      return this.typedText || this.submitter.name || this.t('signature')\n    },\n"
     "    submitterSlug () {\n"),
    ("app/javascript/submission_form/signature_step.vue",
     "      if (!fontLoadPromise) {\n"
     "        const font = new FontFace('Dancing Script', `url(${this.baseUrl}/fonts/DancingScript-Regular.otf) format(\"opentype\")`)\n\n"
     "        fontLoadPromise = font.load().then((loadedFont) => {\n"
     "          document.fonts.add(loadedFont)\n"
     "        }).catch((error) => {\n"
     "          console.error('Font loading failed:', error)\n"
     "        })\n"
     "      }\n\n"
     "      return fontLoadPromise\n",
     "      fontLoadPromise = loadSignatureFonts(this.baseUrl, this.$refs.textInput?.value || this.submitter.name)\n\n"
     "      return fontLoadPromise\n"),
    ("app/javascript/submission_form/signature_step.vue",
     "      this.isSignatureStarted = !!e.target.value\n\n"
     "      const canvas = this.$refs.canvas\n"
     "      const context = canvas.getContext('2d')\n\n"
     "      const fontFamily = 'Dancing Script'\n"
     "      const initialFontSize = 44\n"
     "      const fontStyle = 'italic'\n"
     "      const fontWeight = ''\n",
     "      this.isSignatureStarted = !!e.target.value\n"
     "      this.typedText = e.target.value\n\n"
     "      const canvas = this.$refs.canvas\n"
     "      const context = canvas.getContext('2d')\n\n"
     "      const font = fontFor(this.signatureFont, e.target.value)\n\n"
     "      this.signatureFont = font.family\n\n"
     "      const fontFamily = `\"${font.family}\"`\n"
     "      const initialFontSize = font.size\n"
     "      const fontStyle = font.style\n"
     "      const fontWeight = ''\n"),
    ("app/javascript/submission_form/signature_step.vue",
     "      context.fillText(e.target.value, canvas.width / 2 / scale, canvas.height / 2 / scale + 11)\n    },\n",
     "      context.fillText(e.target.value, canvas.width / 2 / scale, canvas.height / 2 / scale + 11)\n\n"
     "      if (e.target.value && !e.reloaded && !document.fonts.check(fontSpec(font), e.target.value)) {\n"
     "        loadSignatureFonts(this.baseUrl, e.target.value).then(() => {\n"
     "          if (this.$refs.textInput && this.$refs.textInput.value === e.target.value) {\n"
     "            this.updateWrittenSignature({ target: this.$refs.textInput, reloaded: true })\n"
     "          }\n"
     "        })\n"
     "      }\n"
     "    },\n"
     "    selectSignatureFont (family) {\n"
     "      this.signatureFont = family\n\n"
     "      if (this.$refs.textInput) {\n"
     "        this.updateWrittenSignature({ target: this.$refs.textInput })\n"
     "      }\n"
     "    },\n"),
    ("app/javascript/submission_form/signature_step.vue",
     "      type=\"text\"\n      @input=\"updateWrittenSignature\"\n    >\n",
     "      type=\"text\"\n      @input=\"updateWrittenSignature\"\n    >\n"
     "    <div\n"
     "      v-if=\"isTextSignature && !modelValue && !computedPreviousValue && !computedPrefillData\"\n"
     "      class=\"flex flex-wrap gap-2 mt-3\"\n"
     "      role=\"group\"\n"
     "      :aria-label=\"t('signature')\"\n"
     "    >\n"
     "      <button\n"
     "        v-for=\"font in signatureFonts\"\n"
     "        :key=\"font.family\"\n"
     "        type=\"button\"\n"
     "        class=\"btn btn-sm h-auto min-h-0 py-1.5 px-4 normal-case font-normal text-2xl rounded-xl max-w-full overflow-hidden whitespace-nowrap\"\n"
     "        :class=\"font.family === signatureFont ? 'btn-neutral' : 'btn-outline border-base-300'\"\n"
     "        :style=\"{ fontFamily: `'${font.family}', cursive`, fontStyle: font.style || 'normal' }\"\n"
     "        :aria-label=\"font.family\"\n"
     "        :aria-pressed=\"font.family === signatureFont\"\n"
     "        @click=\"selectSignatureFont(font.family)\"\n"
     "      >\n"
     "        {{ signaturePreviewText }}\n"
     "      </button>\n"
     "    </div>\n"),

    # Test: la firma ora parte scritta (per disegnare si preme «Draw»), e la frase sui link condivisi non ha più la guida.
    ("spec/system/signing_form_spec.rb",
     "      find('#expand_form_button').click\n      page.find('canvas').click([], { x: 150, y: 100 })\n",
     "      find('#expand_form_button').click\n      click_button 'Draw'\n      page.find('canvas').click([], { x: 150, y: 100 })\n"),
    ("spec/system/signing_form_spec.rb",
     "      find('#expand_form_button').click\n      click_button 'Type'\n      fill_in 'signature_text_input', with: 'John Doe'\n",
     "      find('#expand_form_button').click\n      fill_in 'signature_text_input', with: 'John Doe'\n"),
    ("spec/system/signing_form_spec.rb",
     "                                     'To resolve this, follow this guide to define the default signer details.')\n"
     "        expect(page).to have_link('guide', href: 'https://www.docuseal.com/resources/pre-filling-recipients')\n",
     "                                     'To resolve this, set the default signer details in the template.')\n"),
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
