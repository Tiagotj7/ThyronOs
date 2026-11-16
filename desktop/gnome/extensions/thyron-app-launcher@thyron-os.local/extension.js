import Clutter from 'gi://Clutter';
import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import Pango from 'gi://Pango';
import Shell from 'gi://Shell';
import St from 'gi://St';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import * as PanelMenu from 'resource:///org/gnome/shell/ui/panelMenu.js';

const TILE_W = 104;
const TILE_H = 96;
const GAP = 8;
const SIDEBAR_W = 198;
const DETAIL_W = 224;

const CATEGORY_MAP = [
    ['Security', 'Segurança'],
    ['Network', 'Internet'],
    ['Development', 'Desenvolvimento'],
    ['Graphics', 'Gráficos'],
    ['AudioVideo', 'Multimídia'],
    ['Audio', 'Multimídia'],
    ['Video', 'Multimídia'],
    ['Office', 'Escritório'],
    ['Game', 'Jogos'],
    ['Settings', 'Configurações'],
    ['System', 'Sistema'],
    ['Utility', 'Utilitários'],
];

// Categorias especiais (não vêm do .desktop)
const ESSENTIAL_KEY = '__essenciais__';
const FAV_KEY = 'Favoritos';
const RECENT_KEY = 'Recém usados';

// Ordem da barra lateral (como no design); "Outros" sempre por último.
const SIDEBAR_ORDER = ['Multimídia', 'Internet', 'Escritório', 'Jogos', 'Configurações',
    'Sistema', 'Segurança', 'Desenvolvimento', 'Gráficos', 'Utilitários', 'Outros'];

// Ícones simbólicos (o primeiro que existir no tema é usado)
const CAT_ICONS = {
    'Todos': ['view-grid-symbolic', 'view-app-grid-symbolic'],
    'Favoritos': ['starred-symbolic', 'emblem-favorite-symbolic'],
    'Recém usados': ['document-open-recent-symbolic', 'appointment-soon-symbolic'],
    'Multimídia': ['applications-multimedia-symbolic', 'multimedia-player-symbolic', 'video-x-generic-symbolic'],
    'Internet': ['network-workgroup-symbolic', 'web-browser-symbolic'],
    'Escritório': ['applications-office-symbolic', 'x-office-document-symbolic'],
    'Jogos': ['applications-games-symbolic', 'input-gaming-symbolic'],
    'Configurações': ['preferences-system-symbolic', 'emblem-system-symbolic'],
    'Sistema': ['computer-symbolic', 'applications-system-symbolic'],
    'Segurança': ['security-high-symbolic', 'channel-secure-symbolic', 'dialog-password-symbolic'],
    'Desenvolvimento': ['utilities-terminal-symbolic', 'applications-engineering-symbolic'],
    'Gráficos': ['applications-graphics-symbolic', 'image-x-generic-symbolic'],
    'Utilitários': ['applications-utilities-symbolic', 'preferences-other-symbolic'],
    'Outros': ['view-more-symbolic', 'view-more-horizontal-symbolic'],
};

// Cartões da seção "Categorias Populares" (só aparecem se a categoria existir)
const POPULAR = [
    ['Internet', 'Acesse a web'],
    ['Multimídia', 'Ouça e assista'],
    ['Escritório', 'Trabalhe melhor'],
    ['Jogos', 'Divirta-se'],
    ['Configurações', 'Personalize'],
];

// Aplicativos Essenciais: um por função, só os que estão instalados.
// Cada função lista identificadores .desktop (sem a extensão) em ordem de
// preferência; vale o primeiro encontrado.
const ESSENTIALS = [
    ['Navegador', ['firefox-esr', 'firefox', 'org.mozilla.firefox']],
    ['Arquivos', ['org.gnome.nautilus']],
    ['Terminal', ['org.gnome.terminal', 'org.gnome.console']],
    ['Editor de texto', ['org.gnome.texteditor', 'gedit']],
    ['Documentos', ['libreoffice-writer']],
    ['Planilhas', ['libreoffice-calc']],
    ['Apresentações', ['libreoffice-impress']],
    ['Imagens', ['org.gnome.loupe', 'eog']],
    ['Vídeos', ['vlc', 'org.gnome.totem']],
    ['Compactador', ['org.gnome.fileroller']],
    ['Calculadora', ['org.gnome.calculator']],
    ['Configurações', ['org.gnome.settings', 'gnome-control-center']],
    ['Rede', ['nm-connection-editor']],
    ['Monitor do sistema', ['gnome-system-monitor', 'org.gnome.systemmonitor']],
    ['Loja de apps', ['org.thyron.store']],
];
// Os 6 mostrados no painel da tela inicial (completa com os demais se faltar)
const HOME_PREFERRED = ['Navegador', 'Editor de texto', 'Vídeos', 'Documentos', 'Planilhas', 'Terminal'];

function themedIcon(names) {
    return new Gio.ThemedIcon({names});
}

function categoryOf(app) {
    const raw = app.get_categories?.() ?? '';
    const set = new Set(raw.split(';').filter(Boolean));
    for (const [key, label] of CATEGORY_MAP) {
        if (set.has(key))
            return label;
    }
    return 'Outros';
}

function iconOf(app) {
    return app.get_icon() ?? new Gio.ThemedIcon({name: 'application-x-executable'});
}

function ellipsized(text, styleClass, props = {}) {
    const l = new St.Label({text, style_class: styleClass, ...props});
    l.clutter_text.ellipsize = Pango.EllipsizeMode.END;
    return l;
}

