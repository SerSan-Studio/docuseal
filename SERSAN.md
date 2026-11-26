# SerSan Sign: il fork SerSan di DocuSeal

Questo repository è il fork di [DocuSeal](https://github.com/docusealco/docuseal) che SerSan usa per far firmare i documenti ai clienti.

**Licenza.** AGPL-3.0 con i termini aggiuntivi di DocuSeal (`LICENSE`, `LICENSE_ADDITIONAL_TERMS`):
- il servizio è usato via web da persone esterne, quindi il codice modificato sta qui, pubblico;
- l'interfaccia mostra «Powered by DocuSeal» con accanto il link «Codice sorgente» a questo repository;
- l'attribuzione a DocuSeal non si toglie.

## Rami e versioni

- **`master`:** copia di DocuSeal, senza modifiche. Si aggiorna con «Sync fork» su GitHub o con `git fetch upstream`.
- **`sersan`**, il ramo predefinito: una release di DocuSeal più le modifiche SerSan. Oggi la base è **3.4.0**.
- **Tag `sersan-<versione DocuSeal>-<n>`**, per esempio `sersan-3.4.0-1`. Ogni tag costruisce l'immagine `ghcr.io/sersan-studio/docuseal:<tag>`, privata, e la lascia anche come artefatto del workflow per 7 giorni (`.github/workflows/sersan-image.yml`). Il server non ha credenziali di GitHub: l'immagine gli arriva dall'artefatto, con `docker load`. Il workflow `docker.yml` di DocuSeal (Docker Hub) in questo fork è spento.

## Cosa cambia rispetto a DocuSeal

Poche modifiche, tutte isolate, perché gli aggiornamenti restino facili. Le applica `sersan/applica-marchio.py` (sostituzioni sui file di DocuSeal, più i file da togliere), le immagini le rifà `sersan/genera-icone.sh`. Quello che è solo nostro sta in file a parte: `app/javascript/sersan.css`, `public/sersan-*`, le traduzioni russe.

- **Nome:** «SerSan Sign», da `PRODUCT_NAME` in `lib/docuseal.rb`. Lo usano anche titoli, meta, manifest, email di sistema e PDF. Nello stesso file `GITHUB_URL` punta a questo fork. Nella barra in alto «SerSan» è pieno e «Sign» è nel blu del marchio (`shared/_title.html.erb`).
- **Logo SerSan**, lo stesso di sersan.io (le due metà dell'esagono, navy e blu):
  - `public/sersan-logo.svg`, che usano `app/views/shared/_logo.html.erb` e `app/javascript/template_builder/logo.vue`;
  - favicon e icone in `public/` (la favicon SVG diventa chiara se il browser è scuro). I browser le tengono in cache 180 giorni: negli indirizzi c'è `?v=…` (costante `ICONE` in `applica-marchio.py`), da cambiare quando cambiano logo o icone;
  - logo del registro di firma e scritta del timbro nei PDF, in `lib/pdf_icons/`;
  - le forme stanno in `sersan/marchio.swift`, che disegna i PNG.
- **Attribuzione:** «Powered by DocuSeal» resta, con accanto il link «Codice sorgente» nella lingua di chi legge (chiave `sersan_source_code`: `config/locales/sersan.yml` per le pagine, `en` e `it` in `submission_form/i18n.js` e `i18n_ru.js` per chi firma). File: `shared/_powered_by.html.erb`, `submission_form/completed.vue`, `templates_share_link_qr/_branding.html.erb` e `shared/_email_attribution.html.erb`.
- **Stile di sersan.io:**
  - colori nel tema di `tailwind.config.js` (e `tailwind.dynamic.config.js`): testo e pulsanti nel navy del marchio, blu e ciano per gli accenti, sfondi chiari freddi al posto del beige di DocuSeal; scritte dei pulsanti non tutte maiuscole;
  - `app/javascript/sersan.css`, importato da `application.scss` e `form.scss`: caratteri, titoli, bagliore ciano in alto, pulsanti e campi;
  - caratteri **Inter** (testo, anche cirillico) e **Fraunces** (titoli), licenza OFL, in `app/javascript/sersan-fonts/` con le licenze (webpack li pubblica in `/packs/static/`). Switzer, il carattere di sersan.io, non ha una licenza che permetta di metterlo in un repository pubblico.
- **Niente newsletter di DocuSeal:** dopo il primo accesso si va al cruscotto invece che alla pagina «Developer Newsletters», che mandava l'email a docuseal.com. Tolti controller, vista, rotta e test.
- **Italiano:**
  - lingua predefinita dei conti nuovi (`app/models/account.rb`);
  - chi firma vede la lingua del suo browser; se è una lingua che DocuSeal non ha, vede l'italiano invece dell'inglese (`app/controllers/application_controller.rb`).
- **Russo**, che DocuSeal non ha:
  - traduzioni nostre in `config/locales/ru.yml` (interfaccia, email, PDF), `app/javascript/submission_form/i18n_ru.js` (chi firma) e `app/javascript/template_builder/i18n_ru.js` (editor dei modelli);
  - negli elenchi delle lingue: `config/application.rb`, `accounts_controller.rb` (lingua del conto), `devise/shared/_links.html.erb`, i due `i18n.js`, formati di data e numeri in `builder.vue`, `field_settings.vue`, `dynamic_variable.vue`;
  - le chiavi nuove che arrivano con gli aggiornamenti di DocuSeal, finché non le traduciamo, compaiono in inglese.
- **Email e PDF:** mittente predefinito «SerSan Sign \<sign@sersan.io\>» (`app/mailers/application_mailer.rb`); nei PDF, testo del registro di firma e motivo della firma digitale.

## Aggiornare a una versione nuova di DocuSeal

```bash
git fetch upstream --tags
git switch sersan
git merge 3.4.1                        # la versione nuova; gli eventuali conflitti stanno nei file qui sopra
python3 sersan/applica-marchio.py      # deve dire "fatto" o "già fatto" ovunque; "DA GUARDARE" = upstream ha cambiato quel punto
sersan/genera-icone.sh                 # solo se upstream ha cambiato icone o logo (gira su un Mac: sips, ffmpeg, swift)
grep -rn "DocuSeal" app/views app/javascript lib --include='*.erb' --include='*.vue' --include='*.rb' | grep -v -i "powered\|attribution"   # scritte nuove?
git diff 3.4.0 3.4.1 -- config/locales/i18n.yml app/javascript/*/i18n.js   # chiavi nuove da tradurre in russo (ru.yml, i18n_ru.js)?
git commit -am "SerSan: DocuSeal 3.4.1"
git push origin sersan
git tag sersan-3.4.1-1 && git push origin sersan-3.4.1-1      # costruisce l'immagine (Actions, pochi minuti)
```

Poi sul server: un dump del database, l'immagine nuova caricata dall'artefatto (`gh run download`, poi `docker load`), il tag nuovo nel Compose e `docker compose up -d`. Le migrazioni del database partono da sole all'avvio.

L'installazione (server, database, posta, backup) è descritta nella documentazione interna di SerSan.
