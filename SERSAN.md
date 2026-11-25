# SerSan Sign: il fork SerSan di DocuSeal

Questo repository è il fork di [DocuSeal](https://github.com/docusealco/docuseal) che SerSan usa per far firmare i documenti ai clienti.

**Licenza.** AGPL-3.0 con i termini aggiuntivi di DocuSeal (`LICENSE`, `LICENSE_ADDITIONAL_TERMS`):
- il servizio è usato via web da persone esterne, quindi il codice modificato sta qui, pubblico;
- l'interfaccia mostra «Powered by DocuSeal» con accanto il link «Codice sorgente» a questo repository;
- l'attribuzione a DocuSeal non si toglie.

## Rami e versioni

- **`master`:** copia di DocuSeal, senza modifiche. Si aggiorna con «Sync fork» su GitHub o con `git fetch upstream`.
- **`sersan`**, il ramo predefinito: una release di DocuSeal più le modifiche SerSan. Oggi la base è **3.4.0**.
- **Tag `sersan-<versione DocuSeal>-<n>`**, per esempio `sersan-3.4.0-1`. Ogni tag costruisce l'immagine `ghcr.io/sersan-studio/docuseal:<tag>` (`.github/workflows/sersan-image.yml`). Il workflow `docker.yml` di DocuSeal (Docker Hub) in questo fork è spento.

## Cosa cambia rispetto a DocuSeal

Poche modifiche, tutte isolate, perché gli aggiornamenti restino facili. Le applica `sersan/applica-marchio.py`, le immagini le rifà `sersan/genera-icone.sh`.

- **Nome:** «SerSan Sign», da `PRODUCT_NAME` in `lib/docuseal.rb`. Lo usano anche titoli, meta, manifest, email di sistema e PDF. Nello stesso file `GITHUB_URL` punta a questo fork.
- **Logo SerSan:**
  - `public/sersan-logo.png`, che usano `app/views/shared/_logo.html.erb` e `app/javascript/template_builder/logo.vue`;
  - favicon e icone in `public/`;
  - logo del registro di firma e scritta del timbro nei PDF, in `lib/pdf_icons/`.
- **Attribuzione:** «Powered by DocuSeal» resta, con accanto «Codice sorgente». File: `shared/_powered_by.html.erb`, `submission_form/completed.vue`, `templates_share_link_qr/_branding.html.erb` e `shared/_email_attribution.html.erb`.
- **Colori:** colori SerSan sui pulsanti e negli accenti (`tailwind.config.js`). Sfondi e testo restano quelli di DocuSeal.
- **Italiano:**
  - lingua predefinita dei conti nuovi (`app/models/account.rb`);
  - chi firma vede la lingua del suo browser; se è una lingua che DocuSeal non ha, vede l'italiano invece dell'inglese (`app/controllers/application_controller.rb`).
- **Email e PDF:** mittente predefinito «SerSan Sign \<sign@sersan.io\>» (`app/mailers/application_mailer.rb`); nei PDF, testo del registro di firma e motivo della firma digitale.

## Aggiornare a una versione nuova di DocuSeal

```bash
git fetch upstream --tags
git switch sersan
git merge 3.4.1                        # la versione nuova; gli eventuali conflitti stanno nei file qui sopra
python3 sersan/applica-marchio.py      # deve dire "fatto" o "già fatto" ovunque; "DA GUARDARE" = upstream ha cambiato quel punto
sersan/genera-icone.sh                 # solo se upstream ha cambiato icone o logo (gira su un Mac: sips, ffmpeg, swift)
grep -rn "DocuSeal" app/views app/javascript lib --include='*.erb' --include='*.vue' --include='*.rb' | grep -v -i "powered\|attribution"   # scritte nuove?
git commit -am "SerSan: DocuSeal 3.4.1"
git push origin sersan
git tag sersan-3.4.1-1 && git push origin sersan-3.4.1-1      # costruisce l'immagine (Actions, circa 15 minuti)
```

Poi sul server si cambia il tag dell'immagine nel Compose: `docker compose pull && docker compose up -d`. Le migrazioni del database partono da sole all'avvio. Prima, un dump del database.

L'installazione (server, database, posta, backup) è descritta nella documentazione interna di SerSan.