function infoRow(key, value) {
    const row = new St.BoxLayout({style_class: 'thyron-d-row', x_expand: true});
    row.add_child(new St.Label({
        text: key,
        style_class: 'thyron-d-key',
        y_align: Clutter.ActorAlign.CENTER,
    }));
    row.add_child(ellipsized(value, 'thyron-d-val', {
        x_expand: true,
        x_align: Clutter.ActorAlign.END,
        y_align: Clutter.ActorAlign.CENTER,
    }));
    return row;
}

function wrapLabel(text, styleClass) {
    const l = new St.Label({text, style_class: styleClass});
    l.clutter_text.line_wrap = true;
    l.clutter_text.line_wrap_mode = Pango.WrapMode.WORD_CHAR;
    l.clutter_text.ellipsize = Pango.EllipsizeMode.NONE;
    return l;
}

export default class ThyronAppLauncher extends Extension {
    enable() {
        this._button = new PanelMenu.Button(0.0, 'THYRON', true);
        this._button.add_child(new St.Label({
            text: 'THYRON',
            y_align: Clutter.ActorAlign.CENTER,
            style_class: 'thyron-launcher-label',
        }));
        this._button.connect('button-press-event', () => {
            this._open();
            return Clutter.EVENT_STOP;
        });
        Main.panel.addToStatusArea(this.uuid, this._button, 1, 'left');

        // Intercepta o botão de 9 pontos (Dash to Dock e dash nativo)
        this._busy = false;
        this._hooks = [];
        this._hooked = new Set();
        this._tickId = 0;
        this._retryId = 0;
        this._idleId = 0;
        this._hookStage();
        this._hookButtons();
        log(`[THYRON] ganchos: ${this._hooked.size} botao(oes) localizado(s); captura de cliques ativa`);
        this._retryId = GLib.timeout_add(GLib.PRIORITY_DEFAULT, 1500, () => {
            this._retryId = 0;
            this._hookButtons();
            return GLib.SOURCE_REMOVE;
        });
    }

    _chain(actor) {
        const out = [];
        for (let a = actor, i = 0; a && i < 8; a = a.get_parent(), i++)
            out.push(`${a.constructor?.name}[${a.style_class ?? ''}|${a.icon_name ?? ''}|${a.accessible_name ?? ''}]`);
        return out.join(' < ');
    }

    _isAppsButton(actor) {
        for (let a = actor; a; a = a.get_parent()) {
            if (a instanceof St.Icon && (a.icon_name === 'view-app-grid-symbolic' ||
                a.gicon?.names?.includes?.('view-app-grid-symbolic')))
                return true;
            if (a instanceof St.Button) {
                const cls = a.style_class ?? '';
                if (cls.includes('show-apps') || a.accessible_name === 'Show Applications')
                    return true;
            }
        }
        return false;
    }

    _hookStage() {
        const id = global.stage.connect('captured-event', (_s, ev) => {
            const t = ev.type();
            if (t !== Clutter.EventType.BUTTON_PRESS && t !== Clutter.EventType.BUTTON_RELEASE)
                return Clutter.EVENT_PROPAGATE;
            if (this._overlay || ev.get_button() !== Clutter.BUTTON_PRIMARY)
                return Clutter.EVENT_PROPAGATE;
            if (!this._isAppsButton(ev.get_source())) {
                if (t === Clutter.EventType.BUTTON_RELEASE)
                    log(`[THYRON] clique fora do botao de apps: ${this._chain(ev.get_source())}`);
                return Clutter.EVENT_PROPAGATE;
            }
            if (t === Clutter.EventType.BUTTON_RELEASE) {
                log('[THYRON] clique no botao de aplicativos interceptado');
                this._schedule();
            }
            return Clutter.EVENT_STOP;
        });
        this._hooks.push([global.stage, id]);
    }

    _showAppsButtons() {
        const list = [];
        if (Main.overview.dash?.showAppsButton)
            list.push(Main.overview.dash.showAppsButton);
        try {
            const ext = Main.extensionManager.lookup('dash-to-dock@micxgx.gmail.com');
            const docks = ext?.stateObj?.dockManager?._allDocks ?? [];
            for (const d of docks) {
                if (d.dash?.showAppsButton)
                    list.push(d.dash.showAppsButton);
            }
        } catch (e) {
            log(`[THYRON] Dash to Dock não localizado: ${e.message}`);
        }
        return list;
    }

    _hookButtons() {
        // Captura o clique antes do próprio botão: ele nunca alterna a
        // visão geral do GNOME, e só a tela THYRON é aberta.
        for (const btn of this._showAppsButtons()) {
            if (this._hooked.has(btn))
                continue;
            this._hooked.add(btn);
            if (typeof btn?.connect !== 'function') {
                log(`[THYRON] item ignorado (nao e um botao): ${btn?.constructor?.name}`);
                continue;
            }
            log(`[THYRON] botao ligado: ${btn.constructor?.name} classe=${btn.style_class}`);

            const press = btn.connect('button-press-event', () => Clutter.EVENT_STOP);
            const release = btn.connect('button-release-event', (_a, ev) => {
                if (ev.get_button() === Clutter.BUTTON_PRIMARY)
                    this._schedule();
                return Clutter.EVENT_STOP;
            });
            const key = btn.connect('key-press-event', (_a, ev) => {
                const sym = ev.get_key_symbol();
                if (sym === Clutter.KEY_Return || sym === Clutter.KEY_KP_Enter ||
                    sym === Clutter.KEY_space) {
                    this._schedule();
                    return Clutter.EVENT_STOP;
                }
                return Clutter.EVENT_PROPAGATE;
            });
            this._hooks.push([btn, press], [btn, release], [btn, key]);
        }
    }

