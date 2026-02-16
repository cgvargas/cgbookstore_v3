/**
 * EBookReader — Modern EPUB Reader
 * 
 * Parses EPUB directly with JSZip and renders HTML into the DOM
 * (no iframe, no epub.js). Pagination via CSS columns.
 */

class EBookReader {
    constructor() {
        this.bookData = window.EBOOK_DATA || {};
        this.zip = null;          // JSZip instance
        this.spine = [];          // ordered list of {href, id}
        this.toc = [];            // table of contents
        this.metadata = {};       // title, author, etc.
        this.basePath = '';       // relative path prefix inside ZIP
        this.blobUrls = new Map();// href -> blob URL for images

        // Pagination state
        this.currentPage = 1;
        this.totalPages = 1;
        this.pageWidth = 0;
        this.columnGap = 80;

        // Session
        this.sessionStartTime = Date.now();
        this.autoSaveTimer = null;

        // Settings
        this.settings = {
            theme: 'dark',
            fontSize: 18,
            fontFamily: 'serif',
        };

        // DOM refs
        this.el = {
            page: document.getElementById('reader-page'),
            content: document.getElementById('reader-content'),
            frame: document.getElementById('content-frame'),
            viewport: document.getElementById('reader-viewport'),
            chapterTitle: document.getElementById('chapter-title'),
            pageInfo: document.getElementById('page-info'),
            progressFill: document.getElementById('progress-fill'),
            progressPct: document.getElementById('progress-pct'),
            loading: document.getElementById('loading-screen'),
            loaderText: document.getElementById('loader-text'),
            loaderProgress: document.getElementById('loader-progress'),
            panel: document.getElementById('side-panel'),
            panelOverlay: document.getElementById('panel-overlay'),
            tocList: document.getElementById('toc-list'),
            bookmarksContainer: document.getElementById('bookmarks-container'),
            fontSizeValue: document.getElementById('font-size-value'),
            btnBookmark: document.getElementById('btn-bookmark'),
        };

        this.init();
    }

    // ╔══════════════════════════════════════════╗
    // ║           INITIALIZATION                 ║
    // ╚══════════════════════════════════════════╝

    async init() {
        if (!this.bookData.epubUrl) {
            this.showError('URL do livro não disponível');
            return;
        }

        try {
            this.bindEvents();
            this.loadSettings();
            await this.loadBook();
            this.hideLoading();
            this.startAutoSave();
            console.log('[Reader] Livro carregado com sucesso!');
        } catch (err) {
            console.error('[Reader] Erro ao carregar livro:', err);
            this.showError('Erro ao carregar o livro. Tente novamente.');
        }
    }

    // ╔══════════════════════════════════════════╗
    // ║          EPUB PARSING (JSZip)            ║
    // ╚══════════════════════════════════════════╝

    async loadBook() {
        // 1) Fetch EPUB as ArrayBuffer
        this.setLoaderText('Baixando livro...');
        const response = await fetch(this.bookData.epubUrl);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const arrayBuffer = await response.arrayBuffer();
        console.log('[Reader] EPUB baixado:', (arrayBuffer.byteLength / 1024).toFixed(0), 'KB');

        // 2) Decompress with JSZip
        this.setLoaderText('Descompactando...');
        this.zip = await JSZip.loadAsync(arrayBuffer);

        // 3) Parse container.xml → find OPF path
        const containerXml = await this.zip.file('META-INF/container.xml').async('text');
        const containerDoc = this.parseXml(containerXml);
        const rootfilePath = containerDoc.querySelector('rootfile').getAttribute('full-path');
        this.basePath = rootfilePath.includes('/')
            ? rootfilePath.substring(0, rootfilePath.lastIndexOf('/') + 1)
            : '';

        // 4) Parse OPF → manifest, spine, metadata
        this.setLoaderText('Processando conteúdo...');
        const opfText = await this.zip.file(rootfilePath).async('text');
        const opfDoc = this.parseXml(opfText);
        const manifest = this.parseManifest(opfDoc);
        this.spine = this.parseSpine(opfDoc, manifest);
        this.metadata = this.parseMetadata(opfDoc);

        // 5) Parse TOC (NCX or nav)
        this.toc = await this.parseTOC(manifest);

        // 6) Render ALL spine content into DOM
        this.setLoaderText('Renderizando páginas...');
        await this.renderAllContent();

        // 7) Calculate pagination
        this.recalculatePages();

        // 8) Build TOC UI
        this.buildTOC();

        // 9) Restore saved position
        this.restoreProgress();

        // 10) Load bookmarks
        this.loadBookmarks();
    }

