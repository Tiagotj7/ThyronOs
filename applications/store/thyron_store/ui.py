import csv
import json
import sys
from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parent / "assets"
SETTINGS_FILE = Path.home() / ".config" / "thyron-store" / "settings.json"


def load_settings() -> dict:
    """Carrega preferências locais; usa padrões seguros em caso de erro."""
    try:
        data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return {"show_read_only_notice": bool(data.get("show_read_only_notice", True))}
    except (OSError, json.JSONDecodeError, TypeError):
        pass
    return {"show_read_only_notice": True}


def save_settings(settings: dict) -> None:
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary = SETTINGS_FILE.with_suffix(".json.tmp")
    temporary.write_text(
        json.dumps(settings, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    temporary.replace(SETTINGS_FILE)

CSS = """
window {
    background: #050d19;
    color: #edf5ff;
}
.sidebar {
    background: #07172a;
    border-right: 1px solid #123a60;
}
.title {
    color: #f3f8ff;
    font-weight: 700;
}
.muted {
    color: #9bb4d2;
}
.hero {
    background: #06172d;
    border: 1px solid #075b9d;
    border-radius: 16px;
}
.hero-title {
    color: #ffffff;
    font-size: 26px;
    font-weight: 800;
}
.hero-subtitle {
    color: #b8d4f6;
    font-size: 14px;
}
.card {
    background: #0b2340;
    border: 1px solid #075b91;
    border-radius: 14px;
    padding: 16px;
}
.stat-value {
    color: #ffffff;
    font-size: 25px;
    font-weight: 800;
}
.stat-title {
    color: #65c4ff;
    font-weight: 700;
}
button.nav-button {
    min-height: 42px;
    border-radius: 10px;
    background: #102943;
    color: #eaf4ff;
    border: 1px solid #183d60;
}
button.nav-button:hover {
    background: #153b60;
}
button.nav-button.active {
    background: #087fca;
    color: #ffffff;
    border-color: #159bfa;
}
.app-icon {
    background: #102943;
    border: 1px solid #15517d;
    border-radius: 10px;
    padding: 7px;
}
.app-meta {
    color: #76bce9;
    font-size: 12px;
}
button.details-button {
    background: #0d3157;
    color: #eaf5ff;
    border: 1px solid #087fc4;
    border-radius: 9px;
}
button.details-button:hover {
    background: #104779;
}

.installed-browser {
    background: transparent;
}
.installed-app-card {
    background: #071827;
    color: #edf5ff;
    border: 1px solid #123b5a;
    border-radius: 13px;
    padding: 12px 8px;
    min-height: 118px;
}
.installed-app-card:hover {
    background: #0b2d4b;
    border-color: #078fff;
}
.installed-app-icon {
    background: #0a2035;
    border-radius: 12px;
    padding: 8px;
}
.installed-app-name {
    color: #f4f8ff;
    font-weight: 700;
    font-size: 12px;
}
.installed-app-category {
    color: #8eafd0;
    font-size: 11px;
}
.detail-panel {
    background: #061522;
    border: 1px solid #12466b;
    border-radius: 14px;
    padding: 16px;
}
.detail-app-name {
    color: #ffffff;
    font-size: 20px;
    font-weight: 800;
}
.detail-app-summary {
    color: #9fc4e8;
    font-size: 13px;
}
.detail-section-title {
    color: #70c8ff;
    font-weight: 700;
    font-size: 12px;
}
.sort-control {
    color: #edf5ff;
}
button.favorite-button {
    color: #ffd34e;
    font-size: 20px;
    font-weight: 700;
}
button.feature-button {
    min-height: 58px;
    background: #0d3157;
    color: #eaf5ff;
    border: 1px solid #087fc4;
    border-radius: 12px;
    font-weight: 700;
}
button.feature-button:hover {
    background: #104779;
}
.installed-page-title {
    color: #f4f8ff;
    font-size: 23px;
    font-weight: 800;
}
.installed-page-subtitle {
    color: #9bb4d2;
    font-size: 12px;
}
.installed-app-card {
    min-height: 142px;
}
.installed-app-icon {
    padding: 9px;
}
button.toggle {
    color: #eaf5ff;
    background: #0b2038;
    border: 1px solid #15517d;
    border-radius: 8px;
}
button.toggle:checked {
    background: #075b9d;
    border-color: #079cff;
}
entry {
    background: #0b2038;
    color: #f3f8ff;
    border: 1px solid #15517d;
    border-radius: 10px;
}
scrolledwindow {
    border: none;
}
"""

def main() -> int:
    try:
        import gi
        gi.require_version("Gtk", "4.0")
        from gi.repository import Gtk, Gdk
    except (ImportError, ValueError) as exc:
        print("THYRON Store: GTK 4 / PyGObject não está disponível.", file=sys.stderr)
        print(f"Detalhe: {exc}", file=sys.stderr)
        return 2

    from .catalog import list_desktop_apps, list_installed
    from .favorites import load_favorites, save_favorites, favorite_key

    class StoreWindow(Gtk.ApplicationWindow):
        def __init__(self, app):
            super().__init__(application=app, title="THYRON Store")
            # GTK 4/window-manager compatibility: use the named icon when the
            # backend exposes the legacy window icon hook. On GTK 4 backends
            # without it, the desktop entry (Icon=thyron-store) supplies the
            # application icon to the shell/window manager.
            set_icon_name = getattr(self, "set_icon_name", None)
            if callable(set_icon_name):
                set_icon_name("thyron-store")
            self.set_default_size(1080, 560)
            self.set_size_request(760, 520)

            provider = Gtk.CssProvider()
            provider.load_from_data(CSS.encode())
            Gtk.StyleContext.add_provider_for_display(
                Gdk.Display.get_default(),
                provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
            )

            self.desktop = list_desktop_apps()
            self.installed = list_installed()
            self.favorites = load_favorites()
            self.settings = load_settings()
            self.current_page = "overview"
            self.nav_buttons = {}
            self.selected_installed_key = None
            self.installed_sort_index = 0
            self.installed_view_mode = "grid"

            outer = Gtk.Box(
                orientation=Gtk.Orientation.HORIZONTAL,
                spacing=0,
            )
            self.set_child(outer)

            sidebar = Gtk.Box(
                orientation=Gtk.Orientation.VERTICAL,
                spacing=12,
            )
            sidebar.add_css_class("sidebar")
            sidebar.set_size_request(218, -1)
            sidebar.set_margin_top(18)
            sidebar.set_margin_bottom(18)
            sidebar.set_margin_start(14)
            sidebar.set_margin_end(12)

            logo_path = ASSETS_DIR / "thyron-store-logo.png"
            if logo_path.is_file():
                logo = Gtk.Picture()
                logo.set_filename(str(logo_path))
                logo.set_content_fit(Gtk.ContentFit.CONTAIN)
                logo.set_size_request(190, 104)
                logo.set_can_shrink(True)
                sidebar.append(logo)
            else:
                brand = Gtk.Label(label="THYRON STORE")
                brand.add_css_class("title")
                sidebar.append(brand)

            navigation = (
                ("overview", "⌂   Visão geral"),
                ("all", "▦   Todos os aplicativos"),
                ("installed", "✓   Instalados"),
                ("updates", "↻   Atualizações"),
                ("favorites", "★   Favoritos"),
                ("settings", "⚙   Configurações"),
            )

            for page_id, label in navigation:
                button = Gtk.Button(label=label)
                button.add_css_class("nav-button")
                button.set_halign(Gtk.Align.FILL)
                button.connect("clicked", self.on_nav_clicked, page_id)
                sidebar.append(button)
                self.nav_buttons[page_id] = button

            outer.append(sidebar)

            content = Gtk.Box(
                orientation=Gtk.Orientation.VERTICAL,
                spacing=12,
            )
            content.set_hexpand(True)
            content.set_margin_top(16)
            content.set_margin_end(18)
            content.set_margin_bottom(14)
            content.set_margin_start(4)
            outer.append(content)

            hero = Gtk.Overlay()
            hero.add_css_class("hero")
            hero.set_size_request(-1, 166)
            hero.set_hexpand(True)

            # O conteúdo principal define a altura do banner. A imagem é
            # uma sobreposição e não pode impor sua altura natural (panorâmica).
            hero_base = Gtk.Box()
            hero_base.set_size_request(-1, 166)
            hero.set_child(hero_base)

            banner_path = ASSETS_DIR / "thyron-wolf-banner.png"
            if banner_path.is_file():
                banner = Gtk.Picture()
                banner.set_filename(str(banner_path))
                banner.set_content_fit(Gtk.ContentFit.COVER)
                banner.set_can_shrink(True)
                banner.set_hexpand(True)
                banner.set_vexpand(True)
                banner.set_halign(Gtk.Align.FILL)
                banner.set_valign(Gtk.Align.FILL)
                hero.add_overlay(banner)
                hero.set_measure_overlay(banner, False)

            hero_text = Gtk.Box(
                orientation=Gtk.Orientation.VERTICAL,
                spacing=7,
            )
            hero_text.set_halign(Gtk.Align.START)
            hero_text.set_valign(Gtk.Align.CENTER)
            hero_text.set_margin_start(22)
            hero_text.set_margin_top(12)
            hero_text.set_margin_bottom(12)

            self.heading = Gtk.Label(label="Visão geral")
            self.heading.add_css_class("hero-title")
            self.heading.set_halign(Gtk.Align.START)

            self.info = Gtk.Label(label="Bem-vindo à THYRON Store.")
            self.info.add_css_class("hero-subtitle")
            self.info.set_halign(Gtk.Align.START)
            self.info.set_wrap(True)

            hero_text.append(self.heading)
            hero_text.append(self.info)
            hero.add_overlay(hero_text)
            content.append(hero)

            self.search = Gtk.SearchEntry()
            self.search.set_placeholder_text("Pesquisar aplicativos...")
            self.search.set_hexpand(True)
            self.search.connect("search-changed", self.on_search_changed)
            content.append(self.search)

            scroller = Gtk.ScrolledWindow()
            scroller.set_hexpand(True)
            scroller.set_vexpand(True)
            content.append(scroller)

            self.listbox = Gtk.ListBox()
            self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)
            self.listbox.set_hexpand(True)
            self.listbox.add_css_class("catalog-list")
            scroller.set_child(self.listbox)

            self.results_label = Gtk.Label()
            self.results_label.add_css_class("muted")
            self.results_label.set_halign(Gtk.Align.START)
            content.append(self.results_label)

            self.footer = Gtk.Label()
            self.footer.add_css_class("muted")
            self.footer.set_halign(Gtk.Align.START)
            content.append(self.footer)

            self.notice = Gtk.Label(
                label=(
                    "Modo de leitura: instalação, remoção e atualização "
                    "de pacotes ainda não estão habilitadas."
                )
            )
            self.notice.add_css_class("muted")
            self.notice.set_halign(Gtk.Align.START)
            self.notice.set_wrap(True)
            self.notice.set_visible(self.settings["show_read_only_notice"])
            content.append(self.notice)

            self.show_page("overview")

        def on_nav_clicked(self, button, page_id):
            self.show_page(page_id)

        def on_search_changed(self, search_entry):
            self.render_page()

        def show_page(self, page_id):
            self.current_page = page_id
            self.search.set_text("")

            for key, button in self.nav_buttons.items():
                if key == page_id:
                    button.add_css_class("active")
                else:
                    button.remove_css_class("active")

            searchable = page_id in ("all", "installed", "favorites")
            self.search.set_visible(searchable)
            self.results_label.set_visible(searchable)
            self.render_page()

        def clear_list(self):
            child = self.listbox.get_first_child()
            while child is not None:
                next_child = child.get_next_sibling()
                self.listbox.remove(child)
                child = next_child

        def add_card(self, title, description):
            card = Gtk.Box(
                orientation=Gtk.Orientation.VERTICAL,
                spacing=7,
            )
            card.add_css_class("card")
            card.set_hexpand(True)

            name = Gtk.Label(label=title)
            name.set_halign(Gtk.Align.START)
            name.add_css_class("stat-title")
            name.set_wrap(True)

            detail = Gtk.Label(label=description)
            detail.set_halign(Gtk.Align.START)
            detail.set_wrap(True)
            detail.add_css_class("muted")

            card.append(name)
            card.append(detail)
            self.listbox.append(card)

        def add_stat_card(self, grid, column, row, title, value, description):
            card = Gtk.Box(
                orientation=Gtk.Orientation.VERTICAL,
                spacing=6,
            )
            card.add_css_class("card")
            card.set_hexpand(True)
            card.set_vexpand(True)

            label = Gtk.Label(label=title)
            label.add_css_class("stat-title")
            label.set_halign(Gtk.Align.START)

            number = Gtk.Label(label=value)
            number.add_css_class("stat-value")
            number.set_halign(Gtk.Align.START)

            detail = Gtk.Label(label=description)
            detail.add_css_class("muted")
            detail.set_halign(Gtk.Align.START)
            detail.set_wrap(True)

            card.append(label)
            card.append(number)
            card.append(detail)
            grid.attach(card, column, row, 1, 1)

        def add_feature_buttons(self):
            row = Gtk.Box(
                orientation=Gtk.Orientation.HORIZONTAL,
                spacing=10,
            )
            row.set_hexpand(True)
            for label, page_id in (
                ("Explorar aplicativos  →", "all"),
                ("Abrir favoritos  →", "favorites"),
                ("Configurações  →", "settings"),
            ):
                button = Gtk.Button(label=label)
                button.add_css_class("feature-button")
                button.set_hexpand(True)
                button.connect("clicked", self.on_nav_clicked, page_id)
                row.append(button)
            self.listbox.append(row)

        def make_app_icon(self, entry, pixel_size=42):
            icon_path = Path(entry.icon_name) if entry.icon_name else None
            if icon_path is not None and icon_path.is_file():
                icon = Gtk.Picture()
                icon.set_filename(str(icon_path))
                icon.set_content_fit(Gtk.ContentFit.CONTAIN)
                icon.set_size_request(pixel_size, pixel_size)
            else:
                icon = Gtk.Image.new_from_icon_name(
                    entry.icon_name or "application-x-executable"
                )
                icon.set_pixel_size(pixel_size)
            return icon

        def add_app_card(self, entry):
            key = favorite_key(entry)
            is_favorite = key in self.favorites

            card = Gtk.Box(
                orientation=Gtk.Orientation.HORIZONTAL,
                spacing=12,
            )
            card.add_css_class("card")
            card.set_hexpand(True)

            icon = self.make_app_icon(entry, 42)
            icon.add_css_class("app-icon")
            card.append(icon)

            details = Gtk.Box(
                orientation=Gtk.Orientation.VERTICAL,
                spacing=4,
            )
            details.set_hexpand(True)

            name = Gtk.Label(label=entry.name)
            name.set_halign(Gtk.Align.START)
            name.add_css_class("title")
            name.set_wrap(True)

            description = Gtk.Label(
                label=entry.summary or entry.app_id
            )
            description.set_halign(Gtk.Align.START)
            description.set_wrap(True)
            description.add_css_class("muted")

            meta = Gtk.Label(label=f"{entry.source}  •  {entry.version or ('Instalado' if entry.installed else 'Não instalado')}")
            meta.set_halign(Gtk.Align.START)
            meta.add_css_class("app-meta")
            meta.set_wrap(True)

            details.append(name)
            details.append(description)
            details.append(meta)
            card.append(details)

            details_button = Gtk.Button(label="Detalhes")
            details_button.add_css_class("details-button")
            details_button.connect("clicked", self.on_details_clicked, entry)
            card.append(details_button)

            favorite_button = Gtk.Button(
                label="★" if is_favorite else "☆"
            )
            favorite_button.add_css_class("favorite-button")
            favorite_button.set_tooltip_text(
                "Remover dos favoritos" if is_favorite
                else "Adicionar aos favoritos"
            )
            favorite_button.connect(
                "clicked",
                self.on_favorite_clicked,
                entry,
            )
            card.append(favorite_button)
            self.listbox.append(card)

        def category_label(self, categories: str) -> str:
            """Converte categorias .desktop comuns em rótulos amigáveis."""
            raw = (categories or "").split(";", 1)[0].strip()
            labels = {
                "AudioVideo": "Multimídia",
                "Audio": "Multimídia",
                "Video": "Multimídia",
                "Development": "Desenvolvimento",
                "Education": "Educação",
                "Game": "Jogos",
                "Graphics": "Gráficos",
                "Network": "Internet",
                "Office": "Escritório",
                "Science": "Ciência",
                "Settings": "Sistema",
                "System": "Sistema",
                "Utility": "Utilitários",
            }
            return labels.get(raw, raw or "Aplicativo")

        def on_installed_sort_changed(self, dropdown, _pspec):
            self.installed_sort_index = dropdown.get_selected()
            self.render_page()

        def on_installed_app_selected(self, button, entry):
            self.selected_installed_key = favorite_key(entry)
            self.render_page()

        def render_installed_details(self, panel, entry):
            child = panel.get_first_child()
            while child is not None:
                following = child.get_next_sibling()
                panel.remove(child)
                child = following

            icon = self.make_app_icon(entry, 88)
            icon.set_halign(Gtk.Align.CENTER)
            panel.append(icon)

            title = Gtk.Label(label=entry.name)
            title.add_css_class("detail-app-name")
            title.set_halign(Gtk.Align.START)
            title.set_wrap(True)
            panel.append(title)

            category = Gtk.Label(label=self.category_label(entry.categories))
            category.add_css_class("detail-app-summary")
            category.set_halign(Gtk.Align.START)
            panel.append(category)

            status = Gtk.Label(label="●  Instalado")
            status.add_css_class("detail-app-summary")
            status.set_halign(Gtk.Align.START)
            panel.append(status)

            separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
            panel.append(separator)

            description_title = Gtk.Label(label="DESCRIÇÃO")
            description_title.add_css_class("detail-section-title")
            description_title.set_halign(Gtk.Align.START)
            panel.append(description_title)

            description = Gtk.Label(
                label=entry.summary or "Não há descrição disponível para este aplicativo."
            )
            description.set_halign(Gtk.Align.START)
            description.set_wrap(True)
            description.add_css_class("muted")
            panel.append(description)

            metadata = (
                ("Identificador", entry.app_id),
                ("Origem", entry.source or "Sistema"),
                ("Versão", entry.version or "Gerenciada pelo sistema"),
                ("Categoria", self.category_label(entry.categories)),
            )
            for label_text, value_text in metadata:
                label = Gtk.Label(label=label_text.upper())
                label.add_css_class("detail-section-title")
                label.set_halign(Gtk.Align.START)
                value = Gtk.Label(label=value_text)
                value.add_css_class("muted")
                value.set_halign(Gtk.Align.START)
                value.set_wrap(True)
                panel.append(label)
                panel.append(value)

            note = Gtk.Label(
                label="Ações de instalação e remoção permanecem desativadas nesta versão."
            )
            note.add_css_class("muted")
            note.set_wrap(True)
            panel.append(note)

        def on_installed_view_changed(self, button, mode):
            if not button.get_active():
                return
            self.installed_view_mode = mode
            self.render_page()

        def export_installed_list(self, button):
            dialog = Gtk.FileChooserNative.new(
                "Exportar aplicativos instalados",
                self,
                Gtk.FileChooserAction.SAVE,
                "_Exportar",
                "_Cancelar",
            )
            dialog.set_current_name("thyron-aplicativos-instalados.csv")

            def on_response(native_dialog, response):
                if response == Gtk.ResponseType.ACCEPT:
                    selected_file = native_dialog.get_file()
                    destination = selected_file.get_path() if selected_file else None
                    if destination:
                        try:
                            with open(destination, "w", newline="", encoding="utf-8-sig") as stream:
                                writer = csv.writer(stream, delimiter=";")
                                writer.writerow(["Aplicativo", "Categoria", "Identificador", "Origem", "Versão"])
                                for entry in sorted(self.desktop, key=lambda item: item.name.casefold()):
                                    if entry.installed:
                                        writer.writerow([
                                            entry.name,
                                            self.category_label(entry.categories),
                                            entry.app_id,
                                            entry.source,
                                            entry.version,
                                        ])
                            self.notice.set_text(f"Lista exportada: {destination}")
                            self.notice.set_visible(True)
                        except OSError as exc:
                            self.notice.set_text(f"Não foi possível exportar a lista: {exc}")
                            self.notice.set_visible(True)
                native_dialog.hide()

            dialog.connect("response", on_response)
            dialog.show()

        def add_installed_browser(self, matches):
            browser = Gtk.Box(
                orientation=Gtk.Orientation.HORIZONTAL,
                spacing=14,
            )
            browser.add_css_class("installed-browser")
            browser.set_hexpand(True)

            main_column = Gtk.Box(
                orientation=Gtk.Orientation.VERTICAL,
                spacing=12,
            )
            main_column.set_hexpand(True)

            page_header = Gtk.Box(
                orientation=Gtk.Orientation.HORIZONTAL,
                spacing=10,
            )
            page_heading = Gtk.Box(
                orientation=Gtk.Orientation.VERTICAL,
                spacing=3,
            )
            page_title = Gtk.Label(label="Aplicativos Instalados")
            page_title.add_css_class("installed-page-title")
            page_title.set_halign(Gtk.Align.START)
            page_subtitle = Gtk.Label(
                label="Gerencie e consulte os aplicativos gráficos disponíveis no sistema."
            )
            page_subtitle.add_css_class("installed-page-subtitle")
            page_subtitle.set_halign(Gtk.Align.START)
            page_subtitle.set_wrap(True)
            page_heading.append(page_title)
            page_heading.append(page_subtitle)
            page_header.append(page_heading)
            page_header.set_hexpand(True)

            export_button = Gtk.Button(label="⬇  Exportar lista")
            export_button.add_css_class("details-button")
            export_button.set_valign(Gtk.Align.CENTER)
            export_button.connect("clicked", self.export_installed_list)
            page_header.append(export_button)
            main_column.append(page_header)

            toolbar = Gtk.Box(
                orientation=Gtk.Orientation.HORIZONTAL,
                spacing=8,
            )
            toolbar.set_hexpand(True)
            toolbar.append(Gtk.Label(label="Exibir:"))
            grid_button = Gtk.ToggleButton(label="▦")
            grid_button.set_tooltip_text("Visualização em grade")
            list_button = Gtk.ToggleButton(label="☷")
            list_button.set_tooltip_text("Visualização em lista")
            grid_button.set_group(list_button)
            grid_button.set_active(self.installed_view_mode == "grid")
            list_button.set_active(self.installed_view_mode == "list")
            grid_button.connect("toggled", self.on_installed_view_changed, "grid")
            list_button.connect("toggled", self.on_installed_view_changed, "list")
            toolbar.append(grid_button)
            toolbar.append(list_button)
            spacer = Gtk.Box()
            spacer.set_hexpand(True)
            toolbar.append(spacer)
            sort_label = Gtk.Label(label="Ordenar por:")
            sort_label.add_css_class("muted")
            toolbar.append(sort_label)
            sort = Gtk.DropDown.new_from_strings(
                ["Nome A–Z", "Nome Z–A", "Categoria"]
            )
            sort.add_css_class("sort-control")
            sort.set_selected(min(self.installed_sort_index, 2))
            sort.connect("notify::selected", self.on_installed_sort_changed)
            toolbar.append(sort)
            main_column.append(toolbar)

            flow = Gtk.FlowBox()
            flow.set_selection_mode(Gtk.SelectionMode.NONE)
            flow.set_homogeneous(self.installed_view_mode == "grid")
            flow.set_min_children_per_line(1 if self.installed_view_mode == "list" else 2)
            flow.set_max_children_per_line(1 if self.installed_view_mode == "list" else 6)
            flow.set_row_spacing(10)
            flow.set_column_spacing(10)
            flow.set_activate_on_single_click(True)
            flow.set_hexpand(True)

            for entry in matches:
                card_content = Gtk.Box(
                    orientation=(Gtk.Orientation.HORIZONTAL if self.installed_view_mode == "list" else Gtk.Orientation.VERTICAL),
                    spacing=12 if self.installed_view_mode == "list" else 7,
                )
                card_content.set_halign(Gtk.Align.FILL if self.installed_view_mode == "list" else Gtk.Align.CENTER)
                card_content.set_valign(Gtk.Align.CENTER)

                icon = self.make_app_icon(entry, 64 if self.installed_view_mode == "grid" else 48)
                icon.add_css_class("installed-app-icon")
                icon.set_halign(Gtk.Align.CENTER)
                card_content.append(icon)

                text_column = Gtk.Box(
                    orientation=Gtk.Orientation.VERTICAL,
                    spacing=4,
                )
                text_column.set_hexpand(True)
                name = Gtk.Label(label=entry.name)
                name.add_css_class("installed-app-name")
                name.set_max_width_chars(24)
                name.set_halign(Gtk.Align.CENTER if self.installed_view_mode == "grid" else Gtk.Align.START)
                name.set_wrap(True)
                text_column.append(name)

                category = Gtk.Label(label=self.category_label(entry.categories))
                category.add_css_class("installed-app-category")
                category.set_halign(Gtk.Align.CENTER if self.installed_view_mode == "grid" else Gtk.Align.START)
                text_column.append(category)
                card_content.append(text_column)

                card = Gtk.Button()
                card.add_css_class("installed-app-card")
                card.set_hexpand(True)
                card.set_child(card_content)
                card.connect("clicked", self.on_installed_app_selected, entry)
                flow.append(card)

            main_column.append(flow)
            browser.append(main_column)

            details = Gtk.Box(
                orientation=Gtk.Orientation.VERTICAL,
                spacing=10,
            )
            details.add_css_class("detail-panel")
            details.set_size_request(248, -1)
            details.set_vexpand(True)
            browser.append(details)

            selected = next(
                (entry for entry in matches
                 if favorite_key(entry) == self.selected_installed_key),
                matches[0] if matches else None,
            )
            if selected is not None:
                self.selected_installed_key = favorite_key(selected)
                self.render_installed_details(details, selected)
            else:
                empty = Gtk.Label(label="Nenhum aplicativo encontrado.")
                empty.add_css_class("muted")
                empty.set_wrap(True)
                details.append(empty)

            self.listbox.append(browser)

        def on_details_clicked(self, button, entry):
            dialog = Gtk.Dialog(
                title=f"Detalhes — {entry.name}",
                transient_for=self,
                modal=True,
            )
            dialog.set_default_size(460, 360)
            dialog.add_button("Fechar", Gtk.ResponseType.CLOSE)
            dialog.connect("response", lambda window, _response: window.close())

            body = dialog.get_content_area()
            body.set_spacing(10)
            body.set_margin_top(18)
            body.set_margin_bottom(18)
            body.set_margin_start(18)
            body.set_margin_end(18)

            heading = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            app_icon = self.make_app_icon(entry, 56)
            heading.append(app_icon)

            title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            title = Gtk.Label(label=entry.name)
            title.add_css_class("title")
            title.set_halign(Gtk.Align.START)
            title.set_wrap(True)
            summary = Gtk.Label(label=entry.summary or "Sem descrição disponível.")
            summary.add_css_class("muted")
            summary.set_halign(Gtk.Align.START)
            summary.set_wrap(True)
            title_box.append(title)
            title_box.append(summary)
            heading.append(title_box)
            body.append(heading)

            fields = (
                ("Identificador", entry.app_id),
                ("Versão", entry.version or "Não informada"),
                ("Origem", entry.source),
                ("Estado", "Instalado" if entry.installed else "Não instalado"),
                ("Categorias", entry.categories or "Não informadas"),
                ("Arquivo .desktop", entry.desktop_file or "Não disponível"),
            )
            for label_text, value_text in fields:
                line = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
                label = Gtk.Label(label=label_text.upper())
                label.add_css_class("app-meta")
                label.set_halign(Gtk.Align.START)
                value = Gtk.Label(label=value_text)
                value.add_css_class("muted")
                value.set_halign(Gtk.Align.START)
                value.set_wrap(True)
                line.append(label)
                line.append(value)
                body.append(line)

            dialog.present()

        def on_favorite_clicked(self, button, entry):
            key = favorite_key(entry)

            if key in self.favorites:
                del self.favorites[key]
            else:
                self.favorites[key] = entry

            try:
                save_favorites(self.favorites)
            except OSError as exc:
                self.footer.set_text(
                    f"Não foi possível salvar os favoritos: {exc}"
                )
                self.render_page()
                return

            self.render_page()

        def show_empty(self, message):
            label = Gtk.Label(label=message)
            label.add_css_class("muted")
            label.set_wrap(True)
            label.set_margin_top(24)
            label.set_margin_bottom(24)
            self.listbox.append(label)

        def on_notice_setting_toggled(self, check_button):
            self.settings["show_read_only_notice"] = check_button.get_active()
            self.notice.set_visible(check_button.get_active())
            try:
                save_settings(self.settings)
                self.footer.set_text("Preferências salvas neste usuário.")
            except OSError as exc:
                self.footer.set_text(f"Não foi possível salvar a preferência: {exc}")

        def on_refresh_catalog_clicked(self, button):
            button.set_sensitive(False)
            button.set_label("Atualizando catálogo...")
            try:
                self.desktop = list_desktop_apps()
                self.installed = list_installed()
                self.render_page()
                self.footer.set_text(
                    f"Catálogo atualizado: {len(self.desktop)} atalhos e "
                    f"{len(self.installed)} pacotes inventariados."
                )
            except Exception as exc:
                self.footer.set_text(f"Falha ao atualizar o catálogo: {exc}")
            finally:
                button.set_sensitive(True)
                button.set_label("↻  Atualizar catálogo agora")

        def render_page(self):
            self.clear_list()
            query = self.search.get_text().strip().casefold()

            if self.current_page == "overview":
                self.heading.set_text("Visão geral")
                self.info.set_text("Bem-vindo à THYRON Store.")

                grid = Gtk.Grid()
                grid.set_column_spacing(12)
                grid.set_row_spacing(12)
                grid.set_column_homogeneous(True)
                grid.set_row_homogeneous(True)
                grid.set_hexpand(True)

                self.add_stat_card(
                    grid, 0, 0, "APLICATIVOS", str(len(self.desktop)),
                    "Atalhos gráficos encontrados no sistema"
                )
                self.add_stat_card(
                    grid, 1, 0, "PACOTES INSTALADOS", f"{len(self.installed):,}".replace(",", "."),
                    "Pacotes inventariados por APT/Flatpak"
                )
                self.add_stat_card(
                    grid, 0, 1, "FAVORITOS", str(len(self.favorites)),
                    "Aplicativos salvos nesta conta"
                )
                self.add_stat_card(
                    grid, 1, 1, "STATUS", "LOCAL",
                    "Catálogo em modo de leitura"
                )
                self.listbox.append(grid)

                section = Gtk.Label(label="Destaques da Store")
                section.add_css_class("title")
                section.set_halign(Gtk.Align.START)
                section.set_margin_top(8)
                section.set_margin_bottom(4)
                self.listbox.append(section)
                self.add_feature_buttons()

                self.footer.set_text(
                    "THYRON Store  •  Catálogo local"
                )

            elif self.current_page == "all":
                self.heading.set_text("Todos os aplicativos")
                self.info.set_text(
                    "Aplicativos gráficos encontrados nos arquivos .desktop. "
                    "Use a estrela para salvar um favorito."
                )

                matches = [
                    entry for entry in self.desktop
                    if not query or query in " ".join((
                        entry.name, entry.summary, entry.app_id
                    )).casefold()
                ]

                for entry in matches[:120]:
                    self.add_app_card(entry)

                if not matches:
                    self.show_empty("Nenhum aplicativo encontrado.")

                self.results_label.set_text(
                    f"{len(matches)} aplicativo(s) encontrado(s)"
                )
                self.footer.set_text(
                    f"{len(self.desktop)} atalhos gráficos no catálogo"
                )

            elif self.current_page == "installed":
                self.heading.set_text("Aplicativos instalados")
                self.info.set_text(
                    "Seus aplicativos gráficos disponíveis no sistema. "
                    "Selecione um cartão para ver os detalhes."
                )

                # A aba mostra lançadores gráficos .desktop, não cada biblioteca
                # ou dependência interna listada pelo dpkg.
                matches = [
                    entry for entry in self.desktop
                    if entry.installed and (
                        not query or query in " ".join((
                            entry.name, entry.summary, entry.app_id,
                            entry.categories,
                        )).casefold()
                    )
                ]

                if self.installed_sort_index == 1:
                    matches.sort(key=lambda item: item.name.casefold(), reverse=True)
                elif self.installed_sort_index == 2:
                    matches.sort(
                        key=lambda item: (
                            self.category_label(item.categories).casefold(),
                            item.name.casefold(),
                        )
                    )
                else:
                    matches.sort(key=lambda item: item.name.casefold())

                self.add_installed_browser(matches)
                self.results_label.set_text(
                    f"{len(matches)} aplicativo(s) instalado(s)"
                )
                self.footer.set_text(
                    f"{len(self.desktop)} atalhos gráficos encontrados • "
                    f"{len(self.installed)} pacotes no inventário APT/Flatpak"
                )

            elif self.current_page == "favorites":
                self.heading.set_text("Favoritos")
                self.info.set_text(
                    "Seus aplicativos salvos. As alterações ficam guardadas "
                    "neste usuário mesmo depois de fechar a Store."
                )

                matches = [
                    entry for entry in self.favorites.values()
                    if not query or query in " ".join((
                        entry.name, entry.summary, entry.app_id
                    )).casefold()
                ]
                matches.sort(key=lambda item: item.name.casefold())

                for entry in matches:
                    self.add_app_card(entry)

                if not matches:
                    self.show_empty(
                        "Nenhum favorito encontrado. "
                        "Adicione aplicativos usando a estrela no catálogo."
                    )

                self.results_label.set_text(
                    f"{len(matches)} favorito(s) encontrado(s)"
                )
                self.footer.set_text(
                    f"{len(self.favorites)} favorito(s) salvo(s)"
                )

            elif self.current_page == "updates":
                self.heading.set_text("Atualizações")
                self.info.set_text("Gerenciamento de atualizações")
                self.add_card(
                    "Verificação ainda não disponível",
                    "A Store ainda não consulta atualizações pendentes "
                    "nem executa operações APT ou Flatpak.",
                )
                self.footer.set_text(
                    "Nenhuma atualização foi verificada nesta versão."
                )

            elif self.current_page == "settings":
                self.heading.set_text("Configurações")
                self.info.set_text(
                    "Personalize o comportamento da THYRON Store. "
                    "As preferências ficam salvas neste usuário."
                )

                self.add_card(
                    "Modo de operação",
                    "Modo seguro de leitura: esta versão não instala, remove "
                    "nem altera pacotes do sistema.",
                )

                notice_row = Gtk.Box(
                    orientation=Gtk.Orientation.HORIZONTAL,
                    spacing=12,
                )
                notice_row.add_css_class("card")
                notice_row.set_hexpand(True)
                notice_text = Gtk.Box(
                    orientation=Gtk.Orientation.VERTICAL,
                    spacing=4,
                )
                notice_text.set_hexpand(True)
                notice_title = Gtk.Label(label="Aviso de modo de leitura")
                notice_title.add_css_class("stat-title")
                notice_title.set_halign(Gtk.Align.START)
                notice_description = Gtk.Label(
                    label="Mostrar o aviso informativo na parte inferior da janela."
                )
                notice_description.add_css_class("muted")
                notice_description.set_halign(Gtk.Align.START)
                notice_description.set_wrap(True)
                notice_text.append(notice_title)
                notice_text.append(notice_description)
                notice_row.append(notice_text)
                notice_toggle = Gtk.CheckButton()
                notice_toggle.set_valign(Gtk.Align.CENTER)
                notice_toggle.set_active(self.settings["show_read_only_notice"])
                notice_toggle.set_tooltip_text("Mostrar ou ocultar o aviso")
                notice_toggle.connect("toggled", self.on_notice_setting_toggled)
                notice_row.append(notice_toggle)
                self.listbox.append(notice_row)

                refresh_row = Gtk.Box(
                    orientation=Gtk.Orientation.VERTICAL,
                    spacing=7,
                )
                refresh_row.add_css_class("card")
                refresh_title = Gtk.Label(label="Atualização do catálogo")
                refresh_title.add_css_class("stat-title")
                refresh_title.set_halign(Gtk.Align.START)
                refresh_description = Gtk.Label(
                    label="Lê novamente os atalhos .desktop e o inventário local "
                    "de pacotes APT/Flatpak, sem instalar ou modificar nada."
                )
                refresh_description.add_css_class("muted")
                refresh_description.set_halign(Gtk.Align.START)
                refresh_description.set_wrap(True)
                refresh_button = Gtk.Button(label="↻  Atualizar catálogo agora")
                refresh_button.add_css_class("details-button")
                refresh_button.set_halign(Gtk.Align.START)
                refresh_button.connect("clicked", self.on_refresh_catalog_clicked)
                refresh_row.append(refresh_title)
                refresh_row.append(refresh_description)
                refresh_row.append(refresh_button)
                self.listbox.append(refresh_row)

                self.add_card(
                    "Dados e privacidade",
                    f"Preferências: {SETTINGS_FILE}\n"
                    "Favoritos: ~/.local/share/thyron-store/favorites.json",
                )
                self.footer.set_text(
                    "Configurações carregadas. As alterações são salvas automaticamente."
                )

    application = Gtk.Application(
        application_id="org.thyron.Store"
    )
    application.connect(
        "activate",
        lambda app: StoreWindow(app).present(),
    )

    return application.run(sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())