    _schedule() {
        if (this._busy || this._overlay || this._idleId)
            return;
        this._idleId = GLib.idle_add(GLib.PRIORITY_DEFAULT_IDLE, () => {
            this._idleId = 0;
            this._trigger();
            return GLib.SOURCE_REMOVE;
        });
    }

    _trigger() {
        if (this._busy || this._overlay)
            return;
        this._busy = true;
        this._tries = 0;
        this._tick();
    }

    _tick() {
        this._tickId = 0;
        try {
            if (!Main.overview.visible) {
                for (const btn of this._showAppsButtons()) {
                    if (btn.checked)
                        btn.checked = false;
                }
                this._busy = false;
                this._open();
                return;
            }
            if (this._tries++ > 40) {
                this._busy = false;
                return;
            }
            if (Main.overview._shownState === 'SHOWN')
                Main.overview.hide();
        } catch (e) {
            this._busy = false;
            log(`[THYRON] erro ao abrir a tela: ${e.message}`);
            return;
        }
        this._tickId = GLib.timeout_add(GLib.PRIORITY_DEFAULT, 100, () => {
            this._tick();
            return GLib.SOURCE_REMOVE;
        });
    }

    // ---- Preferências persistentes: modo, favoritos e recém usados ----
    _stateDir() {
        return GLib.build_filenamev([GLib.get_user_data_dir(), 'thyron-app-launcher']);
    }

    _loadState() {
        const state = {mode: 'iniciante', favorites: [], recents: []};
        try {
            const path = GLib.build_filenamev([this._stateDir(), 'state.json']);
            const [ok, bytes] = GLib.file_get_contents(path);
            if (ok) {
                const d = JSON.parse(new TextDecoder().decode(bytes));
                if (d.mode === 'avancado')
                    state.mode = 'avancado';
                if (Array.isArray(d.favorites))
                    state.favorites = d.favorites.filter(x => typeof x === 'string');
                if (Array.isArray(d.recents))
                    state.recents = d.recents.filter(x => typeof x === 'string').slice(0, 12);
            }
        } catch (e) {
            // primeira execução ou arquivo inválido: usa o padrão
        }
        return state;
    }

    _saveState() {
        try {
            GLib.mkdir_with_parents(this._stateDir(), 0o755);
            const file = Gio.File.new_for_path(GLib.build_filenamev([this._stateDir(), 'state.json']));
            file.replace_contents(
                new TextEncoder().encode(JSON.stringify(this._state)),
                null, false, Gio.FileCreateFlags.REPLACE_DESTINATION, null);
        } catch (e) {
            log(`[THYRON] nao foi possivel salvar preferencias: ${e.message}`);
        }
    }

    _isFav(entry) {
        return this._state.favorites.includes(entry.app.get_id());
    }

    _toggleFav(entry) {
        const id = entry.app.get_id();
        const i = this._state.favorites.indexOf(id);
        if (i >= 0)
            this._state.favorites.splice(i, 1);
        else
            this._state.favorites.push(id);
        this._saveState();
    }

    _recordRecent(id) {
        if (!id || !this._state)
            return;
        const list = this._state.recents.filter(x => x !== id);
        list.unshift(id);
        this._state.recents = list.slice(0, 12);
        this._saveState();
    }

    _recentEntries() {
        return this._state.recents
            .map(id => this._appsById.get(id))
            .filter(Boolean);
    }

    _isHome() {
        return this._state.mode === 'iniciante' && !this._cat && !this._query.trim();
    }

    _homeTiles() {
        const withRole = this._apps.filter(e => e.role);
        const out = [];
        for (const role of HOME_PREFERRED) {
            const e = withRole.find(x => x.role === role);
            if (e)
                out.push(e);
        }
        for (const [role] of ESSENTIALS) {
            if (out.length >= 6)
                break;
            const e = withRole.find(x => x.role === role);
            if (e && !out.includes(e))
                out.push(e);
        }
        return out.slice(0, 6);
    }