    parseXml(xmlString) {
        return new DOMParser().parseFromString(xmlString, 'application/xml');
    }

    parseHtml(htmlString) {
        // Parse EPUB XHTML as HTML so elements are in the HTML namespace
        // and respond to CSS selectors properly
        return new DOMParser().parseFromString(htmlString, 'text/html');
    }

    parseManifest(opfDoc) {
        const manifest = {};
        // Handle namespaced and non-namespaced
        const items = opfDoc.querySelectorAll('manifest > item')
            || opfDoc.getElementsByTagName('item');
        for (const item of items) {
            manifest[item.getAttribute('id')] = {
                href: item.getAttribute('href'),
                mediaType: item.getAttribute('media-type'),
                properties: item.getAttribute('properties') || '',
            };
        }
        return manifest;
    }

    parseSpine(opfDoc, manifest) {
        const spine = [];
        const refs = opfDoc.querySelectorAll('spine > itemref')
            || opfDoc.getElementsByTagName('itemref');
        for (const ref of refs) {
            const id = ref.getAttribute('idref');
            if (manifest[id] && manifest[id].mediaType?.includes('html')) {
                spine.push({ id, href: manifest[id].href });
            }
        }
        return spine;
    }

    parseMetadata(opfDoc) {
        const getText = (tag) => {
            const el = opfDoc.getElementsByTagName(tag)[0]
                || opfDoc.querySelector(`metadata > *[*|${tag}]`);
            return el ? el.textContent.trim() : '';
        };
        return {
            title: getText('dc:title') || getText('title') || this.bookData.title,
            author: getText('dc:creator') || getText('creator') || this.bookData.author,
            language: getText('dc:language') || getText('language') || 'en',
        };
    }

    async parseTOC(manifest) {
        // Try NCX first (EPUB 2)
        for (const [id, item] of Object.entries(manifest)) {
            if (item.mediaType === 'application/x-dtbncx+xml') {
                return await this.parseNCX(item.href);
            }
        }
        // Try nav document (EPUB 3)
        for (const [id, item] of Object.entries(manifest)) {
            if (item.properties.includes('nav')) {
                return await this.parseNavDoc(item.href);
            }
        }
        // Fallback: generate from spine
        return this.spine.map((s, i) => ({
            label: `Capítulo ${i + 1}`,
            href: s.href,
            spineIndex: i,
        }));
    }

    async parseNCX(ncxHref) {
        const file = this.zip.file(this.basePath + ncxHref);
        if (!file) return [];
        const ncxText = await file.async('text');
        const doc = this.parseXml(ncxText);
        const toc = [];
        const navPoints = doc.querySelectorAll('navMap > navPoint');
        for (const np of navPoints) {
            const label = np.querySelector('navLabel > text')?.textContent?.trim() || '';
            const src = np.querySelector('content')?.getAttribute('src') || '';
            const href = src.split('#')[0];
            const spIdx = this.spine.findIndex(s => s.href === href || s.href.endsWith(href));
            toc.push({ label, href, spineIndex: spIdx >= 0 ? spIdx : 0 });

            // Sub-items (depth 1)
            const subPoints = np.querySelectorAll(':scope > navPoint');
            for (const sub of subPoints) {
                const subLabel = sub.querySelector('navLabel > text')?.textContent?.trim() || '';
                const subSrc = sub.querySelector('content')?.getAttribute('src') || '';
                const subHref = subSrc.split('#')[0];
                const subIdx = this.spine.findIndex(s => s.href === subHref || s.href.endsWith(subHref));
                toc.push({ label: subLabel, href: subHref, spineIndex: subIdx >= 0 ? subIdx : 0, sub: true });
            }
        }
        return toc;
    }

