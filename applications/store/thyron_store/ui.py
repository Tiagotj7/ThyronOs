import sys

CSS = """
window { background: #07111f; color: #e8f2ff; }
.header { background: #0b1d31; }
.sidebar { background: #09182a; }
.title { color: #f2f7ff; font-weight: 700; }
.muted { color: #91a9c4; }
.card { background: #102943; border: 1px solid #17466b; border-radius: 12px; padding: 12px; }
button.suggested-action { background: #087fca; }
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

    class StoreWindow(Gtk.ApplicationWindow):
        def __init__(self, app):
            super().__init__(application=app, title="THYRON Store")
            self.set_default_size(1080, 700)
            self.set_size_request(760, 520)

            provider = Gtk.CssProvider()
            provider.load_from_data(CSS.encode())
            Gtk.StyleContext.add_provider_for_display(
                Gdk.Display.get_default(), provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
            )

            outer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
            self.set_child(outer)

            sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
            sidebar.add_css_class("sidebar")
            sidebar.set_size_request(210, -1)
            sidebar.set_margin_top(22); sidebar.set_margin_bottom(18)
            sidebar.set_margin_start(16); sidebar.set_margin_end(12)
            brand = Gtk.Label(label="THYRON STORE")
            brand.add_css_class("title")
            sidebar.append(brand)
            for label in ("Visão geral", "Todos os aplicativos", "Instalados", "Atualizações", "Favoritos", "Configurações"):
                button = Gtk.Button(label=label)
                button.set_halign(Gtk.Align.FILL)
                sidebar.append(button)
            outer.append(sidebar)

            content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
            content.set_margin_top(22); content.set_margin_end(22)
            content.set_margin_bottom(18)
            outer.append(content)

            heading = Gtk.Label(label="Aplicativos")
            heading.add_css_class("title")
            heading.set_halign(Gtk.Align.START)
            content.append(heading)

            search = Gtk.SearchEntry()
            search.set_placeholder_text("Pesquisar aplicativos…")
            content.append(search)

            info = Gtk.Label(label="Catálogo inicial — inventário local somente leitura")
            info.add_css_class("muted")
            info.set_halign(Gtk.Align.START)
            content.append(info)

            scroller = Gtk.ScrolledWindow()
            scroller.set_vexpand(True)
            content.append(scroller)
            listbox = Gtk.ListBox()
            listbox.set_selection_mode(Gtk.SelectionMode.NONE)
            listbox.set_spacing(8)
            scroller.set_child(listbox)

            desktop = list_desktop_apps()
            installed = list_installed()
            for entry in desktop[:120]:
                row = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
                row.add_css_class("card")
                name = Gtk.Label(label=entry.name)
                name.set_halign(Gtk.Align.START)
                name.add_css_class("title")
                desc = Gtk.Label(label=entry.summary or entry.app_id)
                desc.set_halign(Gtk.Align.START)
                desc.add_css_class("muted")
                row.append(name); row.append(desc)
                listbox.append(row)

            footer = Gtk.Label(
                label=f"{len(desktop)} atalhos gráficos · {len(installed)} pacotes inventariados"
            )
            footer.add_css_class("muted")
            footer.set_halign(Gtk.Align.START)
            content.append(footer)

            warning = Gtk.Label(label="Instalação, remoção e atualização ainda não estão habilitadas.")
            warning.add_css_class("muted")
            warning.set_halign(Gtk.Align.START)
            content.append(warning)

    application = Gtk.Application(application_id="org.thyron.Store")
    application.connect("activate", lambda app: StoreWindow(app).present())
    return application.run(sys.argv)