    _open() {
        if (this._overlay)
            return;

        const m = Main.layoutManager.primaryMonitor;
        this._state = this._loadState();
        this._apps = Gio.AppInfo.get_all()
            .filter(a => a.should_show())
            .map(a => ({app: a, name: a.get_name(), cat: categoryOf(a), role: null}));
        this._appsById = new Map(this._apps.map(e => [e.app.get_id(), e]));
        const byShortId = new Map(this._apps.map(e =>
            [(e.app.get_id() ?? '').replace(/\.desktop$/, '').toLowerCase(), e]));
        for (const [role, ids] of ESSENTIALS) {
            for (const id of ids) {
                const found = byShortId.get(id);
                if (found) {
                    found.role = role;
                    break;
                }
            }
        }
        this._cat = null;
        this._query = '';
        this._asc = true;
        this._page = 0;
        this._selected = null;
        this._moreInfo = false;
        this._tiles = new Map();
        this._navButtons = [];

        const W = Math.min(m.width - 64, 1360);
        const H = Math.min(m.height - 96, 820);
        const centerW = W - 28 - SIDEBAR_W - DETAIL_W - 28;
        this._centerW = centerW;
        this._cols = Math.max(3, Math.floor((centerW - 8) / (TILE_W + GAP)));
        this._rows = Math.max(2, Math.floor((H - 236) / (TILE_H + GAP)));

        // O overlay é um contêiner neutro (BinLayout). O fundo clicável
        // (backdrop) e o painel são IRMÃOS: nenhum pai bloqueia os cliques.
        this._overlay = new St.Widget({
            style_class: 'thyron-overlay',
            layout_manager: new Clutter.BinLayout(),
            reactive: true,
            x: m.x, y: m.y, width: m.width, height: m.height,
        });
        // Despachante de cliques: captura os cliques no overlay e acha o botão
        // pela POSIÇÃO do ponteiro (não depende de ev.get_source()).
        this._overlay.connect('captured-event', (_a, ev) => this._onOverlayEvent(ev));
        const backdrop = new St.Button({
            style: 'background-color: transparent; border: none; box-shadow: none;',
            reactive: true,
            can_focus: false,
            x_expand: true,
            y_expand: true,
        });
        this._wire(backdrop, () => {
            this._later(() => this._close());
        });
        this._overlay.add_child(backdrop);
        this._overlay.connect('key-press-event', (_a, ev) => {
            if (ev.get_key_symbol() === Clutter.KEY_Escape) {
                this._close();
                return Clutter.EVENT_STOP;
            }
            return Clutter.EVENT_PROPAGATE;
        });

        const panel = new St.BoxLayout({
            style_class: 'thyron-panel',
            reactive: true,
            x_expand: true, y_expand: true,
            x_align: Clutter.ActorAlign.CENTER,
            y_align: Clutter.ActorAlign.CENTER,
        });
        panel.set_size(W, H);
        this._panel = panel;
        this._overlay.add_child(panel);

        // ---- Coluna esquerda: categorias ----
        const side = new St.BoxLayout({style_class: 'thyron-sidebar', vertical: true});
        side.set_width(SIDEBAR_W);
        side.add_child(new St.Label({text: 'APLICATIVOS', style_class: 'thyron-side-title'}));
        const navScroll = new St.ScrollView({
            y_expand: true,
            overlay_scrollbars: true,
            hscrollbar_policy: St.PolicyType.NEVER,
        });
        this._navBox = new St.BoxLayout({vertical: true, style_class: 'thyron-navbox'});
        navScroll.set_child(this._navBox);
        side.add_child(navScroll);
        const brand = new St.BoxLayout({vertical: true, style_class: 'thyron-brand'});
        brand.add_child(new St.Label({
            text: 'THYRON OS',
            style_class: 'thyron-brand-name',
            x_align: Clutter.ActorAlign.CENTER,
        }));
        brand.add_child(new St.Label({
            text: 'LIBERDADE • DESEMPENHO • INOVAÇÃO',
            style_class: 'thyron-brand-slogan',
            x_align: Clutter.ActorAlign.CENTER,
        }));
        side.add_child(brand);
        panel.add_child(side);

        // ---- Coluna central ----
        const center = new St.BoxLayout({style_class: 'thyron-center', vertical: true, y_expand: true});
        center.set_width(centerW);
        const top = new St.BoxLayout({style_class: 'thyron-top'});
        const titles = new St.BoxLayout({vertical: true, x_expand: true});
        titles.add_child(new St.Label({text: 'Aplicativos', style_class: 'thyron-h1'}));
        this._subtitle = new St.Label({text: '', style_class: 'thyron-sub'});
        titles.add_child(this._subtitle);
        top.add_child(titles);

        // Alternância Iniciante / Avançado
        const toggle = new St.BoxLayout({style_class: 'thyron-mode', y_align: Clutter.ActorAlign.CENTER});
        this._modeBtns = {};
        for (const [key, label, icons] of [
            ['iniciante', 'Iniciante', ['avatar-default-symbolic', 'system-users-symbolic']],
            ['avancado', 'Avançado', ['preferences-system-symbolic', 'emblem-system-symbolic']],
        ]) {
            const row = new St.BoxLayout();
            row.add_child(new St.Icon({
                gicon: themedIcon(icons), icon_size: 16,
                style_class: 'thyron-mode-icon', y_align: Clutter.ActorAlign.CENTER,
            }));
            row.add_child(new St.Label({
                text: label, style_class: 'thyron-mode-label', y_align: Clutter.ActorAlign.CENTER,
            }));
            const b = new St.Button({child: row, style_class: 'thyron-mode-btn', can_focus: true, track_hover: true});
            this._wire(b, () => this._setMode(key));
            toggle.add_child(b);
            this._modeBtns[key] = b;
        }
        top.add_child(toggle);

        const closeBtn = new St.Button({
            label: '✕', style_class: 'thyron-close', can_focus: true, track_hover: true,
            y_align: Clutter.ActorAlign.CENTER,
        });
        this._wire(closeBtn, () => {
            this._later(() => this._close());
        });
        top.add_child(closeBtn);
        center.add_child(top);

        const toolbar = new St.BoxLayout({style_class: 'thyron-toolbar'});
        this._entry = new St.Entry({
            hint_text: 'Pesquisar aplicativos...',
            style_class: 'thyron-search',
            x_expand: true,
            can_focus: true,
        });
        this._entry.set_primary_icon(new St.Icon({
            icon_name: 'edit-find-symbolic',
            style_class: 'thyron-search-icon',
        }));
        this._entry.clutter_text.connect('text-changed', () => {
            this._query = this._entry.get_text();
            this._page = 0;
            this._selected = null;
            this._refresh();
        });
        this._entry.clutter_text.connect('activate', () => {
            if (this._selected)
                this._launch(this._selected.app);
        });
        toolbar.add_child(this._entry);
        toolbar.add_child(new St.Label({
            text: 'Ordenar por:',
            style_class: 'thyron-sort-label',
            y_align: Clutter.ActorAlign.CENTER,
        }));
        this._sortBtn = new St.Button({
            label: 'Nome A–Z  ▾', style_class: 'thyron-sort', can_focus: true, track_hover: true,
            y_align: Clutter.ActorAlign.CENTER,
        });
        this._wire(this._sortBtn, () => {
            this._asc = !this._asc;
            this._sortBtn.label = this._asc ? 'Nome A–Z  ▾' : 'Nome Z–A  ▾';
            this._page = 0;
            this._refresh();
        });
        toolbar.add_child(this._sortBtn);
        center.add_child(toolbar);

        this._gridBox = new St.BoxLayout({vertical: true, y_expand: true, style_class: 'thyron-grid'});
        center.add_child(this._gridBox);
        this._pager = new St.BoxLayout({style_class: 'thyron-pager', x_align: Clutter.ActorAlign.CENTER});
        center.add_child(this._pager);
        panel.add_child(center);

        // ---- Coluna direita: detalhes ----
        const detailScroll = new St.ScrollView({
            style_class: 'thyron-detail-scroll',
            overlay_scrollbars: true,
            hscrollbar_policy: St.PolicyType.NEVER,
        });
        detailScroll.set_width(DETAIL_W);
        this._detail = new St.BoxLayout({vertical: true, style_class: 'thyron-detail'});
        detailScroll.set_child(this._detail);
        panel.add_child(detailScroll);

        Main.layoutManager.uiGroup.add_child(this._overlay);
        this._grab = Main.pushModal(this._overlay, {actionMode: Shell.ActionMode.POPUP});
        if (!this._grab) {
            this._close();
            return;
        }

        this._renderSidebar();
        this._updateMode();
        this._refresh();
        this._entry.grab_key_focus();
    }