    async parseNavDoc(navHref) {
        const file = this.zip.file(this.basePath + navHref);
        if (!file) return [];
        const navText = await file.async('text');
        const doc = this.parseXml(navText);
        const toc = [];
        const links = doc.querySelectorAll('nav[*|type="toc"] a, nav.toc a, nav[role="doc-toc"] a');
        for (const a of links) {
            const label = a.textContent.trim();
            const href = (a.getAttribute('href') || '').split('#')[0];
            const spIdx = this.spine.findIndex(s => s.href === href || s.href.endsWith(href));
            toc.push({ label, href, spineIndex: spIdx >= 0 ? spIdx : 0 });
        }
        return toc.length > 0 ? toc : this.spine.map((s, i) => ({
            label: `Capítulo ${i + 1}`, href: s.href, spineIndex: i
        }));
    }

    // ╔══════════════════════════════════════════╗
    // ║           RENDERING                      ║
    // ╚══════════════════════════════════════════╝

    async renderAllContent() {
        const fragment = document.createDocumentFragment();

        for (let i = 0; i < this.spine.length; i++) {
            const spineItem = this.spine[i];
            const filePath = this.basePath + spineItem.href;
            const file = this.zip.file(filePath);

            if (!file) {
                console.warn('[Reader] Spine item not found:', filePath);
                continue;
            }

            // Load XHTML content (parse as HTML for proper CSS styling)
            const xhtml = await file.async('text');
            const doc = this.parseHtml(xhtml);

            // Get body content
            const body = doc.querySelector('body');
            if (!body) continue;

            // Resolve image URLs
            await this.resolveImages(body, spineItem.href);

            // Create chapter wrapper
            const chapter = document.createElement('div');
            chapter.className = 'chapter-block';
            chapter.dataset.spine = i;
            chapter.dataset.href = spineItem.href;

            // Copy sanitized content
            for (const child of Array.from(body.childNodes)) {
                chapter.appendChild(this.importNode(child));
            }

            // Add chapter separator (forces page break between chapters)
            if (i > 0) {
                const sep = document.createElement('div');
                sep.className = 'chapter-separator';
                fragment.appendChild(sep);
            }

            fragment.appendChild(chapter);

            // Progress feedback
            if (i % 5 === 0) {
                this.setLoaderProgress(`${i + 1} / ${this.spine.length} seções`);
            }
        }

        this.el.content.innerHTML = '';
        this.el.content.appendChild(fragment);
    }

    importNode(node) {
        // Deep import, stripping <script> tags and harmful inline styles
        if (node.nodeType === Node.ELEMENT_NODE) {
            if (node.tagName.toLowerCase() === 'script') {
                return document.createComment('script removed');
            }
            if (node.tagName.toLowerCase() === 'link') {
                return document.createComment('link removed');
            }
            // Strip <style> tags from EPUB (they override our theme)
            if (node.tagName.toLowerCase() === 'style') {
                return document.createComment('style removed');
            }
        }
        try {
            const imported = document.importNode(node, true);
            // Strip color-related inline styles from all elements
            if (imported.nodeType === Node.ELEMENT_NODE) {
                this.stripInlineStyles(imported);
            }
            return imported;
        } catch {
            return document.createTextNode(node.textContent || '');
        }
    }

    stripInlineStyles(el) {
        // Remove color/background/font styles that conflict with our theme
        if (el.style) {
            el.style.removeProperty('color');
            el.style.removeProperty('background');
            el.style.removeProperty('background-color');
            el.style.removeProperty('font-family');
        }
        // Recurse into children
        for (const child of el.children) {
            this.stripInlineStyles(child);
        }
    }

