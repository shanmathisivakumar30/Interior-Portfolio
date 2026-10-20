# Shanmathi Sivakumar — Interior Design Portfolio

The portfolio website of **Shanmathi Sivakumar**, interior designer and architect based in Dallas, Texas.

**Live site:** [theshansstudio.com](https://theshansstudio.com)

The site is designed in Claude Design and published with GitHub Pages. It is a static site: there is no build step and no server code.

## What's on the site

| Page | File | What it shows |
|---|---|---|
| Studio (home) | `Home.dc.html`, served as `index.html` | Hand-drawn studio illustration and opening animation |
| About | `About.dc.html` | Contact, skills, software, experience, education, CV download |
| Projects | `Main.dc.html` | Index of all six projects |
| Light, Within! | `Chapter1.dc.html` | Residential interior, Raipur |
| A House That Listens | `Chapter3.dc.html` | Residential interior, Dallas |
| A Little Unbuttoned | `Chapter4.dc.html` | Glamping project |
| The Breakfast Club | `Chapter2.dc.html` | Hospitality interior |
| A Softer Landing | `Chapter5.dc.html` | Healthcare interior |
| Spatial Fragments | `Chapter6.dc.html` | Mood board compilations |

## Repository layout

```
.
├── README.md            This file
├── tools/
│   └── update_site.py   Merges new Claude Design exports into docs/
└── docs/                The published website (GitHub Pages serves this folder)
    ├── index.html       Copy of Home.dc.html, so the domain opens the homepage
    ├── *.dc.html        Pages, plus the components they load (Slot-*, Annot*, DreamFooter)
    ├── assets/          Images, drawings, fonts and the CV PDF
    ├── vendor/          React, used by the Claude Design page runtime
    ├── support.js       Claude Design page runtime
    ├── Library.dc.html  Redirects an old link to the Projects page
    ├── CNAME            Custom domain for GitHub Pages
    └── .nojekyll        Tells GitHub Pages to serve files as-is
```

Pages and their components sit side by side in `docs/` on purpose. The Claude Design runtime loads each component by name from the page's own folder, so moving them into subfolders would break the site.

## Updating the site

1. In Claude Design, open the page that changed and choose **Export → Download as .zip**.
2. Merge the export and check every link:

   ```sh
   python3 tools/update_site.py ~/Downloads/Export.zip
   ```

   The script copies the export into `docs/`, rebuilds `index.html` from the homepage, and lists any link, image or component that doesn't resolve. It exits with an error if something is missing.
3. Commit and push. GitHub Pages republishes in about a minute.

Several exports can be merged at once: `python3 tools/update_site.py one.zip two.zip`.
To list images no page uses anymore: `python3 tools/update_site.py --unused`.

### Rules that keep the site working

- **Don't rename exported files.** Pages link to each other by their exported names (`About.dc.html`, `Chapter1.dc.html` and so on), and the names are case-sensitive.
- **Don't edit files in `docs/` by hand.** The next export overwrites them. Make changes in Claude Design and re-export.
- **Keep `CNAME`, `.nojekyll`, `index.html` and `Library.dc.html`.** They belong to this site, not to any export, and the update script never overwrites them (it regenerates `index.html` itself).

## Hosting

- **GitHub Pages:** Settings → Pages → Deploy from a branch → `main`, folder `/docs`.
- **Domain:** `theshansstudio.com`, registered at GoDaddy. DNS points to GitHub Pages: four `A` records for `@` (`185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`) and a `CNAME` record for `www` pointing to `shanmathisivakumar30.github.io`.

## Rights

© Shanmathi Sivakumar. All designs, drawings, renders and images in this repository are her work and may not be reused without permission.