    _setMode(mode) {
        this._state.mode = mode;
        this._saveState();
        this._page = 0;
        this._selected = null;
        this._updateMode();
        this._refresh();
    }

    _updateMode() {
        for (const [key, btn] of Object.entries(this._modeBtns ?? {})) {
            if (key === this._state.mode)
                btn.add_style_class_name('thyron-mode-active');
            else
                btn.remove_style_class_name('thyron-mode-active');
        }
    }

    _filtered() {
        const q = this._query.trim().toLowerCase();
        let base;
        if (this._cat === FAV_KEY)
            base = this._apps.filter(e => this._isFav(e));
        else if (this._cat === RECENT_KEY)
            base = this._recentEntries();
        else if (this._cat === ESSENTIAL_KEY)
            base = this._apps.filter(e => e.role);
        else if (this._cat)
            base = this._apps.filter(e => e.cat === this._cat);
        else
            base = this._apps.slice();
        const list = base.filter(e =>
            !q || e.name.toLowerCase().includes(q) || (e.app.get_id() ?? '').toLowerCase().includes(q));
        // "Recém usados" mantém a ordem de uso; as demais seguem a ordenação.
        if (this._cat !== RECENT_KEY)
            list.sort((a, b) => a.name.localeCompare(b.name) * (this._asc ? 1 : -1));
        return list;
    }

    _renderSidebar() {
        this._navBox.destroy_all_children();
        this._navButtons = [];
        const counts = new Map();
        for (const e of this._apps)
            counts.set(e.cat, (counts.get(e.cat) ?? 0) + 1);
        const rank = c => {
            const i = SIDEBAR_ORDER.indexOf(c);
            return i < 0 ? SIDEBAR_ORDER.length : i;
        };
        const items = [
            [null, 'Todos', this._apps.length],
            [FAV_KEY, 'Favoritos', 0],
            [RECENT_KEY, 'Recém usados', 0],
            ...[...counts.entries()]
                .sort((a, b) => rank(a[0]) - rank(b[0]))
                .map(([c, n]) => [c, c, n]),
        ];

        for (const [cat, label, n] of items) {
            const row = new St.BoxLayout({x_expand: true});
            row.add_child(new St.Icon({
                gicon: themedIcon(CAT_ICONS[label] ?? CAT_ICONS['Outros']),
                icon_size: 18,
                style_class: 'thyron-nav-icon',
                y_align: Clutter.ActorAlign.CENTER,
            }));
            row.add_child(new St.Label({
                text: label,
                style_class: 'thyron-nav-label',
                x_expand: true,
                y_align: Clutter.ActorAlign.CENTER,
            }));
            const countLabel = new St.Label({
                text: String(n),
                style_class: 'thyron-count',
                y_align: Clutter.ActorAlign.CENTER,
            });
            row.add_child(countLabel);
            const btn = new St.Button({
                child: row,
                style_class: 'thyron-nav',
                x_expand: true,
                can_focus: true,
                track_hover: true,
            });
            this._wire(btn, () => {
                log(`[THYRON] categoria: ${label}`);
                this._cat = cat;
                this._page = 0;
                this._selected = null;
                this._updateNav();
                this._refresh();
            });
            this._navBox.add_child(btn);
            this._navButtons.push({cat, btn, countLabel});
        }
        this._updateNav();
        this._updateCounts();
    }

    _updateCounts() {
        for (const {cat, countLabel} of this._navButtons ?? []) {
            if (cat === FAV_KEY)
                countLabel.text = String(this._apps.filter(e => this._isFav(e)).length);
            else if (cat === RECENT_KEY)
                countLabel.text = String(this._recentEntries().length);
        }
    }

    _updateNav() {
        for (const {cat, btn} of this._navButtons ?? []) {
            if (cat === this._cat)
                btn.add_style_class_name('thyron-nav-active');
            else
                btn.remove_style_class_name('thyron-nav-active');
        }
    }