    async resolveImages(body, spineHref) {
        const imgs = body.querySelectorAll('img, image');
        const spineDir = spineHref.includes('/')
            ? spineHref.substring(0, spineHref.lastIndexOf('/') + 1)
            : '';

        for (const img of imgs) {
            let src = img.getAttribute('src') || img.getAttributeNS('http://www.w3.org/1999/xlink', 'href');
            if (!src || src.startsWith('data:') || src.startsWith('blob:')) continue;

            // Decode URL (fix %20 spaces etc)
            try { src = decodeURIComponent(src); } catch (e) { }

            // Resolve relative path and normalize (handle ../)
            let resolvedPath = this.normalizePath(this.basePath + spineDir + src);

            // Check cache
            if (this.blobUrls.has(resolvedPath)) {
                const url = this.blobUrls.get(resolvedPath);
                this.setImageSrc(img, url);
                continue;
            }

            // Try direct path first
            let file = this.zip.file(resolvedPath);

            // Fallback 1: try without basePath
            if (!file) {
                const altPath = this.normalizePath(spineDir + src);
                file = this.zip.file(altPath);
            }

            // Fallback 2: try just the filename (search entire ZIP)
            if (!file) {
                const filename = src.split('/').pop();
                const matches = this.zip.file(new RegExp('(^|/)' + filename.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '$'));
                if (matches.length > 0) {
                    file = matches[0];
                    resolvedPath = file.name;
                }
            }

            if (file) {
                try {
                    const blob = await file.async('blob');
                    const url = URL.createObjectURL(blob);
                    this.blobUrls.set(resolvedPath, url);
                    this.setImageSrc(img, url);
                } catch { /* skip broken images */ }
            }
        }
    }

    setImageSrc(img, url) {
        if (img.tagName.toLowerCase() === 'image') {
            img.setAttributeNS('http://www.w3.org/1999/xlink', 'href', url);
            img.setAttribute('href', url);
        } else {
            img.setAttribute('src', url);
        }
    }

    normalizePath(path) {
        // Resolve ../ and ./ in paths
        const parts = path.split('/');
        const result = [];
        for (const part of parts) {
            if (part === '..') {
                result.pop();
            } else if (part !== '.' && part !== '') {
                result.push(part);
            }
        }
        return result.join('/');
    }

    // ╔══════════════════════════════════════════╗
    // ║         PAGINATION (CSS Columns)         ║
    // ╚══════════════════════════════════════════╝

    recalculatePages() {
        const frame = this.el.frame;
        const content = this.el.content;

        const pageHeight = frame.clientHeight;

        // Calculate actual column width (content area minus padding)
        const cs = getComputedStyle(content);
        const padLeft = parseFloat(cs.paddingLeft) || 0;
        const padRight = parseFloat(cs.paddingRight) || 0;
        this.columnWidth = content.clientWidth - padLeft - padRight;
        this.pageWidth = this.columnWidth; // for other references

        // Apply CSS column layout using actual content width
        content.style.height = pageHeight + 'px';
        content.style.columnWidth = this.columnWidth + 'px';
        content.style.columnGap = this.columnGap + 'px';

        // Force layout
        void content.offsetHeight;

        // Step = column width + gap (NOT frame width + gap)
        this.pageStep = this.columnWidth + this.columnGap;
        this.totalPages = Math.max(1, Math.ceil(content.scrollWidth / this.pageStep));

        // Clamp current page
        this.currentPage = Math.min(this.currentPage, this.totalPages);

        this.updateUI();
        console.log(`[Reader] Paginação: ${this.totalPages} páginas (col=${this.columnWidth}, step=${this.pageStep})`);
    }

    goToPage(page) {
        page = Math.max(1, Math.min(page, this.totalPages));
        this.currentPage = page;

        // Use pageStep (columnWidth + gap) for correct column alignment
        const offset = (page - 1) * this.pageStep;
        this.el.content.style.transform = `translateX(-${offset}px)`;

        this.updateUI();
        this.debouncedSave();
    }

    nextPage() {
        if (this.currentPage < this.totalPages) {
            this.goToPage(this.currentPage + 1);
        }
    }