    _refresh() {
        if (!this._overlay)
            return;
        const home = this._isHome();
        const list = home ? this._homeTiles() : this._filtered();
        const perPage = this._cols * this._rows;
        const pages = home ? 1 : Math.max(1, Math.ceil(list.length / perPage));
        this._page = Math.min(this._page, pages - 1);
        if (!this._selected || !list.includes(this._selected))
            this._selected = list[0] ?? null;

        if (home)
            this._subtitle.text = 'Explore e abra seus aplicativos favoritos';
        else if (this._cat === ESSENTIAL_KEY)
            this._subtitle.text = `${list.length} aplicativo(s) essenciais para começar`;
        else if (this._cat === FAV_KEY)
            this._subtitle.text = `${list.length} aplicativo(s) favoritos`;
        else if (this._cat === RECENT_KEY)
            this._subtitle.text = `${list.length} aplicativo(s) abertos recentemente por aqui`;
        else
            this._subtitle.text = `${list.length} aplicativo(s)` +
                (this._cat ? ` em ${this._cat}` : ' com lançador gráfico');

        if (home)
            this._renderHome(list);
        else
            this._renderGrid(list, perPage);
        this._renderPager(pages);
        this._renderDetails();
        this._updateCounts();
    }

    _renderHome(list) {
        this._gridBox.destroy_all_children();
        this._tiles = new Map();
        const cw = this._centerW;

        // ---- Aplicativos Essenciais ----
        const ess = new St.BoxLayout({style_class: 'thyron-ess', vertical: true, x_expand: true});
        const head = new St.BoxLayout({style_class: 'thyron-ess-head'});
        head.add_child(new St.Icon({
            gicon: themedIcon(['starred-symbolic']), icon_size: 22,
            style_class: 'thyron-ess-icon', y_align: Clutter.ActorAlign.CENTER,
        }));
        const headTitles = new St.BoxLayout({vertical: true, x_expand: true, y_align: Clutter.ActorAlign.CENTER});
        headTitles.add_child(new St.Label({text: 'Aplicativos Essenciais', style_class: 'thyron-ess-title'}));
        headTitles.add_child(new St.Label({text: 'Os mais úteis para começar', style_class: 'thyron-ess-sub'}));
        head.add_child(headTitles);
        const seeAll = new St.Button({
            label: 'Ver todos  →', style_class: 'thyron-seeall', can_focus: true, track_hover: true,
            y_align: Clutter.ActorAlign.CENTER,
        });
        this._wire(seeAll, () => {
            this._cat = ESSENTIAL_KEY;
            this._page = 0;
            this._selected = null;
            this._updateNav();
            this._refresh();
        });
        head.add_child(seeAll);
        ess.add_child(head);

        if (list.length === 0) {
            ess.add_child(new St.Label({
                text: 'Nenhum aplicativo essencial encontrado neste sistema.',
                style_class: 'thyron-empty',
            }));
        } else {
            const tileGap = 12;
            const tileW = Math.floor((cw - 30 - list.length * tileGap) / 6);
            const row = new St.BoxLayout({style_class: 'thyron-ess-row'});
            for (const e of list) {
                const b = new St.Button({style_class: 'thyron-ess-tile', can_focus: true, track_hover: true});
                b.set_size(tileW, 112);
                const box = new St.BoxLayout({vertical: true, x_expand: true});
                box.add_child(new St.Icon({
                    gicon: iconOf(e.app), icon_size: 46, x_align: Clutter.ActorAlign.CENTER,
                }));
                box.add_child(ellipsized(e.role ?? e.name, 'thyron-ess-role', {x_align: Clutter.ActorAlign.CENTER}));
                box.add_child(ellipsized(`(${e.name})`, 'thyron-ess-app', {x_align: Clutter.ActorAlign.CENTER}));
                b.set_child(box);
                if (e === this._selected)
                    b.add_style_class_name('thyron-tile-selected');
                this._wire(b, () => {
                    log(`[THYRON] essencial: ${e.name}`);
                    this._select(e);
                });
                row.add_child(b);
                this._tiles.set(e, b);
            }
            ess.add_child(row);
        }
        this._gridBox.add_child(ess);

        // ---- Categorias Populares ----
        const cards = POPULAR
            .map(([cat, sub], i) => ({cat, sub, i}))
            .filter(c => this._apps.some(e => e.cat === c.cat));
        if (cards.length === 0)
            return;
        const ph = new St.BoxLayout({style_class: 'thyron-pop-head'});
        ph.add_child(new St.Icon({
            gicon: themedIcon(['starred-symbolic']), icon_size: 20,
            style_class: 'thyron-pop-star', y_align: Clutter.ActorAlign.CENTER,
        }));
        ph.add_child(new St.Label({
            text: 'Categorias Populares', style_class: 'thyron-pop-title', y_align: Clutter.ActorAlign.CENTER,
        }));
        this._gridBox.add_child(ph);

        const cardGap = 12;
        const cardW = Math.floor((cw - cards.length * cardGap) / cards.length);
        const popRow = new St.BoxLayout({style_class: 'thyron-pop-row'});
        for (const {cat, sub, i} of cards) {
            const b = new St.Button({
                style_class: `thyron-pop thyron-pop-${i}`, can_focus: true, track_hover: true,
            });
            b.set_size(cardW, 84);
            const box = new St.BoxLayout({vertical: true, x_expand: true});
            box.add_child(new St.Icon({
                gicon: themedIcon(CAT_ICONS[cat] ?? CAT_ICONS['Outros']), icon_size: 26,
                style_class: 'thyron-pop-icon', x_align: Clutter.ActorAlign.CENTER,
            }));
            box.add_child(ellipsized(cat, 'thyron-pop-name', {x_align: Clutter.ActorAlign.CENTER}));
            box.add_child(ellipsized(sub, 'thyron-pop-sub', {x_align: Clutter.ActorAlign.CENTER}));
            b.set_child(box);
            this._wire(b, () => {
                log(`[THYRON] categoria popular: ${cat}`);
                this._cat = cat;
                this._page = 0;
                this._selected = null;
                this._updateNav();
                this._refresh();
            });
            popRow.add_child(b);
        }
        this._gridBox.add_child(popRow);
    }

    _renderGrid(list, perPage) {
        this._gridBox.destroy_all_children();
        this._tiles = new Map();

        if (list.length === 0) {
            this._gridBox.add_child(new St.Label({
                text: this._cat === FAV_KEY
                    ? 'Nenhum favorito ainda. Selecione um aplicativo e use "Adicionar aos favoritos".'
                    : this._cat === RECENT_KEY
                        ? 'Nenhum aplicativo aberto por aqui ainda.'
                        : 'Nenhum aplicativo encontrado',
                style_class: 'thyron-empty',
            }));
            return;
        }

        const slice = list.slice(this._page * perPage, (this._page + 1) * perPage);
        let row = null;
        slice.forEach((e, i) => {
            if (i % this._cols === 0) {
                row = new St.BoxLayout({style_class: 'thyron-row'});
                this._gridBox.add_child(row);
            }
            const btn = new St.Button({
                style_class: 'thyron-tile',
                can_focus: true,
                track_hover: true,
            });
            btn.set_size(TILE_W, TILE_H);
            const box = new St.BoxLayout({vertical: true, x_expand: true});
            box.add_child(new St.Icon({
                gicon: iconOf(e.app),
                icon_size: 48,
                x_align: Clutter.ActorAlign.CENTER,
            }));
            box.add_child(ellipsized(e.name, 'thyron-tile-name', {
                x_align: Clutter.ActorAlign.CENTER,
            }));
            box.add_child(ellipsized(this._cat === ESSENTIAL_KEY && e.role ? e.role : e.cat, 'thyron-tile-cat', {
                x_align: Clutter.ActorAlign.CENTER,
            }));
            btn.set_child(box);
            if (e === this._selected)
                btn.add_style_class_name('thyron-tile-selected');
            this._wire(btn, () => {
                log(`[THYRON] tile: ${e.name}`);
                this._select(e);
            });
            row.add_child(btn);
            this._tiles.set(e, btn);
        });
    }

    _select(entry) {
        this._selected = entry;
        this._moreInfo = false;
        for (const [e, btn] of this._tiles) {
            if (e === entry)
                btn.add_style_class_name('thyron-tile-selected');
            else
                btn.remove_style_class_name('thyron-tile-selected');
        }
        this._renderDetails();
    }

    _renderPager(pages) {
        this._pager.destroy_all_children();
        if (pages <= 1)
            return;

        const make = (text, page, active = false) => {
            const b = new St.Button({
                label: text,
                style_class: 'thyron-page' + (active ? ' thyron-page-active' : ''),
                can_focus: true,
                track_hover: true,
            });
            this._wire(b, () => {
                log(`[THYRON] pagina: ${page + 1}`);
                // adia a reconstrução: o próprio botão é destruído por ela
                this._later(() => {
                    this._page = page;
                    this._refresh();
                });
            });
            return b;
        };

        if (this._page > 0)
            this._pager.add_child(make('‹', this._page - 1));

        const shown = new Set([0, pages - 1, this._page - 1, this._page, this._page + 1]);
        const nums = [...shown].filter(p => p >= 0 && p < pages).sort((a, b) => a - b);
        let prev = -1;
        for (const p of nums) {
            if (p - prev > 1)
                this._pager.add_child(new St.Label({text: '…', style_class: 'thyron-page-gap'}));
            this._pager.add_child(make(String(p + 1), p, p === this._page));
            prev = p;
        }

        if (this._page < pages - 1)
            this._pager.add_child(make('›', this._page + 1));
    }

    _renderDetails() {
        const d = this._detail;
        d.destroy_all_children();
        const e = this._selected;
        if (!e) {
            d.add_child(new St.Label({
                text: 'Nenhum aplicativo selecionado',
                style_class: 'thyron-empty',
            }));
            return;
        }

        const app = e.app;
        d.add_child(new St.Bin({
            style_class: 'thyron-d-iconbox',
            x_align: Clutter.ActorAlign.CENTER,
            child: new St.Icon({gicon: iconOf(app), icon_size: 72}),
        }));

        const title = new St.Label({
            text: e.name, style_class: 'thyron-d-title', x_align: Clutter.ActorAlign.CENTER,
        });
        title.clutter_text.line_wrap = true;
        title.clutter_text.line_wrap_mode = Pango.WrapMode.WORD_CHAR;
        d.add_child(title);
        const generic = app.get_generic_name?.();
        if (generic && generic !== e.name) {
            d.add_child(new St.Label({
                text: generic, style_class: 'thyron-d-name', x_align: Clutter.ActorAlign.CENTER,
            }));
        }

        const openRow = new St.BoxLayout({x_align: Clutter.ActorAlign.CENTER});
        openRow.add_child(new St.Icon({
            gicon: themedIcon(['media-playback-start-symbolic']), icon_size: 16,
            style_class: 'thyron-open-icon', y_align: Clutter.ActorAlign.CENTER,
        }));
        openRow.add_child(new St.Label({text: 'Abrir', y_align: Clutter.ActorAlign.CENTER}));
        const open = new St.Button({
            child: openRow,
            style_class: 'thyron-open',
            can_focus: true,
            track_hover: true,
            x_expand: true,
        });
        this._wire(open, () => this._launch(app));
        d.add_child(open);

        const isFav = this._isFav(e);
        const fav = new St.Button({
            label: isFav ? '★  Remover dos favoritos' : '☆  Adicionar aos favoritos',
            style_class: 'thyron-fav' + (isFav ? ' thyron-fav-on' : ''),
            can_focus: true,
            track_hover: true,
            x_expand: true,
        });
        this._wire(fav, () => {
            this._toggleFav(e);
            this._later(() => this._refresh());
        });
        d.add_child(fav);

        d.add_child(new St.Widget({style_class: 'thyron-d-sep', height: 1}));
        d.add_child(infoRow('Categoria', e.cat));
        if (e.role)
            d.add_child(infoRow('Função', e.role));
        d.add_child(infoRow('Identificador', (app.get_id() ?? '—').replace(/\.desktop$/, '')));
        d.add_child(infoRow('Comando', app.get_commandline?.() ?? '—'));

        d.add_child(new St.Label({text: 'Descrição', style_class: 'thyron-d-section'}));
        d.add_child(wrapLabel(app.get_description() || 'Sem descrição disponível.', 'thyron-d-desc'));

        d.add_child(new St.Widget({style_class: 'thyron-d-sep', height: 1}));
        const more = new St.Button({
            label: this._moreInfo ? 'ⓘ  Mostrar menos' : 'ⓘ  Saiba mais',
            style_class: 'thyron-more',
            can_focus: true,
            track_hover: true,
            x_expand: true,
        });
        this._wire(more, () => {
            this._moreInfo = !this._moreInfo;
            this._later(() => this._renderDetails());
        });
        d.add_child(more);
        if (this._moreInfo) {
            d.add_child(infoRow('Arquivo', app.get_filename?.() ?? '—'));
            d.add_child(infoRow('Nome completo', app.get_display_name?.() ?? e.name));
        }
    }