    prevPage() {
        if (this.currentPage > 1) {
            this.goToPage(this.currentPage - 1);
        }
    }

    // ╔══════════════════════════════════════════╗
    // ║            UI UPDATES                    ║
    // ╚══════════════════════════════════════════╝

    updateUI() {
        const pct = this.totalPages > 1
            ? Math.round(((this.currentPage - 1) / (this.totalPages - 1)) * 100)
            : 0;

        this.el.pageInfo.textContent = `${this.currentPage} / ${this.totalPages}`;
        this.el.progressPct.textContent = `${pct}%`;
        this.el.progressFill.style.width = `${pct}%`;

        // Update chapter title based on visible content
        this.updateChapterTitle();
    }

    updateChapterTitle() {
        // Find which chapter is currently visible
        const chapters = this.el.content.querySelectorAll('.chapter-block');
        const scrollOffset = (this.currentPage - 1) * this.pageStep;

        let activeChapter = null;
        for (const ch of chapters) {
            if (ch.offsetLeft <= scrollOffset + this.pageWidth / 2) {
                activeChapter = ch;
            }
        }

        if (activeChapter) {
            const spineIdx = parseInt(activeChapter.dataset.spine);
            const tocEntry = this.toc.find(t => t.spineIndex === spineIdx);
            if (tocEntry) {
                this.el.chapterTitle.textContent = tocEntry.label;
                // Highlight in TOC
                document.querySelectorAll('.toc-item').forEach(el => {
                    el.classList.toggle('active', parseInt(el.dataset.spine) === spineIdx);
                });
            }
        }
    }

    // ╔══════════════════════════════════════════╗
    // ║           EVENT BINDING                  ║
    // ╚══════════════════════════════════════════╝

    bindEvents() {
        // Navigation buttons
        document.getElementById('btn-prev')?.addEventListener('click', () => this.prevPage());
        document.getElementById('btn-next')?.addEventListener('click', () => this.nextPage());

        // Keyboard
        document.addEventListener('keydown', (e) => {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
            switch (e.key) {
                case 'ArrowLeft': e.preventDefault(); this.prevPage(); break;
                case 'ArrowRight': e.preventDefault(); this.nextPage(); break;
                case 'Escape': this.closePanel(); break;
            }
        });

        // Touch / swipe
        let touchStartX = 0;
        const vp = this.el.viewport;
        vp.addEventListener('touchstart', (e) => { touchStartX = e.touches[0].clientX; }, { passive: true });
        vp.addEventListener('touchend', (e) => {
            const dx = e.changedTouches[0].clientX - touchStartX;
            if (Math.abs(dx) > 50) {
                dx > 0 ? this.prevPage() : this.nextPage();
            }
        }, { passive: true });

        // Click on viewport sides
        vp.addEventListener('click', (e) => {
            const rect = vp.getBoundingClientRect();
            const x = e.clientX - rect.left;
            if (e.target.closest('.nav-arrow, .reader-content a, button')) return;
            if (x < rect.width * 0.3) this.prevPage();
            else if (x > rect.width * 0.7) this.nextPage();
        });

        // Panel toggle
        document.getElementById('btn-panel')?.addEventListener('click', () => this.togglePanel());
        document.getElementById('btn-close-panel')?.addEventListener('click', () => this.closePanel());
        this.el.panelOverlay?.addEventListener('click', () => this.closePanel());

        // Panel tabs
        document.querySelectorAll('.panel-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                document.querySelectorAll('.panel-tab').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.panel-section').forEach(s => s.classList.remove('active'));
                tab.classList.add('active');
                document.getElementById(`section-${tab.dataset.tab}`)?.classList.add('active');
            });
        });

        // Theme buttons (only settings panel buttons, not the reader-page itself)
        document.querySelectorAll('.setting-btn[data-theme]').forEach(btn => {
            btn.addEventListener('click', () => this.setTheme(btn.dataset.theme));
        });

        // Font buttons
        document.querySelectorAll('.setting-btn[data-font]').forEach(btn => {
            btn.addEventListener('click', () => this.setFont(btn.dataset.font));
        });

        // Font size
        document.getElementById('btn-font-up')?.addEventListener('click', () => this.changeFontSize(2));
        document.getElementById('btn-font-down')?.addEventListener('click', () => this.changeFontSize(-2));

        // Bookmark
        this.el.btnBookmark?.addEventListener('click', () => this.toggleBookmark());

        // Progress bar click
        document.getElementById('progress-bar')?.addEventListener('click', (e) => {
            const rect = e.currentTarget.getBoundingClientRect();
            const pct = (e.clientX - rect.left) / rect.width;
            const targetPage = Math.max(1, Math.round(pct * this.totalPages));
            this.goToPage(targetPage);
        });

        // Window resize → recalculate
        let resizeTimer;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(() => this.recalculatePages(), 200);
        });
    }

    // ╔══════════════════════════════════════════╗
    // ║              TOC                         ║
    // ╚══════════════════════════════════════════╝

    buildTOC() {
        if (!this.toc.length) {
            this.el.tocList.innerHTML = '<li class="empty-state"><i class="fas fa-list"></i>Índice não disponível</li>';
            return;
        }

        this.el.tocList.innerHTML = '';
        for (const entry of this.toc) {
            const li = document.createElement('li');
            const btn = document.createElement('button');
            btn.className = 'toc-item' + (entry.sub ? ' sub' : '');
            btn.textContent = entry.label;
            btn.dataset.spine = entry.spineIndex;
            btn.addEventListener('click', () => this.goToSpineItem(entry.spineIndex));
            li.appendChild(btn);
            this.el.tocList.appendChild(li);
        }
    }

    goToSpineItem(index) {
        const chapter = this.el.content.querySelector(`[data-spine="${index}"]`);
        if (chapter) {
            // Calculate which page this chapter starts on
            const step = this.pageStep;
            const page = Math.max(1, Math.floor(chapter.offsetLeft / step) + 1);
            this.goToPage(page);
        }
        this.closePanel();
    }

    // ╔══════════════════════════════════════════╗
    // ║           SETTINGS / THEME               ║
    // ╚══════════════════════════════════════════╝

    setTheme(theme) {
        this.settings.theme = theme;
        this.el.page.dataset.theme = theme;
        // Update active btn (only settings panel buttons)
        document.querySelectorAll('.setting-btn[data-theme]').forEach(b => {
            b.classList.toggle('active', b.dataset.theme === theme);
        });
        this.saveSettingsToServer();
    }

    setFont(family) {
        this.settings.fontFamily = family;
        const fonts = {
            serif: "'Georgia', 'Times New Roman', serif",
            sans: "'Inter', -apple-system, sans-serif",
            mono: "'Courier New', 'Consolas', monospace",
        };
        document.documentElement.style.setProperty('--reader-book-font', fonts[family] || fonts.serif);
        // Update active btn
        document.querySelectorAll('[data-font]').forEach(b => {
            b.classList.toggle('active', b.dataset.font === family);
        });
        this.recalculatePages();
        this.saveSettingsToServer();
    }

    changeFontSize(delta) {
        this.settings.fontSize = Math.max(12, Math.min(32, this.settings.fontSize + delta));
        document.documentElement.style.setProperty('--reader-book-size', this.settings.fontSize + 'px');
        this.el.fontSizeValue.textContent = this.settings.fontSize + 'px';
        // Preserve approximate position
        const pct = (this.currentPage - 1) / Math.max(1, this.totalPages - 1);
        this.recalculatePages();
        const newPage = Math.max(1, Math.round(pct * (this.totalPages - 1)) + 1);
        this.goToPage(newPage);
        this.saveSettingsToServer();
    }

    loadSettings() {
        // Load from page dataset
        const theme = this.el.page?.dataset.theme || 'dark';
        this.settings.theme = theme;

        // Apply initial state
        document.querySelectorAll('.setting-btn[data-theme]').forEach(b => {
            b.classList.toggle('active', b.dataset.theme === theme);
        });
        document.querySelectorAll('.setting-btn[data-font]').forEach(b => {
            b.classList.toggle('active', b.dataset.font === this.settings.fontFamily);
        });
        this.el.fontSizeValue.textContent = this.settings.fontSize + 'px';
    }

    async saveSettingsToServer() {
        try {
            await fetch(this.bookData.apiUrls.settings, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.bookData.csrfToken,
                },
                body: JSON.stringify({
                    theme: this.settings.theme,
                    font_family: this.settings.fontFamily,
                    font_size: this.settings.fontSize,
                }),
            });
        } catch { /* silent */ }
    }

    // ╔══════════════════════════════════════════╗
    // ║         PROGRESS SAVE / RESTORE          ║
    // ╚══════════════════════════════════════════╝

    restoreProgress() {
        const saved = this.bookData.savedProgress;
        if (!saved) return;

        // Try to restore from Page Number (stored in CFI as "page:current:total")
        if (saved.cfi && saved.cfi.startsWith('page:')) {
            const parts = saved.cfi.split(':');
            if (parts.length >= 2) {
                const page = parseInt(parts[1], 10);
                if (!isNaN(page) && page > 0) {
                    console.log(`[Reader] Progresso restaurado via CFI: página ${page}`);
                    this.goToPage(page);
                    return;
                }
            }
        }

        // Fallback to percentage
        if (saved.percentage > 0) {
            const pct = saved.percentage / 100;
            const targetPage = Math.max(1, Math.round(pct * this.totalPages));
            this.goToPage(targetPage);
            console.log(`[Reader] Progresso restaurado via %: página ${targetPage} (${saved.percentage}%)`);
        }
    }

    async saveProgress() {
        if (this.totalPages <= 1) return;

        const percentage = ((this.currentPage - 1) / (this.totalPages - 1)) * 100;
        const sessionDuration = Math.floor((Date.now() - this.sessionStartTime) / 60000);

        // Save current_cfi as "page:N:Total" for exact page restoration
        const cfi = `page:${this.currentPage}:${this.totalPages}`;

        try {
            await fetch(this.bookData.apiUrls.saveProgress, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.bookData.csrfToken,
                },
                body: JSON.stringify({
                    current_cfi: cfi,
                    percentage: Math.min(100, Math.max(0, percentage)),
                    session_duration: sessionDuration,
                }),
                keepalive: true // Ensure request completes when closing tab
            });
        } catch (err) {
            console.error('[Reader] Erro ao salvar progresso:', err);
        }
    }

    _saveTimeout = null;
    debouncedSave() {
        clearTimeout(this._saveTimeout);
        this._saveTimeout = setTimeout(() => this.saveProgress(), 2000);
    }

    startAutoSave() {
        // Save every 30 seconds
        this.autoSaveTimer = setInterval(() => this.saveProgress(), 30000);

        // Save on exit
        window.addEventListener('beforeunload', () => {
            this.saveProgress();
        });

        // Save on visibility change (mobile/tab switch)
        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'hidden') {
                this.saveProgress();
            }
        });
    }

    // ╔══════════════════════════════════════════╗
    // ║            BOOKMARKS                     ║
    // ╚══════════════════════════════════════════╝

    async loadBookmarks() {
        try {
            const res = await fetch(this.bookData.apiUrls.bookmarks);
            if (!res.ok) return;
            const data = await res.json();
            this.renderBookmarks(data.bookmarks || []);
        } catch { /* silent */ }
    }

    renderBookmarks(bookmarks) {
        if (!bookmarks.length) {
            this.el.bookmarksContainer.innerHTML = `
                <div class="empty-state">
                    <i class="far fa-bookmark"></i>
                    Nenhum marcador ainda
                </div>`;
            return;
        }

        this.el.bookmarksContainer.innerHTML = '';
        for (const bk of bookmarks) {
            const div = document.createElement('div');
            div.className = 'bookmark-item';
            div.innerHTML = `
                <span class="bk-icon"><i class="fas fa-bookmark"></i></span>
                <div class="bk-text">
                    <div class="bk-title">${bk.title || 'Marcador'}</div>
                    <div class="bk-chapter">${bk.chapter_title || ''}</div>
                </div>
                <button class="bk-delete" data-id="${bk.id}" title="Remover">
                    <i class="fas fa-trash-alt"></i>
                </button>`;

            // Click to go to bookmark
            div.addEventListener('click', (e) => {
                if (e.target.closest('.bk-delete')) return;
                // Parse page from CFI
                const match = (bk.cfi || '').match(/page:(\d+)/);
                if (match) this.goToPage(parseInt(match[1]));
                this.closePanel();
            });

            // Delete
            div.querySelector('.bk-delete').addEventListener('click', async (e) => {
                e.stopPropagation();
                await this.deleteBookmark(bk.id);
            });

            this.el.bookmarksContainer.appendChild(div);
        }
    }

    async toggleBookmark() {
        const cfi = `page:${this.currentPage}:${this.totalPages}`;
        const chapterTitle = this.el.chapterTitle.textContent;

        try {
            const res = await fetch(this.bookData.apiUrls.createBookmark, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.bookData.csrfToken,
                },
                body: JSON.stringify({
                    ebook: this.bookData.id,
                    cfi: cfi,
                    title: `Página ${this.currentPage}`,
                    chapter_title: chapterTitle,
                }),
            });

            if (res.ok) {
                // Toggle icon
                const icon = this.el.btnBookmark.querySelector('i');
                icon.className = 'fas fa-bookmark';
                setTimeout(() => { icon.className = 'far fa-bookmark'; }, 2000);
                this.loadBookmarks();
            }
        } catch (err) {
            console.error('[Reader] Erro ao criar marcador:', err);
        }
    }

    async deleteBookmark(id) {
        try {
            await fetch(this.bookData.apiUrls.deleteBookmarkBase + id + '/delete/', {
                method: 'DELETE',
                headers: { 'X-CSRFToken': this.bookData.csrfToken },
            });
            this.loadBookmarks();
        } catch { /* silent */ }
    }

    // ╔══════════════════════════════════════════╗
    // ║            PANEL                         ║
    // ╚══════════════════════════════════════════╝

    togglePanel() {
        const open = this.el.panel.classList.toggle('open');
        this.el.panelOverlay.classList.toggle('open', open);
    }

    closePanel() {
        this.el.panel.classList.remove('open');
        this.el.panelOverlay.classList.remove('open');
    }

    // ╔══════════════════════════════════════════╗
    // ║           LOADING / ERRORS               ║
    // ╚══════════════════════════════════════════╝

    setLoaderText(text) {
        if (this.el.loaderText) this.el.loaderText.textContent = text;
    }

    setLoaderProgress(text) {
        if (this.el.loaderProgress) this.el.loaderProgress.textContent = text;
    }

    hideLoading() {
        if (this.el.loading) {
            this.el.loading.classList.add('hidden');
        }
    }

    showError(msg) {
        if (this.el.loaderText) this.el.loaderText.textContent = msg;
        if (this.el.loaderProgress) this.el.loaderProgress.textContent = '';
        const spinner = this.el.loading?.querySelector('.loader-spinner');
        if (spinner) spinner.style.display = 'none';
    }

    // ╔══════════════════════════════════════════╗
    // ║            CLEANUP                       ║
    // ╚══════════════════════════════════════════╝

    destroy() {
        // Revoke blob URLs
        for (const url of this.blobUrls.values()) {
            URL.revokeObjectURL(url);
        }
        this.blobUrls.clear();

        if (this.autoSaveTimer) clearInterval(this.autoSaveTimer);

        this.saveProgress();
    }
}

// ── Bootstrap ──
document.addEventListener('DOMContentLoaded', () => {
    window.reader = new EBookReader();

    // Save on page leave
    window.addEventListener('beforeunload', () => {
        window.reader?.destroy();
    });
});