    // Registra a ação de um botão: usada pelo despachante e, como reserva,
    // pelo sinal 'clicked' (o despachante bloqueia o clique para não duplicar).
    _wire(actor, fn) {
        actor._thyronClick = fn;
        actor.connect('clicked', fn);
    }

    _onOverlayEvent(ev) {
        const t = ev.type();
        if (t !== Clutter.EventType.BUTTON_PRESS && t !== Clutter.EventType.BUTTON_RELEASE)
            return Clutter.EVENT_PROPAGATE;
        if (ev.get_button() !== Clutter.BUTTON_PRIMARY)
            return Clutter.EVENT_PROPAGATE;

        const [x, y] = ev.get_coords();
        const picked = global.stage.get_actor_at_pos(Clutter.PickMode.REACTIVE, x, y);
        let action = null;
        let inPanel = false;
        for (let a = picked; a && a !== this._overlay; a = a.get_parent()) {
            if (!action && a._thyronClick)
                action = a;
            if (a === this._panel)
                inPanel = true;
        }
        const isPress = t === Clutter.EventType.BUTTON_PRESS;
        // campo de busca e rolagem seguem o fluxo normal
        if (!action && inPanel)
            return Clutter.EVENT_PROPAGATE;
        if (!action && !inPanel) {
            // clique fora do painel fecha (na soltura)
            if (!isPress) {
                log('[THYRON] clique fora do painel: fechando');
                this._later(() => this._close());
            }
            return Clutter.EVENT_STOP;
        }
        if (isPress) {
            this._pressed = action;
            return Clutter.EVENT_STOP;
        }
        const same = this._pressed === action;
        this._pressed = null;
        if (same) {
            log(`[THYRON] clique despachado em ${action.constructor?.name}`);
            this._later(() => action._thyronClick?.());
        }
        return Clutter.EVENT_STOP;
    }

    // Executa fn fora do handler de clique atual (evita destruir um ator
    // dentro do próprio sinal 'clicked').
    _later(fn) {
        this._laterIds ??= new Set();
        const id = GLib.idle_add(GLib.PRIORITY_DEFAULT, () => {
            this._laterIds?.delete(id);
            try {
                fn();
            } catch (e) {
                log(`[THYRON] erro: ${e.message}\n${e.stack}`);
            }
            return GLib.SOURCE_REMOVE;
        });
        this._laterIds.add(id);
    }

    _launch(app) {
        log(`[THYRON] abrir: ${app.get_id()}`);
        this._recordRecent(app.get_id());
        this._later(() => {
            this._close();
            try {
                app.launch([], global.create_app_launch_context(0, -1));
            } catch (e) {
                log(`[THYRON] falha ao abrir ${app.get_id()}: ${e.message}`);
                Main.notifyError('THYRON', `Falha ao abrir ${app.get_name()}: ${e.message}`);
            }
        });
    }

    _close() {
        if (this._grab) {
            Main.popModal(this._grab);
            this._grab = null;
        }
        this._overlay?.destroy();
        this._overlay = null;
        this._panel = null;
        this._pressed = null;
        this._entry = null;
        this._gridBox = null;
        this._pager = null;
        this._detail = null;
        this._navBox = null;
        this._subtitle = null;
        this._sortBtn = null;
        this._modeBtns = null;
        this._tiles = null;
        this._navButtons = null;
    }

    disable() {
        for (const [obj, id] of this._hooks ?? []) {
            try {
                obj.disconnect(id);
            } catch (e) {
                // objeto já destruído
            }
        }
        this._hooks = null;
        this._hooked = null;
        if (this._tickId)
            GLib.source_remove(this._tickId);
        this._tickId = 0;
        if (this._idleId)
            GLib.source_remove(this._idleId);
        this._idleId = 0;
        if (this._retryId)
            GLib.source_remove(this._retryId);
        this._retryId = 0;
        for (const id of this._laterIds ?? [])
            GLib.source_remove(id);
        this._laterIds = null;
        this._busy = false;
        this._close();
        this._button?.destroy();
        this._button = null;
        this._apps = null;
        this._selected = null;
    }
}
